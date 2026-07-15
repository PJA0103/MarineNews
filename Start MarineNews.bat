@echo off

cd /d C:\vscode\MarineNews

echo Updating Marine News...

python crawler.py

echo.
echo Starting Streamlit...

python -m streamlit run app.py

pause