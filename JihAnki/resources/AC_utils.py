"""
AnkiConnect utility functions:
Fetch card field information, update cards, delete cards.
"""
#%%
from json import JSONDecodeError
import requests
import pandas as pd
import numpy as np

colnames = ["entryID",
                    "hyougen",
                    "imi",
                    "yomikata",
                    "reibun",
                    "reibun_imi",
                    "reibun_yomikata",
                    "source_tag",
                    "audio",
                    "jiten"]
userColnames=["hyougen",
              "imi",
              "reibun",
              "reibun_imi",
              "source_tag"]

# New method since WSL2 2.0.0
# Requires windowsIP mirroring

URL="http://127.0.0.1:8765"
#%%
def request(json):
    res=requests.post(URL, json)
    return res.json()

def wakeAnki():
    #TODO doesn't quite work right
    delta=0.4
    try:
        response=requests.get(URL, timeout=delta)
    except requests.exceptions.ConnectionError:
        print("Calling cmd")
        ### Launching anki properly requires calling cmd to call a script that calls the program
        import os
        batchfile=r"""cd C:\Users\grego\AppData\Local\Programs\Anki |"""+\
        r""" start C:\Users\grego\AppData\Local\Programs\Anki\anki.exe |"""+\
        r""" exit"""
        with open("/mnt/c/Users/grego/Documents/Nihongo/launchAnki.bat",'w') as file:
            file.write(batchfile)
        command=r'cmd.exe /C "C:\Users\grego\Documents\Nihongo\launchAnki.bat" &'
        os.system(command)
        while True:
            try:
                response=requests.get(URL, timeout=delta)
                if response.status_code==200:
                    break
            except requests.exceptions.ConnectionError:
                pass
    except requests.exceptions.Timeout:
        print("The request timed out")
    return response


#%%
def SelectCard(id:int):
    res = requests.get(URL,timeout=1.0)
    res = requests.post(URL, json={
        "action":"guiSelectNote",
        "version": 6,
        "params":{"note":id} # 0 is a dummy card (clears selection)    
    })
    return res

def CardBrowserOpen():
    return SelectCard(0).json()["result"]

def load(deckname, cardType=None):
    if cardType==None:
        if deckname=="JihAnki":
            model="JihAnki"
        if deckname=="Takoboto":
            model="jp.takoboto"
        if deckname=="~DOJG":
            model="aDOJG"
    else:
        model=cardType
    res = requests.get(URL,timeout=1.0)
    res = requests.post(URL, json={
        'action': 'findNotes',
        'version': 6,
        'params': {
            'query': 'deck:'+deckname+" "\
                     'note:'+model
            ,
        },
    }).json()
    detail_res = requests.post(URL, json={
        'action': 'notesInfo',
        'version': 6,
        'params': {
            'notes': res['result']
        },
    }).json()
    return detail_res

def AnkiConnect_to_Pandas(collection,colnames):
    adhocColNames = list(collection[0]["fields"].keys())
    DF = pd.DataFrame(data=np.empty((len(collection),len(colnames)),dtype=str),
                        columns=adhocColNames)
    for i in range(len(collection)):
        entry = collection[i]["fields"]
        for key in colnames:
            DF.iloc[i][key]=entry[key]["value"]
    return DF

def AddFromDF(myDF):
    mycol = Pandas_to_JHKCollection(myDF)
    res = requests.post(URL, json={
            'action': 'addNotes',
            'version': 6,
            'params': {
                'notes': mycol,
            },
        }).json()
    return res

def Pandas_to_JHKCollection(df):
    outCollection=[None]*len(df)
    for i in range(len(df)):
        fieldsdict = dict.fromkeys(df.columns.values)
        for key in df.columns.values:
            fieldsdict[key]=str(df.iloc[i][key])
        outCollection[i]=({
            "deckName":"JihAnki",
            "modelName":"JihAnki",
            "fields":fieldsdict,
            "tags":[], # changed
        })
    return outCollection

def getNoteIDFromDeck(deckname):
    collection=load(deckname)["result"]
    collectionIDlist=[]
    for entry in collection:
        collectionIDlist.append(entry["noteId"])
    return collectionIDlist

def flushNotes(deckname="Takoboto"):
    collectionIDlist=getNoteIDFromDeck(deckname)
    res = requests.post(URL,json={
        'action':"deleteNotes",
        "version":6,
        "params":{"notes":collectionIDlist}}
        )
    return res

def update_all(fn=lambda x:{"jiten":""}):
    """
    use with caution
    fn should take a dict of all fields as input
    and put out a dict of only the fields to be updated.
    If the cards themselves are not to be changed, fn can return None.
    """
    notes=load("JihAnki")["result"]
    for note in notes:
        noteID=note["noteId"]
        args={}
        for field in list(note["fields"].keys()):
            # sorry about the redundant dereferencing
            fieldkey=field
            fieldvalue=note["fields"][field]["value"]
            args[fieldkey]=fieldvalue
        if int(args["entryID"])%100==0:
            print(args["entryID"]+"/"+str(len(notes)))
        update=fn(args)
        if update is None:
            continue
        if "hyougen" in list(update.keys()):
            print(" illegal request to update hyougen from AC.update_all")
            return 1
        if "entryID" in list(update.keys()):
            print(" illegal request to update entryID from AC.update_all")
            return 1

        SelectCard(0)
        requests.post(URL,json={
            "action": "updateNoteFields",
            "version": 6,
            "params": {
            "note": {
            "id": noteID,
            "fields": update,
            }
            }
            })
        SelectCard(noteID) # snap back to the modified card        


def update_one(hyougen, fn):
    res = requests.post(URL, json={
        'action': 'findNotes',
        'version': 6,
        'params': {
            'query': 'deck:'+"JihAnki"+" "\
                     'hyougen:'+hyougen
            ,
        },
    }).json()
    detail_res = requests.post(URL, json={
        'action': 'notesInfo',
        'version': 6,
        'params': {
            'notes': res['result']
        },
    }).json()
    try:
        if len(detail_res["result"])>1:
            print(" WARNING : several cards matched identifier "+hyougen)
        note=((detail_res["result"])[0])
    except IndexError:
        print(" ERROR : Couldn't find card with identifier "+hyougen)
        return None
    noteID = note["noteId"]
    args={}
    for field in list(note["fields"].keys()):
        # sorry about the redundant dereferencing
        fieldkey=field
        fieldvalue=note["fields"][field]["value"]
        args[fieldkey]=fieldvalue

    update=fn(args)
    if update is None:
        return None

    SelectCard(0) # DEselects cards; prevents http conflict
    modification_res = requests.post(URL,json={
    "action": "updateNoteFields",
    "version": 6,
    "params": {
        "note": {
            "id": noteID,
            "fields": update
    }
    }
    })
    SelectCard(noteID) # snap back to the modified card
    print(str(modification_res)=="<Response [200]>")

if __name__=="__main__":
    print("checkBrowserOpen: ")
    print(CardBrowserOpen())