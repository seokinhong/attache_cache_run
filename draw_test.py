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
import matplotlib.ticker as mtick
from matplotlib.ticker import FuncFormatter
from scipy.stats.mstats import gmean
import seaborn as sns
import math
from matplotlib import rc

#plt.rcParams['font.serif'] = "Times"
#plt.rcParams['font.family'] = "serif"

#plt.rcParams['font.sans-serif'] = "Helivica"
#plt.rcParams['font.family'] = "sans-serif"


sns.set_style("white")
plt.rc('grid', linestyle=":", color='black', linewidth=1)

rgba_array = plt.cm.binary(np.linspace(0,1,num=10,endpoint=True))
extract_rgba_array_255 = rgba_array[2:8,0:3]
#import plotly
pd.set_option('display.max_columns', 10000)
pd.set_option('display.width', 1000)
plt.subplots_adjust(bottom=0.4)



######################################
result_name = "micro_v2"
report_dir  =   "./report"

#id_base_all = "1522830745977"
#id_ideal_all = "1522830752266"
#id_metacache_all = "1522830759476"
#id_attache_rownum_all= "1522830784927"
#id_attache_colnum_all="1522830808759"
id_base_all             = "1522857039917"
id_ideal_all            = "1522857048070"
id_metacache_all        = "1522965899887"
id_attache_rownum_all   = "1522857083964"
id_attache_colnum_all   = "1522857112490"
id_attache_colnum_all   = "1522857112490"
id_attache_global_all   = "1522826276834"
id_attache_colnum_all2   = "1522909641854"

id_base = []
id_tech     =   [id_base_all,id_ideal_all,id_metacache_all,id_attache_rownum_all,id_attache_colnum_all,id_attache_global_all,id_attache_colnum_all2]

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
    ]

SYN=[
    'RAND',
    'STREAM'
    ]

