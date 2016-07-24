import inspect
import random
import json

class NobleManager:
    """Deals with the normal, day-to-day creation, execution and boring old management of Nobles.
     Probably isn't paid enough"""
    def __init__(self):
        self.noble_dictionary = self.load_file("nobles_dictionary.json", {})
        self.noble_instances = self.load_instances()
        self.id_lookup = self.load_id()
        self.noble_creator_instance = NobleCreator(self)

    def run_events(self):
        string = ""
        for name, noble in self.noble_instances.items():
            string += noble.perform_action()
        return string

    def list_names(self):
        return self.id_lookup

    def view_nobles(self):
        noble_list = []
        for name, noble in self.noble_instances.items():
            noble_list.append(noble)
        noble_list = sorted(noble_list, key=lambda noble: (noble.nobility), reverse=True)
        string = ""
        for noble in noble_list:
            string += ("\n{}\nNobility: {}\nWealth: {}\n".format(noble.extended_title, noble.nobility, noble.wealth))

        string += "\n"
        return string

    def view_single_noble(self, name):
        print("In here!")
        print(name)
        if type(name) == int:
            name = get_name_from_id(name)
        noble = self.noble_instances[name]
        return "{}\nNobility: {}".format(noble.extended_title, noble.nobility)

    def execute_noble(self, name):
        del self.noble_dictionary[name]
        self.noble_instances = self.load_instances()
        self.id_lookup = self.load_id()
        self.save_file()
        if name in self.noble_dictionary:
            return("Something went wrong")
        else:
            return("{} executed!".format(name))

    def execute_all(self):
        self.noble_dictionary = {}
        self.id_lookup = []
        self.noble_instances = self.load_instances()
        self.save_file()
        return("Everybody's dead, Dave")

    def patch_nobles(self, stat, value, mode="ignore"):
        """Adds or modifies a single stat of all nobles"""
        for noble in self.noble_dictionary:
            try:
                self.noble_dictionary[noble][stat]
                if mode == "overwrite": self.noble_dictionary[noble][stat] = value
                if mode == "delete": del self.noble_dictionary[noble][stat]
            except KeyError:
                if mode != "delete": self.noble_dictionary[noble][stat] = value

    def create_noble(self):
        """Uses the NobleCreator instance to create a new noble, and automitically creates an NobleInstance for it"""
        new_noble = self.noble_creator_instance.create_noble()
        new_noble_instance = NobleInstance(new_noble, self)
        noble_welcomes = []
        for name, noble in self.noble_instances.items():
            noble_welcomes.append(noble.welcome_noble(new_noble_instance))
        self.noble_dictionary[new_noble["full_name"]] = new_noble
        self.id_lookup.append((new_noble["full_name"], new_noble["id"]))
        noble_instance = NobleInstance(new_noble, self)
        self.noble_instances[new_noble["full_name"]] = noble_instance
        self.save_file()
        string = "New noble created: {}\n".format(new_noble["extended_title"])
        for item in noble_welcomes:
            string += "\n{}".format(item)
        return string

    def view_relations(self, name):
        string = ""
        noble = self.noble_instances[name]
        for name, value in noble.relations.items():
            string += "{}: {}\n".format(name, value)
        return string

    def get_name_from_id(self, ident):
        try:
            ident = int(ident)
        except TypeError:
            pass
        for item in self.id_lookup:
            if item[1] == ident: return item[0]
        return("ERROR")

    def load_instances(self):
        """Uses nobles_dictionary to create seperate NobleInstance instances of all nobles, and stores
        them in self.nobles_instances"""
        instances = {}
        for noble, stats in self.noble_dictionary.items():
            try:
                instances[noble] = NobleInstance(stats, self)
            except KeyError as e:
                print("Error! {} is missing a stat. ({})".format(stats["full_name"], e))
        return instances

    def load_id(self):
        id_list = []
        for name, noble in self.noble_instances.items():
            id_list.append((noble.full_name, noble.id))
        return id_list

    def load_file(self, var_file, default = None):
        """Loads specified file"""
        try:
            with open(var_file, "r") as file:
                raw_load = file.read()
            return json.loads(raw_load)
        except FileNotFoundError:
            print('"%s": File not found' % var_file)
            return default

    def save_file(self):
        """Saves self.nobles_dictionary and self.id_lookup"""
        dump = json.dumps(self.noble_dictionary)
        with open("nobles_dictionary.json", "w") as file:
            file.write(dump)

