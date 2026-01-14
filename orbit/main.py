import time
from gravityEngine import GravityEngine
from simulationWindow import SimulationWindow

def main():
    #create celestial bodies and the simulation framework
    gravity_engine = GravityEngine(alghorithm = 2)

    #creat simulation handler for window drawing, scaling, button presses, etc.
    simulation_window = SimulationWindow(gravity_engine)

    #start simulation
    simulation_window.simulation_start(updateLoop, gravity_engine)

def updateLoop(dt, gravity_engine:GravityEngine, simulation_window:SimulationWindow):
    start_time = time.time_ns()

    #stop engine when paused
    if (simulation_window.running == True):
        #update forces, positions, etc or every object.
        gravity_engine.update()

    #update window
    simulation_window.update(gravity_engine.body_list, dt, start_time)
    
if __name__ == "__main__":
    main()