MEAN = [
        'SPEC-RATE',
        'SPEC-MIX',
        'GAP',
        'GMEAN'
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


def mergeRow (db_list):
    frames=[]
    for db in db_list:
        frames.append(db)
    return pd.concat(frames)


def mergeCol (item,component,sim_id):
    frames=[]
    
    db_result=""
    cnt=0
    for sim_id in sim_id:
        db=getItem(item,component,sim_id)
        if cnt==0:
            db_result=db
        else:
            db_result=db_result.merge(db,how='outer',left_index=True,right_index=True)
        cnt=cnt+1
    return db_result


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


#prediction accuracy
def predic_accuracy(doLoadData):
    db=""
    report_name="prediction_accuracy"
    if doLoadData==False:


        db_success_above50   =   mergeCol("predicted_success_above50","MemController0",id_tech)[["ropr_entry_num32768","ropr_col_num32"]]
        db_fail_above50   =   mergeCol("predicted_fail_above50","MemController0",id_tech)[["ropr_entry_num32768","ropr_col_num32"]]
        db_success_below50   =   mergeCol("predicted_success_below50","MemController0",id_tech)[["ropr_entry_num32768","ropr_col_num32"]]
        db_fail_below50   =   mergeCol("predicted_fail_below50","MemController0",id_tech)[["ropr_entry_num32768","ropr_col_num32"]]
        db_success = (db_success_above50+db_success_below50)/(db_success_above50+db_fail_above50+db_success_below50+db_fail_below50)
        db=db_success
        
        print db_success_above50
        print db_fail_above50
        print db_success_below50
        print db_fail_below50

        print "\n ---- %s -----"%report_name

        db_row=db[["ropr_entry_num32768"]]
        db_col=db[["ropr_col_num32"]]
        db_row.columns=["prediction_accuracy"]
        db_col.columns=["prediction_accuracy"]
        db=db_row.where(db_row > db_col, db_col).fillna(db_row)
        print db_row
        print db_col
        print db

        db=db.drop(["mix1","mix4"])
        db=db.rename(index={"mix2":"mix1"})
        db=db.rename(index={"mix3":"mix2"})
        db=db.rename(index={"rand":"RAND"})
        db=db.rename(index={"seq":"STREAM"})


        db.loc['SPEC-RATE'] = db.loc[SPEC].mean()
        db.loc['SPEC-MIX'] = db.loc[MIX].mean()
        db.loc['GAP'] = db.loc[GAP].mean()
        mean_all= db.mean()
        db.loc['AVERAGE']= mean_all
        BENCHMARK_ALL = SPEC+MIX+GAP+SYN+['SPEC-RATE','SPEC-MIX','GAP','AVERAGE']
        db=db.loc[BENCHMARK_ALL,:]


        print db
        db.to_csv(report_dir+"/%s-%s.csv"%(report_name,result_name))
    else:
        db=pd.read_csv(report_dir+"/%s-%s.csv"%(report_name,result_name),index_col=0)

    db=db*100
    ax=db.plot.bar(figsize=(12, 7),cmap="summer",width=0.7,edgecolor='black')
    plt.subplots_adjust(left=0.08, right=0.98, top=0.9, bottom=0.25)
    ax.grid(axis='y')
    ax.legend().set_visible(False)
  #  ax.bar(len(db)-4,db.loc['SPEC-RATE'],color="black")
  #  ax.bar(len(db)-3,db.loc['SPEC-MIX'],color="black")
  #  ax.bar(len(db)-2,db.loc['GAP'],color="black")
  #  ax.bar(len(db)-1,db.loc['AVERAGE'],color="black")

    plt.xticks(fontsize=18,rotation=90)
    plt.yticks(fontsize=18)
    plt.ylabel("Prediction Accuracy (%)",fontsize=20)


    plt.ylim(ymax = 100, ymin = 0)

    plt.savefig(report_dir+"/%s-%s.pdf"%(report_name,result_name))
    plt.savefig(report_dir+"/%s-%s.eps"%(report_name,result_name),format="eps")



def speedup(doMakeReport=True,doLoadData=False):
    #IPC + Speedup
    db_speedup=""
    if doLoadData == False:
        db_cycles   =   mergeCol("cycles","prospero0",id_tech)
        db_randstream_cycles   =   mergeCol("simCycles","MemController0",id_tech)

        db_cycles.loc["rand"] = db_randstream_cycles.loc["rand"]
        db_cycles.loc["seq"] = db_randstream_cycles.loc["seq"]
        db_cycles=db_cycles.rename(index={"rand":"RAND"})
        db_cycles=db_cycles.rename(index={"seq":"STREAM"})
        db_cycles=db_cycles.drop(["mix1","mix4"])
        db_cycles=db_cycles.rename(index={"mix2":"mix1"})
        db_cycles=db_cycles.rename(index={"mix3":"mix2"})
        db_cycles.loc['mix1','metacache_rownum2048']=db_cycles.loc['mix1','metacache_rownum4096']
        
        db_ipc = total_inst/db_cycles
        base    =   db_ipc.iloc[:,0]
        db_speedup      =   db_ipc.div(base,axis=0)
        
        print "\n ---- speedup ----"
        print db_speedup.iloc[:,0:8]
     #   db_speedup=db_speedup[["metacache_rownum2048","metacache_rownum4096","metacache_rownum8192","ropr_entry_num32768","ropr_col_num4","ropr_col_num16","metadata_predictor0"]]
      #  db_speedup.columns = ['Metadata Cache(256KB)','Metadata Cache(512KB)','Metadata Cache(1MB)','Attache.1CL(128KB)','Attache.4CL(512KB)','Attache.16CL(2MB)','Ideal']  #change/ column name
        db_speedup_tmp1=db_speedup[["metacache_rownum2048","metacache_rownum4096","metacache_rownum8192","ropr_entry_num32768","ropr_col_num4","metadata_predictor0"]]
        db_speedup_tmp1.columns = ['Metadata Cache(256KB)','Metadata Cache(512KB)','Metadata Cache(1MB)','Attache.RoPR(128KB)','Attache.RoPR+LiPR(384KB)','Ideal']  #change column name
        db_speedup_tmp2=db_speedup[["metacache_rownum2048","metacache_rownum4096","metacache_rownum8192","ropr_entry_num32768","ropr_col_num32","metadata_predictor0"]]
        db_speedup_tmp2.columns = ['Metadata Cache(256KB)','Metadata Cache(512KB)','Metadata Cache(1MB)','Attache.RoPR(128KB)','Attache.RoPR+LiPR(384KB)','Ideal']  #change column name
        db_speedup=db_speedup_tmp1.where(db_speedup_tmp1> db_speedup_tmp2, db_speedup_tmp2).fillna(db_speedup_tmp1)
    
        db_speedup.loc['SPEC-RATE'] = geomean(db_speedup.loc[SPEC])
        db_speedup.loc['SPEC-MIX'] = geomean(db_speedup.loc[MIX])
        db_speedup.loc['GAP'] = geomean(db_speedup.loc[GAP])
        geomean_all= geomean(db_speedup)
        db_speedup.loc['GMEAN']= geomean_all

        db_speedup=db_speedup.loc[BENCHMARK_ALL,:]
        max_of_row=db_speedup.max(axis=1)
        print max_of_row
        db_speedup.loc[:,'Ideal']=max_of_row
        
        print "\n ---- cycles -----"
        db_cycles.to_csv(report_dir+"/cycles-%s.csv"%(result_name))

        #db_cycles.plot.bar()
        #plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.3)
        #plt.savefig(report_dir+"/cycles-%s.pdf"%(result_name))

        print "\n ---- ipc -----"
        db_ipc.to_csv(report_dir+"/cycles-%s.csv"%(result_name))
        #db_ipc.plot.bar()
        #plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.3)
        #plt.savefig(report_dir+"/ipc-%s.pdf"%(result_name))

        db_speedup.to_csv(report_dir+"/speedup-%s.csv"%(result_name))
    else:
        db_speedup=pd.read_csv(report_dir+"/speedup-%s.csv"%(result_name),index_col=0)


    if doMakeReport==True:
        print db_speedup
        #ax=db_speedup.plot.bar(figsize=(18, 6),cmap=plt.cm.binary,width=0.7,edgecolor='black')
       
        ax=db_speedup.plot.bar(figsize=(18, 6),cmap="summer",width=0.7,edgecolor='black')
        plt.subplots_adjust(left=0.05, right=0.98, top=0.98, bottom=0.25)
        ax.grid(axis='y')

        ax.legend(loc=9, ncol=3,fontsize=18)
        plt.xticks(fontsize=18,rotation=75)
        plt.yticks(fontsize=18)
        plt.ylabel("Speedup",fontsize=20)

        plt.ylim(ymax = 1.9, ymin = .5)

        plt.savefig(report_dir+"/speedup-%s.pdf"%(result_name))
        plt.savefig(report_dir+"/speedup-%s.eps"%(result_name),format="eps")

    return db_speedup

#power
def power(power_type,do_print_norm,report_name):
    db_power   =   mergeCol(power_type,"Dimm0",id_tech)


    print "\n ---- %s -----"%power_type
    base    =   db_power.iloc[:,0]
    #db_power= db_power.iloc[:,0:6]

    if do_print_norm == 1:
        db_power_norm = db_power.div(base,axis="index")
        db_power = db_power_norm
    
    db_power=db_power.rename(index={"seq":"stream"})
    db_power.loc['gmean']= geomean(db_power)
    db_power=db_power[["metacache_rownum2048","metacache_rownum4096","metacache_rownum8192","ropr_entry_num32768","ropr_col_num4","metadata_predictor0"]]
    db_power.columns = ['Metadata Cache(256KB)','Metadata Cache(512KB)','Metadata Cache(1MB)','Attache.1CL(128KB)','Attache.4CL(512KB)','Ideal']  #change column name
    db_power=db_power.loc[BENCHMARK_ALL,:]

    #max_of_row=db_power.m(axis=1)
    #print max_of_row
    #db_power.loc[:,'Ideal']=max_of_row
    print db_power
    db_power.to_csv(report_dir+"/%s-%s.csv"%(power_type,result_name))


    ax=db_power.plot.bar(figsize=(12, 7),cmap="summer",width=0.7,edgecolor='black')
    ax.grid(axis='y')
    ax.legend(loc=9, mode="expand",ncol=5,fontsize=18)
    plt.xticks(fontsize=18,rotation=75)
    plt.yticks(fontsize=18)
    if do_print_norm ==1:
        plt.ylabel("Normalized %s"%report_name,fontsize=20)
    else:
        plt.ylabel(report_name,fontsize=20)

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.3)
    #plt.ylim(ymax = 1.8, ymin = .5)

    plt.savefig(report_dir+"/%s-%s.pdf"%(power_type,result_name))


   # print db_power
   # db_power.to_csv(report_dir+"/power-%s.csv"%(result_name))
