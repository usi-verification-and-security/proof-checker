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

    $SCRIPTDIR/proofparser \
        -o $TMPDIR/proof.tar.bz2 \
        $trail \
        > $TMPDIR/parser.out

    if (grep '^sat' $TMPDIR/parser.out > /dev/null); then
        echo "sat"
        return 0
    elif (grep '^invalid' $TMPDIR/parser.out > /dev/null); then
        echo "invalid"
        return 1
    elif (grep '^unknown' $TMPDIR/parser.out > /dev/null); then
        echo "unknown"
        return 0
    elif (grep -v '^unsat' $TMPDIR/parser.out); then
        echo "invalid"
        return 1
    fi

    logic=$(grep '^unsat' $TMPDIR/parser.out |awk '{print $2}')

    cd $TMPDIR;
    tar jxf proof.tar.bz2 > /dev/null 2>&1

    # The compressed trail is not a .tar.bz2
    if [ $? -ne 0 ]; then
        echo "invalid"
        return 0
    fi

    cd proof

    python3 $SCRIPTDIR/check_cnfization.py &> $cnfizationOut
    $SCRIPTDIR/drat-trim input.cnf proof.drat &> $dratOut

    if [[ "$logic" == "QF_LRA" ]]; then
        python3 $SCRIPTDIR/check_lra_lraTheory.py &> $lraOut
        python3 $SCRIPTDIR/check_lraTheoryProp.py &> $lraPropOut
    elif [[ "$logic" == "QF_LIA" ]]; then
        python3 $SCRIPTDIR/check_lia_lraTheory.py &> $lraOut
        python3 $SCRIPTDIR/check_lraTheoryProp.py &> $lraPropOut
        python3 $SCRIPTDIR/check_liaTheory.py &> $liaOut
        python3 $SCRIPTDIR/check_liaTheoryProp.py &> $liaPropOut
    elif [[ "$logic" == "QF_UF" ]]; then
        python3 $SCRIPTDIR/check_ufTheory.py &> $ufOut
        python3 $SCRIPTDIR/check_ufTheoryProp.py &> $ufPropOut
    fi

    if [[ "$logic" == "QF_LRA" ]]; then
        if (grep -Fqw "True" $cnfizationOut && \
                grep -Fqw "s VERIFIED" $dratOut && \
                grep -Fqw "True" $lraOut && \
                grep -Fqw "True" $lraPropOut); then
            echo "valid"
            return 0
        fi
    elif [[ "$logic" == "QF_LIA" ]]; then
       if (grep -Fqw "True" $cnfizationOut && \
                grep -Fqw "s VERIFIED" $dratOut && \
                grep -Fqw "True" $lraOut && \
                grep -Fqw "True" $lraPropOut && \
                grep -Fqw "True" $liaOut && \
                grep -Fqw "True" $liaPropOut); then
            echo "valid"
            return 0
        fi
    elif [[ "$logic" == "QF_UF" ]]; then
        if (grep -Fqw "True" $cnfizationOut && \
                grep -Fqw "s VERIFIED" $dratOut && \
                grep -Fqw "True" $ufOut && \
                grep -Fqw "True" $ufPropOut); then
            echo "valid"
            return 0
        fi
    fi

    echo "invalid"
    return 1
}

#########################

ok=false

checkTrail $trail && ok=true

#########################

if [[ $ok == true ]]; then
    exit 0;
else
    exit 1;
fi
