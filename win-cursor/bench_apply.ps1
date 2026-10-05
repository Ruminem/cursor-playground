# SPDX-License-Identifier: Apache-2.0
# Temporary: compare old vs new handler.ps1 end to end on a Windows runner (PowerShell 5.1). ASCII only.
# handler.old.ps1 is written by the workflow from the commit before the speedup.
$ErrorActionPreference = 'Stop'
$env:CURSOR_PLAYGROUND_NO_POPUP = '1'
$new = Join-Path $PSScriptRoot 'handler.ps1'
$old = Join-Path $PSScriptRoot 'handler.old.ps1'
$root = Join-Path $env:LOCALAPPDATA 'cursor-playground'
$v = 'aaaaaaaaaaaaaaaa'
$cases = [ordered]@{
    'plain'            = @("rainbowflow/$v", 'rainbowflow')
    'chunky'           = @("rainbowflow/$v/32/0/chunky", 'chunky-rainbowflow')
    'firework'         = @("firework/$v", 'firework')
    'hue120'           = @("rainbowflow/$v/32/120", 'rainbowflow-h120')
    'chunky+hue+dots'  = @("rainbowflow/$v/32/200/chunky/dot.arrow.hand", 'chunky-rainbowflow-h200-dot.arrow.hand')
}
function Run($h, $u) {
    $sw = [Diagnostics.Stopwatch]::StartNew()
    $out = & "$PSHOME\powershell.exe" -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File $h -Url "cursor-playground://apply/$u" | Out-String
    $sw.Stop()
    if ($out -notmatch 'cursor-playground ') { throw "FAILED $h $u :: $out" }
    $sw.Elapsed.TotalMilliseconds
}
function FolderHash($dir) {
    -join (Get-ChildItem (Join-Path $root $dir) -File | Sort-Object Name | ForEach-Object { (Get-FileHash $_.FullName -Algorithm SHA256).Hash.Substring(0, 8) })
}
Get-ChildItem $root -Filter 'csharp-*.dll' -ErrorAction SilentlyContinue | Remove-Item -Force
'new, first run (compiles dll): {0:N0} ms' -f (Run $new $cases['plain'][0])
'dll cached: ' + ((Get-ChildItem $root -Filter 'csharp-*.dll' | ForEach-Object Name) -join ', ')
$t = @{}
foreach ($r in 1..3) {
    foreach ($k in $cases.Keys) {
        $u, $dir = $cases[$k]
        $a = Run $old $u; $ha = FolderHash $dir
        $b = Run $new $u; $hb = FolderHash $dir
        if ($ha -ne $hb) { throw "BYTES DIFFER $k" }
        $t["$k old"] += @($a); $t["$k new"] += @($b)
    }
}
'{0,-18} {1,8} {2,8}   (median of 3, ms; files byte-identical)' -f 'case', 'old', 'new'
foreach ($k in $cases.Keys) {
    $m = foreach ($w in 'old', 'new') { ($t["$k $w"] | Sort-Object)[1] }
    '{0,-18} {1,8:N0} {2,8:N0}' -f $k, $m[0], $m[1]
}
