#!/bin/bash


#python run.py -f sim_spec_base.cfg -d "base,spec,8cores,200M,new_simpoint,correct_l3"
#python run.py -f sim_spec_compare.cfg -d "compare,spec,8cores,200m,modified_l3,new_simpoint,correct_l3"
#python run.py -f sim_gap_1thread_base.cfg -d "base,gap,8cores,200M,new_simpoint,correct_l3"
#python run.py -f sim_gap_1thread_compare.cfg -d "compare, gap, 8cores,200M,modified_l3,new_simpoint,correct_l3"

# with trace files generated with memhierarchy's memory controller 
#python run.py -f sim_spec_base.cfg -d "base,spec,8cores,200M,new_simpoint,trace_memctrl,rand_page"
#python run.py -f sim_spec_compare.cfg -d "compare,spec,8cores,200m,new_simpoint,trace_memctrl,rand_page"

#python run.py -f sim_gap_base.cfg -d "base,gap,8cores,200M,new_simpoint,trace_memctrl,rand_page"
#python run.py -f sim_gap_compare.cfg -d "compare, gap, 8cores,200M,new_simpoint,trace_memctrl,rand_page"

#python run.py -f sim_base.cfg -d "base,mix,8cores,200M,new_simpoint,trace_memctrl,rand_page"
#python run.py -f sim_compare.cfg -d "compare, mix, 8cores,200M,new_simpoint,trace_memctrl,rand_page"

#python run.py -f sim_randstream_base.cfg -d "base,randstream"
#python run.py -f sim_randstream_compare.cfg -d "compare,randstream"

# diff size of metadata cache
#python run.py -f sim_spec_metacache.cfg -d "metacache,spec,8cores,200M,new_simpoint,trace_memctrl,rand_page"
#python run.py -f sim_gap_metacache.cfg -d "metacache,gap,8cores,200M,new_simpoint,trace_memctrl,rand_page"
#python run.py -f sim_metacache.cfg -d "metacache,mix,8cores,200M,new_simpoint,trace_memctrl,rand_page"
#python run.py -f sim_randstream_metacache.cfg -d "metacache,randstream"


# diff replacement policy of metadata cache
#python run.py -f sim_metacache_repl.cfg -d "mcache_repl,spec,8cores,200M,new_simpoint,trace_memctrl,rand_page,metacache_dirty_evict"

# new predictor
#python run.py -f sim_base.cfg -d "base,all,8cores,200M,fixed_energy_re"
#python run.py -f sim_compare.cfg -d "ideal,all,8cores,200M,fixed_energy_re"
#python run.py -f sim_metacache.cfg -d "metacache,all,8cores,200M,fixed_energy_re,metacache_dirty_evict,corrected energy model"
#python run.py -f sim_attache_ropr_rownum.cfg -d "attache,rownum,all,8cores,200M,fixed_energy_re"
#python run.py -f sim_attache_ropr_col.cfg -d "attache,colnum,all,8cores,200M,fixed_energy_re,more fine-grained"
#python run.py -f sim_attache_global.cfg -d "attache,global,all,8cores,200M,fixed_energy_re"

python run.py -f sim_attache_nopredictor.cfg -d "attache,all,8cores,200M,no_predictor"




