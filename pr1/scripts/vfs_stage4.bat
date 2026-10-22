@echo off
chcp 65001 >nul
rem Этап 4: команды ls, cd, whoami, find на VFS vfs\deep.xml.
cd /d "%~dp0.."
call run.bat --vfs vfs\deep.xml --script startup\stage4.txt
