from flask import Flask, render_template, request
import game_Nobles
import misc_tools
import json

app = Flask(__name__)
Nobles = game_Nobles.NoblesClass()

@app.route("/")
def index():
    return render_template("home_template.html")

@app.route("/noblehq")
def noblehq():
    name_list = Nobles.list_names()
    return render_template("noblehq_template.html", name_list = name_list)

@app.route("/noblepost", methods=["GET", "POST"])
def noblepost():
    print("Mark 1")
    try:
        if request.method == "GET":
            pass
        if request.method == "POST":
            print("Mark 2")
            action = (request.form["action"])
            if action == "viewInfo":
                function_return = Nobles.get_stats(request.form["noble"])
                name_list = Nobles.list_names()
            if action == "executeNoble":
                function_return = Nobles.remove_noble(request.form["noble"])
                name_list = Nobles.list_names()
        else: return "nothing hahaha"
    except Exception as e:
        print(e)
        return "you ballsed up m8"
    name_list = misc_tools.list_to_option_string(name_list)
    response = (function_return, name_list)
    json_response = json.dumps(response)
    return json_response

@app.route("/createnoble", methods=["GET"])
def createnoble():
    function_return = Nobles.create_noble_random()
    name_list = Nobles.list_names()
    name_list = misc_tools.list_to_option_string(name_list)
    response = (function_return, name_list)
    json_response = json.dumps(response)
    return json_response

@app.route("/deleteall", methods=["GET"])
def deleteall():
    function_return = Nobles.delete_all()
    name_list = Nobles.list_names()
    name_list = misc_tools.list_to_option_string(name_list)
    response = (function_return, name_list)
    json_response = json.dumps(response)
    return json_response

if __name__ == "__main__":
    app.run()
