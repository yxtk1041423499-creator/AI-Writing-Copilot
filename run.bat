@echo off
chcp 65001 >nul
title AI智能写作助手 - 启动服务

echo ======================================================
echo           ✍️ AI智能写作助手正在启动中...
echo ======================================================
echo.

cd /d "%~dp0"

REM 1. 优先检测当前目录虚拟环境
if exist "venv\Scripts\python.exe" (
    echo [1/2] 正在加载独立虚拟运行环境 (venv)...
    set "PYTHON_EXE=venv\Scripts\python.exe"
    goto LAUNCH
)

REM 2. 检测系统环境变量中的 Python
where python >nul 2>nul
if %errorlevel% equ 0 (
    echo [1/2] 检测到系统环境变量 Python...
    set "PYTHON_EXE=python"
    goto LAUNCH
)

REM 3. 检测 Python Launcher (py)
where py >nul 2>nul
if %errorlevel% equ 0 (
    echo [1/2] 检测到 Python Launcher (py)...
    set "PYTHON_EXE=py"
    goto LAUNCH
)

REM 4. 检测备用常见路径
if exist "D:\python\python2\python.exe" (
    echo [1/2] 检测到系统备用 Python 路径...
    set "PYTHON_EXE=D:\python\python2\python.exe"
    goto LAUNCH
)

echo [警告] 未能自动定位到 Python 解释器，将尝试以默认命令启动...
set "PYTHON_EXE=python"

:LAUNCH
echo [2/2] 正在启动 Streamlit 交互式用户界面...
echo 服务访问地址通常为: http://localhost:8501
echo.

"%PYTHON_EXE%" -m streamlit run app.py --server.port 8501 --browser.gatherUsageStats false

pause
