@echo off
REM ===========================================================================
REM init.bat — Harness Windows diario: FORM + CSEP (hop-run).
REM RData/backup: Hop → wf_create_stg_windows (bajo demanda).
REM Uso: init.bat [local|remote]    (default: remote)
REM ===========================================================================
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "HOP_PROJECT=etl_informes_harness"
if not "%HOP_PROJECT_OVERRIDE%"=="" set "HOP_PROJECT=%HOP_PROJECT_OVERRIDE%"
set "HOP_RUNCONFIG=local"

set "ENV=%~1"
if "%ENV%"=="" set "ENV=remote"
echo ==^> Harness Windows diario: entorno %ENV%

set "PY=%~dp0.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"

set "HOP_RUN="
if defined HOP_HOME if exist "%HOP_HOME%\hop-run.bat" set "HOP_RUN=%HOP_HOME%\hop-run.bat"
if "%HOP_RUN%"=="" if exist "%USERPROFILE%\apps\hop\hop-run.bat" set "HOP_RUN=%USERPROFILE%\apps\hop\hop-run.bat"
if "%HOP_RUN%"=="" (
  echo FAIL: hop-run.bat no encontrado ^(HOP_HOME o %%USERPROFILE%%\apps\hop^)
  exit /b 1
)

echo ==^> Validando feature_list.json
"%PY%" -c "import json,sys;d=json.load(open('feature_list.json',encoding='utf-8'));act=[f for f in d.get('features',[]) if f.get('status')=='in_progress'];print('features: '+str(len(d.get('features',[])))+', in_progress: '+str(len(act)));sys.exit(1 if len(act)>1 else 0)"
if errorlevel 1 (
  echo FAIL: mas de una in_progress en feature_list.json
  exit /b 1
)

echo ==^> Prerrequisitos
java -version >nul 2>&1
if errorlevel 1 (
  echo FAIL: java no esta en PATH
  exit /b 1
)

if not exist "%~dp0project-config.json" (
  echo ==^> Generando project-config.json ^(switch-env %ENV%^)
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0switch-env.ps1" %ENV%
  if errorlevel 1 (
    echo FAIL: switch-env %ENV%
    exit /b 1
  )
)

echo ==^> hop-run pl_form_informes.hpl
call "%HOP_RUN%" -j %HOP_PROJECT% -r %HOP_RUNCONFIG% -f "%~dp0pipelines\pl_form_informes.hpl" -l Basic
if errorlevel 1 (
  echo FAIL: hop-run pl_form_informes.hpl
  exit /b 1
)

echo ==^> hop-run pl_csep_informes.hpl
call "%HOP_RUN%" -j %HOP_PROJECT% -r %HOP_RUNCONFIG% -f "%~dp0pipelines\pl_csep_informes.hpl" -l Basic
if errorlevel 1 (
  echo FAIL: hop-run pl_csep_informes.hpl
  exit /b 1
)

echo.
echo HARNESS OK — diario FORM + CSEP ^(Hop^). RData: wf_create_stg_windows bajo demanda.
exit /b 0
