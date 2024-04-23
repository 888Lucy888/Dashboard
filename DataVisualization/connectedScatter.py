import simpy
import numpy as np
import matplotlib.pyplot as plt

# Define constants
NUM_WORKSTATIONS = 6
FAILURE_PROBABILITIES = [0.20, 0.10, 0.15, 0.05, 0.07, 0.10]
FIXING_TIME_MEAN = 3
SIMULATION_TIME = 5000

class ManufacturingFacility:
    def __init__(self, env):
        self.env = env
        self.fixing_times = [[] for _ in range(NUM_WORKSTATIONS)]

    def production_process(self):
        while True:
            for i in range(NUM_WORKSTATIONS):
                if np.random.random() < FAILURE_PROBABILITIES[i]:
                    fixing_time = max(np.random.exponential(FIXING_TIME_MEAN), 0)  # Ensure non-negative fixing time
                    self.fixing_times[i].append((self.env.now, fixing_time))  # Append (time, fixing_time) tuple

            yield self.env.timeout(1)  # Time unit for checking failures

            # Stop simulation if it reaches the defined simulation time
            if self.env.now >= SIMULATION_TIME:
                break

# Simulation function
def simulate():
    env = simpy.Environment()
    facility = ManufacturingFacility(env)
    env.process(facility.production_process())
    env.run(until=SIMULATION_TIME)

    # Plot connected scatter plot for fixing times per machine
    plt.figure(figsize=(10, 6))
    for i, fixing_times in enumerate(facility.fixing_times):
        if fixing_times:  # Check if there are fixing times for this machine
            times, times_to_fix = zip(*fixing_times)  # Unzip the list of (time, fixing_time) tuples
            plt.plot(times, times_to_fix, '-o', label=f'Machine {i + 1}', markersize=5)

    plt.xlabel('Time')
    plt.ylabel('Fixing Time')
    plt.title('Connected Scatter Plot for Fixing Times per Machine')
    plt.legend()
    plt.grid(True)
    plt.show()

# Main function
def main():
    # Run simulation
    simulate()

if __name__ == "__main__":
    main()
