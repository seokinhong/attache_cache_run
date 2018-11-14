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
parser.add_option("--metacache_entries",  action='store', dest="metacache_entries", help="The number of entries of metacache",default=32)
parser.add_option("--numPCHs",  action='store', dest="numPCHs", help="number of pseudo channels",default=-1)
parser.add_option("--coreCount", action='store',dest="coreCount", help="number of core",default=1)
parser.add_option("--stopAtCycle",  action='store', dest="stopAtCycle", help="stop at cycle",default="0ms")
parser.add_option("--maxInst",  action='store', dest="maxInst", help="stop at cycle",default="0")
parser.add_option("--L3CacheSize", action='store',dest="L3CacheSize", help="l3 cache size(MB)", default="8")
(options, args) = parser.parse_args()


print int(options.PIMSupport)
if int(options.PIMSupport) == 1:
    config_name = "PIM"
elif int(options.PIMSupport) == 2:
    config_name = "PIM++"
elif int(options.PIMSupport) == 3:
    config_name = "Free"
else:
    config_name = "Baseline"

print int(options.WaitCycle)
if int(options.WaitCycle) == 0:
    trace_config = "noWait"
else:   
    trace_config = "Wait"

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
mt_mode=0
spec_trace_dir="spec_trace"
gap_trace_dir="gap_trace"
if options.BenchmarkType=="spec":
    for i in range(0,coreCount):
        trace="./%s/%s-%s0%s" % (spec_trace_dir,options.Benchmark,options.TraceType,extension);
        #trace="./spec_trace/astar-l2-F10B-R4B0.gz" 
        
        if os.path.exists(trace)==False:
            print "trace file (%s) is not exists"%trace
            exit(0)
        else:
           print trace;

        traceName.append(trace)

elif options.BenchmarkType=="gap":
    mt_mode=1;
    for i in range(0,coreCount):
        trace="./%s/%s-%s%d%s" % (gap_trace_dir,options.Benchmark,options.TraceType,i,extension);
        
        if os.path.exists(trace)==False:
            print "trace file (%s) is not exists"%trace
            exit(0)
        else:
            print trace;

        traceName.append(trace)

elif options.BenchmarkType=="mix":
    benchmark_set=options.Benchmark.split(".")
    if len(benchmark_set)<coreCount:
      #  print "the number of benchmarks is less than coreCount"
        exit(0)

    for i in range(0,coreCount):
        trace="./%s/%s-%s-0-0%s" % (spec_trace_dir,benchmark_set[i],options.TraceType,extension);
       # print trace;
        traceName.append(trace)


##########################################################################################
##########################################################################################

# CramSim
comp_L3Cache = sst.Component("l3", "CramSim.c_Cache")
comp_L3Cache.addParams(g_params)
comp_L3Cache.addParams({
    "verbose": cacheDebug,
                "ClockFreq" : coreFrequency,
                "cache_size" : int(options.L3CacheSize)*1024*1024,
                "associativity" :16,
                "repl_policy":"LRU",
                "latency" :20,
                "enableAllHit" : 0
                })

comp_L3Cache.enableAllStatistics()


comp_pageAllocator0 = sst.Component("PageAllocator0", "CramSim.c_PageAllocator")
comp_pageAllocator0.addParams(g_params)
comp_pageAllocator0.addParams({
                "verbose" : pageAllocDebug,
                "corenum"               : coreCount,
                "isMultiThreadMode"     : mt_mode,
                "isPageAllocLink" : 1,
                "pagesize" :            pagesize,
                "memsize" : memSize*1024*1024*1024
                })

comp_pageAllocator0.enableAllStatistics()


comp_controller0 = sst.Component("MemController0", "CramSim.c_ControllerPCA")
comp_controller0.addParams(g_params)
comp_controller0.addParams({
                "verbose" : memDebug,
                "compression_en" : compression_en,
                "loopback_en" : 0,
                "pca_enable"  : options.pca_enable,
                "oracle_mode" : oracle_mode,
                "metadata_predictor" : options.metadata_predictor,   #0: perfect predictor, 1:metacache, 2:2lv
                "metaCache_entries" : options.metacache_entries,
                "TxnConverter" : "CramSim.c_TxnConverter",
                "AddrMapper" : "CramSim.c_AddressHasher",
                "CmdScheduler" : "CramSim.c_CmdScheduler" ,
                "DeviceController" : "CramSim.c_DeviceController",
                "contentline_num" : contentline_num
                })

