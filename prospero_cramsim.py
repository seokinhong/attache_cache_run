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
parser.add_option("--metadata_pred_mode",  action='store', dest="MetaPredMode", help="Metadata prediction mode",default=0)
parser.add_option("--metacache_entries",  action='store', dest="MetaCacheEntries", help="The number of entries of metacache",default=32)
parser.add_option("--stopAtCycle",  action='store', dest="StopAtCycle", help="stop at cycle",default=10s)
parser.add_option("--statName",  action='store', dest="StatName", help="Name of statistic file.")

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
    extension = "-gz.trace"
else:
    extension = ".trace"

# setup CramSim
cramsim_config=options.CramConfig
g_params = setup_config_params(cramsim_config)
memCtrlClockCycle = g_params["clockCycle"]
memCtrlClock = g_params["strControllerClockFreq"]
memSize = int(g_params["numChannels"]) * \
            int(g_params["numRanksPerChannel"]) * \
            int(g_params["numBankGroupsPerRank"]) * \
            int(g_params["numBanksPerBankGroup"]) * \
            int(g_params["numRowsPerBank"]) * \
            int(g_params["numColsPerBank"]) * \
            int(g_params["numBytesPerTransaction"])/(1024*1024*1024);

# Define SST core options
sst.setProgramOption("timebase", "100ps")
sst.setProgramOption("stopAtCycle", StopAtCycle)

## Flags
memDebug = 0
memDebugLevel = 0
coherenceProtocol = "MESI"
rplPolicy = "lru"
cacheFrequency = "3 Ghz"
coreFrequency = "3 Ghz"
busLat = "100ps"
busLat_slow = "2ns"
debug = 0
controller_verbose = 0
cacheLineSize = 64
#corecount = 4
corecount = 4

compression_en = 1
memcontent_link_en =1
oracle_mode =0
metacache_entries=MetaCacheEntries
metadata_predictor=MetaPredMode
contentline_num = corecount

pagesize=4096       #B
pagecount = memSize*1024*1024*1024/pagesize

## Application Info
os.environ['SIM_DESC'] = 'EIGHT_CORES'
os.environ['OMP_NUM_THREADS'] = str(corecount)
sst_root = os.getenv( "SST_ROOT" )


print(config_name)
print(trace_config)
print("memsize:%dGB"%memSize)


##### Prepair benchmarr set #########################
print options.BenchmarkType;
mt_mode=0
spec_trace_dir="./spec_trace"
gap_trace_dir="./gap_trace"
if options.BenchmarkType=="spec":
    for i in range(0,corecount):
        trace="./%s/%s-%s-0-0%s" % (spec_trace_dir,options.Benchmark,options.TraceType,extension);
        
        if os.path.exists(trace)==False:
            print "trace file (%s) is not exists"%trace
            exit(0)
        else:
           print trace;

        traceName.append(trace)
elif options.BenchmarkType=="gap":
    mt_mode=1;
    for i in range(0,corecount):
        trace="./%s/%s-%s-%d-0%s" % (gap_trace_dir,options.Benchmark,options.TraceType,i,extension);
        print trace;
        
        if os.path.exists(trace)==False:
            print "trace file (%s) is not exists"%trace
            exit(0)
        else:
            print trace;

        traceName.append(trace)
elif options.BenchmarkType=="mix":
    benchmark_set=options.Benchmark.split(".")
    if len(benchmark_set)<corecount:
        print "the number of benchmars is less than corecount"
        exit(0)

    for i in range(0,corecount):
        trace="./%s/%s-%s-0-0%s" % (spec_trace_dir,benchmark_set[i],options.TraceType,extension);
        print trace;
        traceName.append(trace)


##########################################################################################
##########################################################################################

# CramSim
# txn gen --> memHierarchy Bridge
comp_memhBridge = sst.Component("memh_bridge", "CramSim.c_MemhBridge")
comp_memhBridge.addParams(g_params);
comp_memhBridge.addParams({
                    "numTxnPerCycle" : g_params["numChannels"]
                    })


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
                "TxnConverter" : "CramSim.c_TxnConverter",
                "AddrMapper" : "CramSim.c_AddressHasher",
                "CmdScheduler" : "CramSim.c_CmdScheduler" ,
                "DeviceController" : "CramSim.c_DeviceController",
                "contentline_num" : contentline_num
                })



