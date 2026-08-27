@echo off
setlocal enabledelayedexpansion
title Arrow Transition - Frame Extractor
cd /d "%~dp0"

echo ============================================================
echo  Arrow Transition - automatic joiner and extractor
echo ============================================================
echo.
echo This will rebuild the animation ZIP from its 23 downloaded
echo parts and extract all 360 animation frames.
echo.
echo Working in this folder:
echo   %~dp0
echo.

set "missing=0"
for /l %%i in (0,1,22) do (
  set "n=0%%i"
  set "n=!n:~-2!"
  if not exist "arrow-transition-png-sequence.zip.part-!n!" (
    echo MISSING: arrow-transition-png-sequence.zip.part-!n!
    set "missing=1"
  )
)
if "!missing!"=="1" (
  echo.
  echo Some part files are missing ^(listed above^). Please download
  echo them into this same folder, then double-click this file again.
  goto :fail
)
echo All 23 parts found.
echo.
echo Step 1 of 2: joining the parts into one ZIP ^(about a minute^)...

set "chain="
for /l %%i in (0,1,22) do (
  set "n=0%%i"
  set "n=!n:~-2!"
  set "chain=!chain!+arrow-transition-png-sequence.zip.part-!n!"
)
copy /b !chain:~1! "arrow-transition-png-sequence.zip" >nul
if errorlevel 1 (
  echo.
  echo Joining the parts failed. Try re-downloading the parts and
  echo running this again.
  goto :fail
)

for %%A in ("arrow-transition-png-sequence.zip") do set "size=%%~zA"
if not "!size!"=="2237413596" (
  echo.
  echo The rebuilt ZIP is !size! bytes but should be exactly
  echo 2237413596 bytes. One of the part files is probably an
  echo incomplete download - re-download the parts and run again.
  goto :fail
)
echo Joined OK - file size matches exactly.
echo.
echo Step 2 of 2: extracting the 360 frames ^(a few minutes^)...

powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -LiteralPath 'arrow-transition-png-sequence.zip' -DestinationPath '.' -Force"
if errorlevel 1 (
  echo.
  echo Extraction failed. Make sure there is at least 3 GB of free
  echo disk space, then run this again.
  goto :fail
)

set "cnt=0"
for /f %%C in ('dir /b "frames-final\*.png" 2^>nul ^| find /c /v ""') do set "cnt=%%C"
if not "!cnt!"=="360" (
  echo.
  echo Expected 360 frames but found !cnt!. Run this file again;
  echo if it keeps happening, re-download the parts.
  goto :fail
)

echo.
echo ============================================================
echo  Done! Your frames are in the "frames-final" folder:
echo    frame_0000.png ... frame_0359.png
echo.
echo  6878 x 1080 pixels, transparent background, 60 frames/sec.
echo  Frame 180 is the fully-covered moment ^(3.00 seconds^) -
echo  that is where you fade in the new scene.
echo.
echo  In Premiere / After Effects: import frame_0000.png with the
echo  "Image Sequence" box ticked, and set it to 60 fps.
echo.
echo  You can now delete the .part files and the big ZIP to free
echo  about 4.5 GB - the frames-final folder is all you need.
echo ============================================================
echo.
pause
exit /b 0

:fail
echo.
echo Something went wrong - see the message above. Nothing has been
echo damaged; you can safely run this file again after fixing it.
echo.
pause
exit /b 1