comp_controller0.enableAllStatistics()

# memory device
comp_dimm0 = sst.Component("Dimm0", "CramSim.c_Dimm")
comp_dimm0.addParams(g_params)
comp_dimm0.addParams({
    "pca_enable" : options.pca_enable}
    )

comp_dimm0.enableAllStatistics()


membus = sst.Component("membus", "memHierarchy.Bus")
membus.addParams({
    "bus_frequency" : cacheFrequency,
    })

# L3Cache <-> Memory Controller 
memHLink = sst.Link("memHLink_1")
memHLink.connect( (comp_L3Cache, "memLink", g_params["clockCycle"]), (comp_controller0, "txngenLink", g_params["clockCycle"]) )

# Controller <-> Dimm
cmdLink = sst.Link("cmdLink_1")
cmdLink.connect( (comp_controller0, "memLink", g_params["clockCycle"]), (comp_dimm0, "ctrlLink", g_params["clockCycle"]) )

# Bus to L3 and L3 <-> MM
MemCtrlLink = sst.Link("L3MemCtrl")
MemCtrlLink.connect((membus, "low_network_0", busLat), (comp_L3Cache, "cpuLink", busLat))
 

## Prospero
prospero={}
for core in range (0, coreCount):
    print "Creating prospero component core " + str(core)
    tracefile=traceName[core];
    print tracefile;
    prospero["prospero" + str(core)] = sst.Component("prospero" + str(core), "prospero.prosperoCPU")
    prospero["prospero" + str(core)].addParams( {
       "clock" : str(coreFrequency),
       "reader" : "prospero.Prospero" + options.TraceFormat + "TraceReader",
       "readerParams.file" : tracefile,
       "readerParams.pimsupport" : str(options.PIMSupport),
       "readerParams.content" : 0,
       "readerParams.atomic" : 0,
       "readerParams.compression": 1,
       "readerParams.instNum": 1,
       "traceformat" : "1",
       "verbose" : cpuDebug,
       "pagesize" : 4096,
       "pagecount" : 4096,
       "profileatomics" : str(options.ProfileAtomics),
       "pimsupport" : str(options.PIMSupport),
      # "waitCycle" : str(options.WaitCycle),
       "waitCycle" : 0,
       "cache_line_size" : cacheLineSize,
       "memcontent_link_en"  : memcontent_link_en,
       "cpuid" : core,
       "skip_cycle" : 0,
       "pagelink_en" : 1,
       "hasROB" : 1,
       "max_issue_per_cycle" : 4,
       "max_outstanding" : 32,
       "sizeROB" : 128,
       "maxCommitPerCycle" : 4,
       "nonCacheable" : 0,
       } )

    #set max. number of instructions
    if options.maxInst != 0 : 
        print "maxInst: " + str(options.maxInst)
        prospero["prospero"+str(core)].addParams({"max_inst" : options.maxInst})


    prospero["prospero" + str(core)].enableAllStatistics()
    prospero_cache_link = sst.Link("prospero_cache_link_" + str(core))
    prospero_cache_link.connect( ( prospero["prospero" + str(core)], "cramsim_cache_link", busLat), (membus, "high_network_%d"%core, busLat) )
    
    MemContentLink = sst.Link("memContent_%d"%core)
    MemContentLink.connect((prospero["prospero" + str(core)], "linkMemContent",busLat), (comp_controller0, "lane_%d"%core, busLat));

    PageAllocLink = sst.Link("pageLink_%d"%core)
    PageAllocLink.connect((prospero["prospero" + str(core)], "pageLink",busLat), (comp_pageAllocator0, "pageLink_%d"%core, busLat));


