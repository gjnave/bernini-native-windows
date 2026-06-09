@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "ROOT=%CD%"
set "WANGP_REPO=https://github.com/deepbeepmeep/Wan2GP.git"
set "WANGP_REF=46537a597c60df8b29adc6c5a0ad7e543b34840a"
set "WANGP_DIR=%ROOT%\vendor\Wan2GP"
set "LOG_DIR=%ROOT%\logs"
set "DRY_RUN=0"
set "SKIP_MODELS=0"
set "REPLACE_POLICY=ask"
set "MEMORY_PROFILE=4"
set "ATTENTION=auto"
set "PORT=7860"

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
if /i "%~1"=="--port" (
    set "PORT=%~2"
    shift
    shift
    goto parse_args
)
echo [ERROR] Unknown argument: %~1
exit /b 1

:parsed_args
title Bernini Wan2GP Low-VRAM Installer

echo ============================================
echo      Bernini Wan2GP Low-VRAM Installer
echo ============================================
echo.
echo Target folder:
echo   %ROOT%
echo.
echo Memory profile: %MEMORY_PROFILE%
echo Attention:      %ATTENTION%
echo Port:           %PORT%
echo.

if "%DRY_RUN%"=="1" goto disclaimer_done

echo ============================================
echo              [[[ DISCLAIMER ]]]
echo ============================================
echo.
echo This path installs Wan2GP for lower-VRAM Bernini use.
echo It is the practical route for 12 GB to 24 GB NVIDIA cards,
echo using Wan2GP memory offload, int8 Bernini weights, CUDA,
echo and Sage/Flash attention when supported.
echo.
echo The native ByteDance installer remains available as install.bat,
echo but native Bernini is not guaranteed on consumer VRAM.
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

echo.
echo [STEP] Cloning Wan2GP
if not exist "%ROOT%\vendor" mkdir "%ROOT%\vendor" >nul 2>nul
if not exist "%WANGP_DIR%\.git" (
    git clone "%WANGP_REPO%" "%WANGP_DIR%"
    if errorlevel 1 exit /b 1
) else (
    echo [OK] Existing Wan2GP clone found.
)
git -C "%WANGP_DIR%" fetch --tags
if errorlevel 1 exit /b 1
git -C "%WANGP_DIR%" checkout "%WANGP_REF%"
if errorlevel 1 exit /b 1

echo.
echo [STEP] Creating Python 3.11 venv
if not exist "%ROOT%\.venv-wan2gp\Scripts\python.exe" (
    py -3.11 -m venv "%ROOT%\.venv-wan2gp"
    if errorlevel 1 exit /b 1
) else (
    echo [OK] Existing Wan2GP venv found.
)

call "%ROOT%\.venv-wan2gp\Scripts\activate.bat"
if errorlevel 1 exit /b 1

set "HF_HOME=%ROOT%\.cache\huggingface"
set "HF_HUB_DISABLE_TELEMETRY=1"
set "HF_HUB_DISABLE_XET=1"
set "PIP_DISABLE_PIP_VERSION_CHECK=1"
set "PYTHONUTF8=1"

echo.
echo [STEP] Updating base Python packaging tools
python -m pip install --upgrade pip setuptools wheel packaging
if errorlevel 1 exit /b 1

echo.
echo [STEP] Installing PyTorch CUDA 13.0 stack
python -m pip install torch==2.10.0 torchvision==0.25.0 torchaudio==2.10.0 --index-url https://download.pytorch.org/whl/cu130
if errorlevel 1 exit /b 1

echo.
echo [STEP] Installing Wan2GP requirements
python -m pip install -r "%WANGP_DIR%\requirements.txt"
if errorlevel 1 exit /b 1

echo.
echo [STEP] Installing fast attention and low-bit kernels
python -m pip install triton-windows
if errorlevel 1 exit /b 1
python -m pip install https://github.com/woct0rdho/SageAttention/releases/download/v2.2.0-windows.post4/sageattention-2.2.0+cu130torch2.9.0andhigher.post4-cp39-abi3-win_amd64.whl
if errorlevel 1 exit /b 1
python -m pip install https://github.com/deepbeepmeep/kernels/releases/download/Flash2/flash_attn-2.8.3-cp311-cp311-win_amd64.whl
if errorlevel 1 exit /b 1
python -m pip install https://github.com/deepbeepmeep/kernels/releases/download/GGUF_Kernels/llamacpp_gguf_cuda-1.0.2+torch210cu13py311-cp311-cp311-win_amd64.whl
if errorlevel 1 exit /b 1

echo.
echo [STEP] Configuring Wan2GP for Bernini low-VRAM mode
python "%ROOT%\tools\configure_wan2gp.py" --root "%ROOT%" --profile "%MEMORY_PROFILE%" --attention "%ATTENTION%"
if errorlevel 1 exit /b 1

echo.
echo [STEP] Adding Bernini prompt prefix dropdown to Wan2GP GUI
python "%ROOT%\tools\patch_wan2gp_prompt_prefixes.py" --repo "%WANGP_DIR%"
if errorlevel 1 exit /b 1

echo.
echo [STEP] Verifying CUDA and fast attention
python "%ROOT%\tools\verify_wan2gp_env.py" --repo "%WANGP_DIR%" --attention "%ATTENTION%" --require-fast-attention
if errorlevel 1 exit /b 1

if "%SKIP_MODELS%"=="1" (
    echo [SKIP] Model download skipped by --no-models.
) else (
    echo.
    echo [STEP] Downloading Wan2GP Bernini int8 model files
    python "%ROOT%\tools\download_wan2gp_models.py" --root "%ROOT%" --replace "%REPLACE_POLICY%"
    if errorlevel 1 exit /b 1
)

call :write_summary
if errorlevel 1 exit /b 1

echo.
echo ============================================
echo Low-VRAM installation complete.
echo Launch with:
echo   %ROOT%\run_wan2gp_bernini.bat --port %PORT%
echo ============================================
echo.
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
> "%LOG_DIR%\WAN2GP_INSTALL_SUMMARY.txt" echo Bernini Wan2GP Low-VRAM Installer
>> "%LOG_DIR%\WAN2GP_INSTALL_SUMMARY.txt" echo Date: %DATE% %TIME%
>> "%LOG_DIR%\WAN2GP_INSTALL_SUMMARY.txt" echo Root: %ROOT%
>> "%LOG_DIR%\WAN2GP_INSTALL_SUMMARY.txt" echo Wan2GP: %WANGP_REPO%
>> "%LOG_DIR%\WAN2GP_INSTALL_SUMMARY.txt" echo Wan2GP ref: %WANGP_REF%
>> "%LOG_DIR%\WAN2GP_INSTALL_SUMMARY.txt" echo Memory profile: %MEMORY_PROFILE%
>> "%LOG_DIR%\WAN2GP_INSTALL_SUMMARY.txt" echo Attention: %ATTENTION%
>> "%LOG_DIR%\WAN2GP_INSTALL_SUMMARY.txt" echo Launch: %ROOT%\run_wan2gp_bernini.bat --port %PORT%
echo [WRITE] %LOG_DIR%\WAN2GP_INSTALL_SUMMARY.txt
exit /b 0
