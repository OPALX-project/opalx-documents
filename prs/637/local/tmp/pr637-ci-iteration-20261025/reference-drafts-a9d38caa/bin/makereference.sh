#!/bin/bash -l 

# check if we can run
if [ -z "${OPALX_EXE_PATH+x}" ]; then
    echo "Error: OPALX_EXE_PATH is not defined."
    exit 1
fi

# now many ranks we use
RANKS=1   # default
while [ $# -gt 0 ]; do
    case "$1" in
        --ranks)
            if [ -n "$2" ] && [[ "$2" =~ ^[0-9]+$ ]]; then
                RANKS="$2"
                shift 2
            else
                echo "Error: --ranks requires a positive integer argument"
                exit 1
            fi
            ;;
        *)
            shift
            ;;
    esac
done
#echo "Using ranks = $RANKS"

#
F=`ls *.in`
FB=`basename -s ".in" $F`

# make the FB.local file
cat > ${FB}.local << EOF
#!/bin/bash
cd "\$(cd "\$(dirname "\$0")" && pwd)"
mpirun -np ${RANKS} "\$OPALX_EXE_PATH/opalx" ${F} --info 2 "\$@" 2>&1
EOF
chmod +x ${FB}.local

#
mpirun -np ${RANKS} ${OPALX_EXE_PATH}/opalx ${F} --info 10 | tee ${FB}.out

# collect output files (supports single and multi-container runs)
OUT_FILE=${FB}.out
shopt -s nullglob
STAT_FILES=(${FB}.stat ${FB}_c*.stat)
shopt -u nullglob

if [ ${#STAT_FILES[@]} -eq 0 ]; then
    echo "Error: no .stat files found for ${FB}"
    exit 1
fi

TIMING_FILE=timing.dat

#
mkdir -p reference
cp ${OUT_FILE} reference/
cp ${TIMING_FILE} reference/
cd reference
md5sum ${OUT_FILE} > ${OUT_FILE}.md5
md5sum ${TIMING_FILE} > ${TIMING_FILE}.md5
cd ..

for SF in "${STAT_FILES[@]}"; do
    cp ${SF} reference/
    cd reference
    md5sum ${SF} > ${SF}.md5
    cd ..
done

rm -rf data *.h5 *.out *.stat timing.dat
