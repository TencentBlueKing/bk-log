#!/bin/bash

export LC_ALL=C
export LANG=C

anynowtime="date +'%Y-%m-%d %H:%M:%S'"
NOW="echo [\`$anynowtime\`][PID:$$]"
TARGET_DIR_PREFIX="/bk_log_extract/distribution/"
function job_start {
    echo "$(eval "$NOW") job_start"
}

function job_log {
    MSG="$*"
    echo "$(eval "$NOW") $MSG"
}

function job_success {
    MSG="$*"
    echo "$(eval "$NOW") job_success:[$MSG]"
    exit 0
}

function job_fail {
    MSG="$*"
    echo "$(eval "$NOW") job_fail:[$MSG]"
    exit 1
}

dst_path=$1;shift
cos_pack_file_name=$1;shift
target_dir=$1;shift
run_ver=$1

# check target_dir must is BKLOG dir
[[ $target_dir == *$TARGET_DIR_PREFIX* ]] || job_fail "$target_dir illegal"


add_ip_to_pack_file() {
  cd "$target_dir" || job_fail "$target_dir not exists"
  not_dir="${target_dir}/[]/"
  if [ -d "$not_dir" ]; then
    cd "[]"
  fi
  for ip in ./* ; do
    cd $ip
    pack_file=$(ls)
    if [ -d "$not_dir" ]; then
      mv $pack_file "../../${ip}_${pack_file}"
      cd "${target_dir}/[]/"
      rm -rf "${target_dir}/[]/${ip}"
      continue
    fi
    mv $pack_file "../${ip}_${pack_file}"
    cd "${target_dir}"
    rm -rf "${target_dir}/${ip}"
  done
  if [ -d "$not_dir" ]; then
    rm -rf "${target_dir}/[]"
  fi
}

add_ip_to_pack_file
job_log "tar -cPf ${dst_path}/${cos_pack_file_name} -C $target_dir ./"
tar -cPf "${dst_path}/${cos_pack_file_name}" -C "$target_dir" ./
rm -rf "$target_dir"

job_success "Cos upload success"
