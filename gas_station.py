import random

import simpy

RANDOM_SEED = 42
NUM_PUMPS = 2               # num of gas pumps in the station
STATION_CAPACITY = 50     # main tank capacity
FILLING_TIME = 5            # how much does a car waits for it to be filled up
FUEL_TANK_LEVEL = [5, 25]   # min/max levels of fuel tanks
TANK_TRUCK_TIME = 100       # time the truck gets to get in
NUM_CARS = 20                # num of cars in the sim
THRESHOLD = 10

class gas_station_c():
    '''
    gas station has a limited number of pumps and of capacity, meaning
    it can have two pumps that are conected to the main tank.

    the tank will get empty every time a car fills gas. if it gets totaly
    empty we need to call a truck to fill it.
    '''
    def __init__(self, env, num_pumps, station_capacity, filling_time):
        self.env = env
        self.gas_pumps = simpy.Resource(self.env, num_pumps)
        self.main_tank = simpy.Container(
            self.env, STATION_CAPACITY, init = STATION_CAPACITY,
        )
        self.filling_time = filling_time
        self.gas_station_control()

    def fill_car(self, car, requested_gas):

        print(f'getting {requested_gas} gas from main tank at {self.env.now}')
        yield self.main_tank.get(10)

        yield self.env.timeout(self.filling_time)
        print(f'filled car at {self.env.now}')
        print(f'gas left in station {self.main_tank.level} at {self.env.now}')

    def gas_station_control(self):
        while True:
            print('im here')
            current_level = self.main_tank.level / self.main_tank.capacity
            if current_level * 100 < THRESHOLD:
                print(f'we need to call the truck at {self.env.now}')
                yield env.process(tank_truck(self.env, self.main_tank))

def car(env, name, gs):
    '''
    create a car, give it a fuel tank level, and go to the gas station
    '''
    car_tank_lvl = random.randint(*FUEL_TANK_LEVEL)
    print(f'car {name} arriving at gas station with {car_tank_lvl} at'
          f' {env.now}')

    with gs.gas_pumps.request() as pump:
        yield pump

        requested_gas = FUEL_TANK_LEVEL[1] - car_tank_lvl
        print(f'car {name} filling gas at {env.now}')
        yield env.process(gs.fill_car(car, int(requested_gas)))

        print(f'car {name} leaving gas station at {env.now}')

def tank_truck(env, main_tank):
    '''
    we need to send the main tank in order to calc how much gas we need to
    refuel
    '''
    yield env.timeout(TANK_TRUCK_TIME)
    print(f'tank truck arriving at {env.now}')
    ammount = main_tank.capacity - main_tank.level
    print(f'tank truck refiling {ammount}')
    yield main_tank.put(ammount)

def setup(env, num_pumps, station_capacity, filling_time):
    gs = gas_station_c(env, num_pumps, station_capacity, filling_time)

    for i in range(NUM_CARS):
        env.process(car(env, i, gs))

    while True:
        yield env.timeout(100)

print('gas station')
random.seed(RANDOM_SEED)

env = simpy.Environment()
env.process(setup(env, NUM_PUMPS, STATION_CAPACITY, FILLING_TIME))

env.run(until = 100)
