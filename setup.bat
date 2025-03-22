@echo off
echo ===============================================
echo           VoidLink Setup Script
echo  Secure Terminal-Based Chat ^& File Share
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python 3.7 or higher and try again.
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv voidlink-env

REM Activate virtual environment
echo Activating virtual environment...
call voidlink-env\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install --upgrade pip

REM Install packages from requirements.txt
echo Installing required packages...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Some packages failed to install. Trying to install them individually...
    
    pip install pycryptodome
    pip install cryptography
    pip install requests
    pip install python-dotenv
    pip install windows-curses
    pip install tqdm
    pip install colorama
    pip install bcrypt
)

REM Create necessary directories
echo Creating necessary directories...
if not exist database mkdir database
if not exist database\files mkdir database\files
if not exist database\metadata mkdir database\metadata
if not exist database\chat_history mkdir database\chat_history

REM Create batch files for easy execution
echo Creating batch files for easy execution...

REM Create run_server.bat
echo @echo off > run_server.bat
echo call voidlink-env\Scripts\activate.bat >> run_server.bat
echo python run_server.py %%* >> run_server.bat

REM Create run_client.bat
echo @echo off > run_client.bat
echo call voidlink-env\Scripts\activate.bat >> run_client.bat
echo python run_client.py %%* >> run_client.bat

REM Create run_simple_tui.bat
echo @echo off > run_simple_tui.bat
echo call voidlink-env\Scripts\activate.bat >> run_simple_tui.bat
echo python simple_tui.py >> run_simple_tui.bat

echo.
echo ===============================================
echo           Setup Complete!
echo ===============================================
echo.
echo To use VoidLink:
echo 1. Run the server:
echo    run_server.bat
echo.
echo 2. Run the client (in another terminal):
echo    run_client.bat --host localhost
echo.
echo 3. Or run the simple TUI:
echo    run_simple_tui.bat
echo.
echo Enjoy using VoidLink!
pause