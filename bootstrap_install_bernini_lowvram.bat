@echo off
setlocal EnableExtensions

set "REPO_URL=https://github.com/gjnave/bernini-native-windows.git"
set "TARGET=D:\apps2review\bernini\bernini"

title Bernini Low-VRAM Bootstrap Installer

echo ============================================
echo    Bernini Wan2GP Low-VRAM Bootstrap
echo ============================================
echo.
echo Repo:
echo   %REPO_URL%
echo Target:
echo   %TARGET%
echo.

where git.exe >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Git for Windows is required.
    pause
    exit /b 1
)

if exist "%TARGET%\.git" (
    echo [UPDATE] Existing repo found.
    git -C "%TARGET%" pull --ff-only
    if errorlevel 1 (
        echo [ERROR] Could not update existing repo.
        pause
        exit /b 1
    )
) else (
    if not exist "D:\apps2review\bernini" mkdir "D:\apps2review\bernini" >nul 2>nul
    echo [CLONE] %REPO_URL%
    git clone "%REPO_URL%" "%TARGET%"
    if errorlevel 1 (
        echo [ERROR] Clone failed. If the repo was just created, wait a moment and rerun.
        pause
        exit /b 1
    )
)

cd /d "%TARGET%"
call install_wan2gp_bernini_lowvram.bat
set "RESULT=%ERRORLEVEL%"
if not "%RESULT%"=="0" (
    echo.
    echo [ERROR] Installer failed with exit code %RESULT%.
    pause
    exit /b %RESULT%
)

echo.
echo [DONE] Bernini low-VRAM setup finished.
pause
exit /b 0
