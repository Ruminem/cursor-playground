# SPDX-License-Identifier: Apache-2.0
# handler.ps1 의 링크 클릭 점(C# Recolor.Mark)을 dist 의 손 커서에 찍어 보고, 윈도우가 그 파일을 읽는지와
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

# 정지 구성표 하나, 움직이는 구성표 하나. 색조를 같이 돌려도 점은 돌린 뒤에 찍혀 파랑 그대로여야 한다
$cur = [IO.File]::ReadAllBytes((Join-Path $PSScriptRoot 'dist\pink\hand.cur'))
$ani = [IO.File]::ReadAllBytes((Join-Path $PSScriptRoot 'dist\heartbeat\hand.ani'))
Test-Cur $cur 'pink 원본' $false
Test-Cur (First-Icon $ani) 'heartbeat 원본' $false
foreach ($deg in 0, 120) {
    $out = [CursorPlayground.Recolor]::Cur($cur, $deg, $true)
    Test-Load $out 'cur' "pink 색조$deg 점"
    Test-Cur $out "pink 색조$deg 점" $true
    $out = [CursorPlayground.Recolor]::Ani($ani, $deg, $true)
    Test-Load $out 'ani' "heartbeat 색조$deg 점"
    Test-Cur (First-Icon $out) "heartbeat 색조$deg 점" $true
}
# 점을 끄고 색조만 돌린 길도 그대로 돈다
Test-Load ([CursorPlayground.Recolor]::Cur($cur, 120, $false)) 'cur' 'pink 색조120'
Test-Cur ([CursorPlayground.Recolor]::Cur($cur, 120, $false)) 'pink 색조120' $false
if ($fail) { '링크 클릭 점 검사 실패' } else { '링크 클릭 점 검사 통과' }
exit $fail
