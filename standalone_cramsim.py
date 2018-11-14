import sst
import sys
import time
import os

spec_arg = {
    "GemsFDTD":"",
    "omnetpp":"./omnetpp.ini",
	"soplex": "-s1 -e -m45000 ./pds-50.mps > soplex.ref.pds-50.out 2> soplex.ref.pds-50.err",
	"mcf": "./inp.in",
	"lbm": "3000 reference.dat 0 0 ./100_100_130_ldc.of",
	"libquantum": "1397 8",
        "milc": "< ./su3imp.in",
        "leslie3d": "< ./leslie3d.in",
        "sphinx3": "./ctlfile . args.an4",
	"astar": "./BigLakes2048.cfg",
        "wrf": "",
        "h264ref": "-d foreman_ref_encoder_baseline.cfg",
        "sjeng": "ref.txt",
	"cactusADM": "./benchADM.par",
	"zeusmp": "",
        "bwaves": "",
        "gcc": "166.i -o 166.s",
        "perlbench": "-I./lib checkspam.pl 2500 5 25 11 150 1 1 1 1",
        "bzip2": "chicken.jpg 30",
        "gamess": "< cytosine.2.config",
        "gromacs": "-silent -deffnm gromacs -nice 0",
        "namd": "--input namd.input --iterations 38 --output namd.out",
        "gobmk": "--quiet --mode gtp < 13x13.tst",
        "dealII": "23",
        "povray": "SPEC-benchmark-ref.ini",
        "calculix": "-i hyperviscoplastic",
        "hmmer": "nph3.hmm swiss41",
        "xalancbmk" : "-v t5.xml xalanc.xsl"
        }


#######################################################################################################
benchmark=""
maxinst=""
statname=""
warmup=""

def read_arguments():
        global benchmark
        global maxinst
        global statname
        global warmup

	config_file = list()
        override_list = list()
        boolDefaultConfig = True;
        
	for arg in sys.argv:
            if arg.find("--configfile=") != -1:
		substrIndex = arg.find("=")+1
		config_file = arg[substrIndex:]
		print "Config file:", config_file
		boolDefaultConfig = False;
            elif arg.find("--executable=") !=-1:
                substrIndex = arg.find("=")+1
                benchmark = arg[substrIndex:]
                print "executable:", benchmark
            elif arg.find("--maxinst=") !=-1:
                substrIndex = arg.find("=")+1
                maxinst = arg[substrIndex:]
                print "maxinst:", maxinst
            elif arg.find("--warmup=") !=-1:
                substrIndex = arg.find("=")+1
                warmup = arg[substrIndex:]
                print "warmup_inst:", warmup

            elif arg.find("--statname=") !=-1:
                substrIndex = arg.find("=")+1
                statname = arg[substrIndex:]
                print "statname:", statname
  	    elif arg != sys.argv[0]:
                if arg.find("=") == -1:
                    print "Malformed config override found!: ", arg
                    exit(-1)
                override_list.append(arg)
                print "Override: ", override_list[-1]

	
	if boolDefaultConfig == True:
		config_file = "../ddr4_verimem.cfg"
		print "config file is not specified.. using ddr4_verimem.cfg"

	return [config_file, override_list]

def setup_config_params(config_file, override_list):
    l_params = {}
    l_configFile = open(config_file, 'r')
    for l_line in l_configFile:
        l_tokens = l_line.split()
         #print l_tokens[0], ": ", l_tokens[1]
        l_params[l_tokens[0]] = l_tokens[1]

    for override in override_list:
        l_tokens = override.split("=")
        print "Override cfg", l_tokens[0], l_tokens[1]
        l_params[l_tokens[0]] = l_tokens[1]
     
    return l_params

#######################################################################################################

# Command line arguments
g_config_file = "/dccstor/memsim1/pca/config/ddr4-3200.cfg"
g_overrided_list = ""

# Setup global parameters
#[g_boolUseDefaultConfig, g_config_file] = read_arguments()
[g_config_file, g_overrided_list] = read_arguments()
g_params = setup_config_params(g_config_file, g_overrided_list)

# Define SST core options
sst.setProgramOption("timebase", "500ps")
#sst.setProgramOption("stopAtCycle", "21000us")


