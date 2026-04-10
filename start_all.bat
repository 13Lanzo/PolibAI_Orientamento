@echo off
echo ==============================================
echo Avvio del Progetto PolibAI (Angular + Backend)
echo ==============================================

echo Avvio del backend Python sulla porta 5000...
start cmd /k "cd backend && python chatbot.py"

echo Avvio del frontend Angular sulla porta 4201...
start cmd /k "npm start"

echo.
echo ATTENZIONE: Sono state aperte due nuove finestre. 
echo - Una gestisce il Server AI Python (backend)
echo - L'altra gestisce il sito web Angular (frontend)
echo.
echo Puoi chiudere questa finestra.
pause
