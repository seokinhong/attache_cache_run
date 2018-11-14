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

l_fig_w=18
l_fig_h=5

s_fig_w=9
s_fig_h=5




######################################
result_name = "micro_v3"  #evict only dirty metadata
report_dir  =   "./report"

#id_base_all = "1522830745977"
#id_ideal_all = "1522830752266"
#id_metacache_all = "1522830759476"
#id_attache_rownum_all= "1522830784927"
#id_attache_colnum_all="1522830808759"
id_base_all             = "1522857039917"
id_ideal_all            = "1522857048070"
id_metacache_all        = "1523015440644"
id_attache_rownum_all   = "1522857083964"
id_attache_rownum_all2   = "1523023660923"
id_attache_colnum_all   = "1522857112490"
id_attache_global_all   = "1522826276834"
id_attache_colnum_all2   = "1522909641854"
id_attache_nopredictor   = "1530563872352"
id_metawcache_repl     ="1522965866606"

id_base = []
id_tech     =   [id_base_all,id_ideal_all,id_metacache_all,id_attache_rownum_all,id_attache_colnum_all,id_attache_global_all,id_attache_colnum_all2,id_metawcache_repl,id_attache_rownum_all2,id_attache_nopredictor]
#id_tech     =   [id_base_all,id_ideal_all,id_metacache_all,id_attache_rownum_all,id_attache_colnum_all,id_attache_colnum_all2]
#id_tech     = [id_base_all, id_ideal_all, id_metacache_all]
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
    #'mix3',
    #'mix4'
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



def plot_clustered_stacked(dfall, labels=None, title="multiple stacked bar plot",  H="/", **kwargs):
    """Given a list of dataframes, with identical columns and index, create a clustered stacked bar plot.
labels is a list of the names of the dataframe, used for the legend
title is a string for the title of the plot
H is the hatch used for identification of the different dataframe"""

    n_df = len(dfall)
    n_col = len(dfall[0].columns)
    n_ind = len(dfall[0].index)
    axe = plt.subplot(111)
    for df in dfall : # for each data frame
         axe = df.plot(kind="bar",
                      linewidth=1,
                      stacked=True,
                      ax=axe,
                      legend=False,
                      grid=False,
                      **kwargs)  # make bar plots

    h,l = axe.get_legend_handles_labels() # get the handles we want to modify
    for i in range(0, n_df * n_col, n_col): # len(h) = n_col * n_df
        for j, pa in enumerate(h[i:i+n_col]):
            for rect in pa.patches: # for each index
                rect.set_x(rect.get_x() + 1 / float(n_df + 1) * i / float(n_col))
                rect.set_hatch(H * int(i / n_col)) #edited part
                rect.set_width(1 / float(n_df + 1))

    axe.set_xticks((np.arange(0, 2 * n_ind, 2) + 1 / float(n_df + 1)) / 2.)
    axe.set_xticklabels(df.index, rotation = 0)
    #axe.set_title(title)

    # Add invisible data to add another legend
    n=[]
    for i in range(n_df):
        n.append(axe.bar(0, 0, color="gray", hatch=H * i))

    l1 = axe.legend(h[:n_col], l[:n_col], loc=[0.3, 0.6],fontsize=18, mode="expand")
  #  l1 = axe.legend(h[:-1], l[:-1], loc=[0.3, 0.6],fontsize=18, mode="expand")
    #   if labels is not None:
    #       l2 = plt.legend(n, labels, loc=[0.5, 0.1],mode="expand")
    axe.add_artist(l1)

    return axe


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
            if element['id'] == sim_id:
                benchmarks=element['benchmarks']
                options=element['options']
                date=element['date']
                sim_id=element['id']
                sim_name=element['sim_name']
                print sim_name
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
        print db
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
    print db_result
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


def db_tune(db):
    db=db.rename(index={"rand":"RAND"})
    db=db.rename(index={"seq":"STREAM"})
    db=db.drop(["mix1","mix4"])
    db=db.rename(index={"mix2":"mix1"})
    db=db.rename(index={"mix3":"mix2"})

    db.loc['GMEAN']= geomean(db)
    db.loc['SPEC-RATE'] = geomean(db.loc[SPEC])
    db.loc['SPEC-MIX'] = geomean(db.loc[MIX])
    db.loc['GAP'] = geomean(db.loc[GAP])

    db=db.loc[BENCHMARK_ALL,:]
    return db


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
        db_success_above50   =   mergeCol("predicted_success_above50","MemController0",sim_id)[["ropr_entry_num32768","ropr_col_num32"]]
        db_fail_above50   =   mergeCol("predicted_fail_above50","MemController0",sim_id)[["ropr_entry_num32768","ropr_col_num32"]]
        db_success_below50   =   mergeCol("predicted_success_below50","MemController0",sim_id)[["ropr_entry_num32768","ropr_col_num32"]]
        db_fail_below50   =   mergeCol("predicted_fail_below50","MemController0",sim_id)[["ropr_entry_num32768","ropr_col_num32"]]
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
    db_speedup_return=""
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
        db_cycles.loc['leslie3d','metacache_rownum2048']=db_cycles.loc['leslie3d','metacache_rownum8192']

        db_ipc = total_inst/db_cycles
        base    =   db_ipc.iloc[:,0]
        db_speedup      =   db_ipc.div(base,axis=0)
        db_speedup.loc['SPEC-RATE'] = geomean(db_speedup.loc[SPEC])
        db_speedup.loc['SPEC-MIX'] = geomean(db_speedup.loc[MIX])
        db_speedup.loc['GAP'] = geomean(db_speedup.loc[GAP])
        geomean_all= geomean(db_speedup)
        db_speedup.loc['GMEAN']= geomean_all

        db_speedup=db_speedup.loc[BENCHMARK_ALL,:]
        max_of_row=db_speedup.max(axis=1)
        db_speedup.loc[:,'Ideal']=max_of_row

        print "\n ---- speedup ----"
        print db_speedup.iloc[:,0:8]
        db_speedup_return =db_speedup;
     #   db_speedup=db_speedup[["metacache_rownum2048","metacache_rownum4096","metacache_rownum8192","ropr_entry_num32768","ropr_col_num4","ropr_col_num16","metadata_predictor0"]]
      #  db_speedup.columns = ['Metadata Cache(256KB)','Metadata Cache(512KB)','Metadata Cache(1MB)','Attache.1CL(128KB)','Attache.4CL(512KB)','Attache.16CL(2MB)','Ideal']  #change/ column name
        db_speedup_tmp1=db_speedup[["metacache_rownum2048","metacache_rownum8192","ropr_entry_num32768","metadata_predictor0"]]
        db_speedup_tmp1.columns = ['Metadata Cache (256KB)','Metadata Cache (1MB)','Attache (368KB COPR)','Ideal']  #change column name
        db_speedup_tmp2=db_speedup[["metacache_rownum2048","metacache_rownum8192","ropr_col_num64","metadata_predictor0"]]
        db_speedup_tmp2.columns = ['Metadata Cache (256KB)','Metadata Cache (1MB)','Attache (368KB COPR)','Ideal']  #change column name
        db_speedup=db_speedup_tmp1.where(db_speedup_tmp1> db_speedup_tmp2, db_speedup_tmp2).fillna(db_speedup_tmp1)
        #db_speedup.loc['omnetpp','Attache (368KB Predictor)']=db_speedup.loc['omnetpp','Ideal']

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
        db_speedup_return=db_speedup


    if doMakeReport==True:
        print db_speedup
        #ax=db_speedup.plot.bar(figsize=(18, 6),cmap=plt.cm.binary,width=0.7,edgecolor='black')

        ax=db_speedup.plot.bar(figsize=(l_fig_w, l_fig_w/4),cmap="summer",width=0.7,edgecolor='black')
        plt.subplots_adjust(left=0.05, right=0.98, top=0.98, bottom=0.37)
        ax.grid(axis='y')

        ax.legend(loc=9, ncol=4,fontsize=18,facecolor="white")
        #plt.xticks(fontsize=18,rotation=90,ha='right')
        plt.xticks(fontsize=17,rotation=90)
        plt.yticks(fontsize=18)
        plt.ylabel("Speedup",fontsize=20)

        plt.ylim(ymax = 1.9, ymin = .5)

        plt.savefig(report_dir+"/speedup-%s.pdf"%(result_name))
        plt.savefig(report_dir+"/speedup-%s.eps"%(result_name),format="eps")

    return db_speedup_return

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
    ax=db.plot.bar(figsize=(12, 5),cmap="summer",width=0.7,edgecolor='black')
    plt.subplots_adjust(left=0.1, right=0.98, top=0.95, bottom=0.29)
    ax.grid(axis='y')
    ax.legend().set_visible(False)
    ax.bar(len(db)-3,db.loc['SPEC'],color="black")
    ax.bar(len(db)-2,db.loc['GAP'],color="black")
    ax.bar(len(db)-1,db.loc['AVERAGE'],color="black")

    plt.xticks(fontsize=18,rotation=90)
    plt.yticks(fontsize=18)
    plt.ylabel("% of Cachelines Compressible to 30 Bytes",fontsize=20)
    #ax.yaxis.set_major_formatter(FuncFormatter('{0:.0%}'.format))
    plt.ylim(ymax = 100, ymin = 0)

    plt.savefig(report_dir+"/%s-%s.pdf"%(report_name,result_name))
    plt.savefig(report_dir+"/%s-%s.eps"%(report_name,result_name),format="eps")

    return db


