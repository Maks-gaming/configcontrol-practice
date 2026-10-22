@echo off
chcp 65001 >nul
rem Ошибки загрузки VFS: нет файла, битый XML, чужой корень, плохой base64.
cd /d "%~dp0.."
for %%V in (vfs\no_such_file.xml vfs\bad_xml.xml vfs\bad_root.xml vfs\bad_base64.xml) do (
    call run.bat --vfs %%V --script startup\stage3.txt
)
