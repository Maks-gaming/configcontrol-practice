@echo off
chcp 65001 >nul
rem Запуск ассемблера в Windows.
set PYTHONUTF8=1
set PYTHONPATH=%~dp0
set MODULE=src.assembler
if "%~1"=="run" (
    set MODULE=src.interpreter
    shift
)
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 -m %MODULE% %*
) else (
    python -m %MODULE% %*
)
