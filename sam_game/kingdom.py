# print("""
# Kingdom Manager
# This should deliver an object which represents the kingdom, and potentionally other kingdoms
# The kingdom should be made up of different regions (shires? counties?)
# There should be sererate stats for the kingdom's resources as a whole, and for shire resources
# For example, while shires can produce food, most food produced will go to feeding the shire that produced it
# A challenge to the player wlil be to manage redistribution of shire goods
# What can shires produce?
#  - Food
#  - Men
#  - Metal
#  - Wood
#  - Coin?
# Shires will produce varying quantities of these resources, and some shires may be far more productive than others
# Shires could also potentionally build higher tier goods, such as:
#  - Weapons
#  - Boats
#  - Tools
#  - Horses
# While shires should potentially start with an ability to produce a higehr tier good, it should be limited
# Secondary good production should require investment
# Finally, some goods could potentially be produced on a kingdom-based level.
# These would be things primarily associated with the nobility, such as art and science.
# """)

import random
import json
import inspect

class LogStat:
    def __init__(self):
        self.log = []

    def __get__(self, instance, owner):
        return self.log

    def __set__(self, instance, value):
        self.log.append(value)

class LogClass:
    log = LogStat()

class KingdomManager:
    def log_wrapper(func):
        def func_wrapper(*args):
            me = None
            if func.__name__ == "__init__":
                func(*args)
            self = args[0]
            func_signature = inspect.signature(func)
            func_parameters = func_signature.parameters
            func_args = args
            arg_list = []
            for item in func_parameters:
                arg_list.append(item)
            for i in range(len(arg_list)):
                arg_list[i] = (arg_list[i], func_args[i])
            owner = arg_list[0][1] if arg_list[0][0] == "self" else None
            string = "{} Func={} Args:".format(owner, func.__name__)
            for item in arg_list:
                string += "({}={})".format(item[0], item[1])
            self.log.log = string
            if func.__name__ == "__init__":
                return
            return func(*args)
        return func_wrapper

    def __init__(self, shires_filename, log):
        self.log = log
        self.shires_filename = shires_filename
        self.shire_instances = {}
        self.id_lookup = []
        self.load_file()
        self.shire_creator = ShireCreator(self, self.log)

    @log_wrapper
    def get_name_from_id(self, shire_name):
        for item in self.id_lookup:
            if item[0] == shire_name:
                return item[1]
        raise AttributeError("No ID for that name!")

    @log_wrapper
    def create_shire(self):
        shire_instance = self.shire_creator.create_shire()
        self.id_lookup.append((shire_instance.name, shire_instance.id))
        self.shire_instances[shire_instance.name] = shire_instance
        self.view_shire(shire_instance.name)
        self.save_file()
        return "Created Shire: {}!".format(shire_instance.name)

    @log_wrapper
    def view_shire(self, shire_name):
        if type(shire_name) == int: shire_name = self.get_name_from_id(shire_name)
        shire = self.shire_instances[shire_name]
        pretty_order = [
        "",
        "ID:                        {}".format(shire.id),
        "Name:                      {}".format(shire.name),
        "population:                {}".format(shire.population),
        "Size (sq miles):           {}".format(shire.size_sqmiles),
        "Lord:                      {}".format(shire.manager),
        "Specialisation:            {}".format(shire.specialisation),
        "",
        "Food Production:           {}".format(shire.food_production),
        "Farming Population:        {}".format(shire.farming_pop),
        "",
        "Metal Production:          {}".format(shire.metal_production),
        "Metalworking Population:   {}".format(shire.metal_pop),
        "Metal Forecast:            {}".format(shire.metal_forecast),
        "",
        "Wood Production:           {}".format(shire.wood_production),
        "Lumberjack Population:     {}".format(shire.wood_pop),
        "Wood Forecast:             {}".format(shire.wood_forecast),
        "",
        "Coin Production:           {}".format(shire.coin_production),
        "Coinsmith Population:      {}".format(shire.coin_pop),
        "Coin Forecast:             {}".format(shire.coin_forecast),
        "",
        "Bums:                      {}".format(shire.bums)
        ]
        for item in pretty_order:
            print(item)

    def view_all(self):
        for name, instance in self.shire_instances.items():
            self.view_shire(name)

    def load_file(self):
        try:
            with open(self.shires_filename, "r") as file:
                coded = file.read()
        except FileNotFoundError:
            self.save_file()
            return
        shires_dict = json.loads(coded)
        for name, dictionary in shires_dict.items():
            self.shire_instances[name] = ShireInstance(self, dictionary, self.log)
        for name, instance in self.shire_instances.items():
            self.id_lookup.append((instance.name, instance.id))

    def save_file(self):
        shires_dict = {}
        for name, instance in self.shire_instances.items():
            shires_dict[instance.name] = instance.export_self()
        dump = json.dumps(shires_dict)
        with open(self.shires_filename, "w") as file:
            file.write(dump)

    def __str__(self):
        return "<Kingdom Manager instance>"

    def __repr__(self):
        return "<Kingdom Manager instance>"