## Flags
maxTxns = 1000000
#maxTxns = 5000000
#maxTxns = 100
memDebug = 0
memDebugLevel = 0
verbose = 0
controller_verbose = 0
coherenceProtocol = "MESI"
rplPolicy = "lru"
#cacheFrequency = "2 Ghz"

#cpuFrequency = "100 Mhz"
#cacheFrequency = "100 Mhz"
#memoryFrequency = "10 Mhz"
cpuFrequency = "4 Ghz"
cacheFrequency = "4 Ghz"
memoryFrequency = "1 Ghz"

g_params["strControllerClockFreq"]= memoryFrequency

defaultLevel = 0
cacheLineSize = 64
trace_type=g_params["traceType"]
corecount = int(g_params["corecount"])
multiprog = 1
memory_size = int(g_params["memsize"])    #GB
metadata_predictor=g_params["metadata_predictor"]
pagesize=4096       #B
pagecount = memory_size*1024*1024*1024/corecount/pagesize
print pagecount
compression_en = g_params["compression_en"]
memcontent_link_en =1
pca_enable = g_params["pca_en"]
oracle_mode =0
metacache_entries=int(g_params["metacache_entries"])*1024

## Application Info
os.environ['SIM_DESC'] = 'EIGHT_CORES'
os.environ['OMP_NUM_THREADS'] = str(corecount)

sst_root = os.getenv( "SST_ROOT" )

## MemHierarchy 
# txn gen --> memHierarchy Bridge
comp_txngen = sst.Component("txngen", "CramSim.c_TxnGen")
comp_txngen.addParams(g_params);
comp_txngen.addParams({
                    "maxTxns" : maxTxns,
                    "verbose" : verbose,
                    "mode" : trace_type,
                    "readWriteRatio" : 0.7,
                    "maxOutstandingReqs" : 512,
                    "numTxnPerCycle" : g_params["numChannels"],
                    })


# controller
comp_controller0 = sst.Component("MemController0", "CramSim.c_ControllerPCA")
comp_controller0.addParams(g_params)
comp_controller0.addParams({
                    "verbose" : controller_verbose,
                    "compression_en" : compression_en,
                    "loopback_en" : 0,
                    "pca_enable"  : pca_enable,
                    "oracle_mode" : oracle_mode,
                    "metadata_predictor" : metadata_predictor,   #0: perfect predictor, 1:metacache, 2:2lv
                    "metaCache_entries" : metacache_entries,
                    "fixed_compression_mode" : 1,
                    "contentline_num" : 0,
                    "TxnConverter" : "CramSim.c_TxnConverter",
                    "AddrMapper" : "CramSim.c_AddressHasher",
                    "CmdScheduler" : "CramSim.c_CmdScheduler" ,
                    "DeviceController" : "CramSim.c_DeviceController",
                    "backing_size" : memory_size*1024*1024*1024
                    })

# memory device
comp_dimm0 = sst.Component("Dimm0", "CramSim.c_Dimm")
comp_dimm0.addParams(g_params)
comp_dimm0.addParams({
        "pca_enable" : pca_enable}
        )



# memhBridge(=TxnGen) <-> Memory Controller 
memHLink = sst.Link("memHLink_1")
memHLink.connect( (comp_txngen, "memLink", g_params["clockCycle"]), (comp_controller0, "txngenLink", g_params["clockCycle"]) )

# Controller <-> Dimm
cmdLink = sst.Link("cmdLink_1")
cmdLink.connect( (comp_controller0, "memLink", g_params["clockCycle"]), (comp_dimm0, "ctrlLink", g_params["clockCycle"]) )



#memMemContentLink = sst.Link("memContent_link")
#memMemContentLink.connect((comp_controller0, "contentLink", g_params["clockCycle"]), (ariel, "linkMemContent",g_params["clockCycle"]));


comp_controller0.enableAllStatistics()
comp_txngen.enableAllStatistics()
comp_dimm0.enableAllStatistics()

sst.setStatisticLoadLevel(7)
sst.setStatisticOutput("sst.statOutputCSV")
sst.setStatisticOutputOptions( {
		"filepath"  : statname+".csv",
		"separator" : ","
    } )
