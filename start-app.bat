@echo off
title ISTQB Chatbot Launcher

echo ================================================
echo       ISTQB Chatbot Application Launcher
echo ================================================
echo.

REM Set OpenAI API Key if you have one (optional)
REM set OPENAI_API_KEY=your-api-key-here

echo Starting ISTQB Chatbot Application...
echo.

python start-app.py

echo.
echo Application stopped. Press any key to close...
pause > nul
