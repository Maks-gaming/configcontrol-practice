@echo off
chcp 65001 >nul
rem Только стартовый скрипт: рабочий и несуществующий.
cd /d "%~dp0.."
call run.bat --script startup\stage2.txt
call run.bat --script startup\no_such_script.txt
