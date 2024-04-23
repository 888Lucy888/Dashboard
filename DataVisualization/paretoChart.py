import simpy
import numpy as np
import matplotlib.pyplot as plt

# Define constants
NUM_WORKSTATIONS = 6
ACCIDENT_PROBABILITY = 0.0001
SIMULATION_TIME = 5000

class ManufacturingFacility:
    def __init__(self, env):
        self.env = env
        self.workstations = [0] * NUM_WORKSTATIONS
        self.accidents = []

    def production_process(self):
        while True:
            # Check for accidents at each workstation
            for i in range(NUM_WORKSTATIONS):
                if np.random.random() < ACCIDENT_PROBABILITY:
                    self.workstations[i] += 1
                    self.accidents.append((self.env.now, i + 1))  # Append (time, workstation) tuple

            yield self.env.timeout(1)  # Time unit for checking accidents

            # Stop simulation if it reaches the defined simulation time
            if self.env.now >= SIMULATION_TIME:
                break

# Simulation function
def simulate():
    env = simpy.Environment()
    facility = ManufacturingFacility(env)
    env.process(facility.production_process())
    env.run(until=SIMULATION_TIME)

    # Plot connected scatter plot for daily accidents per workstation
    accidents = facility.accidents
    times, workstations = zip(*accidents)  # Unzip the list of (time, workstation) tuples
    plt.figure(figsize=(10, 6))
    plt.plot(times, workstations, '-o', markersize=5)
    plt.xlabel('Time')
    plt.ylabel('Workstation')
    plt.title('Connected Scatter Plot for Daily Accidents per Workstation')
    plt.yticks(range(1, NUM_WORKSTATIONS + 1))
    plt.grid(True)
    plt.show()

# Main function
def main():
    # Run simulation
    simulate()

if __name__ == "__main__":
    main()
