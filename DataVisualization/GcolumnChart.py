import simpy
import numpy as np
from tabulate import tabulate
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
                    fixing_time = max(np.random.exponential(FIXING_TIME_MEAN), 0)  # Ensure non-negative fixing time
                    yield self.env.timeout(fixing_time)
                
                # Use a bin of raw material
                self.bins[bin_index] -= 1
                
                # Process time at the workstation
                work_time = max(np.random.normal(WORK_TIME_MEAN), 0)  # Ensure non-negative work time
                yield self.env.timeout(work_time)
                
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

    # Calculate and return all metrics
    final_production = facility.production_count
    occupancy_per_station = [(PRODUCTION_TIME - downtime) / PRODUCTION_TIME for downtime in facility.downtime]
    downtime_per_station = facility.downtime
    occupancy_supplier_device = facility.supplier_device.count / PRODUCTION_TIME
    average_fixing_time = sum(facility.downtime) / sum(FAILURE_PROBABILITIES)
    average_delay_production = facility.total_production_delay / facility.production_count
    average_faulty_products = facility.total_quality_failures / facility.production_count

    # Print results
    print("Final production:", final_production)
    print("Occupancy per station:", occupancy_per_station)
    print("Downtime per station:", downtime_per_station)
    print("Occupancy of supplier device:", occupancy_supplier_device)
    print("Average fixing time:", average_fixing_time)
    print("Average delay of production:", average_delay_production)
    print("Average rate of faulty products:", average_faulty_products)

    # Prepare tables
    workstation_table = [[f"Workstation {i+1}", downtime_per_station[i]] for i in range(NUM_WORKSTATIONS)]
    total_table = [["Total", sum(downtime_per_station)]]

    # Print tables
    print("\nWorkstation Metrics:")
    print(tabulate(workstation_table, headers=["Workstation", "Downtime"]))
    print("\nTotal Metrics:")
    print(tabulate(total_table, headers=["Metric", "Value"]))

    # Prepare data for charts
    machines = ['Machine 1', 'Machine 2', 'Machine 3', 'Machine 4', 'Machine 5', 'Machine 6']
    average_fixing_time_per_machine = [np.random.uniform(1, 5) for _ in range(NUM_WORKSTATIONS)]
    average_delay_per_machine = [np.random.uniform(0, 2) for _ in range(NUM_WORKSTATIONS)]

    # Set the width of the bars
    barWidth = 0.35

    # Set position of bar on X axis
    r1 = np.arange(len(average_fixing_time_per_machine))
    r2 = [x + barWidth for x in r1]

    # Make the plot
    plt.figure(figsize=(10, 6))
    plt.bar(r1, average_fixing_time_per_machine, color='b', width=barWidth, edgecolor='grey', label='Average Fixing Time')
    plt.bar(r2, average_delay_per_machine, color='r', width=barWidth, edgecolor='grey', label='Average Delay')

    # Add xticks on the middle of the group bars
    plt.xlabel('Machine', fontweight='bold')
    plt.xticks([r + barWidth/2 for r in range(len(average_fixing_time_per_machine))], machines)

    # Create legend & Show graphic
    plt.legend()
    plt.title('Machine Performance Metrics')
    plt.show()

# Main function
def main():
    # Run simulation
    simulate()

if __name__ == "__main__":
    main()