class NobleInstance(NobleManager):
    """A class to turn nobles into objects, rather than just having them set around in a dictionary. The point
    of thie exercise!"""
    def __init__(self, noble_dict, noble_manager):
        self.noble_manager = noble_manager
        self.id = noble_dict["id"]
        self.gender = noble_dict["gender"]
        self.nobility = noble_dict["nobility"]
        self.full_name = noble_dict["full_name"]
        self.surname = noble_dict["surname"]
        self.full_title = noble_dict["full_title"]
        self.extended_title = noble_dict["extended_title"]
        self.relations = noble_dict["relations"]
        self.wealth = noble_dict["wealth"]

    def perform_action(self):
        available_actions = [
        self.do_fuck_all,
        self.invest_capital
        ]
        action = random.choice(available_actions)
        return action()

    def do_fuck_all(self):
        return("{} sits on their arse for a week. Nothing much changes. Feudalism!\n".format(self.full_name))

    def invest_capital(self):
        success = random.randrange(-50, 100, 1)
        percentage = success / 1000
        if success < 0:
            result = "{} tries investing some capital, but somehow buys into the only Ponzi scheme in medieval europe. D'oh!\n".format(self.full_name)
        elif success >= 0 and success < 5:
            result = "{} invests their capital into a reliable mining company - a good choice in pre 1980's britain\n".format(self.full_name)
        elif success >= 5:
            result = "{} takes a chance with an internet startup, and is suddenly rolling in cash!\n".format(self.full_name)
        self.wealth = int(self.wealth*(1 + percentage))
        self.save_self()
        return result

    def welcome_noble(self, new_noble):
        if new_noble.surname == self.surname:
            print(new_noble.surname)
            print(self.surname)
            friendship = 10
        else:
            friendship = random.randint(1, 9)
        if friendship < 4:
            string = ("{} turns her nose up at this filthy newcomer".format(self.full_name))
        elif friendship >=4 and friendship < 7:
            string = ("{} eyes the newcomer cautiously".format(self.full_name))
        elif friendship >= 7:
            string = ("{} welcomes the newcomer with open arms!".format(self.full_name))
        self.relations[new_noble.full_name] = friendship
        return string

    def save_self(self):
        """NobleManager passes itself to each NobleInstance to let this work"""
        stat_dict = self.compile_stat_dict()
        self.noble_manager.noble_dictionary[self.full_name] = stat_dict
        self.noble_manager.save_file()

    def compile_stat_dict(self):
        """For when the NobleInstance doesn't really need to be a object after all"""
        stat_dict = {
        "id": self.id,
        "gender": self.gender,
        "nobility": self.nobility,
        "full_name": self.full_name,
        "surname": self.surname,
        "full_title": self.full_title,
        "extended_title": self.extended_title,
        "relations": self.relations,
        "wealth": self.wealth
        }
        return stat_dict

    def __str__(self):
        return 'This is an instance of the noble "{}"'.format(self.full_name)

    def __repr__(self):
        return '<instance of noble {} with stats {}>'.format(self.full_name, self.compile_stat_dict())

