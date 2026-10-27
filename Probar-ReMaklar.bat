@echo off
setlocal
title ReMaklar 0.11 - Prueba de rendimiento
echo ReMaklar 0.11 - Jaguar original sobre Darwin 6 i386
echo.
where wsl.exe >nul 2>nul
if errorlevel 1 (
    echo ERROR: no se encontro WSL. Este entorno de pruebas lo necesita.
    exit /b 1
)
wsl.exe --cd "%~dp0." --exec python3 tools/probar_remaklar.py %*
set "REMAKLAR_RESULT=%ERRORLEVEL%"
echo.
if not "%REMAKLAR_RESULT%"=="0" echo La prueba termino con un error. Revisa el mensaje y la carpeta de logs.
if not defined REMAKLAR_NO_PAUSE pause
exit /b %REMAKLAR_RESULT%
