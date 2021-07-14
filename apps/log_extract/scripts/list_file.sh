#!/bin/bash

export LC_ALL=C
export LANG=C

if [ $# -le 4 ];then
  echo "Usage:"
  echo "./search.sh [search_path] [file_type] [is_search_child] [time_range]"
  exit 1
fi

RANDOM_NUM=$RANDOM
BK_LOG_DIR_LIST="/tmp/bk_log_dir_list_${RANDOM_NUM}"
BK_LOG_FILE_LIST="/tmp/bk_log_file_list_${RANDOM_NUM}"
BK_LOG_RECORD="/tmp/bk_log_record_${RANDOM_NUM}"
SORT_FIELD=3

MAX_FILE_LIST=500


init_tmp_file () {
  echo "" > $BK_LOG_FILE_LIST
  echo "" > $BK_LOG_DIR_LIST
  echo "" > $BK_LOG_RECORD
  echo $BK_LOG_RECORD
  echo $BK_LOG_FILE_LIST
  echo $BK_LOG_DIR_LIST
}

search_path=$1
file_type=$2
is_search_child=$3
time_range=$4
start_time=$5
end_time=$6
# search dir
dir_path=$(echo "$search_path" | awk -F "/" 'OFS="/"{$NF="";print}')
file_path=$(echo "$search_path" |awk -F "/" '{print $NF}')

init_tmp_file


if [ "$file_path" != "" ];then
  is_search_child="1"
fi

if [ "$is_search_child" == "0" ];then
  # shellcheck disable=SC2086
  dirs=$(find $dir_path -maxdepth 1 -type d | grep -v " ")
  for dir in $dirs
    do
      if [ "$dir" != "$search_path" ];then
        dirname=$(ls -d "$dir")
        if echo "$dir" |grep -q '/$'; then
          echo "dirname:$dirname"
        else
          echo "dirname:$dirname/"
        fi
      fi
   done
fi

maxdepth=""
if [ "$is_search_child" == "0" ];then
  maxdepth=" -maxdepth 1"
fi

mtime=""
if [ "$time_range" != "0" ];then
  mtime=" -mtime -$time_range"
fi

if [ "$time_range" == "custom" ]; then
  mtime=" -newermt \"${start_time}\" ! -newermt \"${end_time}\" "
fi

if [ "$file_path" == "" ];then
    # shellcheck disable=SC2086
    echo "find $dir_path $maxdepth $mtime -type f | grep -E \"[^/]($file_type)\" >> $BK_LOG_FILE_LIST"
    for dir in $dir_path
      do
        cmd="find $dir $maxdepth $mtime -type f | grep -E \"[^/]($file_type)\" >> $BK_LOG_FILE_LIST"
        echo $cmd | sh
    done
else
    # shellcheck disable=SC2086
    echo "find $dir_path$file_path $maxdepth $mtime -type f | grep -E \"[^/]($file_type)\" >> $BK_LOG_FILE_LIST"
    for file in ${dir_path}${file_path}
      do
        cmd="find $file $maxdepth $mtime -type f | grep -E \"[^/]($file_type)\" >> $BK_LOG_FILE_LIST"
        echo $cmd | sh
    done
fi


while read file
  do
    # shellcheck disable=SC2012
    ls --full-time "$file" | awk '{print "fname:" $9,"size:" $5, "mtime:" $6 , $7}' | sed -rn "s/(.*)\.(.*)/\1/p" >> $BK_LOG_RECORD
done < "$BK_LOG_FILE_LIST"

# sort file list
sort -t ' ' -k $SORT_FIELD $BK_LOG_RECORD -r -o $BK_LOG_RECORD
head -n $MAX_FILE_LIST $BK_LOG_RECORD

# clear tmp file
rm -f $BK_LOG_DIR_LIST
rm -f $BK_LOG_FILE_LIST
rm -f $BK_LOG_RECORD

exit $?

