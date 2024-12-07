
import sys
sys.path.append('../../')
from resources import AC_utils as AC
import requests

def pull_all():
    def pull_template(modelname):
        return requests.post(AC.URL,json={
        "action": "modelTemplates",
        "version": 6,
        "params": {
            "modelName": modelname
        }
        })

    def pull_styling(modelname):
        return requests.post(AC.URL,json={
        "action": "modelStyling",
        "version": 6,
        "params": {
            "modelName": modelname
        }
        })

    card_info=pull_template("JihAnki").json()
    card_info=card_info["result"]
    styling_info=pull_styling("JihAnki").json()
    styling_info=styling_info["result"]
    
    with open("HyougenFront.html", "w") as text_file:
        text_file.write(card_info["readHyougen"]["Front"])
    with open("HyougenBack.html", "w") as text_file:
        text_file.write(card_info["readHyougen"]["Back"])
    with open("ReibunFront.html", "w") as text_file:
        text_file.write(card_info["readReibun"]["Front"])
    with open("ReibunBack.html", "w") as text_file:
        text_file.write(card_info["readReibun"]["Back"])
    with open("ReibunBack.html", "w") as text_file:
        text_file.write(card_info["readReibun"]["Back"])
    with open("JihAnki.css", "w") as text_file:
        text_file.write(styling_info["css"])

def push_all():
    card={"readHyougen":{"Front":"","Back":""},
        "readReibun":{"Front":"","Back":""}}
    style={"css":""}
    with open("HyougenFront.html", "r") as file:
        card["readHyougen"]["Front"]=file.read()
    with open("HyougenBack.html", "r") as file:
        card["readHyougen"]["Back"]=file.read()
    with open("ReibunFront.html", "r") as file:
        card["readReibun"]["Front"]=file.read()
    with open("ReibunBack.html", "r") as file:
        card["readReibun"]["Back"]=file.read()
    with open("JihAnki.css", "r") as file:
        style["css"]=file.read()

    #%%
    res=requests.post(AC.URL,json={
    "action": "updateModelTemplates",
    "version": 6,
    "params": {
        "model": {
            "name":"JihAnki",
            "templates":{
                "readHyougen":{
                    "Front":card["readHyougen"]["Front"],
                    "Back":card["readHyougen"]["Back"],
                },
                "readReibun":{
                    "Front":card["readReibun"]["Front"],
                    "Back":card["readReibun"]["Back"]
                }
            }
        }}})

    res=requests.post(AC.URL,json={
        "action": "updateModelStyling",
        "version": 6,
        "params": {
            "model": {
                "name":"JihAnki",
                "css":style["css"]
            }}})

if __name__=="__main__":
    push_all()
# %%