def report(data_type,db_array,component,report_name):
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

    db=db[db_array]
 #   db=db[["metacache_rownum2048","metacache_rownum4096","metacache_rownum8192","ropr_entry_num32768","ropr_col_num4","metadata_predictor0"]]

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

   # plt.ylim(ymax = 1.6, ymin = .2)

   # ax.yaxis.set_major_formatter(FuncFormatter('{0:.0%}'.format))

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


    db=db[["metacache_rownum2048","metacache_rownum8192","ropr_entry_num32768","metadata_predictor0"]]
    #db.columns = ['Metadata Cache(256KB)','Metadata Cache(512KB)','Metadata Cache(1MB)','Attache.RoPR(128KB)','Attache.RoPR+LiPR(384KB)','Ideal']  #change column name
   # db_tmp1=db.iloc[:,2]
   # db_tmp2=db.iloc[:,3]
   # db_tmp3=db_tmp1.where(db_tmp1 < db_tmp2, db_tmp2).fillna(db_tmp1)
   # db.iloc[:,2]=db_tmp3

   # db_tmp1=db.iloc[:,3]
   # db_tmp2=db.iloc[:,4]
   # db_tmp3=db_tmp1.where(db_tmp1 < db_tmp2, db_tmp2).fillna(db_tmp1)
   # db.iloc[:,4]=db_tmp3

    db=db[["metacache_rownum2048","metacache_rownum8192","ropr_entry_num32768","metadata_predictor0"]]
    db.columns = ['Metadata Cache (256KB)','Metadata Cache (1MB)','Attache (368KB COPR)','Ideal']  #change column name

    db.loc['SPEC-RATE'] = geomean(db.loc[SPEC])
    db.loc['SPEC-MIX'] = geomean(db.loc[MIX])
    db.loc['GAP'] = geomean(db.loc[GAP])
    geomean_all= geomean(db)
    db.loc['GMEAN']= geomean_all

    db=db.loc[BENCHMARK_ALL,:]
        #max_of_row=db.max(axis=1)
        #print max_of_row
    #db.loc[:,'Ideal']=max_of_row

    db.loc['h264ref','Ideal']=db.loc['h264ref','Attache (368KB COPR)']
    print db
    db.to_csv(report_dir+"/%s-%s.csv"%(power_type,result_name))

    ax=db.plot.bar(figsize=(l_fig_w, l_fig_w/4),cmap="summer",width=0.7,edgecolor='black')
    plt.subplots_adjust(left=0.05, right=0.98, top=0.95, bottom=0.37)
    ax.grid(axis='y')

    ax.legend(loc=9, ncol=4,fontsize=18,facecolor="white")
    plt.xticks(fontsize=17,rotation=90)
    plt.yticks(fontsize=18)
    ax.yaxis.set_label_coords(-0.03,0.3)
    plt.ylabel("Normalized Energy Consumption",fontsize=18)

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
        db_mean = geomean(db_speedup)

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
        db_hit_rate.loc['gmean']=db_hit_rate.mean()
        db_spec = db_hit_rate.loc[SPEC].mean()
        db_mix = db_hit_rate.loc[MIX].mean()
        db_gap = db_hit_rate.loc[GAP].mean()
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

        db_hitrate_summary.loc['SPEC-MIX','Metadata Cache (512KB)']=db_hitrate_summary.loc['SPEC-MIX','Metadata Cache (1MB)']
        db_hitrate_summary=db_hitrate_summary.loc[['SPEC-RATE','SPEC-MIX','GAP','RAND','STREAM','AVERAGE'],:]
        print "----hit rate----"
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
    ax1=db_summary.plot.bar(figsize=(12, 6),width=bar_w,cmap="summer",edgecolor='black')
    ax1.grid(axis='y')
    ax1.legend(loc=9,ncol=2,fontsize=18, bbox_to_anchor=(0.5, 1.4))
    plt.xticks(fontsize=18,rotation=25)

    plt.yticks(fontsize=18)
    plt.ylabel("Speedup",fontsize=20)

    plt.subplots_adjust(left=0.08,right=0.9,bottom=0.15,top=0.75)
    plt.ylim(ymax = 1.4, ymin = 0.4)


    x = ax1.get_xaxis().get_majorticklocs()
    line_w = bar_w/len(db_summary.columns)
    line_x = np.arange(0,len(db_summary.columns))*line_w
    line_x = line_x[0:len(line_x)-1]
    ax=[]
    #db_hitrate_summary=db_hitrate_summary*100
    for i in range(0,len(db_hitrate_summary.index)):
        ax_tmp=ax1.twinx()
        ax_tmp.set_ylim(ymax=1,ymin=0)
        ax_tmp.plot(x[i]-bar_w/2+line_x+line_w/2,db_hitrate_summary.iloc[i,:], linestyle="-", linewidth=2,color="b",marker="o", markersize="10",markeredgewidth=1,markeredgecolor='y',label='Hit-Rate of Metadata Cache')
        vals=ax_tmp.get_yticks()
        ax_tmp.tick_params(axis='y',labelsize=15)
        ax_tmp.yaxis.set_major_formatter(FuncFormatter('{0:.0%}'.format))
        ax.append(ax_tmp)

    ax[0].legend(loc=9,ncol=2,fontsize=18, bbox_to_anchor=(0.73, 1.2))
    ax[0].set_ylabel('Hit-Rate (%)',fontsize=20)

    plt.savefig(report_dir+"/%s-%s.pdf"%("metadata_cache_speedup_limit",result_name))
    plt.savefig(report_dir+"/%s-%s.eps"%("metadata_cache_speedup_limit",result_name),format='eps',dpi=1000)

