@echo off
setlocal enabledelayedexpansion
title Rejoin Vector Convergence master
cd /d "%~dp0"

echo ============================================================
echo   Vector "Convergence" - rejoining the master video file
echo ============================================================
echo.

set "OUT=vectorconvergence6878x1080.mp4"
set "EXPECTED=95885cee00b868d618ee7714ea6a950bf630c95bc40145d09a1c1bb3da09ba03"

if exist "%OUT%" del "%OUT%"

REM Find every part file, whatever it happens to be called,
REM and put them in name order.
set "LIST="
set /a COUNT=0
for /f "delims=" %%F in ('dir /b /a-d /on "*.part*" 2^>nul') do (
    set /a COUNT+=1
    echo    !COUNT!. %%F
    if defined LIST ( set "LIST=!LIST!+"%%F"" ) else ( set "LIST="%%F"" )
)

echo.
echo   Found !COUNT! part files.
echo.

if !COUNT! EQU 0 (
    echo   No part files found in this folder.
    echo   Make sure this file sits in the SAME folder as the parts.
    echo.
    pause
    exit /b 1
)

if not !COUNT! EQU 16 (
    echo   NOTE: expected 16 parts, found !COUNT!.
    echo   Carrying on - the check below will tell you if it worked.
    echo.
)

echo   Joining... this takes under a minute, please wait.
copy /b !LIST! "%OUT%" >nul

if not exist "%OUT%" (
    echo.
    echo   Something went wrong - no output file was created.
    echo.
    pause
    exit /b 1
)

echo   Created: %OUT%
echo.
echo   Checking the file is complete...
echo.

for /f "skip=1 delims=" %%H in ('certutil -hashfile "%OUT%" SHA256') do (
    if not defined GOT set "GOT=%%H"
)
set "GOT=%GOT: =%"

echo     Expected: %EXPECTED%
echo     Actual:   %GOT%
echo.

if /i "%GOT%"=="%EXPECTED%" (
    echo   ================================================
    echo    SUCCESS - the video is correct and complete.
    echo    You can now delete the .part files.
    echo   ================================================
) else (
    echo   ================================================
    echo    WARNING - the two codes above do NOT match.
    echo    A part is missing, duplicated or incomplete.
    echo    Re-download the parts and run this again.
    echo    Do not use the video until they match.
    echo   ================================================
)

echo.
pause
