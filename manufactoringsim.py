import simpy
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate

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
        self.fixing_times = []

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
                    fixing_time = np.random.exponential(FIXING_TIME_MEAN)
                    self.total_fixing_time += fixing_time
                    self.fixing_times.append(fixing_time)
                    yield self.env.timeout(fixing_time)
                
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

    # Calculate and return all metrics
    final_production = facility.production_count
    occupancy_per_station = [(PRODUCTION_TIME - downtime) / PRODUCTION_TIME for downtime in facility.downtime]
    downtime_per_station = facility.downtime
    occupancy_supplier_device = facility.supplier_device.count / PRODUCTION_TIME
    average_fixing_time = sum(facility.fixing_times) / len(facility.fixing_times)
    average_delay_production = facility.total_production_delay / facility.production_count
    average_faulty_products = facility.total_quality_failures / facility.production_count
    final_production = facility.production_count
    total_faulty_products = facility.total_quality_failures
    total_successful_products = final_production - total_faulty_products

    # Print results
    print("Final production:", final_production)
    print("Occupancy per station:", occupancy_per_station)
    print("Downtime per station:", downtime_per_station)
    print("Occupancy of supplier device:", occupancy_supplier_device)
    print("Average fixing time:", average_fixing_time)
    print("Average delay of production:", average_delay_production)
    print("Average rate of faulty products:", average_faulty_products)
    print("Final production:", final_production)
    print("Total faulty products:", total_faulty_products)
    print("Total successful products:", total_successful_products)

    # Create a pie chart
    labels = ['Faulty Products', 'Successful Products']
    sizes = [total_faulty_products, total_successful_products]
    explode = (0.1, 0)  # explode the 1st slice (Faulty Products)
    plt.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('Production Results')
    plt.show()

    # Create a column chart
    labels = ['Final Production', 'Faulty Products', 'Successful Products']
    values = [final_production, total_faulty_products, total_successful_products]
    plt.bar(labels, values, color=['blue', 'red', 'green'])
    plt.xlabel('Production Outcome')
    plt.ylabel('Quantity')
    plt.title('Production Outcome Comparison')
    plt.show()

    # Plot line chart
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, NUM_WORKSTATIONS + 1), downtime_per_station, marker='o', label='Downtime per Station')
    plt.plot(range(1, NUM_WORKSTATIONS + 1), [average_fixing_time] * NUM_WORKSTATIONS, linestyle='--', label='Average Fixing Time')
    plt.xlabel('Workstation')
    plt.ylabel('Time')
    plt.title('Downtime per Station vs Average Fixing Time')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Stacked Bar Chart for Workstation Metrics
    workstation_numbers = range(1, NUM_WORKSTATIONS + 1)
    occupancy_per_station = [0.8, 0.7, 0.85, 0.75, 0.9, 0.95]  # Sample data (occupancy)
    downtime_per_station = [5, 7, 4, 6, 3, 5]  # Sample data (downtime)

    plt.figure(figsize=(10, 6))
    plt.bar(workstation_numbers, occupancy_per_station, label='Occupancy', color='skyblue')
    plt.bar(workstation_numbers, downtime_per_station, label='Downtime', color='orange', bottom=occupancy_per_station)
    plt.xlabel('Workstation')
    plt.ylabel('Count')
    plt.title('Workstation Metrics')
    plt.legend()
    plt.xticks(workstation_numbers)
    plt.show()
    
    # Prepare tables
    workstation_table = [[f"Workstation {i+1}", occupancy_per_station[i], downtime_per_station[i]] for i in range(NUM_WORKSTATIONS)]
    total_table = [["Total", sum(occupancy_per_station), sum(downtime_per_station)]]

    # Print tables
    print("\nWorkstation Metrics:")
    print(tabulate(workstation_table, headers=["Workstation", "Occupancy", "Downtime"]))
    print("\nTotal Metrics:")
    print(tabulate(total_table, headers=["Metric", "Value"]))

# Main function
def main():
    # Run simulation
    simulate()

if __name__ == "__main__":
    main()
