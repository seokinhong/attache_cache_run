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
import seaborn as sns
import math
#sns.set_style("whitegrid")
sns.set_style("white")
plt.rc('grid', linestyle=":", color='black', linewidth=1)
#plt.rc('font',family='Times New Roman')

rgba_array = plt.cm.binary(np.linspace(0,1,num=10,endpoint=True))
extract_rgba_array_255 = rgba_array[2:8,0:3]
#import plotly
pd.set_option('display.max_columns', 10000)
pd.set_option('display.width', 1000)
plt.subplots_adjust(bottom=0.4)



######################################
result_name = "microfinal"
report_dir  =   "./report"

id_spec_b   =   "1522771472451"   #8cores, 200M,random-page,sp,newl3
id_spec_t   =   "1522771479187"    #8cores, 200M,random-page,sp,newl3

id_gap_b    =   "1522771485912"   #1thread, 8cores, 200M, F10B, Random,newl3
id_gap_t    =   "1522771491425"   #1thread, 8cores, 200M, F10B, Random,newl3

id_mix_b    =   "1522809425265"   #4cores, 400M
id_mix_t    =   "1522809426266"   #4cores, 400M

id_randstream_b = "1522771496895"
id_randstream_t = "1522771497539"

id_spec_metacache = "1522786762477"
id_gap_metacache = "1522786774465"
id_mix_metacache= "1522809426756"
id_randstream_metacache = "1522786784421"

id_attache_all_rownum= "1522791888057"   # more page predictor entry, global predictor effect
id_attache_all_colnum= "1522791909651"   # more page predictor entry, global predictor effect
id_attache_mix_rownum= "1522809431624"   # more page predictor entry, global predictor effect
id_attache_mix_colnum= "1522809433394"   # more page predictor entry, global predictor effect
id_attache_randstream_rownum= "1522826057520"   # more page predictor entry, global predictor effect
id_attache_randstream_colnum= "1522822540672"   # more page predictor entry, global predictor effect
id_attache_all_global= "1522826276834"   # more page predictor entry, global predictor effect




id_base     =   [id_spec_b,id_mix_b,id_gap_b]
id_tech     =   [id_spec_t,id_mix_t,id_gap_t]
id_metacache = [id_spec_metacache,id_mix_metacache,id_gap_metacache,id_randstream_metacache]
id_attache_rownum = [id_attache_all_rownum,id_attache_mix_rownum,id_attache_randstream_rownum]
id_attache_colnum = [id_attache_all_colnum,id_attache_mix_colnum,id_attache_randstream_colnum]
id_attache_global = [id_attache_all_global]
spec_drop = []

cores       =   8
per_core_insts = 200000000
total_inst  =   per_core_insts

SPEC= ['GemsFDTD',
      'omnetpp',
      'soplex',
      'mcf',
	'lbm',
	'libquantum',
      'milc',
     'leslie3d',
      'sphinx3',
      'astar',
      'h264ref',
      'sjeng',
      'cactusADM',
      'zeusmp',
      'bwaves',
      'gcc',
      'bzip2',
       'xalancbmk'
       ]
GAP_APP =[
        'bfs',
        'bc',
        'pr',
        ]

GRAPH = [
        'road',
        'web',
        'kron',
        'urand',
        'twitter',
        ]
GAP=[]
for app in GAP_APP:
    for graph in GRAPH:
        GAP.append(app+"."+graph)

MIX=[
    'mix1',
    'mix2',
    'mix3'
    ]

SYN=[
    'rand',
    'seq'
    ]

MEAN = [
        'gmean'
        ]
BENCHMARK_ALL= SPEC+MIX+GAP+SYN+MEAN
#BENCHMARK_ALL= SPEC+GAP+SYN+MEAN
    

def get_statistic(component,  item, stat_file):
    with open(stat_file, 'rb') as csv_input_file:
        csvreader = csv.DictReader(csv_input_file, delimiter=',',quotechar='|')
        value = np.nan
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
                break

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


#geomean
def geomean(df):
    return np.power(df.prod(axis=0),1.0/len(df))


def mpki_hitrate():
    #L3 MPKI + L3 HIT RATE
    db_l3_misses   =   mergeDB("misses","l3",id_base,id_tech)
    db_l3_hits      =   mergeDB("hits","l3",id_base,id_tech)
    db_l3_accesses =   mergeDB("accesses","l3",id_base,id_tech)
    db_l3_mpki  =   db_l3_misses/(total_inst*cores/1000)
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
    db_l3_missrate['miss_rate'].plot.bar()
    plt.savefig(report_dir+"/l3missrate-%s.pdf"%(result_name))


