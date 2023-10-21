#%%
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
                    "audio"]
userColnames=["hyougen",
              "imi",
              "reibun",
              "reibun_imi",
              "source_tag"]


with open("/etc/resolv.conf") as file:
    windowsIP = file.read()
file.close()
NStag = "nameserver"
windowsIP=windowsIP[windowsIP.find(NStag)+len(NStag)+1:]
windowsIP=windowsIP.strip("\n")
URL = "http://"+windowsIP+":8765"
#%%
def load(deckname):
    if deckname=="JihAnki":
        model="JihAnki"
    else:
        model="jp.takoboto"
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
    DF = pd.DataFrame(data=np.empty((len(collection),9),dtype=str),
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
# %%
