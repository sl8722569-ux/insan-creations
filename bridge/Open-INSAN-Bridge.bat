@echo off
title INSAN Bridge
cd /d "%~dp0"
set PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
if not exist "%PY%" set PY=python
if exist "%~dp0.env" echo Using .env
echo Starting INSAN Bridge on http://127.0.0.1:8787/
echo Keep this window open while using SpaceXAI, ONVIF/RTSP, or NEXCODE pairing.
"%PY%" -u server.py
pause
