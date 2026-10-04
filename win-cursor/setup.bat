@echo off
rem SPDX-License-Identifier: Apache-2.0
rem One-time setup by double-click. The preview page offers it as cursor-playground-setup.bat.
rem Same as pasting this line into PowerShell:
rem   irm https://ruminem.github.io/cursor-playground/win-cursor/setup.ps1 | iex
rem Kept ASCII-only on purpose: cmd reads .bat files in the console code page, so Korean text here would break.
powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://ruminem.github.io/cursor-playground/win-cursor/setup.ps1 | iex"
pause
