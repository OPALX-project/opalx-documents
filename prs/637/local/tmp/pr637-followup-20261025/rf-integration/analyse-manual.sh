#!/bin/bash
set -euo pipefail
study=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
: > "$study/integration-checks.tsv"
: > "$study/final-particles.csv"
for name in one-proton-one-rank one-proton-two-ranks two-protons-one-rank two-protons-two-ranks; do
    case_dir="$study/$name"
    result=$(cat "$case_dir/exit-code.txt")
    if test "$result" != 0; then printf '%s\tunexpected_exit\t%s\n' "$name" "$result" >> "$study/integration-checks.tsv"; continue; fi
    if ! rg -q 'EKINSTOP reached after complete gap kick' "$case_dir/run.log"; then printf '%s\tmissing_reference_stop\n' "$name" >> "$study/integration-checks.tsv"; continue; fi
    hdf="$case_dir/Cyclotron-RF-Stop.h5"
    step=$(h5ls "$hdf" | awk '/^Step#/ {sub(/^Step#/,"",$1); if(!found || $1+0>last) last=$1+0; found=1} END {if(found) print last;else exit 2}')
    args=()
    for field in id x y z px py pz; do args+=(-d "/Step#$step/$field"); done
    for field in MASS RefPartP RefPartR TIME; do args+=(-a "/Step#$step/$field"); done
    h5dump -m '%.17g' "${args[@]}" "$hdf" > "$case_dir/final-state.h5dump"
    awk -v caseName="$name" -f "$study/extract-final.awk" "$case_dir/final-state.h5dump" > "$case_dir/final-particles.csv"
    if test ! -s "$study/final-particles.csv"; then head -1 "$case_dir/final-particles.csv" > "$study/final-particles.csv"; fi
    tail -n +2 "$case_dir/final-particles.csv" >> "$study/final-particles.csv"
    awk -F, -v name="$name" 'NR>1 {n++; if($9<73 || $10<73) bad=1; if(n==1){firstEnergy=$9;firstPz=$8;time=$11;ref=$10} printf "%s\tparticle_%s_MeV\t%.15g\n",name,$2,$9} END {printf "%s\tparticles\t%d\n%s\treference_MeV\t%.15g\n%s\ttime_s\t%.17g\n%s\tenergy_target\t%s\n",name,n,name,ref,name,time,name,bad?"FAIL":"PASS"}' "$case_dir/final-particles.csv" >> "$study/integration-checks.tsv"
    awk 'NF>30 && $1 ~ /^[+-]?[0-9]/ {row=$0} END {print row}' "$case_dir/Cyclotron-RF-Stop.stat" > "$case_dir/final-stat-row.txt"
done
for name in failure-one-rank failure-two-ranks failure-probe-verified-one-rank failure-probe-verified-two-ranks; do
    case_dir="$study/$name"
    result=$(cat "$case_dir/exit-code.txt")
    printf '%s\texit_code\t%s\n' "$name" "$result" >> "$study/integration-checks.tsv"
    if test -f "$case_dir/accepted-before-failure.loss"; then
        awk -v name="$name" '!/^#/ && NF>0 {hits++; print > "/dev/stderr"} END {printf "%s\taccepted_hits\t%d\n",name,hits}' "$case_dir/accepted-before-failure.loss" >> "$study/integration-checks.tsv"
    else printf '%s\taccepted_hits\tMISSING\n' "$name" >> "$study/integration-checks.tsv"; fi
    if test -f "$case_dir/accepted-before-failure.hist"; then
        awk -v name="$name" '!/^#/ && NF>0 {sum+=$1} END {printf "%s\thistogram_sum\t%.0f\n",name,sum}' "$case_dir/accepted-before-failure.hist" >> "$study/integration-checks.tsv"
    else printf '%s\thistogram_sum\tMISSING\n' "$name" >> "$study/integration-checks.tsv"; fi
done
awk -F, 'NR==2 {for(i=3;i<=17;i++) baseline[i]=$i;next} NR>2 {for(i=3;i<=17;i++) {d=$i-baseline[i];if(d<0)d=-d;if(d>delta[i])delta[i]=d}} END {split("x_m y_m z_m px_mc py_mc pz_mc particle_MeV reference_MeV time_s ref_x_m ref_y_m ref_z_m ref_px_mc ref_py_mc ref_pz_mc",label," ");for(i=3;i<=17;i++) printf "%s\tmax_abs_difference\t%.17g\n",label[i-2],delta[i]}' "$study/final-particles.csv" > "$study/rank-and-particle-differences.tsv"
cat "$study/integration-checks.tsv"
cat "$study/rank-and-particle-differences.tsv"
