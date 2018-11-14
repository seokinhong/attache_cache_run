#! /bin/bash

# Author: Dimitrios Skarlatos #
# Date: 06/05/2017 #
# Contact: dhmitris.skarlatos@gmail.com #
# Description: Run script for the GAP benchmarks #


VER=0.0
DESC="Run script for the GAP benchmarks with tracing support"
USE="./run.sh -b bench_id -g graph_id -n num_threads \n -h Help \n -t Enables tracing"

#BENCH_ORDER = \
#        bfs-twitter pr-twitter cc-twitter bc-twitter \
#        bfs-w:	eb pr-web cc-web bc-web \
#        bfs-road pr-road cc-road bc-road \
#        bfs-kron pr-kron cc-kron bc-kron tc-kron \
#        bfs-urand pr-urand cc-urand bc-urand tc-urand \
#        sssp-twitter sssp-web sssp-road sssp-kron sssp-urand \
#        tc-twitter tc-web tc-road

### System Configuration ###

BENCH_DIR=/home/mbhealy/Workspace/Benchmarks/gapbs
GRAPH_DIR=$BENCH_DIR/benchmark/graphs

BENCH_BIN_NAME=("bfs" "sssp" "bc" "tc" "pr" "cc")
BENCH_GRAPH=("cit-Patents.el" "amazon0312.el" "fb.3980.el" "soc-LiveJournal1.el" "road.sg" "youtube.el" "dblp.el" "web-Google.el" "roadNet-CA.el" "wiki.el" "roadNet-TX.el" "web.sg" "kron.sg" "urand.sg")

### Handle input parameters ###
  
if [ $# == 0 ] ; then
	echo -e $USE
	exit 1;
fi

while getopts "thb:g:n:" opt
do
	case "$opt" in
		"t")
			echo "Tracing is enabled"
			TRACE_RECORD="$PIN_HOME/pin -t $INDIGO_HOME/IndigoTrace.so"
			;;
		"h")
			echo "$DESC, version: $VER"
			echo -e "$USE"
			exit 0;
			;;
		"b")
			if [ $OPTARG -ge ${#BENCH_BIN_NAME[@]} -o $OPTARG -lt 0 ] ; then
				max_id=`expr ${#BENCH_BIN_NAME[@]} - 1`
				echo "Invalid bench id, accepted values are between: 0 - $max_id"
				exit 0;
			fi
			bench_bin=${BENCH_BIN_NAME[$OPTARG]}
			bench_path=$BENCH_DIR
			;;
		"g")
			if [ $OPTARG -ge ${#BENCH_GRAPH[@]} -o $OPTARG -lt 0 ] ; then
				max_id=`expr ${#BENCH_GRAPH[@]} - 1`
				echo "Invalid bench id, accepted values are between: 0 - $max_id"
				exit 0;
			fi
			bench_graph=${BENCH_GRAPH[$OPTARG]}
			;;
		"n") 
			if [ $OPTARG -lt 1 ] ; then
				echo "Invalid thread number, at least one thread is required."
				exit 0;
			fi
			num_threads=$OPTARG
			;;

		"?")
			echo "Invalid argument -$OPTARG, use -h for help"
			exit 0;
			;;
		*)
	esac	
done

echo $TRACE_RECORD
echo $bench_path
echo $bench_bin
echo $bench_graph

if [ ! $bench_bin ]; then
	echo "Benchmark selection is required"
	exit 0;
fi

if [ ! $bench_graph ]; then
	echo "Graph selection is required"
	exit 0;
fi

if [ ! $num_threads ]; then
	echo "Thread selection is required"
	exit 0;
fi

echo $TRACE_RECORD
echo $bench_path
echo $bench_bin
echo $bench_graph

export OMP_NUM_THREADS=$num_threads

echo "$LD_LIBRARY_PATH"

export LD_LIBRARY_PATH=/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
export DYLD_LIBRARY_PATH=/lib/x86_64-linux-gnu:$DYLD_LIBRARY_PATH

export LD_LIBRARY_PATH=/lib/i386-linux-gnu:$LD_LIBRARY_PATH
export DYLD_LIBRARY_PATH=/lib/i386-linux-gnu:$DYLD_LIBRARY_PATH


echo "$LD_LIBRARY_PATH"

if [ ! -z "$TRACE_RECORD" ] ; then
	echo "$LD_LIBRARY_PATH"
	echo "$TRACE_RECORD -o "$bench_bin"_"$bench_graph" -f text -t $num_threads -a 2 -p 1 -- $bench_path/$bench_bin -f $GRAPH_DIR/$bench_graph -n 1 > "$bench_bin"-"$bench_graph"-"$num_threads"-trace.out"

	$TRACE_RECORD -o "$bench_bin"_"$bench_graph" -f text -t $num_threads -a 2 -p 1 -- $bench_path/$bench_bin -f $GRAPH_DIR/$bench_graph -n 1 > "$bench_bin"-"$bench_graph"-"$num_threads"-trace.out
  
else
	echo "$bench_path/$bench_bin -f $GRAPH_DIR/$bench_graph -n 1 > "$bench_bin"-"$bench_graph"-"$num_threads".out"
	$bench_path/$bench_bin -f $GRAPH_DIR/$bench_graph -n 1 > "$bench_bin"-"$bench_graph"-"$num_threads".out
fi
