@echo off
rem SPDX-License-Identifier: Apache-2.0
rem Double-click: cursor scheme menu (install / remove / status).
rem With arguments they go straight to install.ps1, e.g. cursors.bat -Install -Scheme neon
rem Kept ASCII-only on purpose: cmd reads .bat files in the console code page, so Korean text here would break.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" %*
if errorlevel 1 pause