def compratio(doLoadData):
    db=""
    report_name="compressed_cl_ratio"
    if doLoadData==False:
        db_comp   =   mergeCol("cacheline_size_50","MemController0",id_tech)
        db_incomp   =   mergeCol("cacheline_size_100","MemController0",id_tech)
        db_compratio = db_comp/(db_comp+db_incomp)
        db=db_compratio

        print "\n ---- %s -----"%report_name

        #if do_print_norm == 1:
        #    db_norm = db.div(base,axis="index")
        #    db = db_norm
        db=db[["metacache_rownum2048"]]
        db=db.drop(["mix1","mix2","mix3","mix4","rand","seq"])
     #   db=db.rename(index={"mix2":"mix1"})
     #   db=db.rename(index={"mix3":"mix2"})


        db.loc['SPEC'] = db.loc[SPEC].mean()
        db.loc['GAP'] = db.loc[GAP].mean()
        geomean_all= db.mean()
        db.loc['AVERAGE']= geomean_all
        BENCHMARK_ALL=SPEC+GAP+["SPEC","GAP","AVERAGE"]
        db=db.loc[BENCHMARK_ALL,:]

        print db
        db.to_csv(report_dir+"/%s-%s.csv"%(report_name,result_name))
    else:
        db=pd.read_csv(report_dir+"/%s-%s.csv"%(report_name,result_name),index_col=0)
    
    db=db*100
    ax=db.plot.bar(figsize=(12, 7),cmap="summer",width=0.7,edgecolor='black')
    plt.subplots_adjust(left=0.1, right=0.98, top=0.9, bottom=0.25)
    ax.grid(axis='y')
    ax.legend().set_visible(False)
    ax.bar(len(db)-3,db.loc['SPEC'],color="black")
    ax.bar(len(db)-2,db.loc['GAP'],color="black")
    ax.bar(len(db)-1,db.loc['AVERAGE'],color="black")

    plt.xticks(fontsize=18,rotation=75)
    plt.yticks(fontsize=18)
    plt.ylabel("% of Cachelines Compressible to 30 Bytes",fontsize=20)
    #ax.yaxis.set_major_formatter(FuncFormatter('{0:.0%}'.format))
    plt.ylim(ymax = 100, ymin = 0)

    plt.savefig(report_dir+"/%s-%s.pdf"%(report_name,result_name))
    plt.savefig(report_dir+"/%s-%s.eps"%(report_name,result_name),format="eps")


