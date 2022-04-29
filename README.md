# frensie_restart_mwe
A repository to test increasing the number of histories from a rendezvous restart file

# start the simulation with
python simulation.py

# restart the simulation with history wall 
python restart_and_inc_num_histories.py --rendezvous_file=sphere_rendezvous_2.xml --num_extra_particles=100 --thread=4

# restart the simulation with time wall
python restart_and_inc_num_histories.py --rendezvous_file=sphere_rendezvous_2.xml --wall_time=10 --thread=4

# restart the simulation with history wall and time wall
python restart_and_inc_num_histories.py --rendezvous_file=sphere_rendezvous_2.xml --num_extra_particles=1000 --wall_time=1 --thread=4

# generate results with
python write_results.py --rendezvous_file=sphere_rendezvous_2.xml --NPS=100