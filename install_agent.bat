@echo off
setlocal enabledelayedexpansion
title NodeTrace Agent Installer/Uninstaller
color 0B

:: Get the root directory of the script
set ROOT_DIR=%~dp0

echo =======================================================
echo           NODETRACE UNIFIED AGENT TOOL
echo =======================================================
echo.
echo [1] Install/Configure Agent
echo [2] Uninstall Agent
echo [3] Exit
echo.
set /p mode="Select mode [1-3]: "

if "%mode%"=="1" goto install_menu
if "%mode%"=="2" goto uninstall_menu
if "%mode%"=="3" exit
goto end

:install_menu
echo.
echo --- INSTALLATION ---
echo [1] Python Agent
echo [2] C++ Agent
echo [3] C# Agent
echo [4] Java Agent
echo.
set /p choice="Select agent language [1-4]: "

set /p backend_url="Enter Backend URL (default: http://localhost:8000): "
if "!backend_url!"=="" set backend_url=http://localhost:8000

set /p enroll_key="Enter Enrollment Key: "

if "%choice%"=="1" goto python_install
if "%choice%"=="2" goto cpp_install
if "%choice%"=="3" goto csharp_install
if "%choice%"=="4" goto java_install

:python_install
echo [INFO] Configuring Python Agent...
pushd "%ROOT_DIR%agents\python"
echo BACKEND_URL=!backend_url! > .env
echo ENROLL_KEY=!enroll_key! >> .env
popd
echo [SUCCESS] Python agent configured.
echo To start the agent, run this command from the project root:
echo python agents\python\agent.py
goto end

:cpp_install
echo [INFO] Configuring C++ Agent...
pushd "%ROOT_DIR%agents\cpp"
echo {"backend_url": "!backend_url!", "enroll_key": "!enroll_key!"} > config.json
popd
echo [SUCCESS] C++ agent configured. 
echo To build, go to agents\cpp, then: mkdir build && cd build && cmake .. && make
goto end

:csharp_install
echo [INFO] Configuring C# Agent...
pushd "%ROOT_DIR%agents\csharp\NodeTraceAgent"
echo { > config.json
echo   "DeviceName": "%COMPUTERNAME%", >> config.json
echo   "RegisterUrl": "!backend_url!/api/v1/register", >> config.json
echo   "UpdateUrl": "!backend_url!/api/v1/update", >> config.json
echo   "HeartbeatUrl": "!backend_url!/api/v1/heartbeat", >> config.json
echo   "HeartbeatInterval": 10, >> config.json
echo   "RetryMaxAttempts": 5, >> config.json
echo   "RetryBaseDelay": 1, >> config.json
echo   "EnrollKey": "!enroll_key!" >> config.json
echo } >> config.json
popd
echo [SUCCESS] C# agent configured.
echo To start the agent, run this command from the project root:
echo dotnet run --project agents\csharp\NodeTraceAgent
goto end

:java_install
echo [INFO] Configuring Java Agent...
pushd "%ROOT_DIR%agents\java"
echo backend.url=!backend_url! > agent.properties
echo enroll.key=!enroll_key! >> agent.properties
popd
echo [SUCCESS] Java agent configured.
echo To start the agent, run this command from the project root:
echo mvn spring-boot:run -f agents\java\pom.xml
goto end

:uninstall_menu
echo.
echo --- UNINSTALLATION (CLEANUP) ---
echo [1] Python Agent
echo [2] C++ Agent
echo [3] C# Agent
echo [4] Java Agent
echo.
set /p choice="Select agent to cleanup [1-4]: "

if "%choice%"=="1" (
    if exist "%ROOT_DIR%agents\python\.env" del "%ROOT_DIR%agents\python\.env"
    echo [SUCCESS] Python agent config removed.
)
if "%choice%"=="2" (
    if exist "%ROOT_DIR%agents\cpp\config.json" del "%ROOT_DIR%agents\cpp\config.json"
    echo [SUCCESS] C++ agent config removed.
)
if "%choice%"=="3" (
    if exist "%ROOT_DIR%agents\csharp\NodeTraceAgent\config.json" del "%ROOT_DIR%agents\csharp\NodeTraceAgent\config.json"
    echo [SUCCESS] C# agent config removed.
)
if "%choice%"=="4" (
    if exist "%ROOT_DIR%agents\java\agent.properties" del "%ROOT_DIR%agents\java\agent.properties"
    echo [SUCCESS] Java agent config removed.
)
goto end

:end
echo.
echo =======================================================
echo Operation complete.
echo =======================================================
pause