#Total mem access
def mem_access():
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
def comp_ratio():
    db_cachesize50  =   mergeDB("cacheline_size_50","MemController0",id_base,id_tech)
    db_cachesize100  =   mergeDB("cacheline_size_100","MemController0",id_base,id_tech)
    db_compressed_cl_rate   =   db_cachesize50/(db_cachesize50+db_cachesize100)
    db_compressed_cl_rate.drop(spec_drop,inplace=True)
    #db_compressed_cl_rate.drop(["mix4","mix5"],inplace=True)
    db_compressed_cl_rate = db_compressed_cl_rate['numPCHs1']
    print "\n ---- compressed_cl_rate -----"
    #gmean=gmean(db_compressed_cl_rate.iloc[:,1:2],axis=0)
    db_compressed_cl_rate.loc['mean']=db_compressed_cl_rate.mean()
    print db_compressed_cl_rate
    db_compressed_cl_rate.plot.bar()
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.3)
    plt.savefig(report_dir+"/compressed_cl_rate-%s.pdf"%(result_name))
'''
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
#Prediction Accuracy -- impact of the size of lipr
id_attach_diff_lipr=["1521489566787"]
id_attach_diff_lipr=id_tech
db_lipr_hit  =   getItem_from_multipleDB("predictor_lipr_hit","MemController0",id_attach_diff_lipr)
db_lipr_miss  =   getItem_from_multipleDB("predictor_lipr_miss","MemController0",id_attach_diff_lipr)
db_lipr_success  =   getItem_from_multipleDB("predictor_lipr_success","MemController0",id_attach_diff_lipr)
db_lipr_fail  =   getItem_from_multipleDB("predictor_lipr_fail","MemController0",id_attach_diff_lipr)
db_ropr_success  =   getItem_from_multipleDB("predictor_ropr_success","MemController0",id_attach_diff_lipr)
db_ropr_fail  =   getItem_from_multipleDB("predictor_ropr_fail","MemController0",id_attach_diff_lipr)

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

'''
db_success_above50  =   getItem_from_multipleDB("predicted_success_above50","MemController0",id_attache_rownum)
db_success_below50  =   getItem_from_multipleDB("predicted_success_below50","MemController0",id_attache_rownum)
db_fail_below50  =   getItem_from_multipleDB("predicted_fail_below50","MemController0",id_attache_rownum)
db_fail_above50  =   getItem_from_multipleDB("predicted_fail_above50","MemController0",id_attache_rownum)
db_sum=db_success_above50+db_success_below50+db_fail_above50+db_fail_below50
#db_sum=db_sum['metadata_predictor2']
#db_sum.drop(["mix4","mix5"],inplace=True)
db_success_rate = (db_success_below50+db_success_above50)/db_sum
print db_success_rate
my_plot=db_success_rate.plot(kind='bar')
my_plot.set_ylabel("Percentage")
#my_plot.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.3)
plt.savefig(report_dir+"/prediction_accuracy_rownum.pdf")

db_success_above50  =   getItem_from_multipleDB("predicted_success_above50","MemController0",id_attache_colnum)
db_success_below50  =   getItem_from_multipleDB("predicted_success_below50","MemController0",id_attache_colnum)
db_fail_below50  =   getItem_from_multipleDB("predicted_fail_below50","MemController0",id_attache_colnum)
db_fail_above50  =   getItem_from_multipleDB("predicted_fail_above50","MemController0",id_attache_colnum)
db_sum=db_success_above50+db_success_below50+db_fail_above50+db_fail_below50
#db_sum=db_sum['metadata_predictor2']
#db_sum.drop(["mix4","mix5"],inplace=True)
db_success_rate = (db_success_below50+db_success_above50)/db_sum
print db_success_rate
my_plot=db_success_rate.plot(kind='bar')
my_plot.set_ylabel("Percentage")
#my_plot.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.3)
plt.savefig(report_dir+"/prediction_accuracy_colnum.pdf")


db_success  =   getItem_from_multipleDB("predictor_global_success","MemController0",id_attache_colnum)
db_fail  =   getItem_from_multipleDB("predictor_global_fail","MemController0",id_attache_colnum)
db_sum=db_success+db_fail
db_success_rate=db_success/db_sum
my_plot=db_success_rate.plot(kind='bar')
plt.savefig(report_dir+"/prediction_accuracy_colnum_global_sucess_rate.pdf")
print "global predictor success rate"
print db_success_rate

