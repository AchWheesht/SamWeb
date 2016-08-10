import sys
sys.path.append("sam_game")
sys.path.append("wiki_in_the_valley")
from flask import Flask, render_template, request, make_response
import nobles_management
import misc_tools
import json
import valley_generator
import time

wiki_in_use = False
test_phrase = "hello!"

app = Flask(__name__)
NobleManager = nobles_management.NobleManager("noble_manager/nobles_dictionary.json", "noble_manager/noblenames.json")

@app.route("/")
def index():
    return render_template("home_template.html")

@app.route("/blank")
def blank():
    return render_template("blank.html")

@app.route("/noblehq")
def noblehq():
    name_list = NobleManager.id_lookup
    return render_template("noblehq_template.html", name_list = name_list)

@app.route("/noblepost", methods=["GET", "POST"])
def noblepost():
    print("Mark 1")
    name_list = NobleManager.id_lookup
    try:
        if request.method == "GET":
            pass
        if request.method == "POST":
            print("Mark 2")
            action = (request.form["action"])
            if action == "viewInfo":
                print("Mark 3")
                name = NobleManager.get_name_from_id(request.form["noble"])
                function_return = NobleManager.view_single_noble(name)
            if action == "executeNoble":
                name = NobleManager.get_name_from_id(request.form["noble"])
                function_return = NobleManager.execute_noble(name)
        else: return "nothing hahaha"
    except Exception as e:
        print(e)
        return "you ballsed up m8"
    if name_list: name_list = misc_tools.list_to_option_string(name_list)
    response = (function_return, name_list)
    json_response = json.dumps(response)
    return json_response

@app.route("/createnoble", methods=["GET"])
def createnoble():
    function_return = NobleManager.create_noble()
    name_list = NobleManager.id_lookup
    name_list = misc_tools.list_to_option_string(name_list)
    response = (function_return, name_list)
    json_response = json.dumps(response)
    return json_response

@app.route("/deleteall", methods=["GET"])
def deleteall():
    function_return = NobleManager.execute_all()
    name_list = NobleManager.id_lookup
    name_list = misc_tools.list_to_option_string(name_list)
    response = (function_return, name_list)
    json_response = json.dumps(response)
    return json_response

@app.route("/nobles_play", methods=["POST"])
def nobles_play():
    function_return = NobleManager.run_events()
    print(function_return)
    name_list = NobleManager.id_lookup
    name_list = misc_tools.list_to_option_string(name_list)
    response = (function_return, name_list)
    json_response = json.dumps(response)
    return json_response


@app.route("/wiki_in_the_valley_o")
def wiki_in_the_valley_o():
    return render_template("template_in_the_valley_o.html")

@app.route("/get_song", methods=["POST"])
def get_song():
    global wiki_in_use
    url = request.form["url"]
    if url[:24] != "https://en.wikipedia.org" and url[:25] != "https://www.wikipedia.org":
        return json.dumps(("use a wikipedia url!", "use a wikipedia url!"))
    while True:
        if wiki_in_use == True:
            print("In use, waiting...")
            time.sleep(1)
        elif wiki_in_use == False:
            wiki_in_use = True
            break
    list_and_song = valley_generator.make_a_song(url)
    wiki_in_use = False
    list_and_song[0] = list_to_string(list_and_song[0])
    response = json.dumps(list_and_song)
    return response

@app.route("/wiki_in_the_valley_o/about")
def about_wiki():
    return render_template("about_wiki.html")

def list_to_string(the_list):
    string = ""
    for item in the_list:
        string += item
        string += "\n"
    return string

if __name__ == "__main__":
	bind = "127.0.0.1"

	if len(sys.argv) == 2:
		bind = sys.argv[1]

	app.run(host=bind)
