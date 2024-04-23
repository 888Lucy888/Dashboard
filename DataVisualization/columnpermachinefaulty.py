import simpy
import numpy as np
import matplotlib.pyplot as plt

# Define constants
NUM_WORKSTATIONS = 6
FAILURE_PROBABILITIES = [0.20, 0.10, 0.15, 0.05, 0.07, 0.10]
SIMULATION_TIME = 5000

class ManufacturingFacility:
    def __init__(self, env):
        self.env = env
        self.total_faulty_production = [0] * NUM_WORKSTATIONS

    def production_process(self):
        while True:
            for i in range(NUM_WORKSTATIONS):
                if np.random.random() < FAILURE_PROBABILITIES[i]:
                    self.total_faulty_production[i] += 1  # Increment faulty production count

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

    # Plot bar chart for total faulty production per machine
    plt.figure(figsize=(10, 6))
    plt.bar(range(NUM_WORKSTATIONS), facility.total_faulty_production, align='center', alpha=0.7)
    plt.xlabel('Machine')
    plt.ylabel('Total Faulty Production')
    plt.title('Total Faulty Production per Machine')
    plt.xticks(range(NUM_WORKSTATIONS), [f'Machine {i+1}' for i in range(NUM_WORKSTATIONS)])
    plt.grid(axis='y')
    plt.show()

# Main function
def main():
    # Run simulation
    simulate()

if __name__ == "__main__":
    main()
