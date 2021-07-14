#!/bin/bash

export LC_ALL=C
export LANG=C


function bklog_begin {
  echo -n "#####bklog_begin######"
}
function bklog_end {
  echo -n "#####bklog_end######"
}
ticket_id=$1
random_key=$2
target_path=$3
file_path=$4
bk_biz_id=$5
cstone_url=$6
MD5=$(md5sum "$file_path"  |cut  -d " " -f1)

size=$(ls --full-time "$file_path" | awk "{print int(\$5)}")
echo "$file_path size:$size"

if [ "$size" -gt 1073741824 ];then
  job_fail "file size gather than 1024MB"
fi

bklog_begin
curl -s -XPOST  \
  -F ticket_id="$ticket_id"  \
  -F random_key="$random_key"  \
  -F file_type=server  \
  -F release_note='bk_log_extreact'  \
  -F target_path="$target_path"   \
  -F file=@"$file_path"  \
  -F md5="${MD5}"  \
  -F cc_id="$bk_biz_id" \  \
  -F custom_filed=bk_log  \
  -F version_id=1.0.0 \
  "$cstone_url"
bklog_end

exit $?
