@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "ROOT=%CD%"
set "WANGP_DIR=%ROOT%\vendor\Wan2GP"
set "PORT=7860"
set "ATTENTION=auto"
set "MEMORY_PROFILE=4"
set "EXTRA_ARGS="
set "OPEN_BROWSER=1"

:parse_args
if "%~1"=="" goto parsed_args
if /i "%~1"=="--port" (
    set "PORT=%~2"
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
if /i "%~1"=="--profile" (
    set "MEMORY_PROFILE=%~2"
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--no-open" (
    set "OPEN_BROWSER=0"
    shift
    goto parse_args
)
set "EXTRA_ARGS=%EXTRA_ARGS% %1"
shift
goto parse_args

:parsed_args
if not exist "%ROOT%\.venv-wan2gp\Scripts\python.exe" (
    echo [ERROR] Missing Wan2GP venv. Run install_wan2gp_bernini_lowvram.bat first.
    exit /b 1
)
if not exist "%WANGP_DIR%\wgp.py" (
    echo [ERROR] Missing Wan2GP checkout. Run install_wan2gp_bernini_lowvram.bat first.
    exit /b 1
)
if not exist "%WANGP_DIR%\wgp_config.json" (
    echo [ERROR] Missing Wan2GP config. Run install_wan2gp_bernini_lowvram.bat first.
    exit /b 1
)

call "%ROOT%\.venv-wan2gp\Scripts\activate.bat"
if errorlevel 1 exit /b 1

set "HF_HOME=%ROOT%\.cache\huggingface"
set "HF_HUB_DISABLE_TELEMETRY=1"
set "HF_HUB_DISABLE_XET=1"
set "PYTHONUTF8=1"
if not "%WANGP_ALLOW_ONLINE%"=="1" set "HF_HUB_OFFLINE=1"

echo ============================================
echo        Bernini Wan2GP Low-VRAM Launcher
echo ============================================
echo URL:      http://127.0.0.1:%PORT%
echo Profile:  %MEMORY_PROFILE%
echo Attention:%ATTENTION%
if defined HF_HUB_OFFLINE echo Hub:      offline
echo.

python "%ROOT%\tools\patch_wan2gp_prompt_prefixes.py" --repo "%WANGP_DIR%"
if errorlevel 1 exit /b 1

set "OPEN_ARG=--open-browser"
if "%OPEN_BROWSER%"=="0" set "OPEN_ARG="

cd /d "%WANGP_DIR%"
python wgp.py --profile "%MEMORY_PROFILE%" --attention "%ATTENTION%" --server-port "%PORT%" %OPEN_ARG% %EXTRA_ARGS%
