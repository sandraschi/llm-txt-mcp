@echo off
REM Stop llm-txt-mcp fleet ports
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0web_sota\stop.ps1"
if errorlevel 1 pause

