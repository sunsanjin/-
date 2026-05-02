@echo off
chcp 65001 >nul
echo 正在启动鼠标光标颜色更改器...
python "%~dp0cursor_changer.py"
if %errorlevel% neq 0 (
    echo.
    echo 启动失败，请确保已安装 Python。
    pause
)