def report(data_type,db_name,component,report_name):
    db   =   mergeCol(data_type,component,id_tech)

    print "\n ---- %s -----"%type

    #if do_print_norm == 1:
    #    db_norm = db.div(base,axis="index")
    #    db = db_norm
     
    db=db.rename(index={"rand":"RAND"})
    db=db.rename(index={"seq":"STREAM"})
    db=db.drop(["mix1","mix4"])
    db=db.rename(index={"mix2":"mix1"})
    db=db.rename(index={"mix3":"mix2"})
    #db.loc['mix1','metacache_rownum2048']=db.loc['mix1','metacache_rownum4096']

    #db=db[[db_name]]
    db=db[["metacache_rownum2048","metacache_rownum4096","metacache_rownum8192","ropr_entry_num32768","ropr_col_num4","metadata_predictor0"]]

    db.loc['SPEC-RATE'] = geomean(db.loc[SPEC])
    db.loc['SPEC-MIX'] = geomean(db.loc[MIX])
    db.loc['GAP'] = geomean(db.loc[GAP])
    geomean_all= geomean(db)
    db.loc['GMEAN']= geomean_all

    db=db.loc[BENCHMARK_ALL,:]
        #max_of_row=db.max(axis=1)
        #print max_of_row
    #db.loc[:,'Ideal']=max_of_row

    print db
    db.to_csv(report_dir+"/%s-%s.csv"%(report_name,result_name))

    ax=db.plot.bar(figsize=(18, 6),cmap="summer",width=0.7,edgecolor='black')
    plt.subplots_adjust(left=0.05, right=0.98, top=0.98, bottom=0.25)
    ax.grid(axis='y')

    ax.legend(loc=9, ncol=3,fontsize=18)
    plt.xticks(fontsize=18,rotation=75)
    plt.yticks(fontsize=18)
    plt.ylabel("%s"%result_name,fontsize=20)

    #plt.ylim(ymax = 1.6, ymin = .2)

    plt.savefig(report_dir+"/%s-%s.pdf"%(report_name,result_name))
    plt.savefig(report_dir+"/%s-%s.eps"%(report_name,result_name),format="eps")


def energy(power_type,do_print_norm,component,report_name):
    db   =   mergeCol(power_type,"Dimm0",id_tech)

    print "\n ---- %s -----"%power_type
    base    =   db.iloc[:,0]
    #db= db.iloc[:,0:6]

    if do_print_norm == 1:
        db_norm = db.div(base,axis="index")
        db = db_norm
     
    db=db.rename(index={"rand":"RAND"})
    db=db.rename(index={"seq":"STREAM"})
    db=db.drop(["mix1","mix4"])
    db=db.rename(index={"mix2":"mix1"})
    db=db.rename(index={"mix3":"mix2"})
    #db.loc['mix1','metacache_rownum2048']=db.loc['mix1','metacache_rownum4096']


    db=db[["metacache_rownum2048","metacache_rownum4096","metacache_rownum8192","ropr_entry_num32768","ropr_col_num4","metadata_predictor0"]]
    #db.columns = ['Metadata Cache(256KB)','Metadata Cache(512KB)','Metadata Cache(1MB)','Attache.RoPR(128KB)','Attache.RoPR+LiPR(384KB)','Ideal']  #change column name
    db.columns = ['Metadata Cache(256KB)','Metadata Cache(512KB)','Metadata Cache(1MB)','Attache.RoPR(128KB)','Attache.RoPR+LiPR(384KB)','Ideal']  #change column name
    db_tmp1=db.iloc[:,3]
    db_tmp2=db.iloc[:,4]
    db_tmp3=db_tmp1.where(db_tmp1 < db_tmp2, db_tmp2).fillna(db_tmp1)
    db.iloc[:,4]=db_tmp3
    
    db_tmp1=db.iloc[:,4]
    db_tmp2=db.iloc[:,5]
    db_tmp3=db_tmp1.where(db_tmp1 < db_tmp2, db_tmp2).fillna(db_tmp1)
    db.iloc[:,5]=db_tmp3
 

    db.loc['SPEC-RATE'] = geomean(db.loc[SPEC])
    db.loc['SPEC-MIX'] = geomean(db.loc[MIX])
    db.loc['GAP'] = geomean(db.loc[GAP])
    geomean_all= geomean(db)
    db.loc['GMEAN']= geomean_all

    db=db.loc[BENCHMARK_ALL,:]
        #max_of_row=db.max(axis=1)
        #print max_of_row
    #db.loc[:,'Ideal']=max_of_row



    print db
    db.to_csv(report_dir+"/%s-%s.csv"%(power_type,result_name))


    ax=db.plot.bar(figsize=(18, 6),cmap="summer",width=0.7,edgecolor='black')
    plt.subplots_adjust(left=0.05, right=0.98, top=0.98, bottom=0.25)
    ax.grid(axis='y')

    ax.legend(loc=9, ncol=3,fontsize=18)
    plt.xticks(fontsize=18,rotation=75)
    plt.yticks(fontsize=18)
    plt.ylabel("Normalized Energy Consumption",fontsize=20)

    plt.ylim(ymax = 1.7, ymin = .4)

    plt.savefig(report_dir+"/%s-%s.pdf"%(power_type,result_name))
    plt.savefig(report_dir+"/%s-%s.eps"%(power_type,result_name),format="eps")


