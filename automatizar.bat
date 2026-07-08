@echo off
echo ============================================================
echo   ETL COMPLETO - ACTUALIZACION DE CARTERA
echo ============================================================

:: 1. Nos ubicamos en la ruta del proyecto
cd /d "%~dp0"

echo [1/3] Sincronizando productividad diaria...
python sync_productividad_diaria.py
if %errorlevel% neq 0 (
    echo [ERROR] Fallo en la sincronizacion diaria.
    pause
    exit /b %errorlevel%
)

echo.
echo [2/3] Ejecutando procesamiento principal (main.py)...
python main.py
if %errorlevel% neq 0 (
    echo [ERROR] Fallo en el proceso principal.
    pause
    exit /b %errorlevel%
)

echo.
echo [3/3] Sincronizando el Dashboard en Power BI Service...
"C:\Program Files\PowerShell\7\pwsh.exe" -ExecutionPolicy Bypass -File "refresh_powerbi.ps1"
if %errorlevel% neq 0 (
    echo [ERROR] Fallo en la actualizacion de Power BI.
    pause
    exit /b %errorlevel%
)

echo.
echo ============================================================
echo   PROCESO COMPLETADO CON EXITO
echo ============================================================
timeout /t 5 >nul