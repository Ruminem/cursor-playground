# SPDX-License-Identifier: Apache-2.0
# 시안 페이지 버튼(cursor-playground:// 주소)을 받아 커서 구성표를 적용하거나 되돌린다.
# setup.ps1 이 이 파일을 %LOCALAPPDATA%\cursor-playground 에 내려받고 -Setup 으로 실행한다.
#
# 받는 주소는 아래 여섯 가지뿐이다. 어느 웹 페이지든 이 주소를 부를 수 있으므로 그 밖의 요청은 전부 무시한다.
#   cursor-playground://apply/<구성표>/<방문>[/<크기>]  커서를 내려받아 구성표로 등록하고 바로 적용 (구성표는 schemes.json 에 있는 것만)
#   cursor-playground://size/<크기>/<방문>      포인터 크기만 바꿈. <크기> 는 32, 48, 64, 96, 128 중 하나
#   cursor-playground://restore/<방문>          그 방문에서 처음 적용하기 직전 상태로 되돌림
#   cursor-playground://status                  지금 상태를 알림 창으로 보여 줌
#   cursor-playground://settings                마우스 속성 창을 포인터 탭으로 엶
#   cursor-playground://unlink                  설치할 때 상태로 되돌린 뒤 주소 연결과 설치 폴더까지 지움
# <방문> 은 페이지를 열 때마다 새로 만드는 16자리 번호. 같은 방문 안에서 여러 번 적용해도 백업은 처음 한 번만 뜬다.
#
# 이 파일은 한글 때문에 UTF-8 BOM 으로 저장해야 한다 (Windows PowerShell 5.1 은 BOM 이 없으면 ANSI 로 읽음).
[CmdletBinding(PositionalBinding = $false)]
param([string]$Url, [switch]$Setup)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'  # 내려받기 진행 표시가 꽤 느리게 만든다

$base = 'https://ruminem.github.io/cursor-playground/win-cursor'
if ($env:CURSOR_PLAYGROUND_BASE) { $base = $env:CURSOR_PLAYGROUND_BASE }  # 로컬 시험용

$prefix = 'cursor-playground '
$root = Join-Path $env:LOCALAPPDATA 'cursor-playground'
$initialFile = Join-Path $root 'backup-initial.json'  # 설치할 때 상태. 완전 제거 때 돌아감
$visitFile = Join-Path $root 'backup-visit.json'      # 마지막 방문에서 처음 적용하기 직전 상태. 원래대로 때 돌아감
$cursorsKey = 'HKCU:\Control Panel\Cursors'
$schemesKey = 'HKCU:\Control Panel\Cursors\Schemes'
$linkKey = 'HKCU:\Software\Classes\cursor-playground'
$accessKey = 'HKCU:\Software\Microsoft\Accessibility'  # 설정 앱의 포인터 크기 슬라이더(1~15)가 읽는 곳

# 구성표 17칸 순서와 칸마다 받을 파일 이름. 움직이는 구성표는 .ani, 나머지는 .cur
$slots = [ordered]@{
    Arrow = 'arrow'; Help = 'help'; AppStarting = 'busy'; Wait = 'wait'; Crosshair = 'cross'; IBeam = 'ibeam'
    NWPen = 'pen'; No = 'no'; SizeNS = 'ns'; SizeWE = 'we'; SizeNWSE = 'nwse'; SizeNESW = 'nesw'; SizeAll = 'move'
    UpArrow = 'up'; Hand = 'hand'; Pin = 'pin'; Person = 'person'
}

# 구성표 목록은 Pages 의 schemes.json 에서 읽는다. 테마가 늘어도 이 스크립트를 다시 설치할 필요가 없음
function Get-Scheme($id) {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $bytes = (Invoke-WebRequest -UseBasicParsing -Uri "$base/schemes.json").RawContentStream.ToArray()
    $entry = [Text.Encoding]::UTF8.GetString($bytes) | ConvertFrom-Json | ForEach-Object { $_ } | Where-Object { $_.id -ceq $id } | Select-Object -First 1
    # 레지스트리 이름에 들어가므로 글자·숫자·공백만 허용
    if ($entry -and $entry.name -match '^[\p{L}\p{N} ]{1,20}$') { $entry }
}

function Notify($text, [switch]$IsError) {
    if ($env:CURSOR_PLAYGROUND_NO_POPUP) { if ($IsError) { "오류: $text" } else { $text }; return }
    Add-Type -AssemblyName System.Windows.Forms
    $icon = if ($IsError) { 'Error' } else { 'Information' }
    [void][Windows.Forms.MessageBox]::Show($text, 'cursor-playground', 'OK', $icon)
}

