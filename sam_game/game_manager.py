import nobles_management
import kingdom
import inspect

# noble_manager = nobles_management.NobleManager("nobles_dictionary.json", "noblenames.json")
# kingdom_manager = kingdom.KingdomManager()

class LogStat():
    def __init__(self):
        self.log = []

    def __get__(self, instance, owner):
        return self.log

    def __set__(self, instance, value):
        self.log.append(value)

class LogClass():
    log = LogStat()

class GameManager():
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
                param = arg_list[i]
                try: arg = func_args[i]
                except IndexError: arg = None
                arg_list[i] = (param, arg)
            owner = arg_list[0][1] if arg_list[0][0] == "self" else None
            string = "{} Func={} Args:".format(owner, func.__name__)
            for item in arg_list:
                string += "({}={})".format(item[0], item[1])
            self.log.log = string
            if func.__name__ == "__init__":
                return
            return func(*args)
            return func_wrapper

    def __init__(self):
        self.log = LogClass()
        self.noble_manager = nobles_management.NobleManager("nobles_dictionary.json", "noblenames.json", self.log)
        self.kingdom_manager = kingdom.KingdomManager("shires_dictionary.json", self.log)

    def dump_log(self):
        log_dump = self.log.log
        with open("game_log.txt", "w") as file:
            for item in log_dump:
                file.write("{}\n".format(item))

    @log_wrapper
    def run_events(self):
        event_runner = EventRunner(self, self.noble_manager.compile_instance_list(), self.log)
        return event_runner.run_noble_events()

class EventRunner(GameManager):
    @GameManager.log_wrapper
    def __init__(self, game_manager, action_list, log):
        self.log = log
        self.game_manager = game_manager
        self.action_list = action_list

    @GameManager.log_wrapper
    def run_noble_events(self):
        string = ""
        for noble in self.action_list:
            if noble.marked_for_death:
                string += "{} would do something, but most of their time is being taken up by being dead".format(noble.full_name)
            else:
                string += "\n\n"
                string += noble.perform_action()
                death_message = self.check_for_noble_deaths()
                if death_message:
                    string += death_message
        return string

    @GameManager.log_wrapper
    def check_for_noble_deaths(self):
        death_list = []
        instance_list = self.game_manager.noble_manager.compile_instance_list()
        for noble in instance_list:
            if noble.marked_for_death == True:
                death_list.append(noble)
        string = ""
        for noble in death_list:
            if noble in self.action_list:
                self.action_list.remove(noble)
                string += "\n" + self.game_manager.noble_manager.execute_noble(noble.full_name)

    def __str__(self):
        return "<EventRunner Instance>"

    def __repr__(self):
        return "<EventRunner Instance>"


if __name__ == "__main__":
    game = GameManager()
    nobles_options = [
    ("Create Noble", game.noble_manager.create_noble),
    ("Patch Nobles", game.noble_manager.patch_nobles),
    ("View Nobles", game.noble_manager.view_nobles),
    ("View relations", game.noble_manager.view_relations),
    ("View Single Noble", game.noble_manager.view_single_noble),
    ("Execute Noble", game.noble_manager.execute_noble),
    ("Execute all", game.noble_manager.execute_all),
    ("Torment Nobles", game.noble_manager.torment_nobles),
    ("Save File", game.noble_manager.save_file),
    ("Change Manager", "Change Manager")
    ]

    kingdom_options = [
    ("create shire", game.kingdom_manager.create_shire),
    ("View all", game.kingdom_manager.view_all),
    ("Change Manager", "Change Manager")
    ]

    game_options = [
    ("Run Events", game.run_events),
    ("Dump Log", game.dump_log),
    ("Change Manager", "Change Manager")
    ]

    current_options = game_options

    while True:
        print("\n")
        for i in range(len(current_options)):
            print("({}. {}) ".format(i, current_options[i][0]), end="")
        while True:
            try:
                choice = int(input("\nDo what?"))
                method = current_options[choice][1]
                break
            except ValueError:
                print("Use a number dude")
            except IndexError:
                print("Not a valid choice homie")
        if method == "Change Manager":
            print("Change Where?")
            option_list = [("Noble Manager", nobles_options), ("Kingdom Manager", kingdom_options), ("Game Manager", game_options)]
            for item in option_list:
                print(option_list.index(item), ": ", item[0])
            current_options = option_list[int(input("?"))][1]
            continue
        try:
            print("\n{}".format(method()))
        except Exception as e:
            game.dump_log()
            raise e