class ShireStat:
    def __init__(self, name, **kwargs):
        self.value = None
        self.name = name
        self.max_value = kwargs["max_value"] if "max_value" in kwargs else None
        self.min_value = kwargs["min_value"] if "min_value" in kwargs else None
        self.value_type = kwargs["value_type"] if "value_type" in kwargs else None

    def __get__(self, instance, owner):
        if self.value == None:
            raise AttributeError("Error! Stat value not defined! (Stat: {}, Instance: {}, Owner: {})".format(self.name, instance, owner))
        else:
            return self.value

    def __set__(self, instance, value):
        self.value = value
        if self.max_value:
            if self.value > self.max_value:
                print("Value too high! Setting to max value. (Stat: {}, Owner: {}, Value: {}, Max value: {}".format(self.name, instance, value, self.max_value))
                self.value = self.max_value
        elif self.min_value:
            if self.value < self.min_value:
                print("Value too high! Setting to min value. (Stat: {}, Owner: {}, Value: {}, Max value: {}".format(self.name, instance, value, self.min_value))
                self.value = self.min_value
        if self.value_type:
            try:
                self.value = self.value_type(self.value)
            except ValueError as e:
                print("Buggered up a variables type. (Stat: {}, Stat_Type: {}, Given_Type: {}, Given Value: {}, Instance: {})".format(self.name, self.value_type, type(value), value, instance))

    def __str__(self):
        return "<ShireStat: {}>".format(self.name)

    def __str__(self):
        return "<ShireStat: {}>".format(self.name)

