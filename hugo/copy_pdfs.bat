@echo off
echo Copying PDF files to hugo\static\pdfs...
echo.

if not exist "hugo\static\pdfs" mkdir "hugo\static\pdfs"

if exist "..\docs\progress_presentations\StressSpec_Final_Presentation.marp.pdf" (
    copy "..\docs\progress_presentations\StressSpec_Final_Presentation.marp.pdf" "static\pdfs\" >nul
    echo [OK] Copied StressSpec_Final_Presentation.marp.pdf
) else (
    echo [ERROR] Source file not found: docs\progress_presentations\StressSpec_Final_Presentation.marp.pdf
)

if exist "..\docs\architecture.marp.pdf" (
    copy "..\docs\architecture.marp.pdf" "static\pdfs\" >nul
    echo [OK] Copied architecture.marp.pdf
) else (
    echo [ERROR] Source file not found: docs\architecture.marp.pdf
)

if exist "..\docs\StressSpec_Project_Progress.pdf" (
    copy "..\docs\StressSpec_Project_Progress.pdf" "static\pdfs\" >nul
    echo [OK] Copied StressSpec_Project_Progress.pdf
) else (
    echo [ERROR] Source file not found: docs\StressSpec_Project_Progress.pdf
)

if exist "..\docs\user_guide.pdf" (
    copy "..\docs\user_guide.pdf" "static\pdfs\" >nul
    echo [OK] Copied user_guide.pdf
) else (
    echo [ERROR] Source file not found: docs\user_guide.pdf
)

echo.
echo Done! Verifying files...
dir "static\pdfs\*.pdf" /b
echo.
pause


