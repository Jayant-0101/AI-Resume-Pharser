@echo off
echo Installing Enhanced Parser Dependencies for High Accuracy (>85%%)...
echo.

echo Installing spaCy...
pip install spacy>=3.7.0

echo.
echo Installing spaCy English model (large - best accuracy)...
python -m spacy download en_core_web_lg

if errorlevel 1 (
    echo Large model failed, trying medium model...
    python -m spacy download en_core_web_md
    
    if errorlevel 1 (
        echo Medium model failed, trying small model...
        python -m spacy download en_core_web_sm
    )
)

echo.
echo Installing dateparser...
pip install dateparser>=1.2.0

echo.
echo Installation complete!
echo.
echo The enhanced parser will now use:
echo - spaCy for better Named Entity Recognition
echo - Multiple extraction strategies for higher accuracy
echo - Optimized for <5 second response time
echo.
pause

