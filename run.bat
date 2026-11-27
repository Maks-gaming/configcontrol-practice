@echo off
chcp 65001 >nul
rem Запуск ассемблера в Windows.
set PYTHONUTF8=1
set PYTHONPATH=%~dp0
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 -m src.assembler %*
) else (
    python -m src.assembler %*
)
