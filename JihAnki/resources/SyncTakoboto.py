#%%
"""
Process cards:
1. Take takoboto template cards from takoboto deck
2. Create data for a JihAnki card (processentry, oubunsha, pronounceNHK, etc.)
3. Send update to anki
"""
import requests
import AC_utils as AC #ankiconnect utils
import LangUtils as LU
URL=AC.URL
import pandas as pd
import numpy as np

colnames=AC.colnames
userColnames=AC.userColnames
### Check if card browser is open (AnkiConnect bug: silently prevents updates when true, hence warning)
if AC.CardBrowserOpen():
    print("Card browser is open; aborting SyncTakoboto")
    quit()
### Make a DF for existing collection, a DF for new entries
import os
from datetime import datetime
datestr = datetime.today().strftime('%Y_%m_%d')
existingCollection=AC.load("JihAnki")["result"]
existingDF=AC.AnkiConnect_to_Pandas(existingCollection,colnames)
takobotoCollection=AC.load("Takoboto")["result"]

# copy relevant info from Takoboto into df

tako_df = pd.DataFrame(data=np.empty((len(takobotoCollection),
                            len(colnames)),dtype=str),
                            columns=colnames)
for i in range(len(takobotoCollection)):
    note = takobotoCollection[i]["fields"]
    tako_df.at[i,"hyougen"]=note["Japanese"]["value"]
    tako_df.at[i,"imi"]=note["Meaning"]["value"]
    tako_df.at[i,"reibun"]=note["Sentence"]["value"]
    tako_df.at[i,"reibun_imi"]=note["SentenceMeaning"]["value"]
    tako_df.at[i,"source_tag"]="takoboto"
_inlen=len(tako_df)
tako_df =tako_df[~tako_df["hyougen"].isin(tako_df["hyougen"])]\
    .reset_index(drop=True)
_final_len=len(tako_df)
#%%
prevMax = np.max(existingDF.entryID.values.astype(int))
tako_df["entryID"]=prevMax+1
tako_df["entryID"]+=np.arange(0,len(tako_df))
tako_df["audio"]=""
tako_df["hyougen_yomikata"]=""
tako_df["reibun_yomikata"]=""
import ProcessEntry as pe
import OubunshaLookup as oubunsha
import PronounceNHK
for j in range(len(tako_df)):
    i=tako_df.index.values[j]
    tako_df.at[i, "hyougen"]=tako_df.at[i, "hyougen"].replace(" ","")
    HGback, RBback = pe.parseEntry(tako_df.at[i, "hyougen"],
                    tako_df.at[i, "reibun"])
    tako_df.at[i,"yomikata"]=HGback
    tako_df.at[i,"reibun_yomikata"]=RBback
    tako_df.at[i,"jiten"]=oubunsha.lookup(tako_df.at[i, "hyougen"])
    fetch_audio=PronounceNHK.update_one(tako_df.iloc[i].to_dict())
    if fetch_audio is None: # try to lookup by kana
        PronounceNHK.alt_lookup(tako_df.iloc[i].to_dict(),
            LU.get_yomikata(tako_df.at[i, "hyougen"])[0])
    if fetch_audio is None:
        fetch_audio=""
    else:
        fetch_audio=fetch_audio["audio"]
    tako_df.at[i,"audio"]=fetch_audio
print(f"Processed {len(tako_df)} new entries from Takoboto (skipped {_inlen-_final_len} duplicates)")
addRes = AC.AddFromDF(tako_df)

res = requests.post(URL,json={
    "action": "sync",
    "version": 6
})

AC.flushNotes("Takoboto")