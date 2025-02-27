@echo off
title Sistema ACS
color 0A

echo Iniciando Sistema ACS...
echo.

:: Cambiar al directorio del script
cd /d "%~dp0"

:: Verificar si existe el entorno virtual
if not exist "venv\Scripts\activate.bat" (
    echo Error: No se encontro el entorno virtual.
    echo Por favor, asegurese de que la carpeta 'venv' existe.
    pause
    exit /b 1
)

:: Activar el entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate.bat

:: Verificar si Python está disponible
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python no esta disponible.
    echo Por favor, asegurese de que Python esta instalado correctamente.
    pause
    exit /b 1
)

:: Verificar si el archivo app.py existe
if not exist "app.py" (
    echo Error: No se encontro el archivo app.py
    echo Por favor, asegurese de que el archivo existe.
    pause
    exit /b 1
)

:: Iniciar el servidor Flask
echo Iniciando el servidor...
echo.
echo El sistema se abrira en su navegador web...
echo NO CIERRE ESTA VENTANA mientras use el sistema.
echo Para cerrar el sistema, cierre esta ventana.
echo.
timeout /t 3 > nul

:: Abrir el navegador
start http://localhost:5000

:: Ejecutar la aplicación
python app.py

:: Si el servidor se detiene
echo.
echo El servidor se ha detenido.
echo Presione cualquier tecla para salir...
pause > nul 