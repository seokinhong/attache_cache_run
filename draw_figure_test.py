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
from scipy.stats.mstats import gmean

#import plotly
pd.set_option('display.max_columns', 10000)
pd.set_option('display.width', 1000)
plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.5)

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
               # print sumint
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
                             #  print "* Searching item (%s) of component (%s) in \"%s\"" % (stat_item,component,stat_file)
                             #  print "=>Value: "+str(value)

                return df
 
parser = OptionParser(usage="usage: %prog [options]")
parser.add_option("-i", "--id" , action="store", dest="SimID", help="Specify a simulation id, default is latest one", default=-1)
parser.add_option("-p", "--print" , action="store", dest="PrintMode", help="Print the simulation result file (specify \"log\" or \"stat\")",default="None")
parser.add_option("-l", "--list" , action="store_true", dest="BoolDisplay", help="Show simulation list", default=False)
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
        print element

sim_id=-1;
if options.SimID == -1:
    sim_id = all_data[len(all_data)-1]['id']
else:
    sim_id = options.SimID


if options.PrintMode == "log":
    report_type = "simresult"
elif options.PrintMode == "stat":
    report_type = "simstat"

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
     

def getItem_from_multipleDB (item,component,sim_id_array):
    frames=[]
    db_base=""
    db_tech=""
    for sim_id in sim_id_array:
        db=getItem(item,component,sim_id)
        frames.append(db)
    return pd.concat(frames)


def mergeDB (item,component,sim_id_base,sim_id_tech ):
    frames=[]
    db_base=""
    db_tech=""
    for sim_id in sim_id_base:
        db=getItem(item,component,sim_id)
        frames.append(db)
    if len(frames)>0:
        db_base=pd.concat(frames)

    frames=[]
    for sim_id in sim_id_tech:
        db=getItem(item,component,sim_id)
        frames.append(db)
    
    if len(frames)>0:
        db_tech=pd.concat(frames)
    
    return db_base.merge(db_tech,how='outer',left_index=True, right_index=True)


######################################
#id_spec_b   =   "1521160718357"   #8cores, 200M
#id_spec_t   =   "1521186640927"    #8cores, 200M

id_spec_b   =   "1522386724537"   #8cores, 200M,random-page,sp
id_spec_t   =   "1522149567836"    #8cores, 200M,random-page,sp
#id_spec_t   =   "1521768696252"    #8cores, 200M,random-page,multilane_rowtable,metacache_latency

#id_spec_b   =   "1521499949854"   #4cores, 400M
#id_spec_t   =   "1521489421891"   #4cores, 400M

#id_gap_b    =   "1521500053905"   #4cores, 400M
#id_gap_t    =   "1521507873531"   #4cores, 400M

#id_gap_b    =   "1521605095838"   #1thread, 4cores, F10B, R400M
#id_gap_t    =   "1521605128766"   #1thread, 4cores, 400M, F10B, R400M
id_gap_b    =   "1522149577522"   #1thread, 8cores, 200M, F10B, Random
id_gap_t    =   "1522149582561"   #1thread, 8cores, 200M, F10B, Random
#id_gap_t   =   "1521769315409"    #8cores, 200M,random-page,multilane_rowtable,metacache_latency

id_mix_b    =   "1521509081853"   #4cores, 400M
id_mix_t    =   "1521509224615"   #4cores, 400M


#id_base     =   [id_spec_b,id_mix_b,id_gap_b]
#id_tech     =   [id_spec_t,id_mix_t,id_gap_t]
#id_base     =   [id_gap_b]
#id_tech     =   [id_gap_t]

#id_base     =   [id_spec_b]
#id_tech     =   [id_spec_t]
id_base     =   [id_spec_b,id_gap_b]
id_tech     =   [id_spec_t,id_gap_t]



report_dir  =   "./report"
#result_name =   "specB%s-specT%s-gapB%s-gapT%s"%(id_spec_b,id_gap_b,id_spec_t,id_gap_t)
result_name =   "simpoint"
cores       =   8
per_core_insts = 200000000
total_inst  =   per_core_insts

