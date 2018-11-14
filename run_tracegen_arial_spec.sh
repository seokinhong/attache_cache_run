#!/usr/bin/bash


BENCHMARK=(
#	"GemsFDTD"
#	"omnetpp"
#	"soplex"
#	"mcf"
#	"lbm"
	"libquantum"
#        "milc"
#        "leslie3d"
#        "sphinx3"
#	"astar"
        # "wrf"
#        "h264ref"
       # "sjeng"
#	"cactusADM"
#	"zeusmp"
       # "bwaves"
 #       "gcc"
       # "bzip2"
#        "xalancbmk"
        )

BENCHMARK=(
#    "omnetpp"
#    "soplex"
#    "milc"
#    "leslie3d"
#    "wrf"
#    "xalancbmk"
#    "bwaves"
 #   "gcc"
    "libquantum"
#   "mcf"
#   "sphinx3"
#    "GemsFDTD"
    )

declare -A ARG=(
	["GemsFDTD"]=""
	["omnetpp"]="omnetpp.ini"
	["soplex"]="-s1 -e -m45000 ./pds-50.mps"
	["mcf"]="./inp.in"
	["lbm"]="3000 reference.dat 0 0 ./100_100_130_ldc.of"
	["libquantum"]="1397 8"
        ["milc"]=" < su3imp.in" 
        ["leslie3d"]="< ./leslie3d.in"
        ["sphinx3"]="./ctlfile . args.an4"
	["astar"]="./BigLakes2048.cfg"
        ["wrf"]=" > wrf.ref.out"
        ["h264ref"]="-d foreman_ref_encoder_baseline.cfg"
        ["sjeng"]="ref.txt"
	["cactusADM"]="./benchADM.par"
	["zeusmp"]=""
        ["bwaves"]=""
        ["gcc"]="166.i"
        ["perlbench"]="-I./lib checkspam.pl 2500 5 25 11 150 1 1 1 1"
        ["bzip2"]="chicken.jpg 30"
        ["gamess"]="< cytosine.2.config"
        ["gromacs"]="-silent -deffnm gromacs -nice 0"
        ["namd"]="--input namd.input --iterations 38"
        ["gobmk"]="--quiet --mode gtp <13x13.tst"
        ["dealII"]="23"
        ["povray"]="SPEC-benchmark-ref.ini"
        ["calculix"]="-i hyperviscoplastic"
        ["hmmer"]="nph3.hmm swiss41"
        ["xalancbmk"]="-v t5.xml xalanc.xsl"
	)


#PINEXE="$PIN_HOME/pin"
PINEXE="$PIN_HOME/pin.sh"

#NUM_SIM_INST="10000000"
#NUM_WARMUP_INST="10000000000"

NUM_SIM_INST="1000000"
NUM_WARMUP_INST="10000000000"
NUM_WARMUP_INST="100"

WORKDIR=$(pwd)

OUTPUT_DIR="$WORKDIR/tracegen_output"
CONFIG_DIR="$WORKDIR/config"
CRAMSIM_CFG="ddr4-3200-2ch"
TRACE_FILE="$WORKDIR/spec_trace/test_trace"

for bench in "${BENCHMARK[@]}"
do
    for hitrate in 0  #70 #80 90 100   # 0 --> use a real metadata cache
    do
      #  for rownum in 4 8 16 32 #8 16 32 
        for rank in 1
        do
            cd ./benchmark/$bench
           # SIM_NAME=test.1cpu.metacache16K.hitrate$hitrate"."$CRAMSIM_CFG
            #SIM_NAME=run10M.4cpu.metacache.hitrate$hitrate"."$CRAMSIM_CFG
            SIM_NAME=run10M.4cpu.base.rank$rank"."$CRAMSIM_CFG
            
            SIM_RESULT_=$OUTPUT_DIR/simresult"."$bench"."$SIM_NAME
            SIM_STAT_=$OUTPUT_DIR/simstat"."$bench"."$SIM_NAME
            CRAMSIM_CONFIG_=$CONFIG_DIR/$CRAMSIM_CFG".cfg"
            SST_CFG_OUT_=$OUTPUT_DIR/sstcfg"."$SIM_NAME
            COMPRESSION_EN=0
            PCA_EN=0
            rownum=16
            let "memsize=16 * $rank"

            rm $SIM_RESULT_
            rm $SIM_STAT_

   #        jbsub -q x86_24h -mem 10G -out $SIM_RESULT_ \
            valgrind  --trace-children=yes  --tool=memcheck --leak-check=full --show-leak-kinds=all \
            sst --print-timing-info \
                       --model-options="--configfile=$CRAMSIM_CONFIG_ --warmup=$NUM_WARMUP_INST --maxinst=$NUM_SIM_INST --executable=$bench --statname=$SIM_STAT_ metacache_hitrate=$hitrate metacache_entries=$rownum corecount=1 memsize=$memsize pca_en=$PCA_EN compression_en=$COMPRESSION_EN numRanksPerChannel=$rank metadata_predictor=0 trace_file=$TRACE_FILE" $WORKDIR/ariel.py 

            cd $WORKDIR
        done
    done
done
