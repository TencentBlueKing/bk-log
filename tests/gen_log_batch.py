# -*- coding: utf-8 -*-
"""
批量生成日志
1. 每小时写3000个文件，每个文件增加100条记录，每个文件 100 * 24 => 2400 条记录
2. 文件名：202002120001 => 202002123000
"""
import os
import time
import random
import datetime
import shutil

file_nums = 100
log_nums = 100

path = os.path.dirname(os.path.abspath(__file__)) + "/logs"
log = " DEBUG   [publisher]     pipeline/client.go:155  client: cancelled 0 events\n"
now = time.time()

today = (datetime.datetime.now() - datetime.timedelta(minutes=1)).strftime("%Y%m%d")

# remove dir
files = os.listdir(path)
remain_date = int(today) - 3
for file in files:
    file_path = path + "/" + file
    if not os.path.isdir(file_path):
        continue
    file_date = int(file)
    if file_date < remain_date and file_date > 0:
        shutil.rmtree(file_path)

# create log dir
path = path + "/" + today
if not os.path.exists(path):
    os.mkdir(path)

# gen log file
files = []
for i in range(file_nums):
    files.append(today + str(i + 1).rjust(4, "0"))
files = files * log_nums
random.shuffle(files)

# gen log
i = 0
for file in files:
    fp = open(path + "/" + file + ".log", "a+")
    fp.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + log)
    fp.close()
    if i % 10000 == 9999:
        time.sleep(1)
    i = i + 1

print("spends: " + str(round(time.time() - now, 2)))
