@echo off
echo ============================================
echo SparePartFinder Pro - Starting Servers
echo ============================================
echo.
echo Starting Flask Backend on port 5000...
echo.
start "Flask Backend" cmd /k "cd /d %~dp0 && python app.py"
timeout /t 2 /nobreak > nul
echo.
echo Starting React Frontend on port 5173...
echo.
start "React Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"
echo.
echo ============================================
echo Both servers are starting...
echo.
echo Flask Backend: http://localhost:5000
echo React Frontend: http://localhost:5173
echo.
echo Opening browser in 5 seconds...
echo ============================================
timeout /t 5 /nobreak > nul
start http://localhost:5173
echo.
echo Done! Check the terminal windows for any errors.
pause
