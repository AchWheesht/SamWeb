
from flask import Flask, render_template, request
import nobles_management_beta
import misc_tools
import json
import sys

app = Flask(__name__)
NobleManager = nobles_management_beta.NobleManager()

@app.route("/")
def index():
    return render_template("home_template.html")

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

@app.route("/wiki_in_the_valley_o")
def wiki_in_the_valley_o():
    return render_template("template_in_the_valley_o.html")

@app.route("/get_song", methods=["POST"])
def get_song():
    print("INVOKED")
    return request.form["url"]

if __name__ == "__main__":
	bind = sys.argv[1]

	if not bind:
		bind = "127.0.0.1"

	app.run(host=bind)