# memory device
comp_dimm0 = sst.Component("Dimm0", "CramSim.c_Dimm")
comp_dimm0.addParams(g_params)
comp_dimm0.addParams({
    "pca_enable" : pca_enable}
    )

# MemHierarchy
l3 = sst.Component("L3cache", "memHierarchy.Cache")
l3.addParams({
    "cache_frequency"       : cacheFrequency,
    "cache_size"            : "1MB",
    "cache_line_size"       : cacheLineSize,
    "associativity"         : "4",
    "access_latency_cycles" : "15",    # (20 cycle * (1/3GHz) - link latency (2ns))/(1/3GHz)
    "coherence_protocol"    : coherenceProtocol,
    "replacement_policy"    : rplPolicy,
    "L1"                    : "0",
    "debug"                 : memDebug,  
    "debug_level"           : memDebugLevel, 
    "mshr_num_entries"      : "512",
    "mshr_latency_cycles"   : 4
})

# MemHierarchy
memory = sst.Component("memory", "memHierarchy.MemController")
memory.addParams({
    "do_not_back"				: "1",
    "range_start"           : "0",
    "coherence_protocol"    : coherenceProtocol,
    "debug"                 : memDebug,
    "clock"                 : memCtrlClock,
    "corenum"               : corecount,
    "isMultiThreadMode"     : mt_mode,
    "isPageAllocLink" : 1,
    "pagesize" :            pagesize,
    "backend" : "memHierarchy.cramsim",
    "backend.max_outstanding_requests" : 1024,
    "request_width"         : cacheLineSize,
    "backend.mem_size" : "%dGiB"%memSize,
#    "clock"                 : "800MHz",
#    "backend"               :"memHierarchy.dramsim",
#    "backend.system_ini" : "system.ini",
#    "backend.device_ini" : "DDR3_micron_32M_8B_x8_sg15.ini",
   #  "backend.access_time" : "500ns"
   # "backend" : "memHierarchy.simpleDRAM",    
   # "backend.mem_size" : "%dGiB"%memSize,
#    "backend.verbose" : -1,
#    "backend.tCAS" : 16, # 11@800MHz roughly coverted to 200MHz
#    "backend.tRCD" : 16,
#    "backend.tRP" : 16,
#    "backend.banks" : 16,
#    "backend.bank_interleave_granularity": "8KiB",
#    "backend.cycle_time" : "800ps",
#    "backend.row_size" : "64B",
#    "backend.row_policy" : "open"
#    "backend.access_time" : "1 ns",   # Phy latency
#    "backend.max_outstanding_requests" : 1024,
#    "backend.mem_size" : "%dGiB"%memSize,
#    "request_width"         : cacheLineSize
    })


membus = sst.Component("membus", "memHierarchy.Bus")
membus.addParams({
    "bus_frequency" : cacheFrequency,
    })

link_dir_cramsim_link = sst.Link("link_dir_cramsim_link")
link_dir_cramsim_link.connect( (memory, "cube_link", busLat_slow), (comp_memhBridge,"cpuLink", busLat_slow) )

# memhBridge(=TxnGen) <-> Memory Controller 
memHLink = sst.Link("memHLink_1")
memHLink.connect( (comp_memhBridge, "memLink", g_params["clockCycle"]), (comp_controller0, "txngenLink", g_params["clockCycle"]) )

# Controller <-> Dimm
cmdLink = sst.Link("cmdLink_1")
cmdLink.connect( (comp_controller0, "memLink", g_params["clockCycle"]), (comp_dimm0, "ctrlLink", g_params["clockCycle"]) )


# Bus to L3 and L3 <-> MM
BusL3Link = sst.Link("bus_L3")
BusL3Link.connect((membus, "low_network_0", busLat_slow), (l3, "high_network_0", busLat_slow))
L3MemCtrlLink = sst.Link("L3MemCtrl")
L3MemCtrlLink.connect((l3, "low_network_0", busLat), (memory, "direct_link", busLat))
 