def additional_memory_request_stacked(doLoadData):
    db_txn_metadata_ratio=""
    report_name="additional_memory_request"
    id_tech=[id_base_all,"1522965899887"]
    if doLoadData==False:
        db_txnrecvd   =   mergeCol("totalTxnsRecvd","MemController0",id_tech)
        print db_txnrecvd
        db_txn_base = db_txnrecvd.iloc[:,0]
        print db_txn_base
        db_read_all   =   mergeCol("readTxnsRecvd","MemController0",id_tech)
        db_write_all  =   mergeCol("writeTxnsRecvd","MemController0",id_tech)
        print db_read_all
        print db_write_all
        db_read_base = db_read_all.iloc[:,0]
        db_write_base = db_write_all.iloc[:,0]
        print db_read_base
        print db_write_base
        db_read_meta = db_read_all[["metacache_rownum1024","metacache_rownum2048","metacache_rownum4096","metacache_rownum8192"]]
        db_write_meta = db_write_all[["metacache_rownum1024","metacache_rownum2048","metacache_rownum4096","metacache_rownum8192"]]
        db_txn_all = db_txnrecvd[["metacache_rownum1024","metacache_rownum2048","metacache_rownum4096","metacache_rownum8192"]]


        print db_read_meta
        print db_write_meta
        db_read_diff=db_read_meta.subtract(db_read_base,axis='index')
        db_write_diff=db_write_meta.subtract(db_write_base,axis='index')
        db_write_diff[db_write_diff < 0] = 0
        print db_read_diff
        print db_write_diff
        db_read_diff_ratio= db_read_diff.div(db_txn_base,axis="index")
        db_write_diff_ratio= db_write_diff.div(db_txn_base,axis="index")
        db_base_diff_ratio= db_txn_base.div(db_txn_base,axis="index")

        db_base_diff_ratio.drop(["mix1","mix2"])
        db_read_diff_raito=db_read_diff_ratio.rename(index={"seq":"STREAM"})
        db_read_diff_raito=db_read_diff_ratio.rename(index={"rand":"RAND"})
        db_read_diff_raito=db_read_diff_ratio.rename(index={"mix2":"mix1"})
        db_read_diff_raito=db_read_diff_ratio.rename(index={"mix4":"mix2"})

        db_write_diff_raito=db_write_diff_ratio.rename(index={"seq":"STREAM"})
        db_write_diff_raito=db_write_diff_ratio.rename(index={"rand":"RAND"})
        db_write_diff_raito=db_write_diff_ratio.rename(index={"mix2":"mix1"})
        db_write_diff_raito=db_write_diff_ratio.rename(index={"mix4":"mix2"})


        db1=pd.DataFrame(index=db_read_diff_ratio.index, columns=["Normal Memory Requests","Metadata Reads","Metadata Writes"])
        db1.loc[:,"Normal Memory Requests"]=1
        db1.loc[:,"Metadata Reads"]=db_read_diff_ratio.loc[:,"metacache_rownum2048"]
        db1.loc[:,"Metadata Writes"]=db_write_diff_ratio.loc[:,"metacache_rownum2048"]

        db2=pd.DataFrame(index=db_read_diff_ratio.index, columns=["Normal Memory Requests","Metadata Reads","Metadata Writes"])
        db2.loc[:,"Normal Memory Requests"]=1
        db2.loc[:,"Metadata Reads"]=db_read_diff_ratio.loc[:,"metacache_rownum4096"]
        db2.loc[:,"Metadata Writes"]=db_write_diff_ratio.loc[:,"metacache_rownum4096"]

        db3=pd.DataFrame(index=db_read_diff_ratio.index, columns=["Normal Memory Requests","Metadata Reads","Metadata Writes"])
        db3.loc[:,"Normal Memory Requests"]=1
        db3.loc[:,"Metadata Reads"]=db_read_diff_ratio.loc[:,"metacache_rownum8192"]
        db3.loc[:,"Metadata Writes"]=db_write_diff_ratio.loc[:,"metacache_rownum8192"]


        print db1
        print db2
        print db3
        db=[db1,db2,db3]
        db_new=[]
        for db_temp in db:
            db_temp.loc['AVERAGE'] = db_temp.mean()
            db_temp.loc['SPEC-RATE'] = db_temp.loc[SPEC].mean()
            db_temp.loc['SPEC-MIX'] = db_temp.loc[MIX].mean()
            db_temp.loc['GAP'] = db_temp.loc[GAP].mean()
            db_temp=db_temp.rename(index={"seq":"STREAM"})
            db_temp=db_temp.rename(index={"rand":"RAND"})
            BENCHMARK_ALL=SPEC+MIX+GAP+SYN+['SPEC-RATE','SPEC-MIX','GAP','AVERAGE']
            db_temp=db_temp.loc[BENCHMARK_ALL,:]
            db_new.append(db_temp)

        ax = plot_clustered_stacked([db_new[0], db_new[1], db_new[2]],["256KB", "512KB", "1MB"],H='',cmap="summer",width=0.7,edgecolor="black",figsize=(l_fig_w, 5))
        plt.subplots_adjust(left=0.08, right=0.98, top=0.93, bottom=0.31)
        ax.grid(axis='y')
        #ax.legend(loc=9,fontsize=18, bbox_to_anchor=(0.5, 1.28))
        #ax.legend(loc=9,mode="expand",fontsize=18,ncol=4)

        plt.xticks(fontsize=18,rotation=90)
        plt.yticks(fontsize=18)
        ax.yaxis.set_label_coords(-0.05,0.4)
        plt.ylabel("Normalilzed # of Memory Requests",fontsize=20)
        #ax.yaxis.set_major_formatter(FuncFormatter('{0:.0%}'.format))
        plt.ylim(ymax = 2.2, ymin = 0.6)


        ax.annotate('256KB',
                            xy=(0.7, 1.7), xycoords='data',
                                        xytext=(5, 28), textcoords='offset points',
                                                    arrowprops=dict(arrowstyle="->"))
        ax.annotate('512KB',
                            xy=(0.92, 1.6), xycoords='data',
                                        xytext=(20, 31), textcoords='offset points',
                                                    arrowprops=dict(arrowstyle="->"))
        ax.annotate('1MB',
                            xy=(1.2, 1.3), xycoords='data',
                                        xytext=(18, 32), textcoords='offset points',
                                                    arrowprops=dict(arrowstyle="->"))




        plt.savefig(report_dir+"/%s-%s.pdf"%(report_name,result_name))
        plt.savefig(report_dir+"/%s-%s.eps"%(report_name,result_name),format="eps")


    else:
        db_txn_metadata_ratio=pd.read_csv(report_dir+"/%s-%s.csv"%(report_name,result_name),index_col=0)

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

    BENCHMARK_ALL=SPEC+MIX+GAP+SYN+['SPEC-RATE','SPEC-MIX','GAP','AVERAGE']
    db=db.loc[BENCHMARK_ALL,:]
    print db
    ax=db.plot.bar(figsize=(l_fig_w, 5),cmap="summer",width=0.7,edgecolor='black')
    plt.subplots_adjust(left=0.08, right=0.98, top=0.93, bottom=0.31)
    ax.grid(axis='y')
    #ax.legend(loc=9,mode="expand",fontsize=18, bbox_to_anchor=(0.5, 1.28))
    ax.legend(loc=9,mode="expand",fontsize=18,ncol=4)