class ShireInstance(KingdomManager):
    population = ShireStat("population", value_type=int)
    size_sqmiles = ShireStat("size_sqmiles", value_type=int)
    food_production = ShireStat("food_production", min_value=0, max_value=10, value_type=int)
    metal_production = ShireStat("metal_production", min_value=0, max_value=10, value_type=int)
    metal_percentage = ShireStat("metal_percentage", value_type=int)
    wood_production = ShireStat("wood_production", min_value=0, max_value=10, value_type=int)
    wood_percentage = ShireStat("wood_percentage", value_type=int)
    coin_production = ShireStat("coin_production", min_value=0, max_value=10, value_type=int)
    coin_percentage = ShireStat("coin_percentage", value_type=int)
    food_stores = ShireStat("food_stores", value_type=int)
    metal_stores = ShireStat("metal_stores", value_type=int)
    wood_stores = ShireStat("wood_stores", value_type=int)
    coin_stores = ShireStat("coin_stores", value_type=int)
    farming_pop = ShireStat("farming_pop", value_type=int)
    working_pop = ShireStat("working_pop", value_type=int)
    metal_pop = ShireStat("metal_pop", value_type=int)
    wood_pop = ShireStat("wood_pop", value_type=int)
    coin_pop = ShireStat("coin_pop", value_type=int)
    metal_forecast = ShireStat("metal_forecast", value_type=int)
    wood_forecast = ShireStat("wood_forecast", value_type=int)
    coin_forecast = ShireStat("coin_forecast", value_type=int)

    @KingdomManager.log_wrapper
    def __init__(self, kingdom_manager, shire_dict, log):
        self.log = log
        self.kingdom_manager = kingdom_manager
        self.name = shire_dict["name"]
        self.id = shire_dict["id"]
        self.manager = shire_dict["manager"]
        self.specialisation = shire_dict["specialisation"]
        self.population = shire_dict["population"]
        self.size_sqmiles = shire_dict["size_sqmiles"]
        self.food_production = shire_dict["food_production"]
        self.metal_production = shire_dict["metal_production"]
        self.wood_production = shire_dict["wood_production"]
        self.coin_production = shire_dict["coin_production"]
        self.metal_percentage = shire_dict["metal_percentage"]
        self.wood_percentage = shire_dict["wood_percentage"]
        self.coin_percentage = shire_dict["coin_percentage"]
        self.food_stores = shire_dict["food_stores"]
        self.metal_stores = shire_dict["metal_stores"]
        self.wood_stores = shire_dict["wood_stores"]
        self.coin_stores = shire_dict["coin_stores"]
        self.refresh_dependant_stats()

    @KingdomManager.log_wrapper
    def pass_time(self):
        growth = False
        shrink = False
        log = ["Log for {}".format(self.name)]
        variance = (random.randint(80, 120) / 100)
        log.append("Variance for the year is {}!".format(variance))
        log.append("{} food rots away!".format(int(self.food_stores - (self.food_stores * 0.5))))
        self.food_stores = self.food_stores * 0.9

        food_produced = int(self.farming_pop * self.food_production * variance)
        if food_produced >= self.population:
            food_surplus = food_produced - self.population
            self.food_stores += food_surplus
            log.append("{} food produced! ({} eaten, {} stored, {} stored total)"
            .format(food_produced, self.population, food_surplus, self.food_stores))
            growth = True
        else:
            food_shortage = self.population - food_produced
            if self.food_stores >= food_shortage:
                self.food_stores -= food_shortage
                log.append("{} food produced, food taken from storage to feed everyone. ({} from storage, {} stored total)"
                .format(food_produced, food_shortage, self.food_stores))
            else:
                food_deficit = self.population - food_produced - self.food_stores
                log.append("{} food produced, {} food taken from storage to feed mouths. {} Are left hungry!)"
                .format(food_produced, self.food_stores, food_deficit))
                self.food_stores = 0
                shrink = True

        metal_produced = self.metal_pop * self.metal_production
        self.metal_stores += metal_produced
        log.append("{} metal produced! ({} stored total)".format(metal_produced, self.metal_stores))

        wood_produced = self.wood_pop * self.wood_production
        self.wood_stores += wood_produced
        log.append("{} wood produced! ({} stored total)".format(wood_produced, self.wood_stores))

        coin_produced = self.coin_pop * self.coin_production
        self.coin_stores += coin_produced
        log.append("{} coin produced! ({} stored total)".format(coin_produced, self.coin_stores))

        if growth:
            population_growth = int(food_surplus * 0.2)
            log.append("Population growns by {}!".format(population_growth))
            self.population += population_growth

        if shrink:
            population_shrink = int(food_deficit * 0.5)
            log.append("Starvation! {} people die of hunger".format(population_shrink))
            self.population -= population_shrink

        self.refresh_dependant_stats()

        for item in log:
            print(item)

    @KingdomManager.log_wrapper
    def refresh_dependant_stats(self):
        self.farming_pop = self.forecast_farming()
        self.working_pop = self.population - self.farming_pop
        self.metal_pop = self.working_pop * (self.metal_percentage / 100)
        self.wood_pop = self.working_pop * (self.wood_percentage / 100)
        self.coin_pop = self.working_pop * (self.coin_percentage / 100)
        self.bums = self.working_pop - self.metal_pop - self.wood_pop - self.coin_pop
        self.metal_forecast = self.forecast_stat(self.metal_production, self.metal_pop)
        self.wood_forecast = self.forecast_stat(self.wood_production, self.wood_pop)
        self.coin_forecast = self.forecast_stat(self.coin_production, self.coin_pop)

    @KingdomManager.log_wrapper
    def forecast_farming(self):
        if self.population >= self.size_sqmiles:
            farming_pop = self.size_sqmiles
        else:
            farming_pop = self.population * (1 / (1 + (self.food_production / 10)))
        return farming_pop

    @KingdomManager.log_wrapper
    def forecast_stat(self, stat, pop):
        return pop * (1 + (stat / 10))

    @KingdomManager.log_wrapper
    def export_self(self):
        export_dict = {
        "name": self.name,
        "id": self.id,
        "manager": self.manager,
        "specialisation": self.specialisation,
        "population": self.population,
        "size_sqmiles": self.size_sqmiles,
        "food_production": self.food_production,
        "food_stores": self.food_stores,
        "metal_production": self.metal_production,
        "metal_percentage": self.metal_percentage,
        "metal_stores": self.metal_stores,
        "wood_production": self.wood_production,
        "wood_percentage": self.wood_percentage,
        "wood_stores": self.wood_stores,
        "coin_production": self.coin_production,
        "coin_percentage": self.coin_percentage,
        "coin_stores": self.coin_stores
        }
        return export_dict

    def __str__(self):
        try:
            return "<ShireInstance: {}>".format(self.name)
        except AttributeError:
            return"No name...?"

    def __repr__(self):
        try:
            return "<ShireInstance: {}>".format(self.name)
        except AttributeError:
            return"No name...?"

