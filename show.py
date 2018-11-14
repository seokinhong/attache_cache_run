#!/bin/python
import os
import json
import time
import datetime
from optparse import OptionParser
import csv
import pandas as pd
import numpy as np
import matplotlib; matplotlib.use('PDF')
import matplotlib.pyplot as plt

def get_statistic(component,  item, stat_file):
    with open(stat_file, 'rb') as csv_input_file:
        csvreader = csv.DictReader(csv_input_file, delimiter=',',quotechar='|')
        for csvrow in csvreader:
            found=False
            if component != "None":
                if csvrow["ComponentName"] == component and csvrow["StatisticName"]==item :
                    found=True
            else:
                if csvrow["StatisticName"]==item:
                    found=True

            if found ==True:
                sumint = int (csvrow["Sum.u64"])
                sumfloat = float(csvrow["Sum.f64"])
                cntint = int (csvrow["Count.u64"])
                cntfloat = int(csvrow["Count.u64"])
                value = 0
                sum=0
                cnt=0
                
                if sumfloat>0:
                    sum=sumfloat
                    cnt=cntfloat
                else:
                    sum=sumint
                    cnt=cntint
                print sumint
                if sum > cnt*1.05:
                    value = sum/cnt;
                else:
                    value = sum

                return value


def getItem (stat_item, component,sim_id):
    if stat_item != "None":
        for element in all_data:
            if element['id']==sim_id:
                benchmarks=element['benchmarks']
                options=element['options']
                date=element['date']
                sim_id=element['id']
                sim_name=element['sim_name']
                
                #create panda data frame
                df=pd.DataFrame(index=benchmarks,columns=options)
                for option in options:
                    for benchmark in benchmarks:
                       output_dir="./output/%s"%(date)
                       stat_file="simstat.%s.%s.%s.%s"%(sim_id,benchmark,option,sim_name)
                       dirListing = os.listdir(output_dir)
                       for file_name in dirListing:
                           if stat_file in str(file_name):
                               value = get_statistic(component, stat_item, output_dir+"/"+file_name)
                               df.at[benchmark,option]=value
                               print "* Searching item (%s) of component (%s) in \"%s\"" % (stat_item,component,stat_file)
                               print "=>Value: "+str(value)

                return df
 
parser = OptionParser(usage="usage: %prog [options]")
parser.add_option("-i", "--id" , action="store", dest="SimID", help="Specify a simulation id, default is latest one", default=-1)
parser.add_option("-p", "--print" , action="store", dest="PrintMode", help="Print the simulation result file (specify \"log\" or \"stat\")",default="None")
parser.add_option("-l", "--list" , action="store_true", dest="BoolDisplay", help="Show simulation list", default=False)
parser.add_option("-d", "--detail" , action="store_true", dest="BoolDisplayDetail", help="Show simulation list in details", default=False)
parser.add_option("-t", "--item" , action="store", dest="StatItem", help="Specify a statistic item", default="None")
parser.add_option("-c", "--comp" , action="store", dest="StatComp", help="Specify a component for the statistic item", default="None")
parser.add_option("-b", "--benchmark" , action="store", dest="Benchmark", help="Specify a benchmark for the statistic item", default="None")
parser.add_option("-o", "--option" , action="store", dest="Option", help="Specify a simulation option", default="*")
parser.add_option("-a", "--autoplot" , action="store_true", dest="BoolAutoPlot", help="Create plots automatically", default=False)



(options, arg) = parser.parse_args()

history_file="history.json";
if os.path.exists(history_file)==True:
    with open(history_file,'r') as json_file:
         data=json.load(json_file)
else:
    print "history_file (%s) does not exists"
    exit(0)


all_data=data['log']
if options.BoolDisplay == True:
    for element in all_data:
        if options.BoolDisplayDetail:
            print element
        else: 
            print element['id']+":"+element['description']

sim_id=-1;
if options.SimID == -1:
    sim_id = all_data[len(all_data)-1]['id']
else:
    sim_id = options.SimID


if options.PrintMode == "log":
    report_type = "simresult"
elif options.PrintMode == "stat":
    report_type = "simstat"
elif options.PrintMode == "cfg":
    report_type = "sstcfg"


if options.PrintMode != "None":
    for element in all_data:
        if element['id']==sim_id:
            if options.Benchmark=="None":
                  os.system("cat output/%s/%s.%s*%s*"%(element['date'],report_type,sim_id,options.Option))
            else:
                  os.system("cat output/%s/%s.%s*%s*%s*"%(element['date'],report_type,sim_id,options.Benchmark,options.Option))


stat_item=options.StatItem
component=options.StatComp
if stat_item != "None":
    df=getItem(stat_item,component,sim_id)

    print df

    df.plot.bar()
    plt.savefig("%s-%s.pdf"%(stat_item,sim_id))
    #plot.get_figure().savefig("%s-%s.pdf"%(stat_item,sim_id),format='pdf')
    #writing data frame to a csv file
    output_csv_name="%s-%s.csv"%(stat_item,sim_id)
    df.to_csv(output_csv_name)
     

######################################
if options.BoolAutoPlot == True:
    df_l3_misses=getItem("misses","l3",sim_id)
    df_l3_hits=getItem("hits","l3",sim_id)
    df_l3_accesses=getItem("accesses","l3",sim_id)
    df_l3_mpki=df_l3_misses/200000
    df_l3_hitrate=df_l3_hits/df_l3_accesses
    df_cycles=getItem("cycles","prospero0",sim_id)

    df_ipc = 200000000/df_cycles
    df_speedup = df_ipc.iloc[:,1]/df_ipc.iloc[:,0]
    
    mean=df_speedup.mean()

    df_speedup.loc['mean']=mean
    df_speedup.plot.bar()
    plt.savefig("Speedup-%s.pdf"%(sim_id))

    print "ipc"
    print df_ipc
    print "\n"

    print "l3_mpki"
    print df_l3_mpki
    print "\n"

    print "l3_accesses"
    print df_l3_accesses
    print "\n"

    print "l3_hits"
    print df_l3_hits
    print "\n"

    print "l3_misses"
    print df_l3_misses
    print "\n"

    print "l3_hitrate"
    print df_l3_hitrate
    print "\n"

    df_mem_access=getItem("totalTxnsRecvd","MemController0",sim_id)
    df_cachesize50=getItem("cacheline_size_50","MemController0",sim_id)
    df_cachesize100=getItem("cacheline_size_100","MemController0",sim_id)
    df_compressed_cl_rate=df_cachesize50/df_mem_access

    print "mem_access"
    print df_mem_access
    print "\n"

    print "cachesize50"
    print df_cachesize50
    print "\n"


    print "cachesize100"
    print df_cachesize100
    print "\n"


    print "compressed_cl_rate"
    print df_compressed_cl_rate
    print "\n"