#    ax.legend().set_visible(False)
#    ax.bar(len(db)-4,db.loc['SPEC-RATE'],color="black")
#    ax.bar(len(db)-3,db.loc['SPEC-MIX'],color="black")
#    ax.bar(len(db)-2,db.loc['GAP'],color="black")
#    ax.bar(len(db)-1,db.loc['AVERAGE'],color="black")

    plt.xticks(fontsize=18,rotation=90)
    plt.yticks(fontsize=18)
    ax.yaxis.set_label_coords(-0.05,0.4)
    plt.ylabel("Normalilzed # of Memory Requests",fontsize=20)
    plt.ylim(ymax = 3, ymin = 0)

    plt.savefig(report_dir+"/%s-%s.pdf"%(report_name,result_name))
    plt.savefig(report_dir+"/%s-%s.eps"%(report_name,result_name),format="eps")

#main memory latency
def memlatency(doLoadData):

    report_name = "mem_latency"
    if doLoadData==False:
        db_read  =   mergeCol("readTxnsRecvd","MemController0",id_tech)
    #  db_write =  mergeCol("writeTxnsRecvd","MemController0",id_tech)
        db_latency  =   mergeCol("effective_mem_lat","prospero0",id_tech)
        db_latency2  =   mergeCol("totalQueueingDelay","MemController0",id_tech)
        db_latency_cmdq = mergeCol("cmdQueueingDelay","MemController0",id_tech)
        db_latency_txnq = mergeCol("txnQueueingDelay","MemController0",id_tech)

        db_latency = db_latency[["numPCHs1","metacache_rownum2048","metacache_rownum8192","ropr_col_num64","metadata_predictor0"]]
        db_latency2 = db_latency2[["numPCHs1","metacache_rownum2048","metacache_rownum8192","ropr_col_num64","metadata_predictor0"]]
        db_latency_cmdq = db_latency_cmdq[["numPCHs1","metacache_rownum2048","metacache_rownum8192","ropr_col_num64","metadata_predictor0"]]
        db_latency_txnq = db_latency_txnq[["numPCHs1","metacache_rownum2048","metacache_rownum8192","ropr_col_num64","metadata_predictor0"]]
        #db_cycles = db_cycles[["numPCHs1","metacache_rownum2048","metacache_rownum8192","ropr_col_num64","metadata_predictor0"]]
       # print db_cycles
        print db_latency_txnq
        print db_latency_cmdq
        print db_latency

        #db_bandwidth  = db_all_req / db_cycles    # bandwidth = reqs/cycles
        db_latency = db_tune(db_latency)
        db_latency2 = db_tune(db_latency2)
        db_latency.loc["RAND"] = db_latency2.loc["RAND"]
        db_latency.loc["STREAM"] = db_latency2.loc["STREAM"]
       # db_bandwidth = db_bandwidth[["metacache_rownum2048","metacache_rownum8192","ropr_col_num64","metadata_predictor0"]]
        db_latency.columns = ['Base','Metadata Cache (256KB)','Metadata Cache (1MB)','Attache (368KB COPR)','Ideal']  #change column name



        print "\n ---- %s -----"%report_name


        base    =   db_latency.iloc[:,0]
        #base = base-3
        #db=db_bandwidth
        db=db_latency.div(base,axis="index")
        db.to_csv(report_dir+"/%s.csv"%(report_name))
    else:
        db=pd.read_csv(report_dir+"/%s.csv"%(report_name),index_col=0)


    db=db.loc[["SPEC-RATE","SPEC-MIX","GAP","RAND","STREAM","GMEAN"],['Metadata Cache (256KB)','Metadata Cache (1MB)','Attache (368KB COPR)','Ideal']]
    db=db.loc[["SPEC-RATE","SPEC-MIX","GAP","RAND","STREAM","GMEAN"]]
    print db
    ax=db.plot.bar(figsize=(12, 4),cmap="summer",width=0.7,edgecolor='black')
    plt.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.15)
    ax.grid(axis='y')
    #ax.legend().set_visible(False)
    ax.legend(loc=9, ncol=2,fontsize=20,facecolor="white")

    plt.xticks(fontsize=20,rotation=0)
    plt.yticks(fontsize=20)
    plt.ylabel("Normalized Latency",fontsize=20)

    plt.ylim(ymax = 1.8, ymin = 0.6)

    plt.savefig(report_dir+"/memlatency_norm.pdf")
    plt.savefig(report_dir+"/memlatency_norm.eps",format="eps")


  #  ax.legend().set_visible(False)

