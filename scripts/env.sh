#!/bin/bash

versions=(
  open
  ieod
  tencent
)

run_ver=$1
is_exists=0

for item in "${versions[@]}"; do
    [[ $run_ver == "$item" ]] && is_exists=1
done

if [ $is_exists -eq 0 ];then
  echo "./script/env.sh open|ieod|tencent"
  exit 1
fi

env=`pip --version | grep $run_ver | wc -l`
if [ $env -eq 0 ];then
  echo "python env error, Your python is:"
  pip --version
  exit 1
fi


if [ "$run_ver" = "open" ];then
  rm -rf ./queue_client_python-1.1.2-py2.py3-none-any.whl
  rm -rf ./blueapps
  export BKPAAS_ENGINE_REGION=open
  export BK_PAAS_HOST="http://paasee-bkdata-v3.o.qcloud.com/"
else
  rm -rf ./blueapps
  rm -rf ./blueking
  rm -rf ./bkoauth
  rm -f ./app.yml
  rm -f ./Procfile
  rm -f ./wsgi.py
  export BK_PAAS_HOST=""
  if [ "$run_ver" = "ieod" ];then
    export BKPAAS_ENGINE_REGION=ieod
  else
    export BKPAAS_ENGINE_REGION=tencent
  fi
fi

python ./scripts/change_run_ver.py -V $run_ver
pip install -r requirements.txt > /dev/null
pre-commit install
pre-commit install --hook-type commit-msg
