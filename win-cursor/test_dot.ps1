# SPDX-License-Identifier: Apache-2.0
# handler.ps1 의 클릭 점(C# Recolor.Mark)을 dist 의 커서(손·화살표·모래시계)에 찍어 보고, 윈도우가 그 파일을 읽는지와
# 이미지마다 핫스팟 픽셀이 파란지 본다. C# 은 윈도우 PowerShell(5.1)에서만 컴파일되고 handler 도 5.1 로 돌아서
# CI 가 빌드 뒤에 5.1 로 부른다: powershell -NoProfile -ExecutionPolicy Bypass -File test_dot.ps1
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8
. (Join-Path $PSScriptRoot 'handler.ps1')   # 주소 없이 부르면 안내 한 줄만 찍고 돌아온다. 함수는 남는다
Initialize-Recolor
Add-Type -AssemblyName System.Drawing
Add-Type @'
using System; using System.Runtime.InteropServices;
public static class DotLd {
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern IntPtr LoadCursorFromFile(string name);
  [DllImport("user32.dll")] public static extern bool DestroyCursor(IntPtr h);
}
'@

$fail = 0
# .cur 안 이미지마다 핫스팟 픽셀이 점의 파랑(30,110,255)인지. $want 가 거짓이면 파랗지 않아야 한다 —
# 점을 안 찍은 커서가 걸리는지까지 봐야 이 검사가 아무것도 안 잡는 검사가 아님을 안다
function Test-Cur([byte[]]$cur, [string]$what, [bool]$want) {
    $count = [BitConverter]::ToUInt16($cur, 4)
    for ($i = 0; $i -lt $count; $i++) {
        $e = 6 + 16 * $i
        $hx = [BitConverter]::ToUInt16($cur, $e + 4); $hy = [BitConverter]::ToUInt16($cur, $e + 6)
        $size = [BitConverter]::ToInt32($cur, $e + 8); $offset = [BitConverter]::ToInt32($cur, $e + 12)
        $png = New-Object byte[] $size
        [Buffer]::BlockCopy($cur, $offset, $png, 0, $size)
        $bmp = [Drawing.Bitmap]::new([IO.MemoryStream]::new($png))
        $c = $bmp.GetPixel($hx, $hy)
        $blue = $c.A -eq 255 -and $c.R -eq 30 -and $c.G -eq 110 -and $c.B -eq 255
        "$what · $($bmp.Width)px · 핫스팟 ($hx,$hy) = ARGB($($c.A),$($c.R),$($c.G),$($c.B))"
        $bmp.Dispose()
        if ($blue -ne $want) { "  ↑ 점이 $(if ($want) { '없음' } else { '있음' })"; $script:fail = 1 }
    }
}
function Test-Load([byte[]]$bytes, [string]$ext, [string]$what) {
    $tmp = Join-Path $env:TEMP "cp-dot-test.$ext"
    [IO.File]::WriteAllBytes($tmp, $bytes)
    $h = [DotLd]::LoadCursorFromFile($tmp)
    if ($h -eq [IntPtr]::Zero) { "$what · 윈도우가 못 읽음"; $script:fail = 1 } else { [void][DotLd]::DestroyCursor($h) }
}
# .ani 의 첫 icon 조각(= .cur)
function First-Icon([byte[]]$ani) {
    $at = [Text.Encoding]::ASCII.GetString($ani).IndexOf('icon')
    $n = [BitConverter]::ToInt32($ani, $at + 4)
    $icon = New-Object byte[] $n
    [Buffer]::BlockCopy($ani, $at + 8, $icon, 0, $n)
    , $icon
}

