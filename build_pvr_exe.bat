@echo off
echo ==========================================
echo   Auto PVR EXE Builder
echo   Using Python Launcher: py
echo ==========================================
echo.

REM ---- Clean old build output ----
echo Cleaning old build folders...
IF EXIST build rmdir /s /q build
IF EXIST dist rmdir /s /q dist
IF EXIST PVR.spec del PVR.spec
echo Done.
echo.

REM ---- Ensure PyInstaller is installed ----
echo Checking for PyInstaller...
py -m pyinstaller --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo PyInstaller not found. Installing...
    py -m pip install pyinstaller
)
echo.

REM ---- Build the EXE ----
echo Building EXE...
py -m PyInstaller --onefile --noconsole PVR.py
echo.

echo ==========================================
echo Build complete!
echo Your EXE is located in: dist\PVR.exe
echo ==========================================
pause