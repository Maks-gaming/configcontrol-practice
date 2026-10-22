@echo off
chcp 65001 >nul
rem Этап 5: команда rm на VFS vfs\deep.xml (изменения только в памяти).
cd /d "%~dp0.."
call run.bat --vfs vfs\deep.xml --script startup\stage5.txt
