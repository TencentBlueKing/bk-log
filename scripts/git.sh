#!/bin/bash

actions=(
  release
  sync
  tencent
  tests
)

action=$1
is_exists=0

for item in "${actions[@]}"; do
    [[ $action == "$item" ]] && is_exists=1
done

if [ $is_exists -eq 0 ];then
  echo "./script/git.sh tests|release|sync|tencent"
  exit 1
fi

if [ "$action" = "release" ];then
    git checkout tencent_stag
    git pull

    git checkout stag
    git pull

    git merge tencent_stag
elif [ "$action" = "tests" ];then
    git checkout tencent_stag
    git pull
    git checkout gitopen_stag
    git pull
    git merge tencent_stag
elif [ "$action" = "sync" ];then
    git checkout master
    git pull
    git checkout gitopen_master
    git merge master
else
    git checkout master
    git pull
    git checkout tencent_master
    git merge master
fi

