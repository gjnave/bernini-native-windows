@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "BERNINI_ROOT=%CD%"
set "UPSTREAM_DIR=%BERNINI_ROOT%\vendor\Bernini"
set "SAVE_DIR=%BERNINI_ROOT%\outputs"
set "HF_HOME=%BERNINI_ROOT%\.cache\huggingface"
set "HF_HUB_DISABLE_TELEMETRY=1"
set "TRANSFORMERS_CACHE=%HF_HOME%\transformers"
set "PYTHONPATH=%UPSTREAM_DIR%;%PYTHONPATH%"

if not "%BERNINI_ALLOW_ONLINE%"=="1" set "HF_HUB_OFFLINE=1"

if not exist "%BERNINI_ROOT%\.venv\Scripts\python.exe" (
    echo [ERROR] Missing venv. Run install.bat first.
    exit /b 1
)
if not exist "%UPSTREAM_DIR%\gradio_demo.py" (
    echo [ERROR] Missing upstream Bernini checkout. Run install.bat first.
    exit /b 1
)
if not exist "%BERNINI_ROOT%\config\model_profile.cmd" (
    echo [ERROR] Missing config\model_profile.cmd. Run install.bat first.
    exit /b 1
)
if not exist "%SAVE_DIR%" mkdir "%SAVE_DIR%" >nul 2>nul

call "%BERNINI_ROOT%\.venv\Scripts\activate.bat"
if errorlevel 1 exit /b 1

call "%BERNINI_ROOT%\config\model_profile.cmd"
if errorlevel 1 exit /b 1

if not exist "%BERNINI_CONFIG%\config.json" (
    echo [ERROR] Missing selected model config:
    echo   %BERNINI_CONFIG%\config.json
    exit /b 1
)

echo ============================================
echo        Bernini Native Launcher
echo ============================================
echo Profile: %BERNINI_MODEL_PROFILE%
echo Config:  %BERNINI_CONFIG%
echo Output:  %SAVE_DIR%
echo URL:     http://127.0.0.1:7860
echo.

if defined BERNINI_HIGH_CKPT (
    python "%UPSTREAM_DIR%\gradio_demo.py" --config "%BERNINI_CONFIG%" --high_noise_ckpt "%BERNINI_HIGH_CKPT%" --low_noise_ckpt "%BERNINI_LOW_CKPT%" --save_dir "%SAVE_DIR%" %*
) else (
    python "%UPSTREAM_DIR%\gradio_demo.py" --config "%BERNINI_CONFIG%" --save_dir "%SAVE_DIR%" %*
)

