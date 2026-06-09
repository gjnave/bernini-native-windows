@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "ROOT=%CD%"
set "UPSTREAM_REPO=https://github.com/bytedance/Bernini.git"
set "UPSTREAM_REF=9a366af09c93a94a014e7c6df9782155a67908ef"
set "UPSTREAM_DIR=%ROOT%\vendor\Bernini"
set "LOG_DIR=%ROOT%\logs"
set "DRY_RUN=0"
set "SKIP_MODELS=0"
set "REPLACE_POLICY=ask"
set "PROFILE="

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%" >nul 2>nul

:parse_args
if "%~1"=="" goto parsed_args
if /i "%~1"=="--dry-run" (
    set "DRY_RUN=1"
    shift
    goto parse_args
)
if /i "%~1"=="--no-models" (
    set "SKIP_MODELS=1"
    shift
    goto parse_args
)
if /i "%~1"=="--replace" (
    set "REPLACE_POLICY=replace"
    shift
    goto parse_args
)
if /i "%~1"=="--skip-existing" (
    set "REPLACE_POLICY=skip"
    shift
    goto parse_args
)
if /i "%~1"=="--profile" (
    set "PROFILE=%~2"
    shift
    shift
    goto parse_args
)
echo [ERROR] Unknown argument: %~1
exit /b 1

:parsed_args
title Bernini Native Windows Installer

echo ============================================
echo        Bernini Native Windows Installer
echo ============================================
echo.
echo Target folder:
echo   %ROOT%
echo.

if "%DRY_RUN%"=="1" goto disclaimer_done

echo ============================================
echo              [[[ DISCLAIMER ]]]
echo ============================================
echo.
echo AI SUCCESS STARTS WITH THE RIGHT SETUP
echo.
echo This installation is designed for Windows systems with NVIDIA CUDA GPUs.
echo Initial setup, downloads, build tools, and configuration may be required.
echo Quality depends on hardware compatibility, driver health, CUDA support,
echo available disk space, and the selected model profile.
echo.
echo This installer will clone upstream Bernini, create a Python venv,
echo install CUDA/PyTorch dependencies, verify CUDA, verify fast attention,
echo and download large model files into the local models folder.
echo.
set /p ACK=Type YES to confirm you understand and want to continue: 
if /i not "%ACK%"=="YES" (
    echo [ABORTED] User did not acknowledge the disclaimer.
    exit /b 1
)

:disclaimer_done
echo.
echo [STEP] Inspecting tools
call :need git.exe "Git for Windows"
if errorlevel 1 exit /b 1
call :need curl.exe "curl.exe"
if errorlevel 1 exit /b 1
call :need py.exe "Python launcher"
if errorlevel 1 exit /b 1
call :need nvidia-smi.exe "NVIDIA driver tools"
if errorlevel 1 exit /b 1

py -3.11 --version
if errorlevel 1 (
    echo [ERROR] Python 3.11 is required. Install Python 3.11 and rerun.
    exit /b 1
)

where aria2c.exe >nul 2>nul
if errorlevel 1 (
    echo [INFO] aria2c.exe not found. Model downloads will use curl.exe fallback.
) else (
    echo [OK] aria2c.exe found.
)

nvidia-smi --query-gpu=name,driver_version,memory.total,compute_cap --format=csv,noheader
if errorlevel 1 (
    echo [ERROR] nvidia-smi could not query the GPU.
    exit /b 1
)

if "%DRY_RUN%"=="1" (
    echo [DRY RUN] Tool inspection completed.
    exit /b 0
)

call :select_profile
if errorlevel 1 exit /b 1

echo.
echo [STEP] Creating Python 3.11 venv
if not exist "%ROOT%\.venv\Scripts\python.exe" (
    py -3.11 -m venv "%ROOT%\.venv"
    if errorlevel 1 exit /b 1
) else (
    echo [OK] Existing venv found.
)

call "%ROOT%\.venv\Scripts\activate.bat"
if errorlevel 1 exit /b 1

set "HF_HOME=%ROOT%\.cache\huggingface"
set "HF_HUB_DISABLE_TELEMETRY=1"
set "PIP_DISABLE_PIP_VERSION_CHECK=1"

echo.
echo [STEP] Updating base Python packaging tools
python -m pip install --upgrade pip setuptools wheel packaging
if errorlevel 1 exit /b 1

echo.
echo [STEP] Cloning upstream Bernini
if not exist "%ROOT%\vendor" mkdir "%ROOT%\vendor" >nul 2>nul
if not exist "%UPSTREAM_DIR%\.git" (
    git clone "%UPSTREAM_REPO%" "%UPSTREAM_DIR%"
    if errorlevel 1 exit /b 1
) else (
    echo [OK] Existing upstream clone found.
)
git -C "%UPSTREAM_DIR%" fetch --tags
if errorlevel 1 exit /b 1
git -C "%UPSTREAM_DIR%" checkout "%UPSTREAM_REF%"
if errorlevel 1 exit /b 1

