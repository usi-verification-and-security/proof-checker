#!/usr/bin/env bash

PROOFCHECKERDIR=$(cd $(dirname $0); pwd)/proofchecker-output

usage="Usage: $0 [-h] -b <proofchecker> [instance [instance [...]]]"

while [ $# -gt 0 ]; do
    case $1 in
        -h|--help)
            echo $usage
            exit 1
            ;;
        -b|--binary)
            proofchecker=$2
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

if [ -z $proofchecker ]; then
    echo "Error: proofchecker not specified.  Use -b <proofchecker>"
    exit 1
fi

echo "Adding as follows:"
echo " - proofchecker: $proofchecker ($(date -r ${proofchecker}))"
echo " - files: $@"

echo "Is this ok?"
read -p "y/N? "

if [[ ${REPLY} != y ]]; then
    echo "Aborting."
    exit 1
fi

while [ $# -gt 0 ]; do
    echo $1;
    if [[ -a $1 ]]; then
        sh -c "ulimit -St 60; ${proofchecker} -t $1 \
            > $PROOFCHECKERDIR/$(basename $1).expected.out \
            2> $PROOFCHECKERDIR/$(basename $1).expected.err";
    else
        echo "File does not exist"
    fi;
    shift;
done

