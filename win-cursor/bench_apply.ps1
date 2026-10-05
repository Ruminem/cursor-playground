# SPDX-License-Identifier: Apache-2.0
# Temporary: time each step of handler.ps1 apply on a Windows runner (PowerShell 5.1). ASCII only.
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$env:CURSOR_PLAYGROUND_NO_POPUP = '1'
$h = Join-Path $PSScriptRoot 'handler.ps1'
function T($label, [scriptblock]$b) { $ms = (Measure-Command $b).TotalMilliseconds; '{0,-44} {1,8:N0} ms' -f $label, $ms }

foreach ($i in 1..3) { T "ps startup (powershell -NoProfile exit) #$i" { & "$PSHOME\powershell.exe" -NoProfile -Command exit } }

. $h | Out-Null
T 'Get-Scheme rainbowflow (cold IWR)' { $script:e = Get-Scheme rainbowflow }
T 'Get-Scheme rainbowflow (warm)' { $null = Get-Scheme rainbowflow }
T 'Get-Shape chunky' { $script:s = Get-Shape chunky }
T 'IWR one small file (warm)' { $null = Invoke-WebRequest -UseBasicParsing -Uri "$base/shapes.json" }
T 'Add-Type Native (compile, SPI)' { Update-Cursors }
T 'Update-Cursors again (no compile)' { Update-Cursors }
T 'Initialize-Recolor (compile)' { Initialize-Recolor }
T 'Install-Scheme rainbowflow plain (17 seq)' { $null = Install-Scheme rainbowflow 'b1' ani 0 $null @() }
T 'Install-Scheme rainbowflow chunky (fallback)' { $null = Install-Scheme rainbowflow 'b2' ani 0 chunky @() }
T 'Install-Scheme firework plain (17 seq)' { $null = Install-Scheme firework 'b3' ani 0 $null @() }
T 'Install-Scheme rainbowflow hue120 (recolor)' { $null = Install-Scheme rainbowflow 'b4' ani 120 $null @() }

# parallel download of the same 17 files
Add-Type -AssemblyName System.Net.Http
[Net.ServicePointManager]::DefaultConnectionLimit = 32
$hc = [System.Net.Http.HttpClient]::new()
foreach ($id in 'rainbowflow', 'firework') {
    T "HttpClient parallel 17 $id" {
        $tasks = foreach ($f in $slots.Values) { $hc.GetByteArrayAsync("$base/dist/$id/$f.ani") }
        [Threading.Tasks.Task]::WaitAll([Threading.Tasks.Task[]]@($tasks))
    }
}
T 'HttpClient parallel 17 rainbowflow (again)' {
    $tasks = foreach ($f in $slots.Values) { $hc.GetByteArrayAsync("$base/dist/rainbowflow/$f.ani") }
    [Threading.Tasks.Task]::WaitAll([Threading.Tasks.Task[]]@($tasks))
}

# compile vs load cached dll in a fresh process
$dll = Join-Path $env:TEMP 'cpbench.dll'
$src = '[DllImport("user32.dll")] public static extern bool SystemParametersInfo(uint action, uint param, System.IntPtr vparam, uint winini);'
Add-Type -Namespace CPB -Name N -MemberDefinition $src -OutputAssembly $dll
foreach ($i in 1..2) {
    T "fresh ps + Add-Type compile #$i" { & "$PSHOME\powershell.exe" -NoProfile -Command "Add-Type -Namespace X -Name N -MemberDefinition '$src'" }
    T "fresh ps + Add-Type -Path dll #$i" { & "$PSHOME\powershell.exe" -NoProfile -Command "Add-Type -Path '$dll'" }
}

# end to end, as the browser link does it
foreach ($u in 'rainbowflow/aaaaaaaaaaaaaaaa', 'rainbowflow/aaaaaaaaaaaaaaaa/32/0/chunky', 'firework/aaaaaaaaaaaaaaaa', 'rainbowflow/aaaaaaaaaaaaaaaa/32/120') {
    T "e2e apply $u" { & "$PSHOME\powershell.exe" -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File $h -Url "cursor-playground://apply/$u" | Out-Null }
}
