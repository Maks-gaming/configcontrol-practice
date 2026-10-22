@echo off
chcp 65001 >nul
rem Все параметры сразу, в обеих формах записи.
cd /d "%~dp0.."
call run.bat --vfs vfs\minimal.xml --script startup\stage2.txt
call run.bat --vfs=vfs\minimal.xml --script=startup\stage2.txt
