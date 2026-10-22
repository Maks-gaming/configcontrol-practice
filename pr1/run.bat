@echo off
chcp 65001 >nul
rem Запуск эмулятора из любой папки, аргументы передаются как есть.
rem Интерпретатор: python, если его нет, то py -3.
setlocal
set "PYTHONPATH=%~dp0;%PYTHONPATH%"
python -c "" >nul 2>&1
if errorlevel 1 (
    py -3 -m src.main %*
) else (
    python -m src.main %*
)
