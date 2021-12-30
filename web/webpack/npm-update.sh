#! /bin/sh
set -e
for package in $(npm outdated --parseable --depth=0 | cut -d: -f4)
do
  npm i "$package"
done