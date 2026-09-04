@echo off
setlocal
cd /d "%~dp0"
if not exist .env (
  echo.
  echo [ERROR] No existe .env
  echo Copia .env.example como .env y agrega OPENAI_API_KEY.
  echo.
  pause
  exit /b 1
)
if not exist node_modules (
  echo Instalando dependencias...
  call npm install
  if errorlevel 1 exit /b 1
)
start "" http://localhost:3000
npm start
pause
