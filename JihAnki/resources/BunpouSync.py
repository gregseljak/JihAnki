#%%
import AC_utils as AC
import ProcessEntry as PE

"""
How to use: For a desired grammar point
    1. find relevant cards in "~DOJG deck" and mark with flag:1 (red flag)
    2. run python3 ./BunpouSync.py (just like with SyncStep.py)
SyncStep and BunpouSync are complimentary and should be run together.

- jihanki_bunpou cards can hold up to three sentences. 

- To replace a sentence,
    delete the contents of it reibunI field completely (ex. such that reibun2==""),
    flag the desired sentence in ~DOJG, sync and then run.

jihanki_bunpou cards have a different note type and different entryID numbers
than normal jihanki cards (jihanki_bunpou has more fields,
entryIDs start a 1000001, front/back is slightly different)

(DOJG = dictionary of japanese grammar)

# todo - clean up this file
"""
colnames = ["entryID",
            "hyougen",
            "imi",
            "yomikata",
            "reibun1",
            "reibun1_imi",
            "reibun1_yomikata",
            "reibun2",
            "reibun2_imi",
            "reibun2_yomikata",
            "reibun3",
            "reibun3_imi",
            "reibun3_yomikata",
            "context",
            "dojg Grammar Point",
            "audio"]

## Find User Flagged Cards
import requests
res = requests.post(AC.URL,json={
    "action": "findCards",
    "version":6,
    "params": {
        "query": "deck:~DOJG flag:1",
    }
        }).json()
mc_id=res["result"]
mc_id

### Get info from User-Flagged cards
res = requests.post(AC.URL,json={
    "action": "cardsInfo",
    "version":6,
    "params": {
        "cards": mc_id
    }
        }).json()
flagged_card_info=res["result"]

### For each card:
for idx in range(len(flagged_card_info)):
    cardInfo = flagged_card_info[idx]
    dg_fields=cardInfo["fields"]

    # See if a JihAnki entry exists
    res=requests.post(AC.URL,json={
        "action": "findNotes",
        "version":6,
        "params": {
        "query": 'deck:JihAnki "dojg Grammar Point:'\
            +dg_fields["Grammar Point"]["value"]+'"'
        }
    })
    jihNoteIds=res.json()["result"]
    
    ### If no JihAnki note was found, create one with good entryID
    if len(jihNoteIds)==0:
        existing_notes=AC.load("JihAnki","jihanki_bunpou")["result"]
        prevmax=0
        for jhb_note in existing_notes:
            prevmax=max(prevmax, int(jhb_note["fields"]["entryID"]["value"]))
        # Some DJOG entries have inconsistent formatting; remove ASCII chars
        gp= ''.join([i if ord(i)>128 else '' for i in dg_fields["Grammar Point"]["value"]])
        res=requests.post(AC.URL,json={
            "action":"addNote",
            "version":6,
            "params":{
                "note":{
                    "deckName":"JihAnki",
                    "modelName":"jihanki_bunpou",
                    "fields":{
                        "entryID":str(prevmax+1),
                        "hyougen":gp,
                        "imi":dg_fields["Explanation"]["value"],
                        "dojg grammar point":dg_fields["Grammar Point"]["value"]
                    }
                }
            }
        })
        jihNoteIds=[res.json()["result"]]


    # get info from existing note
    res=requests.post(AC.URL,json={
        "action": "notesInfo",
        "version":6,
        "params": {
            "notes":jihNoteIds
        }
    })
    existing_note=res.json()["result"]
    if len(existing_note)>1:
        print("Warning - found too many matching notes in Jihanki for DOJG gp "\
            +dg_fields["Grammar Point"])
    existing_note=existing_note[0]
    enfields=existing_note["fields"]
    # find an empty space in the note for the sentence
    j=-1
    for i in range(1,4):
        if enfields["reibun"+str(i)]["value"]==dg_fields["Japanese"]["value"]:
            print("skipping sentence; already in note:"+dg_fields["Grammar Point"]["value"])
        if enfields["reibun"+str(i)]["value"]=="":
            j=i
            break
    if j==-1:
        print("Skipping sents; No empty slot was found for a new reibun: "\
              +dg_fields["Grammar Point"]["value"])
        continue
    # construct the sentence
    reibun=dg_fields["Japanese"]["value"]
    imi=dg_fields["English"]["value"]
    yomikata=PE.create_reibun(dg_fields["Japanese"]["value"])
    yomikata=yomikata[yomikata.find("<br>"):]
    yomikata="<strong>"+enfields["hyougen"]["value"]+\
        "</strong>"+yomikata
    # update note
    AC.SelectCard(0)
    res=requests.post(AC.URL,json={
        "action":"updateNoteFields",
        "version":6,
        "params":{
            "note":{
            "id":existing_note["noteId"],
            "fields":{
                "reibun"+str(j):reibun,
                "reibun"+str(j)+"_imi":imi,
                "reibun"+str(j)+"_yomikata":yomikata,
                }
            }
        }
    })
    if idx+1==len(flagged_card_info):
        AC.SelectCard(existing_note["noteId"])
    # clear flag from ~DOJG
    if j in range(1,4): # successful update; redundant check
        res=requests.post(AC.URL,json={
            "action":"setSpecificValueOfCard",
            "version":6,
            "params":{
                "card":flagged_card_info[0]["cardId"],
                "keys":["flags"],
                "newValues":[0]
            }
    })
