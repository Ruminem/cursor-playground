# SPDX-License-Identifier: Apache-2.0
# One-time setup for the cursor-playground preview page buttons:
#   irm https://ruminem.github.io/cursor-playground/win-cursor/setup.ps1 | iex
# Downloads handler.ps1 to %LOCALAPPDATA%\cursor-playground and runs it with -Setup,
# which links the cursor-playground:// address to it and backs up the current pointer settings.
# ASCII only on purpose: irm may decode this file with the wrong code page, so Korean text lives in handler.ps1.
& {
    $ErrorActionPreference = 'Stop'
    $ProgressPreference = 'SilentlyContinue'
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $base = 'https://ruminem.github.io/cursor-playground/win-cursor'
    if ($env:CURSOR_PLAYGROUND_BASE) { $base = $env:CURSOR_PLAYGROUND_BASE }
    $dir = Join-Path $env:LOCALAPPDATA 'cursor-playground'
    New-Item -ItemType Directory -Force $dir | Out-Null
    $handler = Join-Path $dir 'handler.ps1'
    Invoke-WebRequest -UseBasicParsing -Uri "$base/handler.ps1" -OutFile $handler
    & "$PSHOME\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File $handler -Setup
}