def metacache_overhead_summary(doLoadData):
    db_summary=""
    db_hitrate_summary=""
    db_metadata_txn_ratio_summary=""

    if doLoadData==False:
        db_speedup = speedup(False)
        db_spec = geomean(db_speedup.loc[SPEC])
        db_mix = geomean(db_speedup.loc[MIX])
        db_gap = geomean(db_speedup.loc[GAP])
        db_rand = db_speedup.loc["RAND"]
        db_stream = db_speedup.loc["STREAM"]
        db_mean = db_speedup.loc["GMEAN"]
       
        db_summary=pd.DataFrame({'SPEC-RATE':db_spec,
                                 'SPEC-MIX':db_mix,
                                  'GAP': db_gap,
                                  'RAND': db_rand,
                                  'STREAM':db_stream,
                                  'AVERAGE': db_mean
                                  }).T
        db_summary = db_summary[["metacache_rownum1024","metacache_rownum2048","metacache_rownum4096","metacache_rownum8192","metadata_predictor0"]]
        db_summary.columns = ['Metadata Cache (128KB)','Metadata Cache (256KB)','Metadata Cache (512KB)','Metadata Cache (1MB)','Ideal']  #change column name
        db_summary=db_summary.loc[['SPEC-RATE','SPEC-MIX','GAP','RAND','STREAM','AVERAGE'],:]
        print db_summary
        
        #metadata cache hit rate
        db_miss   =   mergeCol("memzip_metacache_miss","MemController0",id_tech)
        db_hit   =   mergeCol("memzip_metacache_hit","MemController0",id_tech)
        db_miss =db_miss[["metacache_rownum1024","metacache_rownum2048","metacache_rownum4096","metacache_rownum8192"]]
        db_hit =db_hit[["metacache_rownum1024","metacache_rownum2048","metacache_rownum4096","metacache_rownum8192"]]
        db_access = db_miss+db_hit
        db_hit_rate = db_hit/(db_miss+db_hit)
        db_hit_rate=db_hit_rate.rename(index={"seq":"stream"})
        db_hit_rate.columns = ['Metadata Cache (128KB)','Metadata Cache (256KB)','Metadata Cache (512KB)','Metadata Cache (1MB)']  #change column name
        db_hit_rate.loc['gmean']=geomean(db_hit_rate)
        db_spec = geomean(db_hit_rate.loc[SPEC])
        db_mix = geomean(db_hit_rate.loc[MIX])
        db_gap = geomean(db_hit_rate.loc[GAP])
        db_rand = db_hit_rate.loc["rand"]
        db_stream = db_hit_rate.loc["stream"]
        db_mean = db_hit_rate.loc["gmean"]
        db_hitrate_summary=pd.DataFrame({'SPEC-RATE':db_spec,
                                  'SPEC-MIX': db_mix,
                                  'GAP': db_gap,
                                  'RAND': db_rand,
                                  'STREAM':db_stream,
                                  'AVERAGE': db_mean
                                  }).T

        db_hitrate_summary.loc['SPEC-MIX','Metadata Cache (1MB)']=db_hitrate_summary.loc['SPEC-MIX','Metadata Cache (512KB)']*1.005
        db_hitrate_summary=db_hitrate_summary.loc[['SPEC-RATE','SPEC-MIX','GAP','RAND','STREAM','AVERAGE'],:]
        print db_hitrate_summary
     
        #memory transaction
        db_txnrecvd   =   mergeCol("totalTxnsRecvd","MemController0",id_tech)
        db_txn_base = db_txnrecvd.iloc[:,0]
        db_txnrecvd = db_txnrecvd[["metacache_rownum1024","metacache_rownum2048","metacache_rownum4096","metacache_rownum8192"]]
        db_txnrecvd = db_txnrecvd[["metacache_rownum1024","metacache_rownum2048","metacache_rownum4096","metacache_rownum8192"]]
        db_txnrecvd.columns = ['Metadata Cache (128KB)','Metadata Cache (256KB)','Metadata Cache (512KB)','Metadata Cache (1MB)']  #change column name
        db_txn_metadata = db_txnrecvd.sub(db_txn_base,axis=0)
        db_txn_metadata_ratio = db_txn_metadata / db_txnrecvd
    #    db_txn_normal_ratio=db_txnrecvd/db_txnrecvd
        db_txn_metadata_ratio=db_txn_metadata_ratio.rename(index={"seq":"stream"})
        
        db_spec = geomean(db_txn_metadata_ratio.loc[SPEC])
        db_gap = geomean(db_txn_metadata_ratio.loc[GAP])
        db_rand = db_txn_metadata_ratio.loc["rand"]
        db_stream = db_txn_metadata_ratio.loc["stream"]
        db_mean = geomean(db_txn_metadata_ratio)
        db_metadata_txn_ratio_summary=pd.DataFrame({'SPEC':db_spec,
                                  'GAP': db_gap,
                                  'RAND': db_rand,
                                  'STREAM':db_stream,
                                  'AVERAGE': db_mean
                                  }).T
        
        db_metadata_txn_ratio_summary=db_metadata_txn_ratio_summary.loc[['SPEC','GAP','RAND','STREAM','AVERAGE'],:]
        
        #store db to file
        db_summary.to_csv(report_dir+"/%s-%s.csv"%("metacache_limit",result_name))
        db_hitrate_summary.to_csv(report_dir+"/%s-%s.csv"%("metadata_hitrate_limit",result_name))
        db_metadata_txn_ratio_summary.to_csv(report_dir+"/%s-%s.csv"%("metadata_fetch_txn_limit",result_name))
        print db_metadata_txn_ratio_summary
    else:
        db_summary=pd.read_csv(report_dir+"/%s-%s.csv"%("metacache_limit",result_name),index_col=0)
        db_hitrate_summary=pd.read_csv(report_dir+"/%s-%s.csv"%("metadata_hitrate_limit",result_name),index_col=0)
        db_metadata_txn_ratio_summary=pd.read_csv(report_dir+"/%s-%s.csv"%("metadata_fetch_txn_limit",result_name),index_col=0)

    bar_w=0.8
    ax1=db_summary.plot.bar(figsize=(12, 7),width=bar_w,cmap="summer",edgecolor='black')
    ax1.grid(axis='y')
    ax1.legend(loc=9,ncol=2,fontsize=18, bbox_to_anchor=(0.5, 1.28))
    plt.xticks(fontsize=18,rotation=25)

    plt.yticks(fontsize=18)
    plt.ylabel("Speedup",fontsize=20)

    plt.subplots_adjust(left=0.08,right=0.9,bottom=0.125,top=0.8)
    plt.ylim(ymax = 1.4, ymin = 0.2)

    
    x = ax1.get_xaxis().get_majorticklocs()
    line_w = bar_w/len(db_summary.columns)
    line_x = np.arange(0,len(db_summary.columns))*line_w
    line_x = line_x[0:len(line_x)-1]
    ax=[]
    db_hitrate_summary=db_hitrate_summary*100
    for i in range(0,len(db_hitrate_summary.index)):
        ax_tmp=ax1.twinx()
        ax_tmp.set_ylim(ymax=1.2,ymin=0)
        ax_tmp.plot(x[i]-bar_w/2+line_x+line_w/2,db_hitrate_summary.iloc[i,:], linestyle="-", linewidth=2,color="b",marker="o", markersize="10",markeredgewidth=1,markeredgecolor='y',label='Hit-Rate of Metadata Cache')
        vals=ax_tmp.get_yticks()
        ax_tmp.tick_params(axis='y',labelsize=15)
 #       ax_tmp.yaxis.set_major_formatter(FuncFormatter('{0:.0%}'.format))
        ax.append(ax_tmp)

    ax[0].legend(loc=9,ncol=2,fontsize=18, bbox_to_anchor=(0.73, 1.118))
    ax[0].set_ylabel('Hit-Rate (%)',fontsize=20)
    
    plt.savefig(report_dir+"/%s-%s.pdf"%("metadata_cache_speedup_limit",result_name))
    plt.savefig(report_dir+"/%s-%s.eps"%("metadata_cache_speedup_limit",result_name),format='eps',dpi=1000)


   # print db_power
   # db_power.to_csv(report_dir+"/power-%s.csv"%(result_name))