# 레지스트리를 바꾼 뒤 윈도우에 커서를 다시 읽으라고 알린다
function Update-Cursors {
    if (-not ('CursorPlayground.Native' -as [type])) {
        Add-Type -Namespace CursorPlayground -Name Native -MemberDefinition '[DllImport("user32.dll")] public static extern bool SystemParametersInfo(uint action, uint param, System.IntPtr vparam, uint winini);'
    }
    # SPI_SETCURSORS, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    [void][CursorPlayground.Native]::SystemParametersInfo(0x57, 0, [IntPtr]::Zero, 0x03)
}

# 포인터 크기는 레지스트리만 바꾸면 반영되지 않는다. 설정 앱이 쓰는 문서화되지 않은 호출(0x2029)로 바꾸며,
# 이 호출이 CursorBaseSize 도 같이 저장한다
function Set-SystemCursorSize([int]$size) {
    [void](Update-Cursors)
    [void][CursorPlayground.Native]::SystemParametersInfo(0x2029, 0, [IntPtr]$size, 0x01)
}

# ── 백업 ────────────────────────────────────────────────────────────────
function Save-State($file, $visit) {
    $key = Get-Item $cursorsKey
    $values = foreach ($name in $key.GetValueNames()) {
        [pscustomobject]@{
            Name  = $name
            Kind  = $key.GetValueKind($name).ToString()
            Value = $key.GetValue($name, $null, 'DoNotExpandEnvironmentNames')
        }
    }
    New-Item -ItemType Directory -Force $root | Out-Null
    $access = (Get-ItemProperty $accessKey -ErrorAction SilentlyContinue).CursorSize
    ConvertTo-Json -Depth 3 ([pscustomobject]@{ Visit = $visit; Values = @($values); AccessCursorSize = $access }) | Set-Content -Path $file -Encoding UTF8
}

function Read-State($file) {
    if (-not (Test-Path $file)) { return $null }
    Get-Content $file -Raw -Encoding UTF8 | ConvertFrom-Json
}

function Restore-State($state) {
    # PowerShell 5.1 의 ConvertFrom-Json 은 배열을 한 덩어리로 넘기므로 ForEach-Object 로 풀어야 한다
    $saved = @($state.Values | ForEach-Object { $_ })
    $key = Get-Item $cursorsKey
    $keep = @($saved | ForEach-Object { $_.Name })
    foreach ($name in $key.GetValueNames()) {
        if ($name -ne '' -and $name -notin $keep) { Remove-ItemProperty -Path $cursorsKey -Name $name }
    }
    foreach ($v in $saved) {
        $name = if ($v.Name -eq '') { '(default)' } else { $v.Name }
        New-ItemProperty -Path $cursorsKey -Name $name -Value $v.Value -PropertyType $v.Kind -Force | Out-Null
    }
    $base = (Get-ItemProperty $cursorsKey).CursorBaseSize
    Set-SystemCursorSize $(if ($base) { $base } else { 32 })
    if ($state.PSObject.Properties['AccessCursorSize']) {
        if ($null -eq $state.AccessCursorSize) { Remove-ItemProperty -Path $accessKey -Name CursorSize -ErrorAction SilentlyContinue }
        else { New-ItemProperty -Path $accessKey -Name CursorSize -Value ([int]$state.AccessCursorSize) -PropertyType DWord -Force | Out-Null }
    }
    Update-Cursors
}

# ── 구성표 ──────────────────────────────────────────────────────────────
function Install-Scheme($id, $name, $ext) {
    $dest = Join-Path $root $id
    New-Item -ItemType Directory -Force $dest | Out-Null
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $paths = foreach ($slot in $slots.Keys) {
        $file = $slots[$slot]
        if (-not $file) { ''; continue }
        $cur = Join-Path $dest "$file.$ext"
        Invoke-WebRequest -UseBasicParsing -Uri "$base/dist/$id/$file.$ext" -OutFile $cur
        $head = [IO.File]::ReadAllBytes($cur)
        $isCur = $head.Length -ge 22 -and $head[0] -eq 0 -and $head[1] -eq 0 -and $head[2] -eq 2 -and $head[3] -eq 0
        $isAni = $head.Length -ge 12 -and [Text.Encoding]::ASCII.GetString($head, 0, 4) -eq 'RIFF' -and [Text.Encoding]::ASCII.GetString($head, 8, 4) -eq 'ACON'
        if (-not (($ext -eq 'cur' -and $isCur) -or ($ext -eq 'ani' -and $isAni))) {
            Remove-Item $cur; throw "$file.$ext 가 커서 파일이 아님"
        }
        $cur
    }
    if (-not (Test-Path $schemesKey)) { New-Item $schemesKey | Out-Null }
    New-ItemProperty -Path $schemesKey -Name "$prefix$name" -Value ($paths -join ',') -PropertyType ExpandString -Force | Out-Null
    $paths
}

