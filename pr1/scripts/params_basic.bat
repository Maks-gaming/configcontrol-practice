@echo off
chcp 65001 >nul
rem Запуск без параметров и вывод справки по параметрам.
cd /d "%~dp0.."
call run.bat --help
call run.bat