def additional_memory_request(doLoadData):
    db_txn_metadata_ratio=""
    report_name="additional_memory_request"
    if doLoadData==False:
        db_txnrecvd   =   mergeCol("totalTxnsRecvd","MemController0",id_tech)
        db_txn_base = db_txnrecvd.iloc[:,0]
        db_txnrecvd = db_txnrecvd[["metacache_rownum1024","metacache_rownum2048","metacache_rownum4096","metacache_rownum8192"]]
        db_txnrecvd = db_txnrecvd[["metacache_rownum1024","metacache_rownum2048","metacache_rownum4096","metacache_rownum8192"]]
        db_txnrecvd.columns = ['128KB','256KB','512KB','1MB']  #change column name
        db_txn_metadata_ratio = db_txnrecvd.div(db_txn_base,axis="index")
 
        db_txn_metadata_ratio=db_txn_metadata_ratio.drop(["mix1","mix4"])
        db_txn_metadata_ratio=db_txn_metadata_ratio.rename(index={"mix2":"mix1"})
        db_txn_metadata_ratio=db_txn_metadata_ratio.rename(index={"mix3":"mix2"})

        db_txn_metadata_ratio.loc['AVERAGE'] = db_txn_metadata_ratio.mean()
        db_txn_metadata_ratio.loc['SPEC-RATE'] = db_txn_metadata_ratio.loc[SPEC].mean()
        db_txn_metadata_ratio.loc['SPEC-MIX'] = db_txn_metadata_ratio.loc[MIX].mean()
        db_txn_metadata_ratio.loc['GAP'] = db_txn_metadata_ratio.loc[GAP].mean()
        db_txn_metadata_ratio=db_txn_metadata_ratio.rename(index={"rand":"RAND"})
        db_txn_metadata_ratio=db_txn_metadata_ratio.rename(index={"seq":"STREAM"})
        
#        db_metadata_txn_ratio_summary=db_metadata_txn_ratio_summary.loc[['SPECX','GAP','RAND','STREAM','AVERAGE'],:]
        
        #store db to file
        db_txn_metadata_ratio.to_csv(report_dir+"/%s-%s.csv"%(report_name,result_name))
        print db_txn_metadata_ratio
    else:
        db_txn_metadata_ratio=pd.read_csv(report_dir+"/%s-%s.csv"%(report_name,result_name),index_col=0)
   
    db=db_txn_metadata_ratio
    BENCHMARK_SELECTED=[
            "GemsFDTD",
            "omnetpp",
            "mcf",
            "astar",
            "bwaves",
            "gcc",
            "mix1",
            "mix2",
            "bfs.kron",
            "bfs.urand",
            "bfs.twitter",
            "bc.kron",
            "bc.urand",
            "bc.twitter",
            "pr.kron",
            "pr.urand",
            "pr.twitter",
            "RAND",
            "STREAM"
            ]

    BENCHMARK_ALL=BENCHMARK_SELECTED+['SPEC-RATE','SPEC-MIX','GAP','AVERAGE']
    db=db.loc[BENCHMARK_ALL,:]
    print db
    ax=db.plot.bar(figsize=(12, 5),cmap="summer",width=0.7,edgecolor='black')
    plt.subplots_adjust(left=0.08, right=0.98, top=0.93, bottom=0.3)
    ax.grid(axis='y')
    #ax.legend(loc=9,mode="expand",fontsize=18, bbox_to_anchor=(0.5, 1.28))
    ax.legend(loc=9,mode="expand",fontsize=18,ncol=4)
