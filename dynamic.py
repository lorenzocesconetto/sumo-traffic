
# Setup path to find Sumo modules
import os, sys
if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

# SUMO imports
import traci
import traci.constants as tc


def initial():
    command = ["/opt/local/bin/sumo", "-c", "manhattan/manhattan-1.5-0.sumo.cfg"]
    traci.start(command)
    vehID = 1
    traci.vehicle.subscribe(vehID, (tc.VAR_ROAD_ID, tc.VAR_LANEPOSITION))
    print(traci.vehicle.getSubscriptionResults(vehID))
    for step in range(3):
        print("step", step)
        traci.simulationStep()
        print(traci.vehicle.getSubscriptionResults(vehID))
    traci.close()


if __name__ == '__main__':
    initial()
