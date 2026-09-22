@echo off
REM ===========================================================================
REM init.bat — Harness Windows (equivalente a init.sh).
REM Debe terminar en "HARNESS OK". Criterios: CHECKPOINTS.md
REM Uso: init.bat [local|remote]    (default: remote)
REM Destino: DW_INF_CONSOL_RDATA + DW_INF_CONSOL_FORM + DW_INF_CSEP_INFORMES_VIEW
REM ===========================================================================
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "H2_JAR=%~dp0h2\lib\h2-2.4.240.jar"

set "ENV=%~1"
if "%ENV%"=="" set "ENV=remote"
echo ==^> Harness Windows: entorno %ENV%

set "PY=%~dp0.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"

REM ---- feature_list.json: max una in_progress ----
echo ==^> Validando feature_list.json
"%PY%" -c "import json,sys;d=json.load(open('feature_list.json',encoding='utf-8'));act=[f for f in d.get('features',[]) if f.get('status')=='in_progress'];print('features: '+str(len(d.get('features',[])))+', in_progress: '+str(len(act)));sys.exit(1 if len(act)>1 else 0)"
if errorlevel 1 (
  echo FAIL: mas de una in_progress en feature_list.json
  exit /b 1
)

REM ---- Prerrequisitos ----
echo ==^> Prerrequisitos
java -version >nul 2>&1
if errorlevel 1 (
  echo FAIL: java no esta en PATH
  exit /b 1
)
if not exist "%H2_JAR%" (
  echo FAIL: jar H2 no encontrado
  exit /b 1
)
if not exist "%~dp0.venv\Scripts\python.exe" (
  echo FAIL: venv ausente o roto. Crear con: python -m venv .venv ^&^& .venv\Scripts\python -m pip install -r python\requirements.txt
  exit /b 1
)
"%PY%" -c "import yaml, pandas, jaydebeapi, pymysql" >nul 2>&1
if errorlevel 1 (
  echo FAIL: el .venv no tiene dependencias. .venv\Scripts\python -m pip install -r python\requirements.txt
  exit /b 1
)

REM ---- Rscript (suele no estar en PATH; se agrega su dir al PATH) ----
where Rscript >nul 2>&1
if errorlevel 1 (
  for /d %%d in ("C:\Program Files\R\R-*") do (
    if exist "%%d\bin\Rscript.exe" set "PATH=%%d\bin;%PATH%"
  )
)
where Rscript >nul 2>&1
if errorlevel 1 (
  echo FAIL: Rscript no esta en PATH
  exit /b 1
)

REM ---- project-config.json via switch-env ----
if not exist "%~dp0project-config.json" (
  echo ==^> Generando project-config.json ^(switch-env %ENV%^)
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0switch-env.ps1" %ENV%
  if errorlevel 1 (
    echo FAIL: switch-env %ENV%
    exit /b 1
  )
)

REM ---- Reset H2 + DDL ----
echo ==^> Reset H2 + DDL
call h2\scripts\reset_and_create.bat
if errorlevel 1 (
  echo FAIL: reset_and_create.bat
  exit /b 1
)

REM ---- Python create STG ----
echo ==^> Python create STG
"%PY%" python\create_stg.py
if errorlevel 1 (
  echo FAIL: create_stg.py
  exit /b 1
)

REM ---- Stage RData ----
echo ==^> Stage RData -^> STG_INF_CONSOL
set "PATH=%PATH%;%~dp0h2\scripts"
"%PY%" python\stage_rdata.py
if errorlevel 1 (
  echo FAIL: stage_rdata.py
  exit /b 1
)

REM ---- Stage MySQL soft ----
echo ==^> Stage MySQL -^> STG_INF_CONSOL_FORM ^(soft^)
"%PY%" python\stage_mysql.py --soft
if errorlevel 1 (
  echo FAIL: stage_mysql.py --soft
  exit /b 1
)

REM ---- Python main (siempre RDATA + FORM) ----
echo ==^> Python main ^(DW_INF_CONSOL_RDATA + DW_INF_CONSOL_FORM siempre^)
set "LOG=%TEMP%\init_harness_main.log"
"%PY%" python\main.py > "%LOG%" 2>&1
set "MAIN_RC=!ERRORLEVEL!"
type "%LOG%"
if not "!MAIN_RC!"=="0" (
  echo FAIL: python\main.py termino con codigo !MAIN_RC!
  exit /b 1
)

REM ---- CSEP soft + load ----
echo ==^> CSEP_INFORMES_VIEW -^> DW_INF_CSEP_INFORMES_VIEW ^(soft + load^)
"%PY%" python\ddl_csep_informes.py --load --soft >> "%LOG%" 2>&1
set "CSEP_RC=!ERRORLEVEL!"
type "%LOG%" | findstr /C:"Destino:" /C:"AVISO:" /C:"ERROR:" /C:"Fuente:"
if not "!CSEP_RC!"=="0" (
  echo FAIL: ddl_csep_informes.py termino con codigo !CSEP_RC!
  exit /b 1
)

echo ==^> Comprobando salidas ^(3 tablas destino^)
findstr /C:"Salida RESULTADO" "%LOG%" >nul
if errorlevel 1 (
  echo FAIL: no hay Salida RESULTADO en el log
  exit /b 1
)
findstr /C:"DW_INF_CONSOL_RDATA" "%LOG%" >nul
if errorlevel 1 (
  echo FAIL: no hay carga Oracle DW_INF_CONSOL_RDATA en el log
  exit /b 1
)
findstr /C:"DW_INF_CONSOL_FORM" "%LOG%" >nul
if errorlevel 1 (
  echo FAIL: no hay carga Oracle DW_INF_CONSOL_FORM en el log
  exit /b 1
)
findstr /C:"Destino: CREATE DW_INF_CSEP_INFORMES_VIEW" "%LOG%" >nul
if errorlevel 1 (
  echo FAIL: no hay CREATE DW_INF_CSEP_INFORMES_VIEW en el log
  exit /b 1
)
findstr /C:"Excel:" "%LOG%" >nul
if errorlevel 1 echo AVISO: no se escribio Excel ^(opcional^)

findstr /L /C:"${" "%LOG%" >nul
if not errorlevel 1 (
  echo FAIL: log contiene variables Hop sin resolver
  exit /b 1
)

echo.
echo HARNESS OK — 3 tablas: DW_INF_CONSOL_RDATA, DW_INF_CONSOL_FORM, DW_INF_CSEP_INFORMES_VIEW
exit /b 0