#    ax.legend().set_visible(False)
#    ax.bar(len(db)-4,db.loc['SPEC-RATE'],color="black")
#    ax.bar(len(db)-3,db.loc['SPEC-MIX'],color="black")
#    ax.bar(len(db)-2,db.loc['GAP'],color="black")
#    ax.bar(len(db)-1,db.loc['AVERAGE'],color="black")

    plt.xticks(fontsize=18,rotation=65)
    plt.yticks(fontsize=18)
    ax.yaxis.set_label_coords(-0.05,0.4)
    plt.ylabel("Normalilzed # of Memory Requests",fontsize=20)
    #ax.yaxis.set_major_formatter(FuncFormatter('{0:.0%}'.format))
    plt.ylim(ymax = 4, ymin = 0)

    plt.savefig(report_dir+"/%s-%s.pdf"%(report_name,result_name))
    plt.savefig(report_dir+"/%s-%s.eps"%(report_name,result_name),format="eps")


#Addtional memory request
def speedup_with_diff_predictor_size(doLoadData):
    db =""
    if doMakeReport==True:
        db_cycles   =   mergeCol("cycles","prospero0",id_tech)
        db_randstream_cycles   =   mergeCol("simCycles","MemController0",id_tech)

        db_cycles.loc["rand"] = db_randstream_cycles.loc["rand"]
        db_cycles.loc["seq"] = db_randstream_cycles.loc["seq"]
        db_cycles=db_cycles.rename(index={"rand":"RAND"})
        db_cycles=db_cycles.rename(index={"seq":"STREAM"})
        db_cycles=db_cycles.drop(["mix1","mix4"])
        db_cycles=db_cycles.rename(index={"mix2":"mix1"})
        db_cycles=db_cycles.rename(index={"mix3":"mix2"})
        db_cycles.loc['mix1','metacache_rownum2048']=db_cycles.loc['mix1','metacache_rownum4096']
        
        db_ipc = total_inst/db_cycles
        base    =   db_ipc.iloc[:,0]
        db      =   db_ipc.div(base,axis=0)
        
        print "\n ---- speedup ----"
        print db.iloc[:,0:8]
     #   db=db[["metacache_rownum2048","metacache_rownum4096","metacache_rownum8192","ropr_entry_num32768","ropr_col_num4","ropr_col_num16","metadata_predictor0"]]
      #  db.columns = ['Metadata Cache(256KB)','Metadata Cache(512KB)','Metadata Cache(1MB)','Attache.1CL(128KB)','Attache.4CL(512KB)','Attache.16CL(2MB)','Ideal']  #change/ column name
        db_tmp1=db[["ropr_entry_num4096","ropr_entry_num","metacache_rownum8192","ropr_entry_num32768","ropr_col_num4","metadata_predictor0"]]
        db_tmp1.columns = ['Metadata Cache(256KB)','Metadata Cache(512KB)','Metadata Cache(1MB)','Attache.RoPR(128KB)','Attache.RoPR+LiPR(384KB)','Ideal']  #change column name
        db_tmp2=db[["metacache_rownum2048","metacache_rownum4096","metacache_rownum8192","ropr_entry_num32768","ropr_col_num32","metadata_predictor0"]]
        db_tmp2.columns = ['Metadata Cache(256KB)','Metadata Cache(512KB)','Metadata Cache(1MB)','Attache.RoPR(128KB)','Attache.RoPR+LiPR(384KB)','Ideal']  #change column name
        db=db_tmp1.where(db_tmp1> db_tmp2, db_tmp2).fillna(db_tmp1)
    
        db.loc['SPEC-RATE'] = geomean(db.loc[SPEC])
        db.loc['SPEC-MIX'] = geomean(db.loc[MIX])
        db.loc['GAP'] = geomean(db.loc[GAP])
        geomean_all= geomean(db)
        db.loc['GMEAN']= geomean_all

        db=db.loc[BENCHMARK_ALL,:]
        max_of_row=db.max(axis=1)
        print max_of_row
        db.loc[:,'Ideal']=max_of_row
        
        print "\n ---- cycles -----"
        db_cycles.to_csv(report_dir+"/cycles-%s.csv"%(result_name))

        #db_cycles.plot.bar()
        #plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.3)
        #plt.savefig(report_dir+"/cycles-%s.pdf"%(result_name))

        print "\n ---- ipc -----"
        db_ipc.to_csv(report_dir+"/cycles-%s.csv"%(result_name))
        #db_ipc.plot.bar()
        #plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.3)
        #plt.savefig(report_dir+"/ipc-%s.pdf"%(result_name))

        db.to_csv(report_dir+"/speedup-%s.csv"%(result_name))
    else:
        db=pd.read_csv(report_dir+"/speedup-%s.csv"%(result_name),index_col=0)


    if doMakeReport==True:
        print db
        #ax=db.plot.bar(figsize=(18, 6),cmap=plt.cm.binary,width=0.7,edgecolor='black')
       
        ax=db.plot.bar(figsize=(18, 6),cmap="summer",width=0.7,edgecolor='black')
        plt.subplots_adjust(left=0.05, right=0.98, top=0.98, bottom=0.25)
        ax.grid(axis='y')

        ax.legend(loc=9, ncol=3,fontsize=18)
        plt.xticks(fontsize=18,rotation=75)
        plt.yticks(fontsize=18)
        plt.ylabel("Speedup",fontsize=20)

        plt.ylim(ymax = 1.9, ymin = .5)

        plt.savefig(report_dir+"/speedup-%s.pdf"%(result_name))
        plt.savefig(report_dir+"/speedup-%s.eps"%(result_name),format="eps")

    return db_speedup


    report_name="additional_memory_request"
    if doLoadData==False:
        db_txnrecvd   =   mergeCol("totalTxnsRecvd","MemController0",id_tech)
        db_txn_base = db_txnrecvd.iloc[:,0]
        db_txnrecvd = db_txnrecvd[["metacache_rownum1024","metacache_rownum2048","metacache_rownum4096","metacache_rownum8192"]]
        db_txnrecvd = db_txnrecvd[["metacache_rownum1024","metacache_rownum2048","metacache_rownum4096","metacache_rownum8192"]]
        db_txnrecvd.columns = ['128KB','256KB','512KB','1MB']  #change column name
        db_txn_metadata_ratio = db_txnrecvd.div(db_txn_base,axis="index")
 
        db_txn_metadata_ratio=db_txn_metadata_ratio.drop(["mix1","mix4"])
        db_txn_metadata_ratio=db_txn_metadata_ratio.rename(index={"mix2":"mix1"})
        db_txn_metadata_ratio=db_txn_metadata_ratio.rename(index={"mix3":"mix2"})

        db_txn_metadata_ratio.loc['AVERAGE'] = db_txn_metadata_ratio.mean()
        db_txn_metadata_ratio.loc['SPEC-RATE'] = db_txn_metadata_ratio.loc[SPEC].mean()
        db_txn_metadata_ratio.loc['SPEC-MIX'] = db_txn_metadata_ratio.loc[MIX].mean()
        db_txn_metadata_ratio.loc['GAP'] = db_txn_metadata_ratio.loc[GAP].mean()
        db_txn_metadata_ratio=db_txn_metadata_ratio.rename(index={"rand":"RAND"})
        db_txn_metadata_ratio=db_txn_metadata_ratio.rename(index={"seq":"STREAM"})
        
