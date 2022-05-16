# frensie_restart_mwe
A directory to test starting a FRENSIE simulation at history N

# start the simulation with
python simulation_start_at_N.py

# generate results
python write_results.py --rendezvous_file=sphere_rendezvous_1.xml --NPS=1
# generate results for starting at 10k histories
python write_results.py --rendezvous_file=sphere_rendezvous_1.xml --NPS=1_s@10