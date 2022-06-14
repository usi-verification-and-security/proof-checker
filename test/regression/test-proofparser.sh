#!/bin/bash
get_abs_filename() {
  echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
}

PROOFPARSERDIR=$(cd $(dirname $0); pwd)/proofparser-output

usage="Usage: $0 [-h] <path-to-proofparser>"

while [ $# -gt 0 ]; do
    case $1 in
        -h|--help)
            echo "${usage}"
            exit 1
            ;;
        -*)
            echo "Error: invalid option '$1'"
            exit 1
            ;;
        *)
            break
    esac
    shift; shift
done


proofparser=$1

if [ -z ${proofparser} ]; then
    echo "Proofparser binary not specified"
    exit 1
fi

echo "This is the script for running regression tests"
echo " - date: $(date '+%Y-%m-%d at %H:%M.%S')"
echo " - host name $(hostname -f)"
echo " - script path: $(get_abs_filename $0)"

export outmod=false
export errmod=false
export rtmod=false

tmpdir=$(mktemp -d)
trap "rm -rf $tmpdir" EXIT

for file in instances/*.osmt; do
    name=$(basename $file)
    sh -c "ulimit -St 60; ${proofparser} -o /dev/null $file > $tmpdir/$name.out 2>$tmpdir/$name.err" 2>/dev/null
    diff -q $tmpdir/$name.out $PROOFPARSERDIR/$name.expected.out
    if [ $? != 0 ]; then
        echo "stdout differs for benchmark $file"
        outmod=true
    fi
    diff -q $tmpdir/$name.err $PROOFPARSERDIR/$name.expected.err
    if [ $? != 0 ]; then
        echo "stderr differs for benchmark $file";
        errmod=true;
    fi
done

if [[ ${outmod} == true || ${errmod} == true ]]; then
    echo "There were anomalies"
    exit 1
fi

