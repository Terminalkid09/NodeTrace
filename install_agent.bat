@echo off
setlocal enabledelayedexpansion
title NodeTrace Agent Installer/Uninstaller
color 0B

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
cd agents\python
echo BACKEND_URL=!backend_url! > .env
echo ENROLL_KEY=!enroll_key! >> .env
echo [SUCCESS] Python agent configured. Run 'python agent.py' to start.
goto end

:cpp_install
echo [INFO] Configuring C++ Agent...
cd agents\cpp
echo {"backend_url": "!backend_url!", "enroll_key": "!enroll_key!"} > config.json
echo [SUCCESS] C++ agent configured. Compile using CMake/Make.
goto end

:csharp_install
echo [INFO] Configuring C# Agent...
cd agents\csharp\NodeTraceAgent
echo { "AgentConfig": { "BackendUrl": "!backend_url!", "EnrollKey": "!enroll_key!" } } > appsettings.json
echo [SUCCESS] C# agent configured. Run 'dotnet run' to start.
goto end

:java_install
echo [INFO] Configuring Java Agent...
cd agents\java
echo backend.url=!backend_url! > agent.properties
echo enroll.key=!enroll_key! >> agent.properties
echo [SUCCESS] Java agent configured. Run 'mvn spring-boot:run' to start.
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
    if exist agents\python\.env del agents\python\.env
    echo [SUCCESS] Python agent config removed.
)
if "%choice%"=="2" (
    if exist agents\cpp\config.json del agents\cpp\config.json
    echo [SUCCESS] C++ agent config removed.
)
if "%choice%"=="3" (
    if exist agents\csharp\NodeTraceAgent\appsettings.json del agents\csharp\NodeTraceAgent\appsettings.json
    echo [SUCCESS] C# agent config removed.
)
if "%choice%"=="4" (
    if exist agents\java\agent.properties del agents\java\agent.properties
    echo [SUCCESS] Java agent config removed.
)
goto end

:end
echo.
echo =======================================================
echo Operation complete.
echo =======================================================
pause
