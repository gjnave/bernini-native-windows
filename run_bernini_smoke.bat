@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "ROOT=%CD%"
set "WANGP_DIR=%ROOT%\vendor\Wan2GP"
set "SETTINGS=%ROOT%\examples\smoke_bernini_textonly.json"
set "OUTPUT_DIR=%ROOT%\outputs-wan2gp\smoke"
set "MEMORY_PROFILE=4"
set "ATTENTION=auto"
set "OPEN_OUTPUT=1"
set "PAUSE_ON_EXIT=1"

:parse_args
if "%~1"=="" goto parsed_args
if /i "%~1"=="--profile" (
    set "MEMORY_PROFILE=%~2"
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--attention" (
    set "ATTENTION=%~2"
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--output-dir" (
    set "OUTPUT_DIR=%~2"
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--no-open" (
    set "OPEN_OUTPUT=0"
    shift
    goto parse_args
)
if /i "%~1"=="--no-pause" (
    set "PAUSE_ON_EXIT=0"
    shift
    goto parse_args
)
echo [ERROR] Unknown argument: %~1
call :finish 1
exit /b 1

:parsed_args
echo ============================================
echo       Bernini One-Click Smoke Render
echo ============================================
echo Root:      %ROOT%
echo Profile:   %MEMORY_PROFILE%
echo Attention: %ATTENTION%
echo Output:    %OUTPUT_DIR%
echo.

if not exist "%ROOT%\.venv-wan2gp\Scripts\python.exe" (
    echo [ERROR] Missing Wan2GP venv.
    echo Run install_wan2gp_bernini_lowvram.bat first.
    call :finish 1
    exit /b 1
)
if not exist "%WANGP_DIR%\wgp.py" (
    echo [ERROR] Missing Wan2GP checkout.
    echo Run install_wan2gp_bernini_lowvram.bat first.
    call :finish 1
    exit /b 1
)
if not exist "%SETTINGS%" (
    echo [ERROR] Missing smoke settings:
    echo   %SETTINGS%
    call :finish 1
    exit /b 1
)

call "%ROOT%\.venv-wan2gp\Scripts\activate.bat"
if errorlevel 1 (
    call :finish 1
    exit /b 1
)

set "HF_HOME=%ROOT%\.cache\huggingface"
set "HF_HUB_DISABLE_TELEMETRY=1"
set "HF_HUB_DISABLE_XET=1"
set "PIP_DISABLE_PIP_VERSION_CHECK=1"
set "PYTHONUTF8=1"

echo [STEP] Verifying CUDA and fast attention
python "%ROOT%\tools\verify_wan2gp_env.py" --repo "%WANGP_DIR%" --attention "%ATTENTION%" --require-fast-attention
if errorlevel 1 (
    echo [ERROR] CUDA or fast attention verification failed.
    call :finish 1
    exit /b 1
)

echo.
echo [STEP] Checking model files
python "%ROOT%\tools\download_wan2gp_models.py" --root "%ROOT%" --replace skip
if errorlevel 1 (
    echo [ERROR] Model check/download failed.
    call :finish 1
    exit /b 1
)

if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%" >nul 2>nul

echo.
echo [STEP] Rendering a tiny Bernini MP4
set "HF_HUB_OFFLINE=1"
cd /d "%WANGP_DIR%"
python wgp.py --process "%SETTINGS%" --output-dir "%OUTPUT_DIR%" --attention "%ATTENTION%" --profile "%MEMORY_PROFILE%" --frames 5 --steps 1 --preload 0 --verbose 1
if errorlevel 1 (
    echo [ERROR] Bernini smoke render failed.
    call :finish 1
    exit /b 1
)

echo.
echo ============================================
echo Render complete. MP4 files in:
echo   %OUTPUT_DIR%
echo ============================================
for %%F in ("%OUTPUT_DIR%\*.mp4") do echo   %%~fF
if "%OPEN_OUTPUT%"=="1" start "" "%OUTPUT_DIR%"
call :finish 0
exit /b 0

:finish
if "%PAUSE_ON_EXIT%"=="1" (
    echo.
    pause
)
exit /b %~1
