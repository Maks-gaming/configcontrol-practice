@echo off
chcp 65001 >nul
rem Запуск эмулятора с VFS vfs\files.xml и скриптом этапа 3.
cd /d "%~dp0.."
call run.bat --vfs vfs\files.xml --script startup\stage3.txt
