# SPDX-License-Identifier: Apache-2.0
# art/*.txt 로 커서를 만들어 윈도우 포인터 구성표로 등록한다.
#   설치:  powershell -ExecutionPolicy Bypass -File install.ps1
#   제거:  powershell -ExecutionPolicy Bypass -File install.ps1 -Uninstall
# 등록만 하고 적용은 하지 않는다. 설정 → 마우스 → 추가 마우스 설정 → 포인터 → 구성표에서 고른다.
param([switch]$Uninstall)
$ErrorActionPreference = 'Stop'

$scheme = 'cursor-playground 분홍'
$dest = Join-Path $env:LOCALAPPDATA 'cursor-playground\pink'
$key = 'HKCU:\Control Panel\Cursors\Schemes'

# 구성표 값은 이 17칸을 이 순서로 쉼표로 이은 것이다. 빈 칸은 윈도우 기본 커서.
# 칸 = @(그림, 핫스팟)
$roles = [ordered]@{
    Arrow       = @('arrow-pink', '0,0')   # 일반 선택
    Help        = $null                    # 도움말 선택
    AppStarting = $null                    # 백그라운드 작업
    Wait        = @('wait', '5,7')         # 사용 중
    Crosshair   = $null                    # 정밀 선택
    IBeam       = @('ibeam', '4,8')        # 텍스트 선택
    NWPen       = $null                    # 필기
    No          = @('no', '9,9')           # 사용할 수 없음
    SizeNS      = $null                    # 세로 크기 조정
    SizeWE      = $null                    # 가로 크기 조정
    SizeNWSE    = $null                    # 대각선 크기 조정 1
    SizeNESW    = $null                    # 대각선 크기 조정 2
    SizeAll     = @('move', '9,9')         # 이동
    UpArrow     = $null                    # 대체 선택
    Hand        = @('heart', '5,4')        # 링크 선택
    Pin         = $null                    # 위치 선택
    Person      = $null                    # 사용자 선택
}

if ($Uninstall) {
    Remove-ItemProperty -Path $key -Name $scheme -ErrorAction SilentlyContinue
    if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
    "구성표 '$scheme' 제거함. 지금 쓰고 있었다면 포인터 설정에서 다른 구성표를 고를 것"
    return
}

# 저장소 밖에 복사해 둬야 저장소를 옮기거나 지워도 커서가 안 풀린다
New-Item -ItemType Directory -Force $dest | Out-Null
$paths = foreach ($role in $roles.Keys) {
    $spec = $roles[$role]
    if (-not $spec) { ''; continue }
    $cur = Join-Path $dest "$($spec[0]).cur"
    python (Join-Path $PSScriptRoot 'make_cur.py') (Join-Path $PSScriptRoot "art\$($spec[0]).txt") $cur --hotspot $spec[1] | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "$($spec[0]) 변환 실패" }
    $cur
}

if (-not (Test-Path $key)) { New-Item $key | Out-Null }
New-ItemProperty -Path $key -Name $scheme -Value ($paths -join ',') -PropertyType ExpandString -Force | Out-Null
"구성표 '$scheme' 등록함 ($dest)"
"설정 → 마우스 → 추가 마우스 설정 → 포인터 → 구성표에서 고르고 확인"
