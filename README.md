# frensie_restart_mwe
A repository to test increasing the number of histories from a rendezvous restart file

# start the simulation with
python simulation.py

# restart the simulation with
python restart_and_inc_num_histories.py --rendezvous_file=sphere_rendezvous_2.xml --num_extra_particles=1 --thread=4