import nobles_management
import kingdom
import inspect

# noble_manager = nobles_management.NobleManager("nobles_dictionary.json", "noblenames.json")
# kingdom_manager = kingdom.KingdomManager()

class GameManager():
    def __init__(self):
        self.log = LogClass()
        self.noble_manager = nobles_management.NobleManager("nobles_dictionary.json", "noblenames.json", self.log)
        self.kingdom_manager = kingdom.KingdomManager("shires_dictionary.json", self.log)

    def dump_log(self):
        log_dump = self.log.log
        with open("game_log.txt", "w") as file:
            for item in log_dump:
                file.write("{}\n".format(item))


class LogStat():
    def __init__(self):
        self.log = []

    def __get__(self, instance, owner):
        return self.log

    def __set__(self, instance, value):
        self.log.append(value)

class LogClass():
    log = LogStat()

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
    ("Run Events", game.noble_manager.run_events),
    ("Save File", game.noble_manager.save_file),
    ("Change Manager", "Change Manager"),
    ("Dump Log", game.dump_log)
    ]

    kingdom_options = [
    ("create shire", game.kingdom_manager.create_shire),
    ("View all", game.kingdom_manager.view_all),
    ("Change Manager", "Change Manager"),
    ("Dump Log", game.dump_log)
    ]

    current_options = nobles_options

    while True:
        print("\n")
        for i in range(len(current_options)):
            print("({}. {}) ".format(i, current_options[i][0]), end="")
        while True:
            try:
                choice = int(input("\nDo what?"))
                break
            except ValueError:
                print("Use a number dude")
        try:
            method = current_options[choice][1]
        except IndexError:
            print("Not a valid choice homie")
        if method == "Change Manager":
            print("Change Where?")
            option_list = [("Noble Manager", nobles_options), ("Kingdom Manager", kingdom_options)]
            for item in option_list:
                print(option_list.index(item), ": ", item[0])
            current_options = option_list[int(input("?"))][1]
            continue
        try:
            print("\n{}".format(method()))
        except Exception as e:
            game.dump_log()
            raise e
