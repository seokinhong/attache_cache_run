import sst 
import os,sys
from optparse import OptionParser

traceDir ="";
traceName = [];


def setup_config_params(configFile):
    l_params = {}
    l_configFile = open(configFile, 'r')
    for l_line in l_configFile:
        l_tokens = l_line.split()
        l_params[l_tokens[0]] = l_tokens[1]
    return l_params

parser = OptionParser(usage="usage: %prog [options]")
parser.add_option("--traceFormat",  action='store', dest="TraceFormat", help="Format of the trace input file.")
parser.add_option("--traceType",  action='store', dest="TraceType", help="Type of the trace input file.")
parser.add_option("--benchmark",  action='store', dest="Benchmark", help="Name of the trace input file.")
parser.add_option("--benchmarkType",  action='store', dest="BenchmarkType", help="Type of the benchmark (spec,mix,gap)")
parser.add_option("--profileAtomics",  action='store', dest="ProfileAtomics", help="Profile atomic instructions")
parser.add_option("--pimSupport",  action='store', dest="PIMSupport", help="Enable PIM support.")
parser.add_option("--waitCycle",  action='store', dest="WaitCycle", help="Follow issue cyles of the trace file.")
parser.add_option("--cramConfig",  action='store', dest="CramConfig", help="CramSim configuration file.")
parser.add_option("--statName",  action='store', dest="StatName", help="Name of statistic file.")
parser.add_option("--pca_enable",  action='store', dest="pca_enable", help="pca enable",default=0)
parser.add_option("--metadata_predictor",  action='store', dest="metadata_predictor", help="Metadata prediction mode",default=0)
parser.add_option("--metacache_rownum",  action='store', dest="metacache_rownum", help="The number of rows of metacache",default=2048)
parser.add_option("--metacache_rpl_policy",  action='store', dest="metacache_rpl_policy", help="The number of rows of metacache",default=0)
parser.add_option("--ropr_entry_num",  action='store', dest="ropr_entry_num", help="The number of predictor entry",default=512*1024)
parser.add_option("--ropr_col_num",  action='store', dest="ropr_col_num", help="The number of predictor entry",default=1)
parser.add_option("--lipr_entry_num",  action='store', dest="lipr_entry_num", help="The number of LiPR entries",default=8*1024)
parser.add_option("--lipr_sel_repl",  action='store', dest="lipr_sel_repl", help="enable selective repl for lipr",default=0)
parser.add_option("--global_entry_num",  action='store', dest="global_entry_num", help="enable selective repl for lipr",default=0)
parser.add_option("--numPCHs",  action='store', dest="numPCHs", help="number of pseudo channels",default=-1)
parser.add_option("--coreCount", action='store',dest="coreCount", help="number of core",default=1)
parser.add_option("--stopAtCycle",  action='store', dest="stopAtCycle", help="stop at cycle",default="0ms")
parser.add_option("--maxInst",  action='store', dest="maxInst", help="stop at cycle",default="0")
parser.add_option("--L3CacheSize", action='store',dest="L3CacheSize", help="l3 cache size(MB)", default="8")
parser.add_option("--metacache_latency", action='store',dest="metacache_latency", help="latency of meta data cache", default=3)  # 3 --> 8 cpu cycles at 4GHz CPU and 1.6GHz mem
parser.add_option("--multilane_rowtable", action='store',dest="multilane_rowtable", help="enable multilane per rowtable entry", default=0)
(options, args) = parser.parse_args()


if options.TraceFormat == "Binary":
    extension = "-bin.trace"
elif options.TraceFormat == "CompressedBinary":
    extension = ".gz"
else:
    extension = ".trace"


# setup prospero+cache
coherenceProtocol = "NONE"  #MESI, NONE
rplPolicy = "lru"
cacheFrequency = "4 Ghz"
coreFrequency = "4 Ghz"
busLat = "100ps"
busLat_slow = "2ns"
debug = 0
controller_verbose = 0
cacheLineSize = 64
coreCount = int(options.coreCount)
memcontent_link_en =1

# setup CramSim
compression_en = 1
oracle_mode =0
contentline_num = coreCount
cramsim_config=options.CramConfig
g_params = setup_config_params(cramsim_config)

numChannel=int(coreCount/4)
if numChannel==0:
    numChannel=1
g_params["numChannels"]=numChannel
if options.numPCHs != -1:
    g_params["numPChannelsPerChannel"]=options.numPCHs

print "# of cores: %d"%coreCount
print "# of memory channel: %d"%numChannel
print "# of memory pchannel: %s"%g_params["numPChannelsPerChannel"]
print "metacache_row_num: %s"%options.metacache_rownum
print "ropr_entry_num: %s"%options.ropr_entry_num

