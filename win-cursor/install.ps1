# SPDX-License-Identifier: Apache-2.0
# art/<구성표>/*.txt 로 커서를 만들어 윈도우 포인터 구성표로 등록한다.
#   설치:  powershell -ExecutionPolicy Bypass -File install.ps1
#   제거:  powershell -ExecutionPolicy Bypass -File install.ps1 -Uninstall
# 등록만 하고 적용은 하지 않는다. 설정 → 마우스 → 추가 마우스 설정 → 포인터 → 구성표에서 고른다.
# 이 파일은 한글 때문에 UTF-8 BOM 으로 저장해야 한다 (Windows PowerShell 5.1 은 BOM 이 없으면 ANSI 로 읽음).
param([switch]$Uninstall)
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

if ($Uninstall) {
    foreach ($id in $schemes.Keys) {
        Remove-ItemProperty -Path $key -Name "cursor-playground $($schemes[$id])" -ErrorAction SilentlyContinue
    }
    if (Test-Path $root) { Remove-Item $root -Recurse -Force }
    "구성표 $($schemes.Count)개 제거함. 지금 쓰고 있었다면 포인터 설정에서 다른 구성표를 고를 것"
    return
}

if (-not (Test-Path $key)) { New-Item $key | Out-Null }
foreach ($id in $schemes.Keys) {
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
    $name = "cursor-playground $($schemes[$id])"
    New-ItemProperty -Path $key -Name $name -Value ($paths -join ',') -PropertyType ExpandString -Force | Out-Null
    "등록함: $name"
}
"설정 → 마우스 → 추가 마우스 설정 → 포인터 → 구성표에서 고르고 확인"
