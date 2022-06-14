#!/usr/bin/env bash

PROOFPARSERDIR=$(cd $(dirname $0); pwd)/proofparser-output

usage="Usage: $0 [-h] -b <proofparser> [instance [instance [...]]]"

while [ $# -gt 0 ]; do
    case $1 in
        -h|--help)
            echo $usage
            exit 1
            ;;
        -b|--binary)
            proofparser=$2
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

if [ -z $proofparser ]; then
    echo "Error: proofparser not specified.  Use -b <proofparser>"
    exit 1
fi

echo "Adding as follows:"
echo " - proofparser: $proofparser ($date -r ${proofparser}))"
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
        sh -c "ulimit -St 60; ${proofparser} -o /dev/null $1 \
            > $PROOFPARSERDIR/$(basename $1).expected.out \
            2> $PROOFPARSERDIR/$(basename $1).expected.err";
    else
        echo "File does not exist"
    fi;
    shift;
done

