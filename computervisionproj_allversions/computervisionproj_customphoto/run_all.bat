@echo off

REM Check and kill existing processes on port 3000 and 3001
for %%p in (3000 3001) do (
    echo Checking for existing processes on port %%p...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%%p') do (
        echo Killing process with PID %%a...
        taskkill /PID %%a /F >nul 2>&1
    )
)

echo Starting Flask server...
start /B python C:\Users\krish\Documents\Project\FeatureRecall\impfiles\PycharmProjects\frfr\app\__init__.py

REM Wait for the Flask server to start using ping for a 10-second delay
ping 127.0.0.1 -n 10 > nul

echo Starting React app...
cd C:\Users\krish\Documents\Project\FeatureRecall\impfiles\PycharmProjects\frfr
set PORT=3001
start /B npm start

echo All processes started.
