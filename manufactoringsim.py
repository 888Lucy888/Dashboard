import simpy
import random
from tabulate import tabulate
import matplotlib.pyplot as plt

random.seed(42)

class WorkStation(object):
    def __init__(self, id, env, refill, error_rate, downstream=None):
        self.id = id
        self.env = env
        self.refill = refill
        self.error_rate = error_rate
        self.downstream = downstream
        self.material = 25
        self.production = 0
        self.occupancy = 0
        self.downtime = 0
        self.fixing_time = 0
        self.rejected = 0
        self.supply_time = 0
        self.action = env.process(self.run())

    def run(self):
        while True:
            try:
                yield self.env.timeout(random.normalvariate(4, 1))
                self.occupancy += random.normalvariate(4, 1)
                if self.material <= 0:
                    yield self.env.process(self.refill_material())
                if random.random() < self.error_rate:
                    start = self.env.now
                    yield self.env.process(self.repair())
                    self.downtime += (self.env.now - start)
                if self.material > 0:
                    self.production += 1
                    self.material -= 1
                    print(f"Work Station {self.id} produced item {self.production}")
                    if random.random() <= 0.05:
                       print(f"Work Station {self.id} item {self.production} REJECTED")
                       self.rejected += 1
                       self.production -= 1  
                    if self.downstream is not None:
                        yield self.downstream.put(self.id)  # Yield the put operation
            except simpy.Interrupt:
                print(f"Work Station {self.id} is interrupted for repair.")

    def refill_material(self):
        with self.refill.request() as req:
            yield req
            yield self.env.timeout(1.5)
            self.supply_time += 1.5
            print(f"Refill full at Work Station {self.id}.")
            self.material = 25

    def repair(self):
        fix_time = random.expovariate(1/3)
        self.fixing_time += fix_time
        yield self.env.timeout(fix_time)
        print(f"Work Station {self.id} is repaired at {self.env.now}.")

class Product(object):
    def __init__(self, env, stations):
        self.env = env
        self.stations = stations
        self.action = env.process(self.run())

    def run(self):
        while True:
            yield self.env.process(self.stations[0].run())

def run_simulation(env, num_stations, error_rates, num_runs):
    refill = simpy.Resource(env, capacity=3)
    stations = []
    downstream = None
    for i in range(num_stations):
        downstream = simpy.Store(env) if i < num_stations - 1 else None
        station = WorkStation(i + 1, env, refill, error_rates[i], downstream)
        if downstream is not None:
            env.process(downstream_consumer(env, downstream))  # Start downstream consumer process
        stations.append(station)
    product = Product(env, stations)
    env.run(until=num_runs)
    return stations

def downstream_consumer(env, downstream):
    while True:
        item = yield downstream.get()  # Wait for an item from upstream
        print(f"Downstream received item {item} at {env.now}")

def main():
    num_stations = 6
    error_rates = [0.20, 0.10, 0.15, 0.05, 0.07, 0.10]
    num_runs = 500

    env = simpy.Environment()
    stations = run_simulation(env, num_stations, error_rates, num_runs)

    workstation_data = []
    total_production = sum(station.production for station in stations)
    total_rejected = sum(station.rejected for station in stations)
    total_supply_time = sum(station.supply_time for station in stations)
    total_occupancy = sum(station.occupancy for station in stations)
    total_downtime = sum(station.downtime for station in stations)
    total_fixing_time = sum(station.fixing_time for station in stations)
    
    for station in stations:
        avg_occupancy = station.occupancy / station.production
        avg_downtime = station.downtime / num_stations
        workstation_data.append([
            f"Work Station {station.id}",
            avg_occupancy,
            avg_downtime
        ])

    avg_production = total_production / num_stations
    avg_fixing_time = total_fixing_time / num_stations
    avg_supply_time = total_supply_time / num_stations
    avg_occupancy = total_occupancy / total_production
    avg_downtime = total_downtime / num_stations

    total_data = [
        ["Total Production", total_production],
        ["Total Production REJECTED", total_rejected],
        ["Average Production Per Workstation", avg_production],
        ["Total Supply Time", total_supply_time],
        ["Average Supply Time For Workstation", avg_supply_time],
        ["Total Fixing Time", total_fixing_time],
        ["Average Fixing Time Per Workstation", avg_fixing_time],
        ["Total Occupancy", total_occupancy],
        ["Average Occupancy Per Product", avg_occupancy],
        ["Total Downtime", total_downtime],
        ["Average Downtime Per Workstation", avg_downtime]
    ]

    print("\n-----------------------------------------------")
    print("Workstation Data")
    print("-----------------------------------------------\n")

    print(tabulate(workstation_data, headers=["Workstation", "Average Occupancy", "Downtime"]))
    print("\nTotal or Average Values:")
    print(tabulate(total_data))

    workstation_data = []
    for station in stations:
        workstation_data.append([
            f"Work Station {station.id}",
            station.production,
            station.fixing_time,
            station.downtime,
            station.occupancy / station.production if station.production != 0 else 0
        ])

    headers = ["Workstation", "Production", "Fixing Time", "Downtime", "Occupancy"]

    print("Workstation Data:")
    print(tabulate(workstation_data, headers=headers))

    # Generate pie chart
    labels = ['Total Production', 'Total Rejected']
    sizes = [total_production, total_rejected]
    colors = ['#ff9999', '#66b3ff']
    explode = (0.1, 0)  # explode 1st slice (i.e. 'Total Production')

    plt.figure(figsize=(7, 7))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('Total Production vs Total Rejected')
    plt.show()

    # Plot production per workstation
    plt.figure(figsize=(10, 5))
    plt.bar([f"Work Station {station.id}" for station in stations], [station.production for station in stations], color='skyblue')
    plt.xlabel('Workstation')
    plt.ylabel('Production')
    plt.title('Production per Workstation')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

    # Plot fixing time per workstation
    plt.figure(figsize=(10, 5))
    plt.bar([f"Work Station {station.id}" for station in stations], [station.fixing_time for station in stations], color='lightgreen')
    plt.xlabel('Workstation')
    plt.ylabel('Fixing Time')
    plt.title('Fixing Time per Workstation')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

    # Plot downtime per workstation
    plt.figure(figsize=(10, 5))
    plt.bar([f"Work Station {station.id}" for station in stations], [station.downtime for station in stations], color='salmon')
    plt.xlabel('Workstation')
    plt.ylabel('Downtime')
    plt.title('Downtime per Workstation')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

    # Plot occupancy per workstation
    plt.figure(figsize=(10, 5))
    plt.bar([f"Work Station {station.id}" for station in stations], [station.occupancy / station.production if station.production != 0 else 0 for station in stations], color='lightcoral')
    plt.xlabel('Workstation')
    plt.ylabel('Occupancy')
    plt.title('Occupancy per Workstation')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()