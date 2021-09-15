#!/bin/bash

export LC_ALL=C
export LANG=C

anynowtime="date +'%Y-%m-%d %H:%M:%S'"
NOW="echo [\`$anynowtime\`][PID:$$]"

ERROR_CPACITY_NOT_ENOUGH=3

MAX_FILE_NAME_LENGTH=200

DF_FILESYSTEM_TOO_LONG=3
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

get_lan_ip () {
    ip addr | awk -F'[ /]+' '/inet/{
               split($3, N, ".")
               if ($3 ~ /^192.168/) {
                   print $3
               }
               if (($3 ~ /^172/) && (N[2] >= 16) && (N[2] <= 31)) {
                   print $3
               }
               if ($3 ~ /^9\./) {
                   print $3
               }
               if ($3 ~ /^10\./) {
                   print $3
               }
               if ($3 ~ /^11\./) {
                   print $3
               }
               if ($3 ~ /^30\./) {
                   print $3
               }
               if ($3 ~ /^100\./) {
                   print $3
               }
          }';
    return $?
}

get_win_lanip () {
    ipconfig | awk '/IP(v4)? /{
               split($NF, N, ".")
               if ($NF ~ /^192.168/) {
                   print $NF
               }
               if (($NF ~ /^172/) && (N[2] >= 16) && (N[2] <= 31)) {
                   print $NF
               }
               if ($NF ~ /^9\./) {
                   print $NF
               }
               if ($NF ~ /^10\./) {
                   print $NF
               }
               if ($NF ~ /^11\./) {
                   print $NF
               }
               if ($NF ~ /^30\./) {
                   print $NF
               }
               if ($NF ~ /^100\./) {
                   print $NF
               }
        }'
}

bk_log () {
  local key=$1; shift
  local value=$1
  echo "<BKLOG>$key:$value</BKLOG>"
}

tail_line () {
    local logfile=$1;
    local target_file=$2
    local line=$3

    tail -n "$line" "$logfile" > "$target_file"
}

match_word () {
    local logfile=$1 ; shift
    local target_file=$1; shift
    local match_type=$1; shift
    local words=$1
    case $match_type in
      keyword_or)
        # shellcheck disable=SC2001
        local or_pattern=$(echo "${words[@]}" | sed 's/ / \|\| /g')
        awk "$or_pattern" "$logfile" > "$target_file"
        ;;
      keyword_and)
        # shellcheck disable=SC2001
        local and_pattern=$(echo "${words[@]}" | sed 's/ / \&\& /g')
        awk "$and_pattern" "$logfile" > "$target_file"
        ;;
      keyword_not)
        # shellcheck disable=SC2001
        local pattern=$(echo "${words[@]}" | sed 's/ /|/g')
        awk '$0 !~ ''/'"$pattern"'/' "$logfile" > "$target_file"
        ;;
      *)
        ;;
    esac
}

match_range () {
    local logfile=$1; shift
    local target_file=$1; shift
    local start=$1 end=$2

    awk -v S="$start" -v E="$end" '$0 ~ S, $0 ~ E'  "$logfile" > "$target_file"
}

line_range () {
    local logfile=$1;
    local target_file=$2;
    local start=$3 end=$4

    tail -n +$((start)) "$logfile" | head -$((end - start + 1)) > "$target_file"
}

check_is_capacity_can_store_all_file () {
  local files=$1
  local tmp_dir=$2
  local files_size_kb=0
  local file_count=0
  for file in $files ; do
    [ -f $file ] || continue
    ((file_count=file_count + 1))
    local file_size_kb=$(du -ck $file | awk 'END{print $1}')
    ((files_size_kb=files_size_kb + file_size_kb))
  done
  local df_line=$(df "${tmp_dir}" | wc -l)
  local tmp_dir_size
  local tmp_total_size
  if [ $df_line -lt $DF_FILESYSTEM_TOO_LONG ]; then
    tmp_dir_size=$(df "${tmp_dir}" | awk 'END{print $3}')
    tmp_total_size=$(df "${tmp_dir}" | awk 'END{printf("%d", $2 * 0.9)}')
  else
    tmp_dir_size=$(df "${tmp_dir}" | awk 'END{print $2}')
    tmp_total_size=$(df "${tmp_dir}" | awk 'END{printf("%d", $1 * 0.9)}')
  fi
  local tmp_and_files_size=0
  ((tmp_and_files_size=tmp_dir_size + files_size_kb))
  bk_log "all_origin_file_size" "$files_size_kb"
  bk_log "file_count" "$file_count"
  [ $tmp_and_files_size -lt $tmp_total_size ] || exit $ERROR_CPACITY_NOT_ENOUGH
}