class NobleCreator(NobleManager):
    """It's called NobleCreator. Take a wild guess as to what it does"""
    def __init__(self, NobleManager):
        self.noble_manager = NobleManager
        self.noblenames = self.load_names()

    def create_noble(self):
        """It's called create_noble. Take a wild guess as to what it does"""
        noble = {}
        noble["gender"] = random.choice(["m", "f"])
        noble["nobility"] = random.randint(1, 10)
        names = self.create_noble_name(noble["gender"], noble["nobility"])
        noble["full_name"] = names[0]
        noble["surname"] = names[1]
        noble["full_title"] = names[2]
        noble["extended_title"] = names[3]
        noble["id"] = self.find_appropriate_id()
        noble["relations"] = self.generate_relations()
        noble["wealth"] = random.randint(10, 9999)
        return noble

    def generate_relations(self):
        relations_dict = {}
        for name, noble in self.noble_manager.noble_instances.items():
            relations_dict[name] = random.randint(1,10)
        return relations_dict

    def load_names(self):
        with open("noblenames.json", "r") as file:
            coded = file.read()
        return json.loads(coded)

    def create_noble_name(self, gender, nobility):
        flag = True
        while flag == True:
            flag = False
            if gender == "m":                                   #Setting appropriate lists to use based on the Nobles stats.
                first_name = self.noblenames["first_male"]           #This part gets the appropriate gender lists
                titles = self.noblenames["titles_male"]
            else:
                first_name = self.noblenames["first_female"]
                titles = self.noblenames["titles_female"]
            if nobility >= 7:                                   #This part sets the appropriate ranked nobility lists
                placenames = self.noblenames["placenames_major"]
            elif nobility >= 4:
                placenames = self.noblenames["placenames_minor"]
            else:                                               #This bit unsets some variables of the noble is too shitty to have a title
                placenames = None
                titles = None
                full_title = None
            surname = random.choice(self.noblenames["surname"])                    #Setting final lists
            nickname = random.choice(self.noblenames["nicknames"])
            full_name_list = []
            for item in self.noble_manager.id_lookup:
                full_name_list.append(item[0])
            while True:
                full_name = "{} {}".format(random.choice(first_name), surname)    #Generates First and second name, stores under full_name
                if not full_name in full_name_list: break
            if titles:                                                  #Generates a title and place, stores under full_title"
                full_title = "{} {}".format(random.choice(titles), random.choice(placenames))
            extended_title = full_name + nickname  #adds a nickname to full_name, stores in extended_title
            if titles:                                          #If the nobility has a title (i.e. they are not shitty), adds it to extended title
                extended_title = "{}, {}".format(extended_title, full_title)

        return[full_name, surname, full_title, extended_title]

    def find_appropriate_id(self):
        """Nobles need to have distinct identification numbers. This lets that happen"""
        default_id = 100
        id_list = []
        for item in self.noble_manager.id_lookup:
            id_list.append(item[1])
        while True:
            if default_id in id_list:
                default_id += 1
                continue
            return default_id

if __name__ == "__main__":
    noble = NobleManager()
    print(noble.noble_instances["Mercy Shaw"].__dict__)
    options = [
    ("Create Noble", noble.create_noble),
    ("Patch Nobles", noble.patch_nobles),
    ("View Nobles", noble.view_nobles),
    ("View relations", noble.view_relations),
    ("View Single Noble", noble.view_single_noble),
    ("Execute Noble", noble.execute_noble),
    ("Execute all", noble.execute_all),
    ("Run Events", noble.run_events),
    ("Save File", noble.save_file)
    ]
    while True:
        print("\n")
        for i in range(len(options)):
            print("({}. {}) ".format(i, options[i][0]), end="")
        while True:
            try:
                choice = int(input("\nDo what?"))
                break
            except ValueError:
                print("Use a number dude")
        try:
            method = options[choice][1]
        except IndexError:
            print("Not a valid choice homie")
        dependancy_list = inspect.signature(method)
        arg_list = []
        for item in dependancy_list.parameters:
            arg_list.append(input("Need argument: {}\n".format(item)))
        print("\n{}".format(method(*arg_list)))
