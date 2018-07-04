#!/bin/bash

if [ $# -ne 4 ]; then
  echo "usage: $0 <srclang> <trglang> <indir> <outdir>"
  echo "  <indir> has subdirectories sentence_alignment, <srclang> and <trglang>"
  echo "  <outdir> has the same structure as sentence_alignment"
fi

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Script directory: $SCRIPTDIR"

SL=$1
TL=$2
INDIR=$3
OUTDIR=$4

ORIGDIR=$(pwd)

# Use /dev/shm as temporary -- is it faster than /tmp?
TMPDIR=/dev/shm/gargantua.$$
mkdir -p $TMPDIR
trap "rm -rf $TMPDIR" EXIT

# Settings specific to Notre Dame
module unload gcc boost python
module load boost/1.66
module load python/3.6.4

export OMP_NUM_THREADS=12 # too many is too slow

#fsync -d 60 $ORIGDIR/gargantua.log &
exec 1>$ORIGDIR/gargantua.log
exec 2>&1

mkdir $TMPDIR/corpus_to_align
python3 $SCRIPTDIR/extract_ltf.py $INDIR $TMPDIR/corpus_to_align $SL $TL > $TMPDIR/files.txt

(cd $TMPDIR/corpus_to_align; $SCRIPTDIR/../src/sentence-aligner)

(cd $TMPDIR; python3 $SCRIPTDIR/make_alignment.py $SL $TL)

mkdir -p $OUTDIR
cp -r $TMPDIR/sentence_alignment/* -t $OUTDIR

