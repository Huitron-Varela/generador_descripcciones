@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\activate.bat (
    echo No se encontro el entorno virtual. Ejecuta INSTALAR.bat primero.
    pause
    exit /b 1
)
call .venv\Scripts\activate.bat
python verificar_entorno.py
if errorlevel 1 (
    echo.
    echo Corrige el entorno antes de iniciar la aplicacion.
    pause
    exit /b 1
)
flet run app.py
