@echo off
setlocal
cd /d "%~dp0"
echo =========================================
echo   UML AI Studio - Instalacion Windows
echo =========================================
if not exist .venv (
    python -m venv .venv
    if errorlevel 1 goto :error
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 goto :error
echo.
echo Instalacion completada.
echo Copia .env.example como .env y agrega tu GEMINI_API_KEY si aun no lo hiciste.
pause
exit /b 0
:error
echo.
echo Ocurrio un error durante la instalacion.
pause
exit /b 1