function Set-Scheme($id, $name, $ext) {
    $paths = @(Install-Scheme $id $name $ext)
    $i = 0
    foreach ($slot in $slots.Keys) {
        New-ItemProperty -Path $cursorsKey -Name $slot -Value $paths[$i] -PropertyType ExpandString -Force | Out-Null
        $i++
    }
    Set-ItemProperty -Path $cursorsKey -Name '(default)' -Value "$prefix$name"
    New-ItemProperty -Path $cursorsKey -Name 'Scheme Source' -Value 1 -PropertyType DWord -Force | Out-Null
    Update-Cursors
}

function Get-OurSchemes {
    if (-not (Test-Path $schemesKey)) { return @() }
    @((Get-Item $schemesKey).GetValueNames() | Where-Object { $_.StartsWith($prefix) })
}

# 지금 쓰고 있지 않은 구성표와 그 커서 폴더만 지운다 (되돌린 곳이 우리 구성표면 그 파일은 남아야 함)
function Remove-UnusedSchemes {
    $c = Get-ItemProperty $cursorsKey
    foreach ($n in Get-OurSchemes) {
        if ($n -ne $c.'(default)') { Remove-ItemProperty -Path $schemesKey -Name $n }
    }
    $keep = if ($c.Arrow -and $c.Arrow.StartsWith("$root\")) { Split-Path $c.Arrow -Parent } else { $null }
    if (Test-Path $root) {
        Get-ChildItem $root -Directory | Where-Object { $_.FullName -ne $keep } | Remove-Item -Recurse -Force
    }
}

# 커서 파일에 32~128px 이미지가 다 들어 있어서, 크기를 바꾸면 윈도우가 맞는 이미지를 골라 씀
function Set-Size([int]$size) {
    Set-SystemCursorSize $size
    if (-not (Test-Path $accessKey)) { New-Item $accessKey | Out-Null }
    New-ItemProperty -Path $accessKey -Name CursorSize -Value (($size - 32) / 16 + 1) -PropertyType DWord -Force | Out-Null
}

function Save-VisitBackup($visit) {
    if (-not (Test-Path $initialFile)) { Save-State $initialFile '' }
    $saved = Read-State $visitFile
    if (-not $saved -or $saved.Visit -ne $visit) { Save-State $visitFile $visit }
}

function Reset-ToDefault {
    foreach ($slot in $slots.Keys) {
        New-ItemProperty -Path $cursorsKey -Name $slot -Value '' -PropertyType ExpandString -Force | Out-Null
    }
    Set-ItemProperty -Path $cursorsKey -Name '(default)' -Value ''
    New-ItemProperty -Path $cursorsKey -Name 'Scheme Source' -Value 0 -PropertyType DWord -Force | Out-Null
    Update-Cursors
}

function Get-StatusText {
    $current = (Get-ItemProperty $cursorsKey).'(default)'
    if (-not $current) { $current = '없음 (칸을 직접 고른 상태이거나 윈도우 기본)' }
    $installed = @(Get-OurSchemes | ForEach-Object { $_.Substring($prefix.Length) })
    $installedText = if ($installed) { $installed -join ', ' } else { '없음' }
    $visit = Read-State $visitFile
    $visitText = if ($visit) {
        $name = ($visit.Values | ForEach-Object { $_ } | Where-Object { $_.Name -eq '' }).Value
        if ($name) { $name } else { '구성표 없음 (윈도우 기본이거나 칸을 직접 고른 상태)' }
    } else { '없음' }
    $initialText = if (Test-Path $initialFile) { '있음' } else { '없음' }
    $size = (Get-ItemProperty $cursorsKey).CursorBaseSize
    if (-not $size) { $size = 32 }
    "지금 적용된 구성표: $current`n포인터 크기: ${size}px`n받아 둔 구성표: $installedText`n원래대로 누르면 돌아갈 곳: $visitText`n설치할 때 상태 백업: $initialText"
}

# ── 진입점 ──────────────────────────────────────────────────────────────
# 주소로 불렸는데 다른 인자가 섞여 있으면 (따옴표를 깨고 -Setup 등을 끼워 넣는 시도) 아무것도 하지 않는다
if ($PSBoundParameters.ContainsKey('Url') -and $PSBoundParameters.Count -gt 1) {
    Notify "알 수 없는 요청이라 무시함`n$Url" -IsError
    return
}

if ($Setup) {
    New-Item -Path "$linkKey\shell\open\command" -Force | Out-Null
    Set-ItemProperty -Path $linkKey -Name '(default)' -Value 'URL:cursor-playground'
    Set-ItemProperty -Path $linkKey -Name 'URL Protocol' -Value ''
    $command = "`"$PSHOME\powershell.exe`" -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$PSCommandPath`" -Url `"%1`""
    Set-ItemProperty -Path "$linkKey\shell\open\command" -Name '(default)' -Value $command
    $made = -not (Test-Path $initialFile)
    if ($made) { Save-State $initialFile '' }
    ''
    '  cursor-playground 준비 끝'
    if ($made) { '  지금 마우스 포인터 설정을 백업함. 페이지 맨 아래 [완전 제거] 를 하면 여기로 돌아옴' }
    else { '  설치할 때 만든 백업이 있어서 그대로 둠' }
    '  이제 시안 페이지에서 구성표의 [이 구성표 적용] 을 누르면 됨'
    ''
    return
}

if (-not $PSBoundParameters.ContainsKey('Url')) {
    'cursor-playground 처리 스크립트. 직접 실행하지 말고 시안 페이지 버튼으로 씀'
    return
}

try {
    if ($Url -cmatch '^cursor-playground://apply/([a-z]{1,20})/([a-z0-9]{16})(?:/(32|48|64|96|128))?/?$') {
        $id = $Matches[1]; $visit = $Matches[2]; $size = $Matches[3]
        $entry = Get-Scheme $id
        if (-not $entry) { Notify "알 수 없는 구성표라 무시함`n$id" -IsError; return }
        $name = $entry.name
        $ext = if ($entry.animated -eq $true) { 'ani' } else { 'cur' }
        Save-VisitBackup $visit
        if ($size) { Set-Size $size }
        Set-Scheme $id $name $ext
        if ($env:CURSOR_PLAYGROUND_NO_POPUP) { "적용함: $prefix$name" }
    }
    elseif ($Url -cmatch '^cursor-playground://size/(32|48|64|96|128)/([a-z0-9]{16})/?$') {
        $size = $Matches[1]
        Save-VisitBackup $Matches[2]
        Set-Size $size
        Update-Cursors
        if ($env:CURSOR_PLAYGROUND_NO_POPUP) { "크기: $size" }
    }
    elseif ($Url -cmatch '^cursor-playground://restore/([a-z0-9]{16})/?$') {
        $visit = $Matches[1]
        $saved = Read-State $visitFile
        if (-not $saved -or $saved.Visit -ne $visit) {
            Notify '이번에 페이지를 연 뒤로 적용한 구성표가 없어서 되돌릴 게 없음.'
        } else {
            Restore-State $saved
            Remove-Item $visitFile
            Remove-UnusedSchemes
            $now = (Get-ItemProperty $cursorsKey).'(default)'
            if (-not $now) { $now = '구성표 없음 (윈도우 기본이거나 칸을 직접 고른 상태)' }
            Notify "페이지를 연 뒤 처음 적용하기 직전으로 되돌림.`n지금: $now"
        }
    }
    elseif ($Url -cmatch '^cursor-playground://status/?$') {
        Notify (Get-StatusText)
    }
    elseif ($Url -cmatch '^cursor-playground://settings/?$') {
        # 마우스 속성 창의 두 번째 탭(포인터)
        Start-Process -FilePath "$env:SystemRoot\System32\control.exe" -ArgumentList 'main.cpl,,1'
    }
    elseif ($Url -cmatch '^cursor-playground://unlink/?$') {
        $initial = Read-State $initialFile
        if ($initial) { Restore-State $initial }
        elseif ((Get-ItemProperty $cursorsKey).'(default)' -like 'cursor-playground *') { Reset-ToDefault }
        # 설치할 때도 우리 구성표를 쓰고 있었다면 파일이 곧 사라지므로 윈도우 기본으로 돌린다
        if ((Get-ItemProperty $cursorsKey).'(default)' -like 'cursor-playground *') { Reset-ToDefault }
        foreach ($n in Get-OurSchemes) { Remove-ItemProperty -Path $schemesKey -Name $n }
        if (Test-Path $linkKey) { Remove-Item $linkKey -Recurse -Force }
        if (Test-Path $root) { Remove-Item $root -Recurse -Force }
        Notify '설치할 때 상태로 되돌리고 웹 버튼 연결과 설치 폴더를 지움. 다시 쓰려면 페이지의 한 줄 설치부터.'
    }
    else {
        Notify "알 수 없는 요청이라 무시함`n$Url" -IsError
    }
} catch {
    Notify "처리 실패: $($_.Exception.Message)" -IsError
}