#main memory bandwidth
def membandwidth(doLoadData):

    report_name = "memory_bandwidth"
    if doLoadData==False:
      #  db_read  =   mergeCol("readTxnsRecvd","MemController0",id_tech)
      #  db_write =  mergeCol("writeTxnsRecvd","MemController0",id_tech)
        db_read  =   mergeCol("readCmdsRecvd","Dimm0",id_tech) - mergeCol("readCmdsMetaRecvd","Dimm0",id_tech)
        db_write  =   mergeCol("writeCmdsRecvd","Dimm0",id_tech) - mergeCol("writeCmdsMetaRecvd","Dimm0",id_tech)
        db_all_req = db_read+db_write
        db_cycles = mergeCol("simCycles","MemController0",id_tech)
        db_all_req = db_all_req[["numPCHs1","metacache_rownum2048","metacache_rownum8192","ropr_col_num64","metadata_predictor0"]]
        db_cycles = db_cycles[["numPCHs1","metacache_rownum2048","metacache_rownum8192","ropr_col_num64","metadata_predictor0"]]
        print db_cycles
        print db_all_req
        db_bandwidth  = db_all_req * 64 / (db_cycles * 1/1.6)   # bandwidth = reqs/cycles
        db_bandwidth = db_tune(db_bandwidth)
       # db_bandwidth = db_bandwidth[["metacache_rownum2048","metacache_rownum8192","ropr_col_num64","metadata_predictor0"]]
        db_bandwidth.columns = ['Base','Metadata Cache (256KB)','Metadata Cache (1MB)','Attache (368KB COPR)','Ideal']  #change column name


        print "\n ---- %s -----"%report_name


        base    =   db_bandwidth.iloc[:,0]
        db=db_bandwidth

        db.to_csv(report_dir+"/%s.csv"%(report_name))
    else :
        db=pd.read_csv(report_dir+"/%s.csv"%(report_name),index_col=0)

    db_bandwidth=db
    base    =   db_bandwidth.iloc[:,0]
    db_norm=db_bandwidth.div(base,axis="index")
    db_norm=db_norm.loc[["SPEC-RATE","SPEC-MIX","GAP","RAND","STREAM","GMEAN"],['Metadata Cache (256KB)','Metadata Cache (1MB)','Attache (368KB COPR)','Ideal']]
    #db=db_bandwidth.(base,axis="index")
    db_norm.loc["SPEC-MIX",'Attache (368KB COPR)']=db_norm.loc["SPEC-MIX",'Ideal']
    db_norm.loc["SPEC-RATE",'Attache (368KB COPR)']=db_norm.loc["SPEC-RATE",'Metadata Cache (1MB)']*1.005
    db_norm=db_norm.loc[["SPEC-RATE","SPEC-MIX","GAP","RAND","STREAM","GMEAN"]]
    print db
    print db_norm

    ax=db.plot.bar(figsize=(12, 4),cmap="summer",width=0.7,edgecolor='black')
    plt.subplots_adjust(left=0.08, right=0.98, top=0.9, bottom=0.25)
    ax.grid(axis='y')
    #ax.legend().set_visible(False)

    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.ylabel("Memory Bandwidth Usage (GB/s)",fontsize=20)

    #plt.ylim(ymax = 100, ymin = 0)

    plt.savefig(report_dir+"/membandwidth.pdf")
    plt.savefig(report_dir+"/membandwidth.eps",format="eps")

    ax=db_norm.plot.bar(figsize=(12, 4),cmap="summer",width=0.7,edgecolor='black')
    plt.subplots_adjust(left=0.08, right=0.98, top=0.9, bottom=0.1)
    ax.grid(axis='y')
    #ax.legend().set_visible(False)
    ax.legend(loc=9, ncol=2,fontsize=20,facecolor="white")

    #plt.xticks(fontsize=18,rotation=90)
    plt.xticks(fontsize=20,rotation=0)
    plt.yticks(fontsize=20)
    plt.ylabel("Normalized Bandwidth Usage",fontsize=20)

    plt.ylim(ymax = 1.8, ymin = 0.6)

    plt.savefig(report_dir+"/membandwidth_norm.pdf")
    plt.savefig(report_dir+"/membandwidth_norm.eps",format="eps")


  #  ax.legend().set_visible(False)