memCtrlClockCycle = g_params["clockCycle"]
memCtrlClock = g_params["strControllerClockFreq"]
memSize = int(g_params["numChannels"]) * \
            int(g_params["numRanksPerChannel"]) * \
            int(g_params["numBankGroupsPerRank"]) * \
            int(g_params["numBanksPerBankGroup"]) * \
            int(g_params["numRowsPerBank"]) * \
            int(g_params["numColsPerBank"]) * \
            int(g_params["numBytesPerTransaction"])/(1024*1024*1024);

pagesize=4096       #B
pagecount = memSize*1024*1024*1024/pagesize


# Define SST core options
sst.setProgramOption("timebase", "50ps")
#print StopAtCycle
if options.stopAtCycle != "0ms":
    print "stopAtCycle: "+options.stopAtCycle
    sst.setProgramOption("stopAtCycle", options.stopAtCycle)



## Flags
cpuDebug = 0
cacheDebug = 0
memDebug = 0
memDebugLevel = 0
pageAllocDebug = 0

## Application Info
os.environ['SIM_DESC'] = 'EIGHT_CORES'
os.environ['OMP_NUM_THREADS'] = str(coreCount)
sst_root = os.getenv( "SST_ROOT" )


# Enable SST Statistics Outputs for this simulation
sst.enableAllStatisticsForAllComponents({"type":"sst.AccumulatorStatistic"})
sst.setStatisticLoadLevel(7)
sst.setStatisticOutput("sst.statOutputCSV")
sst.setStatisticOutputOptions( {
		"filepath"  : "%s.csv"%options.StatName,
		"separator" : ","
    } )


##### Prepair benchmarr set #########################
print options.BenchmarkType;
if options.BenchmarkType != "randstream":
    print "benchmark type error"
    sys.exit()


##########################################################################################
##########################################################################################
# txn gen --> memHierarchy Bridge
comp_txngen = sst.Component("txngen", "CramSim.c_TxnGen")
comp_txngen.addParams(g_params);
comp_txngen.addParams({
                    "maxTxns" : options.maxInst,
                    "verbose" : memDebug,
                    "mode" : options.Benchmark,
                    "readWriteRatio" : 0.7,
                    "maxOutstandingReqs" : 512,
                    "numTxnPerCycle" : g_params["numChannels"],
                    })


comp_controller0 = sst.Component("MemController0", "CramSim.c_ControllerPCA")
comp_controller0.addParams(g_params)
comp_controller0.addParams({
                "verbose" : memDebug,
                "compression_en" : compression_en,
                "loopback_en" : 0,
                "pca_enable"  : options.pca_enable,
                "oracle_mode" : oracle_mode,
                "metadata_predictor" : options.metadata_predictor,   #0: perfect predictor, 1:metacache, 2:2lv
                "metacache_rownum" : options.metacache_rownum,
                "metacache_rpl_policy" :options.metacache_rpl_policy,
                "ropr_entry_num" : options.ropr_entry_num,
                "lipr_entry_num" : options.lipr_entry_num,
                "selectiveRepl" : options.lipr_sel_repl,
                "global_entry_num" :options.global_entry_num,
                "ropr_col_num" :options.ropr_col_num,
                "TxnConverter" : "CramSim.c_TxnConverter",
                "AddrMapper" : "CramSim.c_AddressHasher",
                "CmdScheduler" : "CramSim.c_CmdScheduler" ,
                "DeviceController" : "CramSim.c_DeviceController",
                "contentline_num" : 0,
                "multilane_rowtable" : options.multilane_rowtable,
                "metacache_latency" :options.metacache_latency,
                "fixed_compression_mode" : 1,
                "compression_data_rate" : 50
                })

comp_controller0.enableAllStatistics()

# memory device
comp_dimm0 = sst.Component("Dimm0", "CramSim.c_Dimm")
comp_dimm0.addParams(g_params)
comp_dimm0.addParams({
    "pca_enable" : options.pca_enable}
    )

comp_dimm0.enableAllStatistics()

# memhBridge(=TxnGen) <-> Memory Controller 
memHLink = sst.Link("memHLink_1")
memHLink.connect( (comp_txngen, "memLink", g_params["clockCycle"]), (comp_controller0, "txngenLink", g_params["clockCycle"]) )

# Controller <-> Dimm
cmdLink = sst.Link("cmdLink_1")
cmdLink.connect( (comp_controller0, "memLink", g_params["clockCycle"]), (comp_dimm0, "ctrlLink", g_params["clockCycle"]) )



