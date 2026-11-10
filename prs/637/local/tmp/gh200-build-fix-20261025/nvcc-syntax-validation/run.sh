#!/usr/bin/env bash
set -u
{
  date -u
  hostname
  module -t list 2>&1
  command -v nvcc gcc g++
  nvcc --version
  gcc --version | head -n 1
  printf 'Compile flags: -std=c++20 --extended-lambda -arch=sm_90 -c\n'
} > environment.log
: > status.tsv
for source in bad_private_payload fixed_namespace_payload bad_private_testbody fixed_namespace_helper; do
  nvcc -std=c++20 --extended-lambda -arch=sm_90 -c "$source.cu" -o "$source.o" > "$source.log" 2>&1
  result=$?
  printf '%s\t%s\n' "$source" "$result" >> status.tsv
done
cat status.tsv
for log in *.log; do
  printf '\n%s\n' "$log"
  cat "$log"
done