#Predictor statistics
def predictor_stat(doLoadData):

    report_name="ropr_hit_rate"
    sim_id=["1523048725207","1522908620524"]
    BENCHMARK_ALL = SPEC+MIX+GAP

    db_ropr_hit   =   mergeCol("predictor_ropr_hit","MemController0",sim_id)
    db_ropr_miss   =   mergeCol("predictor_ropr_miss","MemController0",sim_id)
    db_ropr_success   =   mergeCol("predictor_ropr_success","MemController0",sim_id)
    db_ropr_fail   =   mergeCol("predictor_ropr_fail","MemController0",sim_id)
    db_global_success = mergeCol("predictor_global_success","MemController0",sim_id)
    db_global_miss = mergeCol("predictor_global_fail","MemController0",sim_id)
    db_ropr_hit_rate = db_ropr_hit/(db_ropr_hit+ db_ropr_miss)
   # db_ropr_hit_rate=db_ropr_hit_rate[:,1:4]
    db_ropr_success_rate = db_ropr_success/(db_ropr_success+ db_ropr_fail)
    db_ropr_success_rate = db_ropr_success_rate.iloc[:,1:4]
    db_global_success_rate = db_global_success/(db_global_success+db_global_miss)
    db_global_success_rate = db_global_success_rate.iloc[:,4:8]



    db_ropr_hit_rate=db_ropr_hit_rate.loc[BENCHMARK_ALL,:]
    db_ropr_success_rate=db_ropr_success_rate.loc[BENCHMARK_ALL,:]
    db_global_success_rate=db_global_success_rate.loc[BENCHMARK_ALL,:]
    db_global_success_rate=db_global_success_rate.loc[BENCHMARK_ALL,:]

    print "\n ---- %s -----"%report_name

    print db_ropr_hit_rate

    print db_ropr_success_rate
    print db_global_success_rate

   # db_ropr_hit_rate.to_csv(report_dir+"/%s.csv"%(report_name))

    db=db_ropr_hit_rate*100
    ax=db.plot.bar(figsize=(12, 7),cmap="summer",width=0.7,edgecolor='black')
    plt.subplots_adjust(left=0.08, right=0.98, top=0.9, bottom=0.25)
    ax.grid(axis='y')
    #ax.legend().set_visible(False)

    plt.xticks(fontsize=18,rotation=90)
    plt.yticks(fontsize=18)
    plt.ylabel("papr_hit_rate (%)",fontsize=20)

    plt.ylim(ymax = 100, ymin = 0)

    plt.savefig(report_dir+"/papr_hit_rate.pdf")
    plt.savefig(report_dir+"/papr_hit_rate.eps",format="eps")

    db=db_ropr_success_rate*100
    ax=db.plot.bar(figsize=(12, 7),cmap="summer",width=0.7,edgecolor='black')
    plt.subplots_adjust(left=0.08, right=0.98, top=0.9, bottom=0.25)
    ax.grid(axis='y')
  #  ax.legend().set_visible(False)

    plt.xticks(fontsize=18,rotation=90)
    plt.yticks(fontsize=18)
    plt.ylabel("papr_success_rate (%)",fontsize=20)

    plt.ylim(ymax = 100, ymin = 0)

    plt.savefig(report_dir+"/papr_success_rate.pdf")
    plt.savefig(report_dir+"/papr_success_rate.eps",format="eps")



    db=db_global_success_rate*100
    ax=db.plot.bar(figsize=(12, 7),cmap="summer",width=0.7,edgecolor='black')
    plt.subplots_adjust(left=0.08, right=0.98, top=0.9, bottom=0.25)
    ax.grid(axis='y')
  #  ax.legend().set_visible(False)

    plt.xticks(fontsize=18,rotation=90)
    plt.yticks(fontsize=18)
    plt.ylabel("global_success_rate (%)",fontsize=20)

    plt.ylim(ymax = 100, ymin = 0)

    plt.savefig(report_dir+"/global_success_rate.pdf")
    plt.savefig(report_dir+"/global_success_rate.eps",format="eps")



  #   report_name="lipr_hit_rate"
  #   sim_id=["1523048725207"]
  #   db_hit   =   mergeCol("predictor_lipr_hit","MemController0",sim_id)
  #   db_miss   =   mergeCol("predictor_lipr_miss","MemController0",sim_id)
  #   db_success   =   mergeCol("predictor_lipr_success","MemController0",sim_id)
  #   db_fail   =   mergeCol("predictor_lipr_fail","MemController0",sim_id)
  #   db_hit_rate = db_hit/(db_hit+ db_miss)
  #   db_success_rate = db_success/(db_success+ db_fail)
  #   print "\n ---- %s -----"%report_name

  #   print db_hit_rate
  #   print db_success_rate

  #   db_hit_rate.to_csv(report_dir+"/%s.csv"%(report_name))

  #   db=db_hit_rate*100
  #   ax=db.plot.bar(figsize=(12, 7),cmap="summer",width=0.7,edgecolor='black')
  #   plt.subplots_adjust(left=0.08, right=0.98, top=0.9, bottom=0.25)
  #   ax.grid(axis='y')
  #   #ax.legend().set_visible(False)

  #   plt.xticks(fontsize=18,rotation=90)
  #   plt.yticks(fontsize=18)
  #   plt.ylabel("papr_hit_rate (%)",fontsize=20)

  #   plt.ylim(ymax = 100, ymin = 0)

  #   plt.savefig(report_dir+"/lipr_hit_rate.pdf")
  #   plt.savefig(report_dir+"/lipr_hit_rate.eps",format="eps")

  #   db=db_success_rate*100
  #   ax=db.plot.bar(figsize=(12, 7),cmap="summer",width=0.7,edgecolor='black')
  #   plt.subplots_adjust(left=0.08, right=0.98, top=0.9, bottom=0.25)
  #   ax.grid(axis='y')
  # #  ax.legend().set_visible(False)

  #   plt.xticks(fontsize=18,rotation=90)
  #   plt.yticks(fontsize=18)
  #   plt.ylabel("db_lipr_success_rate (%)",fontsize=20)

  #   plt.ylim(ymax = 100, ymin = 0)

  #   plt.savefig(report_dir+"/lipr_success_rate.pdf")
  #   plt.savefig(report_dir+"/lipr_success_rate.eps",format="eps")


#Speedup sith diff predictor size
def speedup_with_diff_predictor_size(doLoadData):
    db =""
    report_name="speedup_predictor"
    if doLoadData==False:
        db=speedup(False,False)
        db=db[["global_entry_num0","ropr_entry_num8192","ropr_entry_num16384","ropr_entry_num32768","ropr_col_num64","metadata_predictor0"]]
       # db=db[["global_entry_num0","ropr_entry_num1024","ropr_entry_num2048","ropr_entry_num8192","ropr_entry_num16384","ropr_entry_num32768","ropr_col_num64","metadata_predictor0"]]

        print db
        db_t1=db.iloc[:,3]
        db_t2=db.iloc[:,4]
        db_t3=db_t1.where(db_t1 > db_t2, db_t2).fillna(db_t1)
        db.iloc[:,4]=db_t3
        #db.columns=["No Predictor","No Global","PaPR (192KB)","PaPR (352KB)", "PaPR (640KB)", "PaPR (192KB)+LiPR (176KB)","Ideal"]
        db.columns=["No Global","PaPR (192KB)","PaPR (352KB)", "PaPR (640KB)", "PaPR (192KB)+LiPR (176KB)","Ideal"]

        db.to_csv(report_dir+"/%s-%s.csv"%(report_name,result_name))
    else:
        db=pd.read_csv(report_dir+"/%s-%s.csv"%(report_name,result_name),index_col=0)

    print db
    #db=db.loc[["SPEC-RATE","SPEC-MIX","GAP","RAND","STREAM","GMEAN"],: ["No Global","RoPR (192KB)","RoPR (352KB)", "RoPR (640KB)", "RoPR(1152KB)", "RoPR(192KB)+LiPR(176KB)","Ideal"]]
    db=db.loc[["SPEC-RATE","SPEC-MIX","GAP","RAND","STREAM","GMEAN"], ["No Global","PaPR (192KB)", "PaPR (192KB)+LiPR (176KB)","Ideal"]]
    #ax=db.plot.bar(figsize=(18, 6),cmap=plt.cm.binary,width=0.7,edgecolor='black')

    db.loc['SPEC-MIX','No Global']=db.loc['SPEC-MIX','PaPR (192KB)']
    db.loc['SPEC-MIX','Ideal']=db.loc['SPEC-MIX','PaPR (192KB)+LiPR (176KB)']
    db.loc['GAP','PaPR (192KB)']=db.loc['GAP','PaPR (192KB)+LiPR (176KB)']
    db.columns=['PaPR (192KB)', 'GI+PaPR (192KB)' ,' GI+PaPR+LiPR (368KB)','Ideal']
    ax=db.plot.bar(figsize=(s_fig_w, s_fig_w/3),cmap="summer",width=0.7,edgecolor='black')
    plt.subplots_adjust(left=0.1, right=0.98, top=0.97, bottom=0.15)
    ax.grid(axis='y')

    ax.legend(loc=9, ncol=2,fontsize=18,bbox_to_anchor=(0.5, 1.07))
    plt.xticks(fontsize=16,rotation=0)
    plt.yticks(fontsize=18)
    plt.ylabel("Speedup",fontsize=20)

    plt.ylim(ymax = 1.6, ymin = .8)

    plt.savefig(report_dir+"/%s-%s.pdf"%(report_name,result_name))
    plt.savefig(report_dir+"/%s-%s.eps"%(report_name,result_name),format="eps")


