"""
In October 2026 I am deciding to use Anki again, which is painful due to the enormous backlog.
I need a way to add new cards as I did before, and to gradually reintroduce my old cards.


"""
#%%
import requests
import AC_utils as AC #ankiconnect utils
import LangUtils as LU
URL=AC.URL
import pandas as pd


colnames=AC.colnames
userColnames=AC.userColnames
### Check if card browser is open (AnkiConnect bug: silently prevents updates when true, hence warning)
if AC.CardBrowserOpen():
    print("Card browser is open; aborting RehabScheduler")
    quit()
import SyncTakoboto
### Make a DF for existing collection
import os
from datetime import datetime
datestr = datetime.today().strftime('%Y_%m_%d')
collection=AC.load("JihAnki")["result"]
df=pd.DataFrame(collection)
class Note:
    def __init__(self, note):
        self.note=note
        self._fields=note["fields"]
        self.entryID=int(self._fields["entryID"]["value"])
        self.cardIDs=self.note["cards"]
    def reorder(self):
        if self.entryID>1856:
            return
        due=int(1e6)+self.entryID
        res = requests.get(URL,timeout=1.0)
        res = requests.post(URL, json={
            "action":"setDueDate",
            "version": 6,
            "params":{
                "cards":self.cardIDs,
                "days":str(due),
            }
        })
        return res
    def getCards(self):
        res = requests.get(URL,timeout=1.0)
        res = requests.post(URL, json={
            "action":"cardsInfo",
            "version": 6,
            "params":{"cards":self.cardIDs}
        })
        return res
    def DueString(self,jsonstr):
        card=jsonstr["result"][0]
        outstr=f"cardID:{card['cardId']}\n"\
            +f"entryID:{card['fields']['entryID']['value']}\n"\
            +f"type:{card['type']}\n"\
            +f"due:{card['due']}"
        return outstr+"\n"

#%%
df['entryID']=[int(fields["entryID"]["value"])\
                for fields in df["fields"]]
cols=[df.columns[-1]]
cols.extend(df.columns[:-1])
df=df[cols]

card_df=[]
for i in range(len(df)):
    card_df.extend(Note(df.iloc[i]).getCards().json()["result"])
card_df=pd.DataFrame(card_df)
del df
card_df["entryID"]=[fields["entryID"]["value"] for fields in card_df["fields"]]
card_df=card_df[["cardId","entryID","note",
                "type","due","reps","lapses","mod"]]
#%%
res = requests.get(URL,timeout=1.0)
res = requests.post(URL, json={
    "action":"areSuspended",
    "version": 6,
    "params":{
        "cards":card_df["cardId"].values.tolist(),
    }
})
card_df.loc[:,"suspended"]=res.json()["result"]
#%%

upnext=card_df[(card_df["type"]==0)&(~card_df["suspended"])]
upnext=upnext.sort_values("due")
#%%
print(f"RehabScheduler::totally new cards: {len(upnext)}")
print("\n".join(str(id) \
                for id in upnext["entryID"].values.tolist()))
if len(upnext)<12:
    candidates=card_df[(card_df["type"])==2\
                    & (card_df["due"]>int(1e6))\
                    & (~card_df['suspended'])]
    candidates.sort_values("due", inplace=True)
    queuesize=12-len(upnext)
    res = requests.get(URL,timeout=1.0)
    print(f"RehabScheduler::reintroducing old cards. entryIDs:")
    print(candidates[:queuesize]["entryID"].values.tolist())
    if True:
        res = requests.post(URL, json={

            "action": "forgetCards",
            "version": 6,
            "params": {
                "cards": [candidates[:queuesize]["cardId"].values.tolist()],
            }
        })
    


# %%