## Prospero
prospero={}
for core in range (0, corecount):
    print "Creating prospero component core " + str(core)
    tracefile=traceName[core];
    print tracefile;
    prospero["prospero" + str(core)] = sst.Component("prospero" + str(core), "prospero.prosperoCPU")
    prospero["prospero" + str(core)].addParams( {
       "clock" : str(coreFrequency),
       "reader" : "prospero.Prospero" + options.TraceFormat + "TraceReader",
       "readerParams.file" : tracefile,
       "readerParams.pimsupport" : str(options.PIMSupport),
       "traceformat" : "1",
       "verbose" : debug,
       "max_outstanding" : 64,
       "max_issue_per_cycle" : 4,
       "pagesize" : 4096,
       "pagecount" : 4096,
       "profileatomics" : str(options.ProfileAtomics),
       "pimsupport" : str(options.PIMSupport),
       "waitCycle" : str(options.WaitCycle),
       "cache_line_size" : cacheLineSize,
       "memcontent_link_en"  : memcontent_link_en,
       "cpuid" : core,
       "skip_cycle" : 10000000000,
       "pagelink_en" : 1
       } )


    l1 = sst.Component("l1cache_%d"%core, "memHierarchy.Cache")
    l1.addParams({
       "cache_frequency"       : cacheFrequency,
       "cache_size"            : "32KB",
       "cache_line_size"       : cacheLineSize,
       "associativity"         : "8",
       "access_latency_cycles" : "4",
       "coherence_protocol"    : coherenceProtocol,
       "replacement_policy"    : rplPolicy,
       "L1"                    : "1",
       "debug"                 : memDebug,  
       "debug_level"           : memDebugLevel, 
       "mshr_num_entries"      : "32",
       "mshr_latency_cycles"   : 2,
       "memlink.latency" : busLat,
       "cpulink.latency" : busLat
       })

    l2 = sst.Component("l2cache_%d"%core, "memHierarchy.Cache")
    l2.addParams({
        "cache_frequency"       : cacheFrequency,
        "cache_size"            : "256KB",
        "cache_line_size"       : cacheLineSize,
        "associativity"         : "8",
        "access_latency_cycles" : "8",
        "coherence_protocol"    : coherenceProtocol,
        "replacement_policy"    : rplPolicy,
        "L1"                    : "0",
        "debug"                 : memDebug,  
        "debug_level"           : memDebugLevel, 
        "mshr_num_entries"      : "64",
        "mshr_latency_cycles" : 2,
        "memlink.latency" : busLat
    })

   ## SST Links
   # Prospero -> L1(PRIVATE) -> L2(PRIVATE)  -> L3 (SHARED) -> DRAM 
   #ArielL1Link = sst.Link("cpu_cache_%d"%core)
   #ArielL1Link.connect((ariel, "cache_link_%d"%core, busLat), (l1, "high_network_0", busLat))

    prospero_cache_link = sst.Link("prospero_cache_link_" + str(core))
    prospero_cache_link.connect( ( prospero["prospero" + str(core)], "cache_link", busLat), (l1, "high_network_0", busLat) )

    L1L2Link = sst.Link("l1_l2_%d"%core)
    L1L2Link.connect((l1, "low_network_0", busLat), (l2, "high_network_0", busLat))
    L2MembusLink = sst.Link("l2_membus_%d"%core)
    L2MembusLink.connect((l2, "low_network_0", busLat_slow), (membus, "high_network_%d"%core, busLat_slow))
    
    MemContentLink = sst.Link("memContent_%d"%core)
    MemContentLink.connect((prospero["prospero" + str(core)], "linkMemContent",busLat_slow), (comp_controller0, "lane_%d"%core, busLat_slow));

    PageAllocLink = sst.Link("pageLink_%d"%core)
    PageAllocLink.connect((prospero["prospero" + str(core)], "pageLink",busLat_slow), (memory, "pageLink_%d"%core, busLat_slow));

    l1.enableAllStatistics()
    l2.enableAllStatistics()
    prospero["prospero" + str(core)].enableAllStatistics()





# Enable SST Statistics Outputs for this simulation
l3.enableAllStatistics()
memory.enableAllStatistics()
comp_controller0.enableAllStatistics()
comp_memhBridge.enableAllStatistics()
comp_dimm0.enableAllStatistics()

sst.enableAllStatisticsForAllComponents({"type":"sst.AccumulatorStatistic"})
sst.setStatisticLoadLevel(7)
#sst.setStatisticOutput("sst.statOutputConsole")


sst.setStatisticOutput("sst.statOutputCSV")
sst.setStatisticOutputOptions( {
		"filepath"  : "%s.csv"%options.StatName,
		"separator" : ","
    } )