check_tmp_have_enough_cap () {
  local tmp_dir=$1
  local df_line=$(df "${tmp_dir}" | wc -l)
  local tmp_use
  if [ $df_line -lt $DF_FILESYSTEM_TOO_LONG ]; then
    tmp_use=$(df "${tmp_dir}" | awk 'END{printf("%d", $5)}')
  else
    tmp_use=$(df "${tmp_dir}" | awk 'END{printf("%d", $4)}')
  fi
  local use_rate=90
  [ $tmp_use -lt $use_rate ] || exit $ERROR_CPACITY_NOT_ENOUGH
}

job_start

# get local ip
case $(uname -s) in
    *Linux) export LAN_IP && LAN_IP=$(get_lan_ip | head -1) ;;
    *CYGWIN*) export LAN_IP && LAN_IP=$(get_win_lanip | head -1) ;;
esac

dst_path=$1
#log_files=$2
target_file_name=$3
is_distributing_packing=$4
log_files="{{ log_files }}"

# file filter
filter_type=$5
cond1=$6
cond2=$7
max_file_size_limit=$8
failed_file=()

# step 1: init dir
if [[ "$dst_path" != *bk_log* && "$is_distributing_packing" == "0" ]];
then
  job_fail "dst_path is not allow"
fi

# strip last char
if [[ "${dst_path: -1}" == "/" ]]; then
  dst_path=${dst_path%?}
fi

tmp_dir=${dst_path%/*}
# delete history file
bk_log_extract_path="${tmp_dir}"
if [[ -d "$bk_log_extract_path" && "${bk_log_extract_path}" == *"/tmp/bk_log_extract"* ]];then
  # shellcheck disable=SC2038
  find "$bk_log_extract_path/" -mmin +60 -type d | xargs rm -rf
fi

mkdir -p "$dst_path/"
cd "$dst_path" || exit $?

tmp_dir=${dst_path%/*}
# check /tmp have enough capacity for log_file
check_is_capacity_can_store_all_file "$log_files" "$tmp_dir"

pack_files_size_kb=0
# step 3: archive file
for log_file in $log_files
  do
    if [ -d "$log_file" ];then
      job_fail "$log_file is not file"
    fi
    log_file_dir=$(dirname $log_file)
    log_file_dir=${log_file_dir#/}
    # replace / to _ -> /asdf/asdf/asdf/ -> asdf_asdf_asdf
    log_file_name=$(echo "$log_file_dir" | sed -e "s/\//_/g")
    log_file_name="${log_file_name}_$(basename $log_file)"
    # if log_file_name over MAX_FILE_NAME_LENGTH turncate over char
    log_file_name_length=${#log_file_name}
    turncate_start=0
    if [ $log_file_name_length -gt $MAX_FILE_NAME_LENGTH ]; then
      turncate_start=$((log_file_name_length - MAX_FILE_NAME_LENGTH))
    fi
    log_file_name=${log_file_name:$turncate_start}
    log_file_name="${LAN_IP}_${log_file_name}"
    target_dir="$dst_path/source"
    target_file="${dst_path}/source/$log_file_name"
    job_log "target_dir=>$target_dir"
    job_log "target_file=>$target_file"
    mkdir -p "$target_dir"

    case $filter_type in
        match_word)
            job_log "match_word $log_file $cond1"
            match_word "$log_file" "$target_file" "$cond2" "$cond1"
            ;;
        match_range)
            job_log "match_range $log_file $cond1 $cond2"
            match_range "$log_file" "$target_file" "$cond1" "$cond2"
            ;;
        line_range)
            job_log "line_range $log_file $cond1 $cond2"
            line_range "$log_file" "$target_file" "$cond1" "$cond2"
            ;;
        tail_line)
            job_log "tail_line $log_file $cond1"
            tail_line "$log_file" "$target_file" "$cond1"
            ;;
        *)
            job_log "cp -av $log_file $target_file"
            cp -av "$log_file" "$target_file"
    esac
    if [ ! -s "$target_file"  ]; then
      failed_file[${#failed_file[@]}]=$log_file
    fi

    file_size_kb=$(du -ck $target_file | awk 'END{print $1}')
    ((pack_files_size_kb=pack_files_size_kb + file_size_kb))
  done

bk_log "all_pack_file_size" "$pack_files_size_kb"
# step 4: tar
check_tmp_have_enough_cap "$tmp_dir"
job_log "tar -zcPf $target_file_name -C $dst_path/source/ ./"
tar -zcPf "$dst_path/$target_file_name" -C "${dst_path}/source/" ./
rm -rf "${dst_path}/source/"

# step 5: check tar size
size=$(ls --full-time "$dst_path/$target_file_name" | awk "{print int(\$5)}")
echo "${LAN_IP}_$target_file_name size:$size"

if [ "$size" -gt "${max_file_size_limit}" ];then
  job_fail "file size gather than ${max_file_size_limit} Bytes"
fi

job_success "packing done"
