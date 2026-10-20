@ECHO OFF
cls
set ZIP_UTILITY_PATH=C:\Program Files\7-Zip
set ZIP_UTILITY=7z.exe
set ZIP_PATH=G:\My Drive\brahe-ai\brahe-ai-0.1\backups
set ZIP_FILENAME_MONTH=%date:~4,2%
set ZIP_FILENAME_DAY=%date:~7,2%
set ZIP_FILENAME_YEAR=%date:~10,4%
if "%ZIP_FILENAME_MONTH%"=="01" (SET ZIP_FILENAME_MONTH=Jan)
if "%ZIP_FILENAME_MONTH%"=="02" (SET ZIP_FILENAME_MONTH=Feb)
if "%ZIP_FILENAME_MONTH%"=="03" (SET ZIP_FILENAME_MONTH=Mar)
if "%ZIP_FILENAME_MONTH%"=="04" (SET ZIP_FILENAME_MONTH=Apr)
if "%ZIP_FILENAME_MONTH%"=="05" (SET ZIP_FILENAME_MONTH=May)
if "%ZIP_FILENAME_MONTH%"=="06" (SET ZIP_FILENAME_MONTH=Jun)
if "%ZIP_FILENAME_MONTH%"=="07" (SET ZIP_FILENAME_MONTH=Jul)
if "%ZIP_FILENAME_MONTH%"=="08" (SET ZIP_FILENAME_MONTH=Aug)
if "%ZIP_FILENAME_MONTH%"=="09" (SET ZIP_FILENAME_MONTH=Sep)
if "%ZIP_FILENAME_MONTH%"=="10" (SET ZIP_FILENAME_MONTH=Oct)
if "%ZIP_FILENAME_MONTH%"=="11" (SET ZIP_FILENAME_MONTH=Nov)
if "%ZIP_FILENAME_MONTH%"=="12" (SET ZIP_FILENAME_MONTH=Dec)
set ZIP_FILENAME=brahe-ai.bkp-%ZIP_FILENAME_MONTH%-%ZIP_FILENAME_DAY%-%ZIP_FILENAME_YEAR%.zip
set ZIP_TEMP_FILENAME=brahe-ai.bkp-%ZIP_FILENAME_MONTH%-%ZIP_FILENAME_DAY%-%ZIP_FILENAME_YEAR%.tmp.zip
set WORKSPACE_PATH=C:\Users\marcb\OneDrive\Personal Managed\Brahe-ai\brahe-ai-workspace

if not exist "%ZIP_UTILITY_PATH%\%ZIP_UTILITY%" (
    echo ERROR: 7-Zip was not found at "%ZIP_UTILITY_PATH%\%ZIP_UTILITY%".
    pause
    exit /b 1
)

if not exist "%ZIP_PATH%\" (
    echo ERROR: Backup destination folder does not exist: "%ZIP_PATH%"
    pause
    exit /b 1
)

if not exist "%WORKSPACE_PATH%\" (
    echo ERROR: Workspace folder does not exist: "%WORKSPACE_PATH%"
    pause
    exit /b 1
)

if exist "%ZIP_PATH%\%ZIP_TEMP_FILENAME%" (
    del /Q "%ZIP_PATH%\%ZIP_TEMP_FILENAME%"
    if errorlevel 1 (
        echo ERROR: Could not remove the previous temporary archive "%ZIP_PATH%\%ZIP_TEMP_FILENAME%".
        pause
        exit /b 1
    )
)

if not exist "%WORKSPACE_PATH%\.env.sample" (
    echo ERROR: The sample environment file was not found: "%WORKSPACE_PATH%\.env.sample"
    pause
    exit /b 1
)

echo Creating temporary backup: "%ZIP_PATH%\%ZIP_TEMP_FILENAME%"
"%ZIP_UTILITY_PATH%\%ZIP_UTILITY%" a "%ZIP_PATH%\%ZIP_TEMP_FILENAME%" "%WORKSPACE_PATH%\*" "%WORKSPACE_PATH%\.env.sample" -xr!log\ -xr!processed\ -xr!processing\ -xr!tmp\ -xr!venv\ -xr!.venv\ -xr!env\ -xr!ENV\ -xr!virtualenv\ -xr!pyvenv.cfg -xr!site-packages\ -xr!.vscode\ -xr!.git\ -xr!.env -xr!token.json -xr!credentials.json -xr!*.log -xr!*.tmp -xr!*.bak
if errorlevel 1 (
    echo ERROR: 7-Zip failed to create the backup.
    if exist "%ZIP_PATH%\%ZIP_TEMP_FILENAME%" del /Q "%ZIP_PATH%\%ZIP_TEMP_FILENAME%"
    pause
    exit /b 1
)

if not exist "%ZIP_PATH%\%ZIP_TEMP_FILENAME%" (
    echo ERROR: 7-Zip reported success, but the backup file was not created.
    pause
    exit /b 1
)

echo Testing backup integrity...
"%ZIP_UTILITY_PATH%\%ZIP_UTILITY%" t "%ZIP_PATH%\%ZIP_TEMP_FILENAME%"
if errorlevel 1 (
    echo ERROR: The temporary backup failed its integrity test.
    del /Q "%ZIP_PATH%\%ZIP_TEMP_FILENAME%"
    pause
    exit /b 1
)

move /Y "%ZIP_PATH%\%ZIP_TEMP_FILENAME%" "%ZIP_PATH%\%ZIP_FILENAME%" > nul
if errorlevel 1 (
    echo ERROR: Could not move the verified backup into place. The existing backup, if any, was preserved.
    pause
    exit /b 1
)

echo Backup created successfully: "%ZIP_PATH%\%ZIP_FILENAME%"
pause
