#!/usr/bin/bash


BENCHMARK=(
#	"GemsFDTD"
	"omnetpp"
	"soplex"
       "mcf"
	"lbm"
	"libquantum"
      "milc"
     "leslie3d"
      "sphinx3"
      "astar"
      "wrf"
      "h264ref"
      "sjeng"
      "cactusADM"
      "zeusmp"
      "bwaves"
       "gcc"
       "bzip2"
       "xalancbmk"
        )

BENCHMARK=(
	"soplex"
        )




declare -A ARG=(
	["GemsFDTD"]=" "
	["omnetpp"]="./omnetpp.ini "
	["soplex"]="-s1 -e -m45000 ./pds-50.mps "
	["mcf"]="./inp.in "
	["lbm"]="3000 reference.dat 0 0 ./100_100_130_ldc.of "
	["libquantum"]="1397 8 "
        ["milc"]="< ./su3imp.in "
        ["leslie3d"]="<./leslie3d.in "
        ["sphinx3"]="./ctlfile . args.an4 "
	["astar"]="./BigLakes2048.cfg "
        ["wrf"]=" "
        ["h264ref"]="-d foreman_ref_encoder_baseline.cfg "
        ["sjeng"]="ref.txt " 
	["cactusADM"]="./benchADM.par "
	["zeusmp"]=""
        ["bwaves"]=""
        ["gcc"]="166.i -o 166.s"
        ["perlbench"]="-I./lib checkspam.pl 2500 5 25 11 150 1 1 1 1 "
        ["bzip2"]="chicken.jpg 30 " 
        ["gamess"]="< cytosine.2.config "
        ["gromacs"]="-silent -deffnm gromacs -nice 0 "
        ["namd"]="--input namd.input --iterations 38 --output namd.out "
        ["gobmk"]="--quiet --mode gtp < 13x13.tst "
        ["dealII"]="23 "
        ["povray"]="SPEC-benchmark-ref.ini "
        ["calculix"]="-i hyperviscoplastic "
        ["hmmer"]="nph3.hmm swiss41 "
        ["xalancbmk"]="-v t5.xml xalanc.xsl"
	)


#declare -A ARG=(
#       ["GemsFDTD"]=" > GemsFDTD.ref.out 2> GemsFDTD.ref.err"
#       ["omnetpp"]="./omnetpp.ini > omnetpp.ref.log 2> omnetpp.ref.err"
#       ["soplex"]="-s1 -e -m45000 ./pds-50.mps > soplex.ref.pds-50.out 2> soplex.ref.pds-50.err"
#       ["mcf"]="./inp.in > mcf.ref.out 2> mcf.ref.err"
#       ["lbm"]="3000 reference.dat 0 0 ./100_100_130_ldc.of > lbm.ref.out 2> lbm.ref.err"
#       ["libquantum"]="1397 8 > libquantum.ref.out 2> libquantum.ref.err"
#       ["milc"]="< ./su3imp.in > milc.ref.out 2> milc.ref.err"
#       ["leslie3d"]="<./leslie3d.in > leslie3d.ref.out 2> leslie3d.ref.err"
#       ["sphinx_livepretend"]="./ctlfile . args.an4 > sphinx3.ref.out 2> sphinx3.ref.err"
#       ["astar"]="./BigLakes2048.cfg > astar.ref.BigLakes2048.out 2> astar.ref.BigLakes2048.err"
#       ["wrf"]=" > wrf.ref.out 2> wrf.ref.err"
#       ["h264ref"]="-d foreman_ref_encoder_baseline.cfg"
#       ["sjeng"]="ref.txt > sjeng.ref.out 2> sjeng.ref.err"
#       ["cactusADM"]="./benchADM.par > cactusADM.ref.out 2> cactusADM.ref.err"
#       ["zeusmp"]=" > zeusmp.ref.out 2> zeusmp.ref.err"
#       ["bwaves"]=" > bwaves.ref.out 2> bwaves.ref.err"
#       ["gcc"]="166.i -o 166.s > gcc.ref.166.out 2> gcc.ref.166.err"
#       ["perlbench"]="-I./lib checkspam.pl 2500 5 25 11 150 1 1 1 1"
#       ["bzip2"]="chicken.jpg 30 > bzip2.ref.chicken.out 2> bzip2.ref.chicken.err"
#       ["gamess"]="< cytosine.2.config > gamess.ref.cytosine.out 2> gamess.ref.cytosine.err"
#       ["gromacs"]="-silent -deffnm gromacs -nice 0 > gromacs.ref.out 2> gromacs.ref.err"
#       ["namd"]="--input namd.input --iterations 38 --output namd.out > namd.ref.out 2> namd.ref.err"
#       ["gobmk"]="--quiet --mode gtp < 13x13.tst > gobmk.ref.13x13.out 2> gobmk.ref.13x13.err"
#       ["dealII"]="23 > dealII.ref.out 2> dealII.ref.err"
#       ["povray"]="SPEC-benchmark-ref.ini > povray.ref.out 2> povray.ref.err"
#       ["calculix"]="-i hyperviscoplastic > calculix.ref.out 2> calculix.ref.err"
#       ["hmmer"]="nph3.hmm swiss41 > hmmer.ref.nph3.out 2> hmmer.ref.nph3.err"
#       )
#

#PINEXE="$PIN_HOME/pin"
PINEXE="$PIN_HOME/pin.sh"
#PINTOOL="$HOME/workspace/sst/src_pca_compression/sst-elements/src/sst/elements/prospero/prosperotrace.so"
PINTOOL="/dccstor/memsim1/attache/src/sst-elements/src/sst/elements/prospero/prosperotrace.so"
#PINTOOL="$HOME/workspace/sst/tools/indigo/obj-intel64/IndigoTrace.so"
TRACE_WRITER="$PINEXE -t $PINTOOL"


RECORD_INTERVAL="10000000000"
RECORD_INTERVAL="100"
NUM_SIM_INST="100000"
NUM_SIMPOINT="1"
WORKDIR=$(pwd)
OUTPUTDIR="$WORKDIR/output"
TRACEDIR="$WORKDIR/spec_trace"
JBSUB_CMD="jbsub"
for bench in "${BENCHMARK[@]}"
do
	TRACE=""$bench"-10B-100M-"$NUM_SIMPOINT"P-CONTENT"
	LOG="$OUTPUTDIR/log_trace_gen.$bench.$TRACE"
	cd ./benchmark/$bench

    #    $JBSUB_CMD -out $LOG -mem 16G \
             $TRACE_WRITER -o $TRACEDIR/$TRACE \
			-f compressed \
			-i $RECORD_INTERVAL \
			-s $NUM_SIM_INST \
                        -n $NUM_SIMPOINT \
                        -m 1 \
                        -c 1 \
                        -x 0 \
			-- ./$bench ${ARG[$bench]}

#    $TRACE_WRITER -o $TRACEDIR/$TRACE \
#			-f compressed \
#                        -m 1 \
#			-- ./$bench ${ARG[$bench]}


	cd $WORKDIR
done
