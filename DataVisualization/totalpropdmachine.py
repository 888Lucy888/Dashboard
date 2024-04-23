import simpy
import numpy as np
import matplotlib.pyplot as plt

# Define constants
NUM_WORKSTATIONS = 6
NUM_BINS = 3
BIN_CAPACITY = 25
PRODUCTION_TIME = 5000
FAILURE_PROBABILITIES = [0.20, 0.10, 0.15, 0.05, 0.07, 0.10]
REJECTION_PROBABILITY = 0.05
ACCIDENT_PROBABILITY = 0.0001
FIXING_TIME_MEAN = 3
WORK_TIME_MEAN = 4

class ManufacturingFacility:
    def __init__(self, env):
        self.env = env
        self.workstations = [simpy.Resource(env) for _ in range(NUM_WORKSTATIONS)]
        self.bins = [BIN_CAPACITY for _ in range(NUM_BINS)]
        self.supplier_device = simpy.Resource(env)
        self.production_count = 0
        self.total_fixing_time = 0
        self.total_production_delay = 0
        self.total_quality_failures = 0
        self.downtime = [0] * NUM_WORKSTATIONS

    def production_process(self):
        while True:
            # Check for accidents
            if np.random.random() < ACCIDENT_PROBABILITY:
                yield self.env.timeout(1)  # Stop production for 1 time unit
                continue
            
            # Get a bin of raw material
            with self.supplier_device.request() as req:
                yield req
                bin_index = np.random.randint(NUM_BINS)
                yield self.env.timeout(1)  # Resupply time
                self.bins[bin_index] = BIN_CAPACITY
            
            # Start production process
            start_time = self.env.now
            for i in range(NUM_WORKSTATIONS):
                # Check if the workstation fails
                if np.random.random() < FAILURE_PROBABILITIES[i]:
                    self.downtime[i] += 1
                    yield self.env.timeout(np.random.exponential(FIXING_TIME_MEAN))
                
                # Use a bin of raw material
                self.bins[bin_index] -= 1
                
                # Process time at the workstation
                yield self.env.timeout(np.random.normal(WORK_TIME_MEAN))
                
                # Check for quality issues
                if i == NUM_WORKSTATIONS - 1 and np.random.random() < REJECTION_PROBABILITY:
                    self.total_quality_failures += 1
                    break
                
                # Move to the next workstation
                yield self.env.timeout(0)  # Placeholder for transfer time
            
            # Calculate production delay
            end_time = self.env.now
            production_time = end_time - start_time
            self.total_production_delay += max(0, production_time - NUM_WORKSTATIONS * WORK_TIME_MEAN)
            
            # Update production count
            self.production_count += 1
            
            if self.production_count >= PRODUCTION_TIME:
                break

# Simulation function
def simulate():
    env = simpy.Environment()
    facility = ManufacturingFacility(env)
    env.process(facility.production_process())
    env.run()
    for ws in facility.workstations:
        print(ws.count)

    # Plot bar chart for total accepted production per machine
    # plt.figure(figsize=(10, 6))
    # plt.bar(range(NUM_WORKSTATIONS), facility.accepted_production, align='center', alpha=0.7)
    # plt.xlabel('Machine')
    # plt.ylabel('Total Accepted Production')
    # plt.title('Total Accepted Production per Machine')
    # plt.xticks(range(NUM_WORKSTATIONS), [f'Machine {i+1}' for i in range(NUM_WORKSTATIONS)])
    # plt.grid(axis='y')
    # plt.show()

# Main function
def main():
    # Run simulation
    simulate()

if __name__ == "__main__":
    main()
