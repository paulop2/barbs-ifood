@echo off
chcp 65001 >nul
title iFood Data Scraper

REM Verificar se foi instalado
if not exist "venv" (
    echo [ERRO] Programa nao instalado!
    echo        Execute INSTALAR.bat primeiro.
    echo.
    pause
    exit /b 1
)

REM Ativar ambiente e executar
call venv\Scripts\activate.bat
python run_scraper.py %*
pause
