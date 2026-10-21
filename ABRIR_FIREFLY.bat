@echo off
title LOGIN ADOBE FIREFLY
echo ========================================================
echo ABRINDO CHROME COM O PERFIL DO FIREFLY...
echo ========================================================
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --user-data-dir="D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation\data\chrome_profile" --no-first-run --no-default-browser-check "https://firefly.adobe.com/generate/video"
echo Chrome disparado!
timeout /t 5
