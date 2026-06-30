@echo off
echo ============================================================
echo   ETL - ACTUALIZACION DE CARTERA Y POWER BI EN LA NUBE
echo ============================================================

:: 1. Nos ubicamos en la ruta exacta del proyecto
cd /d "%~dp0"

echo [1/2] Ejecutando sincronizacion de Base de Datos...
python main.py
if %errorlevel% neq 0 (
    echo [ERROR] Fallo la sincronizacion de datos en Python.
    pause
    exit /b %errorlevel%
)

echo.
echo [2/2] Sincronizando el Dashboard en Power BI Service...
:: Se asume el uso de PowerShell 7 (pwsh.exe)
"C:\Program Files\PowerShell\7\pwsh.exe" -ExecutionPolicy Bypass -File "refresh_powerbi.ps1"
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo conectar a la API de Power BI.
    pause
    exit /b %errorlevel%
)

:: La siguiente linea ha sido comentada para no ejecutar el recordatorio de metas
:: echo.
:: echo [3/3] Verificando envio de recordatorios por WhatsApp...
:: python recordatorio_metas.py

echo.
echo ============================================================
echo   PROCESO COMPLETADO CON EXITO
echo ============================================================
timeout /t 5 >nul