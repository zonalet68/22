@echo off
chcp 65001 >nul

echo ========================================
echo    广州理工学院查寝 - 删除定时任务
echo ========================================
echo.

echo 正在删除定时任务...
echo.

schtasks /delete /tn "广州理工学院查寝" /f

if %errorlevel% == 0 (
    echo.
    echo [成功] 定时任务已删除！
) else (
    echo.
    echo [提示] 任务不存在或已删除
)

echo.
pause