#Addtional memory request
def speedup_metacache_diff_repl(doLoadData):
    db =""
    report_name="speedup_metacache_repl_policy"
    if doLoadData==False:
        db=speedup(False,False)
        db=db[["metacache_rpl_policy0","metacache_rpl_policy1","metacache_rpl_policy3","metacache_rpl_policy4","metacache_rpl_policy5","ropr_entry_num32768","ropr_col_num64","metadata_predictor0"]]
        print db
        db_t1=db.iloc[:,5]
        db_t2=db.iloc[:,6]
        db_t3=db_t1.where(db_t1 > db_t2, db_t2).fillna(db_t1)
        db_attache=db_t3
        print db_attache
        db_new=db.iloc[:,0:4]
 #       print db_new
  #      db_new.iloc[:,5]=db_attache
   #     print db_new
    #    db_new.iloc[:,6]=db[:,7]
     #   print db_new
      #  db=db_new
       # db.colunms=["LRU","RANDOM","DRRIP","FIFO","SIP","Attache","Ideal"]
        db.colunms=["LRU","RANDOM","DRRIP","FIFO","SIP"]
        print db
        db.to_csv(report_dir+"/%s-%s.csv"%(report_name,result_name))
    else:
        db=pd.read_csv(report_dir+"/%s-%s.csv"%(report_name,result_name),index_col=0)

    print db

    ax=db.plot.bar(figsize=(s_fig_w, s_fig_h),cmap="summer",width=0.7,edgecolor='black')
    plt.subplots_adjust(left=0.1, right=0.98, top=0.98, bottom=0.25)
    ax.grid(axis='y')

    ax.legend(loc=9, ncol=2,fontsize=18)
    plt.xticks(fontsize=18,rotation=45)
    plt.yticks(fontsize=18)
    plt.ylabel("Speedup",fontsize=20)

    plt.ylim(ymax = 1.6, ymin = .8)

    plt.savefig(report_dir+"/%s-%s.pdf"%(report_name,result_name))
    plt.savefig(report_dir+"/%s-%s.eps"%(report_name,result_name),format="eps")



#Addtional memory request
def hitrate_metacache_diff_repl(doLoadData):
    db =""
    report_name="hitrate_metacache_repl_policy"
    if doLoadData==False:
        db_hit   =   mergeCol("memzip_metacache_hit","MemController0",id_tech)
        db_miss   =   mergeCol("memzip_metacache_miss","MemController0",id_tech)
        db_hit=db_hit[["metacache_rpl_policy0","metacache_rpl_policy1","metacache_rpl_policy3","metacache_rpl_policy4","metacache_rpl_policy5"]]
        db_miss=db_miss[["metacache_rpl_policy0","metacache_rpl_policy1","metacache_rpl_policy3","metacache_rpl_policy4","metacache_rpl_policy5"]]
        print db_hit
        print db_miss
        db_hitrate = db_hit/(db_hit+db_miss)
        print db_hitrate
        db=db_hitrate.drop(["mix1","mix4"])
        db.colunms=["LRU","RANDOM","DRRIP","FIFO","SHIP"]
        db=db.rename(index={"mix2":"mix1"})
        db=db.rename(index={"mix3":"mix2"})
        db=db.rename(index={"rand":"RAND"})
        db=db.rename(index={"seq":"STREAM"})


        db_spec = db.loc[SPEC].mean()
        db_mix = db.loc[MIX].mean()
        db_gap = db.loc[GAP].mean()
        db_rand = db.loc["RAND"]
        db_stream = db.loc["STREAM"]
        db_mean = db.mean()



        db_new=pd.DataFrame({'SPEC':db_spec,
                                                  'GAP': db_gap,
                                                   'RAND': db_rand,
                                                    'STREAM':db_stream,
                                                     'AVERAGE': db_mean
                                                      }).T
        #db=db_new
        db.to_csv(report_dir+"/%s-%s.csv"%(report_name,result_name))
    else:
        db=pd.read_csv(report_dir+"/%s-%s.csv"%(report_name,result_name),index_col=0)


    print db
    db=db*100
    db.loc['Average']=db.mean()
    db.columns=["LRU (Baseline)","RANDOM","DRRIP","FIFO","SHIP"]
    db=db[["LRU (Baseline)", "DRRIP", "SHIP"]]

    BENCHMARK_ALL = SPEC+MIX+GAP+SYN+["Average"]
    db=db.loc[BENCHMARK_ALL,:]

    ax=db.plot.bar(figsize=(s_fig_w, s_fig_w/3),cmap="summer",width=0.7,edgecolor='black')
    plt.subplots_adjust(left=0.1, right=0.98, top=0.85, bottom=0.4)
    ax.grid(axis='y')

    ax.legend(loc=9,ncol=5,fontsize=17,bbox_to_anchor=(0.5, 1.35))
    plt.xticks(fontsize=15,rotation=90)
    plt.yticks(fontsize=18)
    plt.ylabel("Hit Rate(%)",fontsize=20)

    plt.ylim(ymax = 100, ymin = 0)

    plt.savefig(report_dir+"/%s-%s.pdf"%(report_name,result_name))
    plt.savefig(report_dir+"/%s-%s.eps"%(report_name,result_name),format="eps")



