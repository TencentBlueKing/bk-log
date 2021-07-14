@echo off

set versions=open,ieod,tencent

set run_ver=%1
set is_exists=0

for  %%t in (%versions%) do (
if "%run_ver%"=="%%t" set is_exists=1
)



if %is_exists% == 0 ( echo "./script/env.bat open|ieod|tencent"
                      pause
                      exit)


pip --version|find /c "%run_ver%" > ver.tmp

for /f %%i in (ver.tmp) do ( set env=%%i
del /f /a /q ver.tmp

)

if %env% == 0 (echo "python env error, Your python is:"
 pip --version
 pause
 exit)


if %run_ver% == open (
    set BKPAAS_ENGINE_REGION=open
    set BK_PAAS_HOST="http://paasee-bkdata-v3.o.qcloud.com/"
)else (
    rd /s /q blueapps
    rd /s /q blueking
    del /f /a /q app.yml
    del /f /a /q Procfile
    if %run_ver% == ieod (
        set BKPAAS_ENGINE_REGION=ieod
    ) else (
        set BKPAAS_ENGINE_REGION=ieod
    )
    set BK_PAAS_HOST=""
)


python scripts\change_run_ver.py -V %run_ver%
pip install -r requirements.txt > NUL