#L3 MPKI + L3 HIT RATE
db_l3_misses   =   mergeDB("misses","l3",id_base,id_tech)
db_l3_hits      =   mergeDB("hits","l3",id_base,id_tech)
db_l3_accesses =   mergeDB("accesses","l3",id_base,id_tech)
db_l3_mpki  =   db_l3_misses/(total_inst/1000)
db_l3_missrate=pd.DataFrame(index=db_l3_misses.index.values);
db_l3_missrate['misses']=db_l3_misses.iloc[:,0]
db_l3_missrate['hits']=db_l3_hits.iloc[:,0]
db_tmp=db_l3_misses/db_l3_accesses
db_l3_missrate['miss_rate']=db_tmp.iloc[:,0]


print "\n --- mpki --- "
print db_l3_mpki
db_l3_mpki.plot.bar()
plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.3)
plt.savefig(report_dir+"/l3mpki-%s.pdf"%(result_name))

#L3 Miss RATE
print "\n --- l3 miss rate ---"
print db_l3_missrate
db_l3_missrate.to_csv(report_dir+"/l3missrate-%s.csv"%(result_name))
db_l3_missrate.plot.bar()
plt.savefig(report_dir+"/l3missrate-%s.pdf"%(result_name))


#Total mem access
db_mem_access   =   mergeDB("totalTxnsRecvd","MemController0",id_base,id_tech)
print "\n ---- total_mem_access -----"
print db_mem_access
db_mem_access.plot.bar()
plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.3)
plt.savefig(report_dir+"/mem_access-%s.pdf"%(result_name))


#DRAM cmd
db_act_cmd   =   mergeDB("actCmdsRecvd","Dimm0",id_base,id_tech)
db_read_cmd   =   mergeDB("readCmdsRecvd","Dimm0",id_base,id_tech)
db_write_cmd   =   mergeDB("writeCmdsRecvd","Dimm0",id_base,id_tech)
db_prech_cmd   =   mergeDB("preCmdsRecvd","Dimm0",id_base,id_tech)
print "\n ---- act_cmd -----"
print db_act_cmd
print "\n ---- read_cmd -----"
print db_read_cmd
print "\n ---- write_cmd -----"
print db_write_cmd
print "\n ---- pre_cmd -----"
print db_prech_cmd



#Compression ratio
db_cachesize50  =   mergeDB("cacheline_size_50","MemController0",id_base,id_tech)
db_cachesize100  =   mergeDB("cacheline_size_100","MemController0",id_base,id_tech)
db_compressed_cl_rate   =   db_cachesize50/(db_cachesize50+db_cachesize100)

print "\n ---- compressed_cl_rate -----"
#gmean=gmean(db_compressed_cl_rate.iloc[:,1:2],axis=0)
db_compressed_cl_rate.loc['mean']=db_compressed_cl_rate.mean()
print db_compressed_cl_rate
db_compressed_cl_rate.plot.bar()
plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.3)
plt.savefig(report_dir+"/compressed_cl_rate-%s.pdf"%(result_name))

#allocated pages
db_alloc_pages  =   mergeDB("numAllocPages","PageAllocator0",id_base,id_tech)
print "\n ---- allocated pages -----"
print db_alloc_pages
db_alloc_pages.plot.bar()
plt.subplots_adjust(left=0.2, right=0.9, top=0.9, bottom=0.3)
plt.savefig(report_dir+"/alloc_pages-%s.pdf"%(result_name))

#footprint
db_alloc_pages  =   mergeDB("numAllocPages","PageAllocator0",id_base,id_tech)
print "\n ---- footprint (MB) -----"
db_footprint=db_alloc_pages*4*1024/1024/1024
db_footprint.plot.bar()
print db_footprint
plt.subplots_adjust(left=0.2, right=0.9, top=0.9, bottom=0.3)
plt.savefig(report_dir+"/footprint-%s.pdf"%(result_name))

