#!/bin/bash

SCRIPT_PATH=$(dirname "$0")
source $SCRIPT_PATH/default_env.sh
check_upstream_config() {
  if ! git remote -v | grep -q "upstream";then
    git remote add upstream $DEFAULT_GIT_REP
  fi
}

sync_stag() {

    git fetch upstream
    git merge upstream/stag
}

sync_upstream() {
  git fetch upstream
  current_branch=$(git rev-parse --abbrev-ref HEAD)
  git merge upstream/$current_branch
}

check_upstream_config

actions=(
  sync_upstream
  sync_stag
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
elif [ "$action" = "sync_stag" ];then
  sync_stag
elif [ "$action" = "sync_upstream" ];then
  sync_upstream
fi

delete_upstream_config() {
  if git remote -v | grep -q "upstream";then
    git remote remove upstream
  fi
}

delete_upstream_config

