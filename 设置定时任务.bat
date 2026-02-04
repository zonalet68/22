@echo off
chcp 65001 >nul

echo ========================================
echo    广州理工学院查寝 - 设置定时任务
echo ========================================
echo.

echo 正在创建 Windows 定时任务...
echo.

schtasks /create /tn "广州理工学院查寝" ^
/tr "C:\Users\A3095\OneDrive\Desktop\bed_check-master\启动查寝(显示窗口).bat" ^
/sc daily ^
/st 22:00 ^
/f ^
/rl HIGHEST ^
/ru "SYSTEM" ^
/v1

if %errorlevel% == 0 (
    echo.
    echo ========================================
    echo [成功] 定时任务已创建！
    echo ========================================
    echo.
    echo 任务信息：
    echo   - 名称: 广州理工学院查寝
    echo   - 时间: 每天 22:00
    echo   - 权限: 最高权限
    echo   - 运行方式: SYSTEM 用户（显示窗口）
    echo.
    echo 其他操作：
    echo   - 查看任务: taskschd.msc
    echo   - 手动测试: 启动查寝(显示窗口).bat
    echo   - 删除任务: 删除定时任务.bat
    echo   - 查看日志: 运行时会生成日志
) else (
    echo.
    echo ========================================
    echo [失败] 创建任务失败，请以管理员身份运行
    echo ========================================
    echo.
    pause
)


