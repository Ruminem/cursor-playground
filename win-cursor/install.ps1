# SPDX-License-Identifier: Apache-2.0
# art/<구성표>/*.txt 로 커서를 만들어 윈도우 포인터 구성표로 등록·제거한다.
#   메뉴:       cursors.bat 더블클릭 (또는 인자 없이 이 스크립트 실행)
#   전체 등록:  install.ps1 -Install
#   개별 등록:  install.ps1 -Install -Scheme neon,fantasy
#   전체 제거:  install.ps1 -Uninstall
#   개별 제거:  install.ps1 -Uninstall -Scheme neon
#   상태:       install.ps1 -Status
# 시안 페이지 버튼으로 바로 적용하는 쪽은 setup.ps1 / handler.ps1 이 맡는다 (클론·Python 필요 없음).
# 등록만 하고 적용은 하지 않는다. 설정 → 마우스 → 추가 마우스 설정 → 포인터 → 구성표에서 고른다.
# 이 파일은 한글 때문에 UTF-8 BOM 으로 저장해야 한다 (Windows PowerShell 5.1 은 BOM 이 없으면 ANSI 로 읽음).
[CmdletBinding(PositionalBinding = $false)]
param([switch]$Install, [switch]$Uninstall, [switch]$Status, [string[]]$Scheme)
$ErrorActionPreference = 'Stop'

# 폴더 이름 = 표시 이름
$schemes = [ordered]@{
    pink    = '분홍'
    neon    = '네온'
    minimal = '미니멀'
    onebit  = '1비트'
    fantasy = '판타지'
}
$root = Join-Path $env:LOCALAPPDATA 'cursor-playground'
$key = 'HKCU:\Control Panel\Cursors\Schemes'

# 구성표 값은 이 17칸을 이 순서로 쉼표로 이은 것이다. 그림 파일이 없는 칸은 비워서 윈도우 기본 커서.
$slots = [ordered]@{
    Arrow = 'arrow'; Help = ''; AppStarting = ''; Wait = 'wait'; Crosshair = ''; IBeam = 'ibeam'
    NWPen = ''; No = 'no'; SizeNS = ''; SizeWE = ''; SizeNWSE = ''; SizeNESW = ''; SizeAll = 'move'
    UpArrow = ''; Hand = 'hand'; Pin = ''; Person = ''
}

function RegName($id) { "cursor-playground $($schemes[$id])" }

function Resolve-Ids($ids) {
    if (-not $ids) { return @($schemes.Keys) }
    foreach ($id in $ids) {
        if (-not $schemes.Contains($id)) { throw "없는 구성표: $id (가능: $($schemes.Keys -join ', '))" }
    }
    $ids
}

function Install-Scheme($id) {
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw 'python 을 찾을 수 없음. Python 3.10+ 를 설치할 것' }
    if (-not (Test-Path $key)) { New-Item $key | Out-Null }
    # 저장소 밖에 복사해 둬야 저장소를 옮기거나 지워도 커서가 안 풀린다
    $dest = Join-Path $root $id
    New-Item -ItemType Directory -Force $dest | Out-Null
    $paths = foreach ($slot in $slots.Keys) {
        $src = Join-Path $PSScriptRoot "art\$id\$($slots[$slot]).txt"
        if (-not $slots[$slot] -or -not (Test-Path $src)) { ''; continue }
        $cur = Join-Path $dest "$($slots[$slot]).cur"
        python (Join-Path $PSScriptRoot 'make_cur.py') $src $cur | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "$src 변환 실패" }
        $cur
    }
    New-ItemProperty -Path $key -Name (RegName $id) -Value ($paths -join ',') -PropertyType ExpandString -Force | Out-Null
    "등록함: $(RegName $id)"
}