# .cur 하나, 움직이는 구성표 하나. 색조를 같이 돌려도 점은 돌린 뒤에 찍혀 파랑 그대로여야 한다.
# 정지 구성표(분홍 등)를 2026-10-04 다 지워 dist 에 .cur 가 없다 — .ani 의 첫 조각이 곧 .cur 라 그걸 쓴다
$cur = First-Icon ([IO.File]::ReadAllBytes((Join-Path $PSScriptRoot 'dist\neonpulse\hand.ani')))
$ani = [IO.File]::ReadAllBytes((Join-Path $PSScriptRoot 'dist\heartbeat\hand.ani'))
Test-Cur $cur 'neonpulse 원본' $false
Test-Cur (First-Icon $ani) 'heartbeat 원본' $false
foreach ($deg in 0, 120) {
    $out = [CursorPlayground.Recolor]::Cur($cur, $deg, $true)
    Test-Load $out 'cur' "neonpulse 색조$deg 점"
    Test-Cur $out "neonpulse 색조$deg 점" $true
    $out = [CursorPlayground.Recolor]::Ani($ani, $deg, $true)
    Test-Load $out 'ani' "heartbeat 색조$deg 점"
    Test-Cur (First-Icon $out) "heartbeat 색조$deg 점" $true
}
# 손 말고 다른 칸에도 같은 점이 찍힌다. 화살표는 핫스팟이 (0,0) 구석이라 흰 테가 판 밖으로 나가는 자리,
# 모래시계는 핫스팟이 가운데인 자리
foreach ($slot in 'arrow', 'wait') {
    $one = First-Icon ([IO.File]::ReadAllBytes((Join-Path $PSScriptRoot "dist\neonpulse\$slot.ani")))
    Test-Cur $one "neonpulse $slot 원본" $false
    $out = [CursorPlayground.Recolor]::Cur($one, 0, $true)
    Test-Load $out 'cur' "neonpulse $slot 점"
    Test-Cur $out "neonpulse $slot 점" $true
}

# 주소 풀이: 시안 페이지가 뱉는 꼴을 handler 가 그대로 읽는지. 점 토큰은 링크 칸만(dot)과 칸 여럿(dot.arrow.hand).
# 칸 차례는 주소에 적힌 차례가 아니라 칸 표 차례로 맞춘다
$v = 'a1b2c3d4e5f60789'
$cases = @(
    @("cursor-playground://apply/neonpulse/$v/32/0", '', '', ''),
    @("cursor-playground://apply/neonpulse/$v/32/0/cutout", 'cutout', '', ''),
    @("cursor-playground://apply/neonpulse/$v/32/0/dot", '', 'dot', 'hand'),
    @("cursor-playground://apply/neonpulse/$v/48/120/cutout/dot", 'cutout', 'dot', 'hand'),
    @("cursor-playground://apply/neonpulse/$v/32/0/dot.arrow.wait.hand", '', 'dot.arrow.wait.hand', 'arrow,wait,hand'),
    @("cursor-playground://apply/neonpulse/$v/32/0/cutout/dot.hand.arrow", 'cutout', 'dot.hand.arrow', 'arrow,hand')
)
foreach ($c in $cases) {
    if ($c[0] -cnotmatch $applyPattern) { "주소를 못 읽음: $($c[0])"; $fail = 1; continue }
    $shape = "$($Matches[5])"; $token = "$($Matches[6])"; $files = (Get-DotFiles $token) -join ','
    "$($c[0]) → 모양 '$shape' · 점 '$token' · 칸 '$files'"
    if ($shape -cne $c[1] -or $token -cne $c[2] -or $files -cne $c[3]) { "  ↑ 기대: 모양 '$($c[1])' · 점 '$($c[2])' · 칸 '$($c[3])'"; $fail = 1 }
}
foreach ($bad in "cursor-playground://apply/neonpulse/$v/32/0/dot.", "cursor-playground://apply/neonpulse/$v/32/0/dot/cutout") {
    if ($bad -cmatch $applyPattern) { "엉뚱한 주소를 읽어 버림: $bad"; $fail = 1 }
}
if ($null -ne (Get-DotFiles 'dot.arrow.nope')) { '모르는 칸이 든 점 토큰을 받아 버림'; $fail = 1 }
foreach ($t in @(@('', @()), @('dot', @('hand')), @('dot.arrow.hand', @('arrow', 'hand')))) {
    $got = Get-DotToken $t[1]
    if ($got -cne $t[0]) { "점 토큰을 잘못 만듦: $($t[1] -join ',') → '$got' (기대 '$($t[0])')"; $fail = 1 }
}
$sched = "cursor-playground://schedule/$v/7-neonpulse-0-dot.arrow.hand/22-electric-120-cutout-dot/9-flicker-0-cutout/23-flicker-0"
if ($sched -cnotmatch $schedulePattern) { "예약 주소를 못 읽음: $sched"; $fail = 1 }

# 점을 끄고 색조만 돌린 길도 그대로 돈다
Test-Load ([CursorPlayground.Recolor]::Cur($cur, 120, $false)) 'cur' 'neonpulse 색조120'
Test-Cur ([CursorPlayground.Recolor]::Cur($cur, 120, $false)) 'neonpulse 색조120' $false
if ($fail) { '클릭 점 검사 실패' } else { '클릭 점 검사 통과' }
exit $fail