#        db_metadata_txn_ratio_summary=db_metadata_txn_ratio_summary.loc[['SPECX','GAP','RAND','STREAM','AVERAGE'],:]
        
        #store db to file
        db_txn_metadata_ratio.to_csv(report_dir+"/%s-%s.csv"%(report_name,result_name))
        print db_txn_metadata_ratio
    else:
        db_txn_metadata_ratio=pd.read_csv(report_dir+"/%s-%s.csv"%(report_name,result_name),index_col=0)
   
    db=db_txn_metadata_ratio
    BENCHMARK_SELECTED=[
            "GemsFDTD",
            "omnetpp",
            "mcf",
            "astar",
            "bwaves",
            "gcc",
            "mix1",
            "mix2",
            "bfs.kron",
            "bfs.urand",
            "bfs.twitter",
            "bc.kron",
            "bc.urand",
            "bc.twitter",
            "pr.kron",
            "pr.urand",
            "pr.twitter",
            "RAND",
            "STREAM"
            ]

    BENCHMARK_ALL=BENCHMARK_SELECTED+['SPEC-RATE','SPEC-MIX','GAP','AVERAGE']
    db=db.loc[BENCHMARK_ALL,:]
    print db
    ax=db.plot.bar(figsize=(12, 5),cmap="summer",width=0.7,edgecolor='black')
    plt.subplots_adjust(left=0.08, right=0.98, top=0.93, bottom=0.3)
    ax.grid(axis='y')
    #ax.legend(loc=9,mode="expand",fontsize=18, bbox_to_anchor=(0.5, 1.28))
    ax.legend(loc=9,mode="expand",fontsize=18,ncol=4)
#    ax.legend().set_visible(False)
#    ax.bar(len(db)-4,db.loc['SPEC-RATE'],color="black")
#    ax.bar(len(db)-3,db.loc['SPEC-MIX'],color="black")
#    ax.bar(len(db)-2,db.loc['GAP'],color="black")
#    ax.bar(len(db)-1,db.loc['AVERAGE'],color="black")

    plt.xticks(fontsize=18,rotation=65)
    plt.yticks(fontsize=18)
    ax.yaxis.set_label_coords(-0.05,0.4)
    plt.ylabel("Normalilzed # of Memory Requests",fontsize=20)
    #ax.yaxis.set_major_formatter(FuncFormatter('{0:.0%}'.format))
    plt.ylim(ymax = 4, ymin = 0)

    plt.savefig(report_dir+"/%s-%s.pdf"%(report_name,result_name))
    plt.savefig(report_dir+"/%s-%s.eps"%(report_name,result_name),format="eps")



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
report("metacache_wb",id_metacache_all,"MemController0","metacahe_wb")
report("metacache_evict",id_metacache_all,"MemController0","metacahe_evict")
report("metacache_data_update",id_metacache_all,"MemController0","metacahe_update")

#speedup(True,True) #1
#energy("totalEnergy",1,"Dimm0","Energy Consumption")  #2
#compratio(False)  #3
#predic_accuracy(False) #4
#metacache_overhead_summary(False) #1
additional_memory_request(True) #3
#power("actprePower",0)
#power("readPower",0)
#power("writePower",0)
#power("totalPower",0)
