@echo off
cd /d D:\Proyectos\Actualiacion_carteras
python sync_productividad_diaria.py
:: Cambiar al directorio del proyecto
cd /d D:\Proyectos\Actualiacion_carteras

:: Definir ruta de logs
set LOG_FILE=D:\Proyectos\Actualiacion_carteras\ejecucion.log

echo --- Inicio de ejecucion: %date% %time% --- >> %LOG_FILE%

:: Ejecutar script y redirigir errores al archivo log
python main.py >> %LOG_FILE% 2>&1

:: Verificar si hubo error (el nivel de error 0 significa éxito)
if %errorlevel% neq 0 (
    echo [ERROR] El script finalizo con codigo %errorlevel% >> %LOG_FILE%
) else (
    echo [EXITO] Sincronizacion completada correctamente >> %LOG_FILE%
)

echo --- Fin de ejecucion: %date% %time% --- >> %LOG_FILE%
echo ------------------------------------------ >> %LOG_FILE%