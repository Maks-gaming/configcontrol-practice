@echo off
chcp 65001 >nul
rem Запуск инструмента в Windows (cmd), аргументы передаются как есть.
set PYTHONUTF8=1
set PYTHONPATH=%~dp0
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 -m src.main %*
) else (
    python -m src.main %*
)
