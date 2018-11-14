#!/usr/bin/bash
BENCH_DIR=benchmark_gap

BENCHMARK=(
"bfs"  
"bc"   
"cc"  
)
GRAPH=(
##"road.sg"   
"web.sg"   
"kron.sg"
)

#PINEXE="$PIN_HOME/pin"
PINEXE="$PIN_HOME/pin.sh"

WORKDIR=$(pwd)

OUTPUT_DIR="$WORKDIR/output"
CONFIG_DIR="$WORKDIR/config"

#PINEXE="$PIN_HOME/pin"
PINEXE="$PIN_HOME/pin.sh"
PINTOOL="$HOME/workspace/sst/src_pca_compression/sst-elements/src/sst/elements/prospero/prosperotrace.so"
#PINTOOL="$HOME/workspace/sst/tools/indigo/obj-intel64/IndigoTrace.so"
TRACE_WRITER="$PINEXE -t $PINTOOL"


RECORD_INTERVAL="250000000"
NUM_SIM_INST="200000000"
NUM_SIMPOINT="1"
WORKDIR=$(pwd)
OUTPUTDIR="$WORKDIR/output"
TRACEDIR="$WORKDIR/gap_trace"
JBSUB_CMD="jbsub -q x86_12h"
NUM_THREADS=4
export OMP_NUM_THREADS=$NUM_THREADS

for bench in "${BENCHMARK[@]}"
do
    echo $bench
    for graph in "${GRAPH[@]}"
    do
        echo $graph
        cd ./$BENCH_DIR
        pwd
	TRACE=$bench-$graph-1B-200M-$NUM_SIMPOINT"P"
	LOG=$OUTPUTDIR/log_trace_gen.$TRACE

        $JBSUB_CMD -out $LOG -mem 32G \
             $TRACE_WRITER -o $TRACEDIR/$TRACE \
			-f compressed \
                        -t $NUM_THREADS \
			-i $RECORD_INTERVAL \
			-s $NUM_SIM_INST \
                        -n $NUM_SIMPOINT \
                        -m 1 \
                        -c 1 \
			-- ./$bench -f $graph -n 1 > $LOG
        echo $TRACE_WRITER
        echo $WORKDIR
	cd $WORKDIR
done
done
