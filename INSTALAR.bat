@echo off
chcp 65001 >nul
title Instalador - iFood Scraper

echo.
echo ========================================================
echo           INSTALADOR - iFood Data Scraper
echo ========================================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao foi encontrado!
    echo.
    echo Por favor, instale o Python primeiro:
    echo 1. Acesse: https://www.python.org/downloads/
    echo 2. Baixe e instale o Python 3.10 ou superior
    echo 3. IMPORTANTE: Marque a opcao "Add Python to PATH" durante a instalacao
    echo 4. Reinicie o computador e execute este instalador novamente
    echo.
    pause
    exit /b 1
)

echo [OK] Python encontrado!
python --version
echo.

REM Criar ambiente virtual
echo [1/4] Criando ambiente virtual...
if exist "venv" (
    echo      Ambiente virtual ja existe, pulando...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo [ERRO] Falha ao criar ambiente virtual!
        pause
        exit /b 1
    )
)
echo      Concluido!
echo.

REM Ativar ambiente e instalar dependências
echo [2/4] Instalando dependencias Python...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias!
    pause
    exit /b 1
)
echo      Concluido!
echo.

REM Instalar navegador do Playwright
echo [3/4] Instalando navegador para captura de headers...
echo      (isso pode demorar alguns minutos na primeira vez)
playwright install chromium
if errorlevel 1 (
    echo [AVISO] Falha ao instalar navegador Playwright.
    echo         A captura automatica de headers pode nao funcionar.
)
echo      Concluido!
echo.

echo [4/4] Instalacao finalizada!
echo.
echo ========================================================
echo                    INSTALACAO COMPLETA!
echo ========================================================
echo.
echo Para usar o programa, execute: EXECUTAR.bat
echo.
pause
