#!/bin/python
import os
import json
import time
import ConfigParser
from optparse import OptionParser
import datetime
import shutil

###### SIM OPTION PARSER ###########
parser = OptionParser(usage="usage: %prog [options]")
parser.add_option("-f", "--optionfile" , action="store", dest="optionfile", help="simulation options")
(options, arg) = parser.parse_args()

config = ConfigParser.ConfigParser()
config.optionxform = str
config.read(options.optionfile)
############################################

date=datetime.datetime.now().strftime("%y-%m-%d")
time_h_m=datetime.datetime.now().strftime("%H:%M")
sim_id=str(int(time.time()*1000))


########Setup simulation parameters ######################
CRAMSIM_CFG=config.get("SIM","CRAMSIM_CONFIG")
OUTPUT_DIR="./output/"+date;
CONFIG_DIR="./config";
SST_CONFIG=config.get("SIM","SST_CONFIG")
TRACE_TYPE=config.get("TRACE","TRACE_TYPE")
SIM_NAME=TRACE_TYPE+"."+CRAMSIM_CFG


########### Create Output directory #######################
if os.path.exists(OUTPUT_DIR)==False:
    print "Create %s"%OUTPUT_DIR
    os.mkdir(OUTPUT_DIR)

shutil.copy2(options.optionfile, OUTPUT_DIR+"/"+str(sim_id)+"-"+options.optionfile)

###########Benchmark#################################
GAP_BENCHMARK=config.get("TRACE","GAP_BENCHMARK").split('\n')
GRAPH=config.get("TRACE","GRAPH").split('\n')

GAP_BENCHMARK_GRAPH=[];
for gap_bench in GAP_BENCHMARK:
    for graph in GRAPH:
        GAP_BENCHMARK_GRAPH.append(gap_bench+"-"+graph);

SPEC_BENCHMARK=config.get("TRACE","SPEC_BENCHMARK").split('\n')
MIX_BENCHMARK=config.get("TRACE","MIX_BENCHMARK").split('\n')
BENCHMARK_TYPES=config.get("TRACE","BENCHMARK_TYPES").split('\n')
MPI_CORES=1

#### Write simulation history ####################
history_file="history.json";
print "\nBatch simulation";
print "Date: " +date;
print "Time: " +time_h_m;
print "Simulaiton ID: "+str(sim_id);
print "Simulation History File: "+history_file;
print "Simulation Name: "+SIM_NAME;
#description=input("Description?: ");
#print description
print "Output directory: "+OUTPUT_DIR;

###### Run ###############################################
all_benchmark=[];
all_option=[]
default_options=config.options("DEFAULT_OPTION")
var_options=config.options("VAR_OPTION")

for benchmark_type in BENCHMARK_TYPES:
    benchmark=[]
    if benchmark_type=="spec":
        benchmark=SPEC_BENCHMARK;
    elif benchmark_type=="gap":
        benchmark=GAP_BENCHMARK_GRAPH;
    elif benchmark_type=="mix":
        benchmark=MIX_BENCHMARK;
    
    for bench in benchmark:
        all_benchmark.append(bench)
        
        CRAMSIM_CONFIG=CONFIG_DIR+"/"+CRAMSIM_CFG+".cfg";
        

        for option_name in var_options:
            option_values = config.get("VAR_OPTION",option_name).split("\n")
            for option_value in option_values:
                option = option_name+option_value
                if not option in all_option:
                    all_option.append(option)
                
                SIM_STAT=OUTPUT_DIR+"/simstat."+sim_id+"."+bench+"."+option+"."+SIM_NAME;
                SIM_RESULT=OUTPUT_DIR+"/simresult."+sim_id+"."+bench+"."+option+"."+SIM_NAME;
                SST_CFG_OUT=OUTPUT_DIR+"/sstcfg."+sim_id+"."+bench+"."+option+"."+SIM_NAME;
         
                model_options="\"--cramConfig %s " % CRAMSIM_CONFIG \
                    + " --benchmark %s --benchmarkType %s --traceType %s"%(bench,benchmark_type,TRACE_TYPE) \
                    + " --traceFormat CompressedBinary --profileAtomics 0" \
                    + " --pimSupport 0 --waitCycle 1 "
                
                #default option
                for default_option_name in default_options:
                    default_option_value = config.get("DEFAULT_OPTION",default_option_name)
                    model_options = model_options + "--%s %s "%(default_option_name,default_option_value)


                model_options=model_options \
                    + "--statName %s "%SIM_STAT \
                    + "--%s %s \""%(option_name,option_value)

                cmd = " gdb --args sst --output-json %s --print-timing-info"%SST_CFG_OUT \
                  +" --model-options=%s %s.py"%(model_options,SST_CONFIG);
            
                print cmd;
                os.system(cmd);
                time.sleep(0.1)

#####################################################

for bench in all_benchmark:
    print "\nbenchmark list"
    print bench

for option in all_option:
    print "\noption list"
    print option


data= {}
if os.path.exists(history_file)==True:
    with open(history_file,'r') as json_file:
         data=json.load(json_file)
else:
    data['log']=[]

data['log'].append({
    'id': "%s"%sim_id,
    'date': date,
    'time': time_h_m,
    'sim_name': SIM_NAME,
    'benchmarks':all_benchmark,
    'options':all_option,
    'description':description
    })

with open(history_file,"w") as json_file:
    json.dump(data, json_file)

