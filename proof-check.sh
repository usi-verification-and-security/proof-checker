#!/bin/bash

SCRIPTDIR=$(cd $(dirname "$0"); pwd)

function checkEnv() {
    for tool in proofparser check_cnfization.py check_lra_lraTheory.py check_lia_lraTheory.py \
            check_liaTheory.py check_ufTheory.py check_lraTheoryProp.py check_liaTheoryProp.py \
            check_ufTheoryProp.py drat-trim; do
        if ! test -f $SCRIPTDIR/$tool; then
            echo "$tool not found"; return 1
        fi
    done
    return 0
}

usage="Usage: $0 [-h] -t <osmt-trail>"

while [ $# -gt 0 ]; do
    case $1 in
        -h|--help)
            echo "${usage}"
            exit 1
            ;;
        -t|--trail)
            trail=$2
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

if [[ -z $trail ]]; then
    echo "No trail provided"
    echo $usage
    exit 1
fi

checkEnv || exit 1

TMPDIR=$(mktemp -d)
trap "rm -rf ${TMPDIR}" EXIT

osmtOut="osmt.out"
cnfizationOut="cnfization.out"
dratOut="drat.out"
lraOut="lra.out"
lraPropOut="lraProp.out"
liaOut="lia.out"
liaPropOut="liaProp.out"
ufOut="uf.out"
ufPropOut="ufProp.out"

function checkTrail() {
    trail=$1
    logic=$2

    $SCRIPTDIR/proofparser -t $trail > $TMPDIR/proof.tar.bz2

    cd $TMPDIR;
    tar jxf proof.tar.bz2
    cd proof

    python3 $SCRIPTDIR/check_cnfization.py &> $cnfizationOut
    $SCRIPTDIR/drat-trim input.cnf proof.drat &> $dratOut

    if [[ "$logic" == "QF_LRA" ]]; then
        python3 $SCRIPTDIR/check_lra_lraTheory.py &> $lraOut
        python3 $SCRIPTDIR/check_lraTheoryProp.py &> $lraPropOut
    fi

    if [[ "$logic" == "QF_LIA" ]]; then
        python3 $SCRIPTDIR/check_lia_lraTheory.py &> $lraOut
        python3 $SCRIPTDIR/check_lraTheoryProp.py &> $lraPropOut
        python3 $SCRIPTDIR/check_liaTheory.py &> $liaOut
        python3 $SCRIPTDIR/check_liaTheoryProp.py &> $liaPropOut
    fi

    if [[ "$logic" == "QF_UF" ]]; then
        python3 $SCRIPTDIR/check_ufTheory.py &> $ufOut
        python3 $SCRIPTDIR/check_ufTheoryProp.py &> $ufPropOut
    fi

    if [[ "$logic" == "QF_LRA" ]] && \
            grep -Fqw "True" $cnfizationOut && \
            grep -Fqw "s VERIFIED" $dratOut && \
            grep -Fqw "True" $lraOut && \
            grep -Fqw "True" $lraPropOut; then
        return 0
    elif [[ "$theory" == "QF_LIA" ]] && \
            grep -Fqw "True" $cnfizationOut && \
            grep -Fqw "s VERIFIED" $dratOut && \
            grep -Fqw "True" $lraOut && \
            grep -Fqw "True" $lraPropOut && \
            grep -Fqw "True" $liaOut && \
            grep -Fqw "True" $liaPropOut; then
        return 0
    elif [[ "$logic" == "QF_UF" ]] && \
            grep -Fqw "True" $cnfizationOut && \
            grep -Fqw "s VERIFIED" $dratOut && \
            grep -Fqw "True" $ufOut && \
            grep -Fqw "True" $ufPropOut; then
        return 0
    else
#        echo "Invalid trail: $trail"
        return 1
    fi

#    echo "Problem testing $trail"
    return 1
}

#########################

ok=false

logic=$($SCRIPTDIR/proofparser -l $trail)

checkTrail $trail $logic && ok=true

#########################

if [[ $ok == true ]]; then
    echo "holey"
    exit 0;
else
    echo "invalid"
    exit 1;
fi
