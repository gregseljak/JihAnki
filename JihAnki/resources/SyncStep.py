#%%
import requests
with open("/etc/resolv.conf") as file:
    windowsIP = file.read()
file.close()
NStag = "nameserver"
windowsIP=windowsIP[windowsIP.find(NStag)+len(NStag)+1:]
windowsIP=windowsIP.strip("\n")
URL = "http://"+windowsIP+":8765"
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
existingCollection=load("JihAnki")["result"]

#%%
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
#%%
def AnkiConnect_to_Pandas(collection):
    adhocColNames = list(collection[0]["fields"].keys())
    preDF = pd.DataFrame(data=np.empty((len(collection),9),dtype=str),
                        columns=adhocColNames)
    for i in range(len(collection)):
        entry = collection[i]["fields"]
        for key in colnames:
            preDF.iloc[i][key]=entry[key]["value"]
    return preDF
existingDF=AnkiConnect_to_Pandas(existingCollection)


def Pandas_to_Collection(df):
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

def AddFromDF(myDF):
    mycol = Pandas_to_Collection(myDF)
    res = requests.post(URL, json={
            'action': 'addNotes',
            'version': 6,
            'params': {
                'notes': mycol,
            },
        }).json()

#def main():
#%%
import os
from datetime import datetime
datestr = datetime.today().strftime('%Y_%m_%d')
existingDF=AnkiConnect_to_Pandas(existingCollection)

#%%
takobotoCollection=load("Takoboto")["result"]
takobotoIDlist=[]
for entry in takobotoCollection:
    takobotoIDlist.append(entry["noteId"])
res = requests.post(URL,json={
    'action':"deleteNotes",
    "version":6,
    "params":{"notes":takobotoIDlist}}
    )

userDF = pd.DataFrame(data=np.empty((len(takobotoCollection),
                                     len(colnames)),dtype=str),
                columns=colnames)
for i in range(len(takobotoCollection)):
    note = takobotoCollection[i]["fields"]
    userDF.at[i,"hyougen"]=note["Japanese"]["value"]
    userDF.at[i,"imi"]=note["Meaning"]["value"]
    userDF.at[i,"reibun"]=note["Sentence"]["value"]
    userDF.at[i,"reibun_imi"]=note["SentenceMeaning"]["value"]
    userDF.at[i,"source_tag"]="takoboto"
localxl = "/home/greg/nihongo/JihAnki/resources/_jihanki.xlsx"
os.popen("cp ~/grego/Desktop/JihAnki.xlsx "\
            +localxl)
path_to_outcsv="~/nihongo/JihAnki/outputCsv/out_"+datestr
#%%
XLuserDF=pd.read_excel(localxl,sheet_name="userSheet",header=0)
XLuserDF.fillna("", inplace=True)
def filter_rows_by_values(df, col, values):
    return df[~df[col].isin(values)]
XLuserDF=filter_rows_by_values(XLuserDF, "hyougen", userDF.hyougen.values)
userDF=filter_rows_by_values(userDF, "hyougen", existingDF.hyougen.values)
#%%
prevMax = 0
for value in existingDF.entryID.values:
    if int(value)>prevMax:
        prevMax=int(value)
userDF["entryID"]=prevMax+1
userDF["entryID"]+=np.arange(0,len(userDF))
userDF["audio"]=""
userDF["hyougen_yomikata"]=""
userDF["reibun_yomikata"]=""
import ProcessEntry as pe
#%%
for i in range(len(userDF)):
    userDF.at[i, "hyougen"]=userDF.at[i, "hyougen"].replace(" ","")
    HGback, RBback = pe.parseEntry(userDF.at[i, "hyougen"],
                    userDF.at[i, "reibun"])
    userDF.at[i,"yomikata"]=HGback
    userDF.at[i,"reibun_yomikata"]=RBback
AddFromDF(userDF)

existingDF = pd.concat([existingDF, userDF])
existingDF.to_excel("~/grego/Documents/Nihongo/backend_JihAnki.xlsx",
                     sheet_name="backend_sheet",
                     columns=colnames,
                     index=False,
                     header=True
                     )
#%%
userDF=pd.DataFrame(data=np.empty((1,len(userColnames)),dtype=str),columns=userColnames)
userDF.to_excel("~/grego/Desktop/JihAnki.xlsx",
                sheet_name="userSheet",
                index=False,
                header=userColnames,
                )
# %%