'''
#Prediction Accuracy -- impact of the size of lipr
#id_attach_diff_lipr=["1521489566787"]
id_attach_diff_lipr=id_tech
db_lipr_hit  =   getItem_from_multipleDB("predictor_lipr_hit","MemController0",id_attach_diff_lipr)
db_lipr_miss  =   getItem_from_multipleDB("predictor_lipr_miss","MemController0",id_attach_diff_lipr)
db_lipr_success  =   getItem_from_multipleDB("predictor_lipr_success","MemController0",id_attach_diff_lipr)
db_lipr_fail  =   getItem_from_multipleDB("predictor_lipr_fail","MemController0",id_attach_diff_lipr)
db_ropr_success  =   getItem_from_multipleDB("predictor_ropr_success","MemController0",id_attach_diff_lipr)
db_ropr_fail  =   getItem_from_multipleDB("predictor_ropr_fail","MemController0",id_attach_diff_lipr)

db_success_above50  =   getItem_from_multipleDB("predicted_success_above50","MemController0",id_tech)
db_success_below50  =   getItem_from_multipleDB("predicted_success_below50","MemController0",id_tech)
db_fail_below50  =   getItem_from_multipleDB("predicted_fail_below50","MemController0",id_tech)
db_fail_above50  =   getItem_from_multipleDB("predicted_fail_above50","MemController0",id_tech)

db_lipr_success_rate =db_lipr_success/ (db_lipr_success+db_lipr_fail)
db_lipr_hit_rate = db_lipr_hit/(db_lipr_hit+db_lipr_miss)
db_ropr_success_rate = db_ropr_success/(db_ropr_success+db_ropr_fail)
#db_success_rate = ((db_success_above50+db_success_below50)/(db_success_above50+db_success_below50+db_fail_below50+db_fail_abobe_50))
print "\n ---- LiPR hit rate  ---"
print db_lipr_hit_rate
print "\n ---- LiPR success rate ---"
print db_lipr_success_rate
print "\n ---- RoPR success rate ---"
print db_ropr_success_rate
print "\n ---- Overall success rate ---"
print (db_ropr_success+db_lipr_success)/(db_ropr_success+db_ropr_fail+db_lipr_success+db_lipr_fail)
'''

#IPC + Speedup
db_cycles   =   mergeDB("cycles","prospero0",id_base,id_tech)
db_multilane_cycles   =   getItem("cycles","prospero0","1521775897964")
print db_multilane_cycles
db_ipc = total_inst/db_cycles
base    =   db_ipc.iloc[:,0]
#db_cycle_norm   =   db_cycles.div(base, axis=0)
db_speedup      =   db_ipc.div(base,axis=0)
mean            =   db_speedup.mean()
db_speedup.loc['mean']=mean

print "\n ---- cycles -----"
print db_cycles
db_cycles.plot.bar()
plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.3)
plt.savefig(report_dir+"/cycles-%s.pdf"%(result_name))


print "\n ---- ipc -----"
print db_ipc
db_ipc.plot.bar()
plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.3)
plt.savefig(report_dir+"/ipc-%s.pdf"%(result_name))


print "\n ---- speedup ----"
#print db_ipc.iloc[:,0]
print db_speedup
db_speedup=db_speedup.iloc[:,2:5]
db_speedup.columns = ['Ideal','Metadata Cache','Attache']  #change column name
db_speedup = db_speedup[['Metadata Cache','Attache','Ideal']] #change column order
db_speedup.plot.bar(figsize=(18, 6))
plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.3)
plt.ylim(ymax = 1.8, ymin = .5)
plt.savefig(report_dir+"/speedup-%s.pdf"%(result_name))
db_speedup.to_csv(report_dir+"/speedup-%s.csv"%(result_name))


'''
#diff # of metacache entries
id_spec_metacache="1521507154299"
id_mix_metacache="1521514473466"
id_gap_metacache="1521514367387"
id_metacache = [id_spec_metacache,id_mix_metacache,id_gap_metacache]

db_metacache_cycles = getItem_from_multipleDB("cycles","prospero0",id_metacache)
db_metacache_cycles=db_cycles.merge(db_metacache_cycles,how='outer',left_index=True, right_index=True)
db_ipc = per_core_insts/db_metacache_cycles
print "\n ---cycles with diff # of metacache "
print db_ipc
'''


#metacahe hitrate
db_metacache=pd.DataFrame(columns=["miss","hit","total", "miss_rate"])
db_metacache["miss"] = getItem_from_multipleDB("memzip_metacache_miss","MemController0",id_tech).iloc[:,1]
db_metacache["hit"] = getItem_from_multipleDB("memzip_metacache_hit","MemController0",id_tech).iloc[:,1]
db_metacache["total"] = db_metacache["miss"]+db_metacache["hit"]
db_metacache["miss_rate"]=db_metacache["miss"]/db_metacache["total"]
db_metacache.to_csv(report_dir+"/mcache_miss-%s.csv"%(result_name))
#db_metacache_hitrate = db_metacache_hit/(db_metacache_hit+db_metacache_miss)
print "\n ---metacache miss"
print db_metacache

#predictor accuracy

