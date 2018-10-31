# Imports
import os
import sys

# Setup path to find Sumo modules
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)

else:
    # Stop execution if SUMO_HOME is not a environment variable
    sys.exit("please declare environment variable 'SUMO_HOME'")

# SUMO imports
import traci
import traci.constants as tc


def initial(gui_simulation: bool):
    sumo_executable_path = "/opt/local/bin/sumo"
    sumo_executable_path_gui = "/opt/local/bin/sumo-gui"

    sumo_cfg_file_path = "manhattan/manhattan-1.5-0.sumo.cfg"

    if gui_simulation:
        sumo_path = sumo_executable_path_gui
    else:
        sumo_path = sumo_executable_path

    command = [sumo_path, "-c", sumo_cfg_file_path]
    traci.start(command)

    vehicle_id = 1

    traci.vehicle.subscribe(vehicle_id, (tc.VAR_ROAD_ID, tc.VAR_LANEPOSITION))
    print(traci.vehicle.getSubscriptionResults(vehicle_id))

    for step in range(3):
        print("step", step)
        traci.simulationStep()
        print(traci.vehicle.getSubscriptionResults(vehicle_id))
    traci.close()


if __name__ == '__main__':
    initial(gui_simulation=True)
