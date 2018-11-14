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
python run.py -f sim_metacache.cfg -d "metacache,mix,8cores,200M,new_simpoint,trace_memctrl,rand_page"
#python run.py -f sim_randstream_metacache.cfg -d "metacache,randstream"


# diff replacement policy of metadata cache
#python run.py -f sim_spec_mcache_repl.cfg -d "mcache_repl,spec,8cores,200M,new_simpoint,trace_memctrl,rand_page"
#python run.py -f sim_gap_mcache_repl.cfg -d "mcache_repl,gap,8cores,200M,new_simpoint,trace_memctrl,rand_page"
#python run.py -f sim_mcache_repl.cfg -d "mcache_repl,mix,8cores,200M,new_simpoint,trace_memctrl,rand_page"
#python run.py -f sim_randstream_mcache_repl.cfg -d "mcache_repl,randstream,radn_page"

# new predictor
#python run.py -f sim_attache_ropr_rownum.cfg -d "attache,randstream,8cores,200M,new_simpoint,trace_memctrl,rand_page,ropr_rownum"
#python run.py -f sim_attache_ropr_col.cfg -d "attache,randstream,8cores,200M,new_simpoint,trace_memctrl,rand_page,ropr_col"




