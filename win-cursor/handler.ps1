# SPDX-License-Identifier: Apache-2.0
# 시안 페이지 버튼(cursor-playground:// 주소)을 받아 커서 구성표를 적용하거나 되돌린다.
# setup.ps1 이 이 파일을 %LOCALAPPDATA%\cursor-playground 에 내려받고 -Setup 으로 실행한다.
#
# 받는 주소는 아래 다섯 가지뿐이다. 어느 웹 페이지든 이 주소를 부를 수 있으므로 그 밖의 요청은 전부 무시한다.
#   cursor-playground://apply/<구성표>/<방문>   커서를 내려받아 구성표로 등록하고 바로 적용
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

$schemes = [ordered]@{ pink = '분홍'; neon = '네온'; minimal = '미니멀'; onebit = '1비트'; fantasy = '판타지' }
$root = Join-Path $env:LOCALAPPDATA 'cursor-playground'
$initialFile = Join-Path $root 'backup-initial.json'  # 설치할 때 상태. 완전 제거 때 돌아감
$visitFile = Join-Path $root 'backup-visit.json'      # 마지막 방문에서 처음 적용하기 직전 상태. 원래대로 때 돌아감
$cursorsKey = 'HKCU:\Control Panel\Cursors'
$schemesKey = 'HKCU:\Control Panel\Cursors\Schemes'
$linkKey = 'HKCU:\Software\Classes\cursor-playground'

# 구성표 17칸 순서. 값이 있는 칸만 커서 파일을 받고 나머지는 윈도우 기본 커서.
$slots = [ordered]@{
    Arrow = 'arrow'; Help = ''; AppStarting = ''; Wait = 'wait'; Crosshair = ''; IBeam = 'ibeam'
    NWPen = ''; No = 'no'; SizeNS = ''; SizeWE = ''; SizeNWSE = ''; SizeNESW = ''; SizeAll = 'move'
    UpArrow = ''; Hand = 'hand'; Pin = ''; Person = ''
}

function RegName($id) { "cursor-playground $($schemes[$id])" }

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
    ConvertTo-Json -Depth 3 ([pscustomobject]@{ Visit = $visit; Values = @($values) }) | Set-Content -Path $file -Encoding UTF8
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
    Update-Cursors
}

# ── 구성표 ──────────────────────────────────────────────────────────────
function Install-Scheme($id) {
    $dest = Join-Path $root $id
    New-Item -ItemType Directory -Force $dest | Out-Null
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $paths = foreach ($slot in $slots.Keys) {
        $file = $slots[$slot]
        if (-not $file) { ''; continue }
        $cur = Join-Path $dest "$file.cur"
        Invoke-WebRequest -UseBasicParsing -Uri "$base/dist/$id/$file.cur" -OutFile $cur
        $head = [IO.File]::ReadAllBytes($cur)
        if ($head.Length -lt 22 -or $head[0] -ne 0 -or $head[1] -ne 0 -or $head[2] -ne 2 -or $head[3] -ne 0) {
            Remove-Item $cur; throw "$file.cur 가 커서 파일이 아님"
        }
        $cur
    }
    if (-not (Test-Path $schemesKey)) { New-Item $schemesKey | Out-Null }
    New-ItemProperty -Path $schemesKey -Name (RegName $id) -Value ($paths -join ',') -PropertyType ExpandString -Force | Out-Null
    $paths
}

function Set-Scheme($id) {
    $paths = @(Install-Scheme $id)
    $i = 0
    foreach ($slot in $slots.Keys) {
        New-ItemProperty -Path $cursorsKey -Name $slot -Value $paths[$i] -PropertyType ExpandString -Force | Out-Null
        $i++
    }
    Set-ItemProperty -Path $cursorsKey -Name '(default)' -Value (RegName $id)
    New-ItemProperty -Path $cursorsKey -Name 'Scheme Source' -Value 1 -PropertyType DWord -Force | Out-Null
    Update-Cursors
}

# 지금 쓰고 있지 않은 구성표만 지운다 (되돌린 곳이 우리 구성표면 그 파일은 남아야 함)
function Remove-UnusedSchemes {
    $current = (Get-ItemProperty $cursorsKey).'(default)'
    foreach ($id in $schemes.Keys) {
        if ((RegName $id) -eq $current) { continue }
        Remove-ItemProperty -Path $schemesKey -Name (RegName $id) -ErrorAction SilentlyContinue
        $dest = Join-Path $root $id
        if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
    }
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
    $values = if (Test-Path $schemesKey) { Get-ItemProperty $schemesKey } else { $null }
    $installed = @($schemes.Keys | Where-Object { $values -and $null -ne $values.(RegName $_) } | ForEach-Object { $schemes[$_] })
    $installedText = if ($installed) { $installed -join ', ' } else { '없음' }
    $visit = Read-State $visitFile
    $visitText = if ($visit) {
        $name = ($visit.Values | ForEach-Object { $_ } | Where-Object { $_.Name -eq '' }).Value
        if ($name) { $name } else { '구성표 없음 (윈도우 기본이거나 칸을 직접 고른 상태)' }
    } else { '없음' }
    $initialText = if (Test-Path $initialFile) { '있음' } else { '없음' }
    "지금 적용된 구성표: $current`n받아 둔 구성표: $installedText`n원래대로 누르면 돌아갈 곳: $visitText`n설치할 때 상태 백업: $initialText"
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
    if ($Url -cmatch '^cursor-playground://apply/([a-z]+)/([a-z0-9]{16})/?$' -and $schemes.Contains($Matches[1])) {
        $id = $Matches[1]; $visit = $Matches[2]
        if (-not (Test-Path $initialFile)) { Save-State $initialFile '' }
        $saved = Read-State $visitFile
        if (-not $saved -or $saved.Visit -ne $visit) { Save-State $visitFile $visit }
        Set-Scheme $id
        if ($env:CURSOR_PLAYGROUND_NO_POPUP) { "적용함: $(RegName $id)" }
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
        foreach ($id in $schemes.Keys) { Remove-ItemProperty -Path $schemesKey -Name (RegName $id) -ErrorAction SilentlyContinue }
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