function Remove-Scheme($id) {
    if ((Get-ItemProperty 'HKCU:\Control Panel\Cursors').'(default)' -eq (RegName $id)) {
        "주의: $(RegName $id) 는 지금 적용 중. 포인터 설정에서 다른 구성표를 골라야 기본 커서로 돌아감"
    }
    Remove-ItemProperty -Path $key -Name (RegName $id) -ErrorAction SilentlyContinue
    $dest = Join-Path $root $id
    if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
    if ((Test-Path $root) -and -not (Get-ChildItem $root)) { Remove-Item $root }
    "제거함: $(RegName $id)"
}

# 콘솔에서 한글은 두 칸을 차지하므로 폭을 따로 세서 맞춘다
function Pad($text, $width) {
    $w = 0; foreach ($ch in $text.ToCharArray()) { $w += 1 + [int]([int]$ch -ge 0x1100) }
    $text + (' ' * [Math]::Max(1, $width - $w))
}

function Show-Status {
    $current = (Get-ItemProperty 'HKCU:\Control Panel\Cursors').'(default)'
    $values = if (Test-Path $key) { Get-ItemProperty $key } else { $null }
    ''
    '  ' + (Pad '구성표' 28) + (Pad '등록' 8) + (Pad '파일' 8) + '적용'
    foreach ($id in $schemes.Keys) {
        $name = RegName $id
        $value = if ($values) { $values.$name } else { $null }
        $reg = if ($null -ne $value) { '예' } else { '아니오' }
        $files = '-'
        if ($null -ne $value) {
            $p = @($value -split ',' | Where-Object { $_ })
            $files = "$(@($p | Where-Object { Test-Path $_ }).Count)/$($p.Count)"
        }
        $applied = if ($current -eq $name) { '◀ 지금' } else { '' }
        '  ' + (Pad $name 28) + (Pad $reg 8) + (Pad $files 8) + $applied
    }
    ''
    if ($current) { "  지금 적용된 구성표: $current" } else { '  지금 적용된 구성표: 없음 (윈도우 기본이거나 칸을 직접 고른 상태)' }
}

# 화면에 목록을 보여 주고, 고른 구성표 id 만 돌려준다
function Read-Ids($verb) {
    $ids = @($schemes.Keys)
    Write-Host ''
    for ($i = 0; $i -lt $ids.Count; $i++) { Write-Host "  $($i + 1)) $($schemes[$ids[$i]])" }
    $answer = Read-Host "  $verb 할 번호 (여러 개는 1,3 처럼, 취소는 그냥 엔터)"
    foreach ($part in ($answer -split '[,\s]+' | Where-Object { $_ })) {
        $n = 0
        if ([int]::TryParse($part, [ref]$n) -and $n -ge 1 -and $n -le $ids.Count) { $ids[$n - 1] }
        else { Write-Host "  무시함: $part" }
    }
}

function Show-Menu {
    while ($true) {
        Write-Host ''
        Write-Host '  cursor-playground 커서 구성표'
        Write-Host '  1) 전체 등록   2) 전체 제거'
        Write-Host '  3) 개별 등록   4) 개별 제거'
        Write-Host '  5) 현재 상태   0) 끝내기'
        $choice = Read-Host '  번호'
        try {
            $out = switch ($choice.Trim()) {
                '1' { $schemes.Keys | ForEach-Object { Install-Scheme $_ }; '  포인터 설정의 구성표 목록에서 고르고 확인' }
                '2' { $schemes.Keys | ForEach-Object { Remove-Scheme $_ } }
                '3' { Read-Ids '등록' | ForEach-Object { Install-Scheme $_ } }
                '4' { Read-Ids '제거' | ForEach-Object { Remove-Scheme $_ } }
                '5' { Show-Status }
                { $_ -in '0', '' } { return }
                default { '  1~5 또는 0 을 입력' }
            }
            $out | ForEach-Object { Write-Host "  $($_.TrimStart())" }
        } catch {
            Write-Host "  오류: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

if ($Install) { Resolve-Ids $Scheme | ForEach-Object { Install-Scheme $_ } }
elseif ($Uninstall) { Resolve-Ids $Scheme | ForEach-Object { Remove-Scheme $_ } }
elseif ($Status) { Show-Status }
else { Show-Menu }
