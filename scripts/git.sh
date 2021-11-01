#!/bin/bash

SCRIPT_PATH=$(dirname "$0")
source $SCRIPT_PATH/default_env.sh
check_upstream_config() {
  if ! git remote -v | grep -q "upstream";then
    git remote add upstream $DEFAULT_GIT_REP
  fi
}

sync() {
    git fetch upstream
    git merge upstream/stag
}

check_upstream_config

actions=(
  sync
  create_branch
)

action=$1
is_exists=0

for item in "${actions[@]}"; do
    [[ $action == "$item" ]] && is_exists=1
done

if [ $is_exists -eq 0 ];then
  echo "./script/git.sh sync|create_branch"
  exit 1
fi

if [ "$action" = "create_branch" ];then
  git checkout stag
  sync
  git push -u origin stag
  git checkout -b "$2"
elif [ "$action" = "sync" ];then
  sync
fi

delete_upstream_config() {
  if git remote -v | grep -q "upstream";then
    git remote remove upstream
  fi
}

delete_upstream_config