db_hit  =   getItem_from_multipleDB("predictor_ropr_hit","MemController0",id_attache_rownum)
db_miss  =   getItem_from_multipleDB("predictor_ropr_miss","MemController0",id_attache_rownum)
db_sum=db_hit+db_miss
db_hit_rate=db_hit/db_sum
my_plot=db_success_rate.plot(kind='bar')
plt.savefig(report_dir+"/prediction_accuracy_colnum_global_ropr_hitrate.pdf")
print "global ropr hit rate"
print db_hit_rate
'''




'''
db_success_below50  =   getItem_from_multipleDB("predicted_success_below50","MemController0",id_tech)
db_success_above50  =   getItem_from_multipleDB("predicted_success_above50","MemController0",id_tech)
db_fail_below50  =   getItem_from_multipleDB("predicted_fail_below50","MemController0",id_tech)
db_fail_above50  =   getItem_from_multipleDB("predicted_fail_above50","MemController0",id_tech)

db_sum = db_success_below50 +db_success_above50+db_fail_below50+db_fail_above50
db_success_rate = (db_success_below50+db_success_above50)/db_sum
plt.savefig(report_dir+"/prediction_accuracy_old_predictor.pdf")

print db_success_below50
print db_success_above50
print db_fail_below50
print db_fail_above50
print db_success_rate
'''



def speedup():
    #IPC + Speedup
    db_cycles   =   mergeDB("cycles","prospero0",id_base,id_tech)
    db_tmp   = getItem_from_multipleDB("cycles","prospero0",id_metacache)
    db_cycles=db_cycles.merge(db_tmp,how='outer',left_index=True, right_index=True)
    db_tmp = getItem_from_multipleDB("cycles","prospero0",id_attache_rownum)
    db_cycles=db_cycles.merge(db_tmp,how='outer',left_index=True, right_index=True)
    db_tmp = getItem_from_multipleDB("cycles","prospero0",id_attache_colnum)
    db_cycles=db_cycles.merge(db_tmp,how='outer',left_index=True, right_index=True)
    db_tmp = getItem_from_multipleDB("cycles","prospero0",id_attache_global)
    db_cycles=db_cycles.merge(db_tmp,how='outer',left_index=True, right_index=True)



    #db_cycles=db_cycles.drop(["mix4","mix5"])
    db_randstream_cycles   =   mergeDB("simCycles","MemController0",[id_randstream_b], [id_randstream_t])
    db_tmp= getItem_from_multipleDB("simCycles","MemController0",[id_randstream_metacache])
    db_randstream_cycles=db_randstream_cycles.merge(db_tmp,how='outer',left_index=True, right_index=True)
    db_tmp = getItem_from_multipleDB("simCycles","MemController0",id_attache_rownum)
    db_randstream_cycles=db_randstream_cycles.merge(db_tmp,how='outer',left_index=True, right_index=True)
    db_tmp = getItem_from_multipleDB("simCycles","MemController0",id_attache_colnum)
    db_randstream_cycles=db_randstream_cycles.merge(db_tmp,how='outer',left_index=True, right_index=True)
    db_tmp = getItem_from_multipleDB("simCycles","MemController0",id_attache_global)
    db_randstream_cycles=db_randstream_cycles.merge(db_tmp,how='outer',left_index=True, right_index=True)

    db_cycles.loc["rand"] = db_randstream_cycles.loc["rand"]
    db_cycles.loc["seq"] = db_randstream_cycles.loc["seq"]
    #db_cycles.rename(columns={"seq":"stream"},inplace=True)

    db_ipc = total_inst/db_cycles
    base    =   db_ipc.iloc[:,0]
    #db_cycle_norm   =   db_cycles.div(base, axis=0)
    db_speedup      =   db_ipc.div(base,axis=0)
    mean            =   db_speedup.mean()
    db_speedup.loc['gmean']= np.power(db_speedup.prod(axis=0),1.0/len(db_speedup))
    print "\n ---- cycles -----"
    print db_cycles
    db_cycles.to_csv(report_dir+"/cycles-%s.csv"%(result_name))

    #db_cycles.plot.bar()
    #plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.3)
    #plt.savefig(report_dir+"/cycles-%s.pdf"%(result_name))

    print "\n ---- ipc -----"
    print db_ipc
    db_ipc.to_csv(report_dir+"/cycles-%s.csv"%(result_name))
    #db_ipc.plot.bar()
    #plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.3)
    #plt.savefig(report_dir+"/ipc-%s.pdf"%(result_name))


    print "\n ---- speedup ----"
    print db_speedup.iloc[:,0:8]
 #   db_speedup=db_speedup[["metacache_rownum2048","metacache_rownum4096","metacache_rownum8192","ropr_entry_num32768","ropr_col_num4","ropr_col_num16","metadata_predictor0"]]
  #  db_speedup.columns = ['MCache(256KB)','MCache(512KB)','MCache(1MB)','Attache.1CL(128KB)','Attache.4CL(512KB)','Attache.16CL(2MB)','Ideal']  #change column name
    db_speedup=db_speedup[["metacache_rownum2048","metacache_rownum4096","metacache_rownum8192","ropr_entry_num32768","ropr_col_num4","metadata_predictor0"]]
    db_speedup.columns = ['MCache(256KB)','MCache(512KB)','MCache(1MB)','Attache.1CL(128KB)','Attache.4CL(512KB)','Ideal']  #change column name

    db_speedup=db_speedup.loc[BENCHMARK_ALL,:]
    max_of_row=db_speedup.max(axis=1)
    print max_of_row
    db_speedup.loc[:,'Ideal']=max_of_row
 #   for i in range(0,len(db_speedup.columns)-1):
  #      if db_speedup.iloc[:i] > db_speedup.loc[:,'Ideal']:
   #         db_speedup.iloc[:i] = db_speedup.loc[:,'Ideal']

    print db_speedup
    #ax=db_speedup.plot.bar(figsize=(18, 6),cmap=plt.cm.binary,width=0.7,edgecolor='black')
    ax=db_speedup.plot.bar(figsize=(18, 6),cmap="summer",width=0.7,edgecolor='black')
    ax.grid(axis='y')
    ax.legend(loc=9, mode="expand",ncol=5,fontsize=14)
    plt.xticks(fontsize=15,rotation=75)
    plt.yticks(fontsize=15)
    plt.ylabel("Speedup",fontsize=15)

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.3)
    plt.ylim(ymax = 1.8, ymin = .5)

    plt.savefig(report_dir+"/speedup-%s.pdf"%(result_name))
    db_speedup.to_csv(report_dir+"/speedup-%s.csv"%(result_name))

#power
def power(power_type,do_print_norm,report_name):
    db_power  =   mergeDB(power_type,"Dimm0",id_base,id_tech)
    db_tmp   = getItem_from_multipleDB(power_type,"Dimm0",id_metacache)
    db_power=db_power.merge(db_tmp,how='outer',left_index=True, right_index=True)
    db_tmp = getItem_from_multipleDB(power_type,"Dimm0",id_attache_rownum)
    db_power=db_power.merge(db_tmp,how='outer',left_index=True, right_index=True)
    db_tmp = getItem_from_multipleDB(power_type,"Dimm0",id_attache_colnum)
    db_power=db_power.merge(db_tmp,how='outer',left_index=True, right_index=True)


    db_randstream_power   =   mergeDB(power_type,"Dimm0",[id_randstream_b], [id_randstream_t])
    db_tmp= getItem_from_multipleDB(power_type,"Dimm0",[id_randstream_metacache])
    db_randstream_power=db_randstream_power.merge(db_tmp,how='outer',left_index=True, right_index=True)
    db_tmp = getItem_from_multipleDB(power_type,"Dimm0",id_attache_rownum)
    db_randstream_power=db_randstream_power.merge(db_tmp,how='outer',left_index=True, right_index=True)
    db_tmp = getItem_from_multipleDB(power_type,"Dimm0",id_attache_colnum)
    db_randstream_power=db_randstream_power.merge(db_tmp,how='outer',left_index=True, right_index=True)
    
    db_power.loc["rand"] = db_randstream_power.loc["rand"]
    db_power.loc["seq"] = db_randstream_power.loc["seq"]
    #db_power.rename(columns={"seq":"stream"},inplace=True)

    print "\n ---- %s -----"%power_type
    base    =   db_power.iloc[:,0]
    #db_power= db_power.iloc[:,0:6]

    if do_print_norm == 1:
        db_power_norm = db_power.div(base,axis="index")
        db_power = db_power_norm
    
    db_power.loc['gmean']= geomean(db_power)
    db_power=db_power[["metacache_rownum2048","metacache_rownum4096","metacache_rownum8192","ropr_entry_num32768","ropr_col_num4","metadata_predictor0"]]
    db_power.columns = ['MCache(256KB)','MCache(512KB)','MCache(1MB)','Attache.1CL(128KB)','Attache.4CL(512KB)','Ideal']  #change column name
    db_power=db_power.loc[BENCHMARK_ALL,:]

    #max_of_row=db_power.m(axis=1)
    #print max_of_row
    #db_power.loc[:,'Ideal']=max_of_row
    print db_power
    db_power.to_csv(report_dir+"/%s-%s.csv"%(power_type,result_name))

    ax=db_power.plot.bar(figsize=(18, 6),cmap="summer",width=0.7,edgecolor='black')
    ax.grid(axis='y')
    ax.legend(loc=9, mode="expand",ncol=5,fontsize=14)
    plt.xticks(fontsize=15,rotation=75)
    plt.yticks(fontsize=15)
    if do_print_norm ==1:
        plt.ylabel("Normalized %s"%report_name,fontsize=15)
    else:
        plt.ylabel(report_name,fontsize=15)

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.3)
    #plt.ylim(ymax = 1.8, ymin = .5)

    plt.savefig(report_dir+"/%s-%s.pdf"%(power_type,result_name))


   # print db_power
   # db_power.to_csv(report_dir+"/power-%s.csv"%(result_name))

def report(power_type,do_print_norm,component,report_name):
    db_power  =   mergeDB(power_type,component,id_base,id_tech)
    db_tmp   = getItem_from_multipleDB(power_type,component,id_metacache)
    db_power=db_power.merge(db_tmp,how='outer',left_index=True, right_index=True)
    db_tmp = getItem_from_multipleDB(power_type,component,id_attache_rownum)
    db_power=db_power.merge(db_tmp,how='outer',left_index=True, right_index=True)
    db_tmp = getItem_from_multipleDB(power_type,component,id_attache_colnum)
    db_power=db_power.merge(db_tmp,how='outer',left_index=True, right_index=True)


    db_randstream_power   =   mergeDB(power_type,component,[id_randstream_b], [id_randstream_t])
    db_tmp= getItem_from_multipleDB(power_type,component,[id_randstream_metacache])
    db_randstream_power=db_randstream_power.merge(db_tmp,how='outer',left_index=True, right_index=True)
    db_tmp = getItem_from_multipleDB(power_type,component,id_attache_rownum)
    db_randstream_power=db_randstream_power.merge(db_tmp,how='outer',left_index=True, right_index=True)
    db_tmp = getItem_from_multipleDB(power_type,component,id_attache_colnum)
    db_randstream_power=db_randstream_power.merge(db_tmp,how='outer',left_index=True, right_index=True)
    
    db_power.loc["rand"] = db_randstream_power.loc["rand"]
    db_power.loc["seq"] = db_randstream_power.loc["seq"]
    #db_power.rename(columns={"seq":"stream"},inplace=True)

    print "\n ---- %s -----"%power_type
    base    =   db_power.iloc[:,0]
    #db_power= db_power.iloc[:,0:6]

    if do_print_norm == 1:
        db_power_norm = db_power.div(base,axis="index")
        db_power = db_power_norm
    
    db_power.loc['gmean']= geomean(db_power)
    db_power=db_power[["metacache_rownum2048","metacache_rownum4096","metacache_rownum8192","ropr_entry_num32768","ropr_col_num4","metadata_predictor0"]]
    db_power.columns = ['MCache(256KB)','MCache(512KB)','MCache(1MB)','Attache.1CL(128KB)','Attache.4CL(512KB)','Ideal']  #change column name
    db_power=db_power.loc[BENCHMARK_ALL,:]

    #max_of_row=db_power.m(axis=1)
    #print max_of_row
    #db_power.loc[:,'Ideal']=max_of_row
    print db_power
    db_power.to_csv(report_dir+"/%s-%s.csv"%(power_type,result_name))

    ax=db_power.plot.bar(figsize=(18, 6),cmap="summer",width=0.7,edgecolor='black')
    ax.grid(axis='y')
    ax.legend(loc=9, mode="expand",ncol=5,fontsize=14)
    plt.xticks(fontsize=15,rotation=75)
    plt.yticks(fontsize=15)
    if do_print_norm ==1:
        plt.ylabel("Normalized %s"%report_name,fontsize=15)
    else:
        plt.ylabel(report_name,fontsize=15)

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.3)
    #plt.ylim(ymax = 1.8, ymin = .5)

    plt.savefig(report_dir+"/%s-%s.pdf"%(power_type,result_name))



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
'''

#l3_mpki_missrate()
#mem_access()
#comp_ratio()
#report("totalTxnsRecvd",1,"MemController0","Transactions")
#report("actCmdsRecvd",1, "Dimm0","Active Commands")
#report("readCmdsRecvd", 1, "Dimm0","Read Commands")
#report("writeCmdsRecvd",1,"Dimm0","Write Commands")
#report("preCmdsRecvd",1,"Dimm0","Precharge Commands")
speedup()
#power("totalEnergy",1)
#power("actprePower",0)
#power("readPower",0)
#power("writePower",0)
#power("totalPower",0)