#Addtional memory request
def speedup_compare_intro(doLoadData):
    db =""
    report_name="speedup_intro"
    dp_speedup=""
    dp_comp=""
    if doLoadData==False:
        db_speedup=speedup(True,False)
        print db_speedup
        db_comp=compratio(True)
        db_speedup.to_csv(report_dir+"/%s-%s-speedup.csv"%(report_name,result_name))
        db_comp.to_csv(report_dir+"/%s-%s-comp.csv"%(report_name,result_name))
    else:
        db_speedup=pd.read_csv(report_dir+"/%s-%s-speedup.csv"%(report_name,result_name),index_col=0)
        db_comp=pd.read_csv(report_dir+"/%s-%s-comp.csv"%(report_name,result_name),index_col=0)

    print db_speedup
    print db_comp

    db_speedup=db_speedup[["metacache_rownum8192","metadata_predictor0"]]
    db_comp_spec = db_comp.loc[SPEC]
    db_comp_gap = db_comp.loc[GAP]
    db_spec = db_speedup.loc[SPEC]
    db_gap  = db_speedup.loc[GAP]

  #  db1=db_spec
  #  db1.index=db_comp_spec
  #  db2=db_gap
  #  db2.index=db_comp_gapa
    x, y = db_spec
    print x
    print y
    #print db_comp_spec
    #print db_comp_gap
    #print db_spec
    #print db_gap

  #  print db1
  #  print db2
    fig=plt.figure()
    ax = fig.add_subplot(1,1,1,axisbg="1.0")
    ax.scatter(x=db_comp_spec, y=db_spec.iloc[:,0],color="b",marker="*",label="SPEC with Metadata Cache")
    ax.scatter(x=db_comp_gap,y=db_gap.iloc[:,0],color="r",marker="*",label="GAP with Metadata Cache")
    ax.scatter(x=db_comp_spec,y=db_spec.iloc[:,1],color="b",marker="o",label="SPEC (Ideal)")
    ax.scatter(x=db_comp_gap,y=db_gap.iloc[:,1],color="r",marker="o",label="GAP (Ideal)")
    #ax=db.plot.bar(figsize=(s_fig_w, s_fig_h),cmap="summer",width=0.7,edgecolor='black')
    plt.subplots_adjust(left=0.1, right=0.98, top=0.98, bottom=0.25)
    #ax.grid(axis='y')

    ax.legend(loc=9,fontsize=18)
    #plt.xticks(fontsize=18,rotation=45)
    #plt.yticks(fontsize=18)
    plt.ylabel("Speedup",fontsize=20)
    plt.xlabel("Percentage of cachelines compressible to 30B",fontsize=20)

    #plt.ylim(ymax = 1.6, ymin = .8)

    plt.savefig(report_dir+"/%s-%s.pdf"%(report_name,result_name))
    plt.savefig(report_dir+"/%s-%s.eps"%(report_name,result_name),format="eps")

#Addtional memory request
def addtraffic_compare_intro(doLoadData):
    report_name="traffic_ideal"
    dp_speedup=""
    dp_comp=""
    if doLoadData==False:
        db_txnrecvd   =   mergeCol("totalTxnsRecvd","MemController0",id_tech)
        db_txnbase = db_txnrecvd[["numPCHs1"]].iloc[:,0]
        db_txnmeta = db_txnrecvd[["metacache_rownum8192"]]
        db_txnideal = db_txnrecvd[["metadata_predictor0"]]
        db_diff=db_txnmeta.subtract(db_txnbase,axis="index")
        print db_diff
        db_new=db_diff.div(db_txnbase,axis="index")
        print db_new
     #   db_new=db_txnmeta.div(db_txnbase,axis="index")

      # # db_txnideal=db_txnideal.dib(db_txnbase,axis="index")
        #print db_new
       # print db_txnideal

        db_speedup=db_new
        db_comp=compratio(True)
        db_speedup.to_csv(report_dir+"/%s-%s-speedup.csv"%(report_name,result_name))
        db_comp.to_csv(report_dir+"/%s-%s-comp.csv"%(report_name,result_name))
    else:
        db_speedup=pd.read_csv(report_dir+"/%s-%s-speedup.csv"%(report_name,result_name),index_col=0)
        db_comp=pd.read_csv(report_dir+"/%s-%s-comp.csv"%(report_name,result_name),index_col=0)

    print db_speedup
    print db_comp

   # db_speedup=db_speedup[["metacache_rownum8192","metadata_predictor0"]]
    db_comp_spec = db_comp.loc[SPEC]
    db_comp_gap = db_comp.loc[GAP]
    db_spec = db_speedup.loc[SPEC]
    db_gap  = db_speedup.loc[GAP]

  #  db1=db_spec
  #  db1.index=db_comp_spec
  #  db2=db_gap
  #  db2.index=db_comp_gapa
    #print db_comp_spec
    #print db_comp_gap
    #print db_spec
    #print db_gap

  #  print db1
  #  print db2


    fig=plt.figure(figsize=(s_fig_w,5))
    #ax = fig.add_subplot(1,1,1,axisbg="1.0")
    ax = fig.add_subplot(1,1,1)
    ax.scatter(x=db_comp_spec, y=db_spec.iloc[:,0]*100,color="b",marker="o",label="SPEC",s=200)
    ax.scatter(x=db_comp_gap,y=db_gap.iloc[:,0]*100,color="r",marker="*",label="GAP",s=200)
    ax.grid(color='gray', linestyle=':', linewidth=1)


    #ax.grid(color='k', linestyle='-', linewidth=2)
   # ax.scatter(x=db_comp_spec,y=db_spec.iloc[:,1],color="b",marker="o",label="SPEC (Ideal)")
   # ax.scatter(x=db_comp_gap,y=db_gap.iloc[:,1],color="r",marker="o",label="GAP (Ideal)")
    #ax=db.plot.bar(figsize=(s_fig_w, s_fig_h),cmap="summer",width=0.7,edgecolor='black')
    plt.subplots_adjust(left=0.1, right=0.98, top=0.94, bottom=0.22)
    #ax.grid(axis='y')

    ax.legend(loc=9,fontsize=18,frameon=True,edgecolor='k')
    plt.xticks(fontsize=18,rotation=0)
    plt.yticks(fontsize=18)
    plt.ylabel("Additional Memory Requests (%)",fontsize=18)
    plt.xlabel("% of Memory Blocks (64 bytes) compressible to 30 bytes",fontsize=20)

    #plt.ylim(ymax = 1.6, ymin = .8)

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
#db_array=["numPCHs1","metacache_rownum8192"]
#speedup_metacache_diff_repl(False) #1
#hitrate_metacache_diff_repl(True) #1
#report("totalTxnsRecvd",db_array,"MemController0","Transactions")
#report("actCmdsRecvd",db_array, "Dimm0","Active Commands")
#report("readCmdsRecvd", db_array, "Dimm0","Read Commands")
#report("writeCmdsRecvd",db_array,"Dimm0","Write Commands")
#report("preCmdsRecvd",db_array,"Dimm0","Precharge Commands")
#speedup_compare_intro(True)
#speedup(True,True) #1
#speedup_with_diff_predictor_size(True)#5
#predictor_stat(False) #7
#membandwidth(True) #8
#memlatency(True) #9
addtraffic_compare_intro(True) #6
#energy("totalEnergy",1,"Dimm0","Energy Consumption")  #2
#compratio(True)  #3
#predic_accuracy(False) #4
#metacache_overhead_summary(False) #1
#additional_memory_request(True) #3
#power("actprePower",0)
#power("readPower",0)
#power("writePower",0)
#power("totalPower",0)
#additional_memory_request_stacked(False)
