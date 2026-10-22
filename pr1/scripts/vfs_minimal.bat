@echo off
chcp 65001 >nul
rem Запуск эмулятора с VFS vfs\minimal.xml и скриптом этапа 3.
cd /d "%~dp0.."
call run.bat --vfs vfs\minimal.xml --script startup\stage3.txt