echo.
echo [STEP] Installing Bernini Python requirements
python -m pip install -r "%UPSTREAM_DIR%\requirements.txt"
if errorlevel 1 exit /b 1

if not "%BERNINI_SKIP_VEOMNI%"=="1" (
    echo.
    echo [STEP] Installing optional VeOmni multi-GPU support
    python -m pip install --no-deps git+https://github.com/ByteDance-Seed/VeOmni.git@v0.1.10
    if errorlevel 1 exit /b 1
)

echo.
echo [STEP] Installing or verifying fast attention
python "%ROOT%\tools\install_fast_attention.py"
if errorlevel 1 (
    echo [ERROR] Fast attention is not ready.
    echo Set BERNINI_ALLOW_SDPA=1 before running install.bat only if SDPA fallback is acceptable.
    exit /b 1
)

echo.
echo [STEP] Verifying CUDA and attention backend
python "%ROOT%\tools\verify_env.py" --repo "%UPSTREAM_DIR%" --require-fast-attention
if errorlevel 1 exit /b 1

if "%SKIP_MODELS%"=="1" (
    echo [SKIP] Model download skipped by --no-models.
    python "%ROOT%\tools\download_models.py" --root "%ROOT%" --profile "%PROFILE%" --configure-only
    if errorlevel 1 exit /b 1
) else (
    echo.
    echo [STEP] Downloading model profile: %PROFILE%
    python "%ROOT%\tools\download_models.py" --root "%ROOT%" --profile "%PROFILE%" --replace "%REPLACE_POLICY%"
    if errorlevel 1 exit /b 1
)

call :write_summary
if errorlevel 1 exit /b 1

echo.
echo ============================================
echo Installation complete.
echo Launch with:
echo   %ROOT%\run.bat
echo ============================================
echo.
exit /b 0

:select_profile
if defined PROFILE goto profile_selected
if defined BERNINI_MODEL_PROFILE (
    set "PROFILE=%BERNINI_MODEL_PROFILE%"
    goto profile_selected
)
echo.
echo [STEP] Select model profile
echo.
echo   1. official-diffusers    Native-safe ByteDance bundle, H100/A100-class VRAM target
echo   2. neuregex-fp8          Self-contained FP8, ComfyUI-proven 24 GB, native experimental
echo   3. kijai-fp8-separate    Kijai FP8 HIGH/LOW plus Wan2.2 base, native experimental
echo   4. abiray-fp8-separate   Abiray FP8 HIGH/LOW plus Wan2.2 base, native experimental
echo.
set /p CHOICE=Choose profile [1]: 
if "%CHOICE%"=="" set "CHOICE=1"
if "%CHOICE%"=="1" set "PROFILE=official-diffusers"
if "%CHOICE%"=="2" set "PROFILE=neuregex-fp8"
if "%CHOICE%"=="3" set "PROFILE=kijai-fp8-separate"
if "%CHOICE%"=="4" set "PROFILE=abiray-fp8-separate"

:profile_selected
if "%PROFILE%"=="official-diffusers" goto profile_ok
if "%PROFILE%"=="neuregex-fp8" goto profile_ok
if "%PROFILE%"=="kijai-fp8-separate" goto profile_ok
if "%PROFILE%"=="abiray-fp8-separate" goto profile_ok
echo [ERROR] Unknown profile: %PROFILE%
exit /b 1

:profile_ok
echo [OK] Model profile: %PROFILE%
exit /b 0

:need
where %~1 >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Missing %~2 - %~1 was not found in PATH.
    exit /b 1
)
echo [OK] %~2
exit /b 0

:write_summary
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%" >nul 2>nul
> "%LOG_DIR%\INSTALL_SUMMARY.txt" echo Bernini Native Windows Installer
>> "%LOG_DIR%\INSTALL_SUMMARY.txt" echo Date: %DATE% %TIME%
>> "%LOG_DIR%\INSTALL_SUMMARY.txt" echo Root: %ROOT%
>> "%LOG_DIR%\INSTALL_SUMMARY.txt" echo Upstream: %UPSTREAM_REPO%
>> "%LOG_DIR%\INSTALL_SUMMARY.txt" echo Upstream ref: %UPSTREAM_REF%
>> "%LOG_DIR%\INSTALL_SUMMARY.txt" echo Model profile: %PROFILE%
>> "%LOG_DIR%\INSTALL_SUMMARY.txt" echo Fast attention required unless BERNINI_ALLOW_SDPA=1.
>> "%LOG_DIR%\INSTALL_SUMMARY.txt" echo Launch: %ROOT%\run.bat
echo [WRITE] %LOG_DIR%\INSTALL_SUMMARY.txt
exit /b 0