class ShireCreator(KingdomManager):
    @KingdomManager.log_wrapper
    def __init__(self, kingdom_manager, log):
        self.log = log
        self.kingdom_manager = kingdom_manager
        self.specialisations = ["shipyards", "weapons", "tools", "horses", "soldiers"]
        with open("shire_names.json", "r") as file:
            self.shire_names = json.loads(file.read())

    @KingdomManager.log_wrapper
    def create_shire(self):
        shire_dict = {}
        while True:
            shire_dict["name"] = random.choice(self.shire_names) + "shire"
            if shire_dict["name"] in self.kingdom_manager.shire_instances:
                continue
            break
        shire_dict["id"] = self.find_appropriate_id()
        shire_dict["manager"] = None
        shire_dict["specialisation"] = random.choice(self.specialisations)
        shire_dict["food_production"] = random.randint(2, 5)
        shire_dict["size_sqmiles"] = random.randint (100, 1000)
        shire_dict["population"] = self.find_starting_population(shire_dict["food_production"], shire_dict["size_sqmiles"])
        shire_dict["metal_production"] = random.randint(1, 5)
        shire_dict["wood_production"] = random.randint(1, 5)
        shire_dict["coin_production"] = random.randint(1, 5)
        shire_dict["metal_percentage"] = 33
        shire_dict["wood_percentage"] = 33
        shire_dict["coin_percentage"] = 33
        shire_dict["food_stores"] = 0
        shire_dict["metal_stores"] = 0
        shire_dict["wood_stores"] = 0
        shire_dict["coin_stores"] = 0
        shire_instance = ShireInstance(self.kingdom_manager, shire_dict, self.log)
        return shire_instance

    @KingdomManager.log_wrapper
    def find_starting_population(self, food_production, size):
        population = int(size * (1 + (food_production / 10)))
        return population

    @KingdomManager.log_wrapper
    def find_appropriate_id(self):
        default_id = 100
        id_list = []
        for item in self.kingdom_manager.id_lookup:
            id_list.append(item[1])
        while True:
            if default_id in id_list:
                default_id += 1
                continue
            return default_id

    def __str__(self):
        return "<Shire Creator Instance>"

    def __repr__(self):
        return "<Shire Creator Instance>"

if __name__ == "__main__":
    log = LogClass()
    kingdom_manager = KingdomManager(log)
    shire = kingdom_manager.create_shire()
    while True:
        input()
        shire.pass_time()
        kingdom_manager.view_shire(shire.name)
        log_dump = log.log
        with open("kingdom_log.txt", "w") as file:
            for item in log_dump:
                file.write("{}\n".format(item))
