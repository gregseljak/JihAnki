import pandas as pd
import LangUtils as LU

small_kana="ュョャ"
cap="</span>"
slLO='<span class="lunder">'
sLO='<span class="under">'
sHI='<span class="over">'
slHI='<span class="lover">'

jhk="/home/greg/nihongo/JihAnki/resources/"
target=jhk+"ja_pitch_accents.tsv"

pitchdf=pd.read_csv(target,sep="\t")
"""pitchcodes={"0-k":"_-...",
           "1-k":"-_...",
           "2-k":"_-_...",
           "3-k":"_--_...",
           "4-k":"_---_..."}"""

def decompose_morae(yomikata:str):
    kana=LU.to_katakana(yomikata)
    morae=[]
    i=0
    while i<len(kana):
        if i+1<len(kana): # check for compound mora (ex. しょ)
            if kana[i+1] in small_kana:
                morae.append(LU.to_hiragana(kana[i:i+2]))
                i+=2
            else:
                morae.append(LU.to_hiragana(kana[i]))
                i+=1
        else:
            morae.append(LU.to_hiragana(kana[i]))
            i+=1
    return morae


def decorate_pitchtags(hyougen:str, yomikata=None)->str:
    """In:  hyougen in kanji/okurigana form
       Out: Yomikata with 
    """
    outstr=""
    entry=pitchdf.loc[pitchdf['word']==hyougen]
    if yomikata is not None:
        entry=entry.loc[entry["kana"].apply(LU.to_katakana)==LU.to_katakana(yomikata)]
    if entry.values.shape[0]>0: # entry found
        df_yomikata=entry["kana"].values[0]
        if yomikata is not None:
            if LU.to_katakana(df_yomikata)!=LU.to_katakana(yomikata):
                print("Warning - provided hyougen ["+hyougen+\
                    "] with yomikata ["+yomikata+\
                    "] doesn't match pitchdf entry"+entry.to_string()+\
                        "; skipping")
        pitchcode=entry["accent"].values[0]
    else:
        return hyougen
    morae=decompose_morae(df_yomikata)
    if pitchcode==1:
        outstr+=sHI
        outstr+=morae.pop(0)+cap
        outstr+=slLO+''.join(morae)
    else:
        outstr+=sLO
        outstr+=morae.pop(0)+cap+slHI
        if pitchcode>0:
            for i in range(pitchcode-1):
                outstr+=morae.pop(0)
            outstr+=cap+slLO
        outstr+=''.join(morae)
    outstr+=cap
    return outstr

def legacy_replace(hyougen, yomikata):
    """ check if the pitchdf entry exists;
    try to match with my old card style element
    in order to tag and replace"""
    entry=pitchdf.loc[pitchdf['word']==hyougen]
    if yomikata is not None:
        entry=entry.loc[entry["kana"].apply(LU.to_katakana)==LU.to_katakana(yomikata)]
    if entry.values.shape[0]>0: # entry found
        df_yomikata=entry["kana"].values[0]
    else: return False
    return hyougen+4*" "+"--"+4*" "+df_yomikata

def sync_to_anki(hyougen, yomikata=None):
    import requests
    import AC_utils
    # New method since WSL2 2.0.0
    # Requires windowsIP mirroring
    URL="http://127.0.0.1:8765"
    target_str=legacy_replace(hyougen, yomikata)
    if target_str==False:
        print(hyougen+"not found in pitchdf")
        return 1
    res = requests.post(URL, json={
        'action': 'findNotes',
        'version': 6,
        'params': {
            'query': 'deck:'+"JihAnki"+" "\
                     'yomikata:'+'*"'+target_str+'"*'
            ,
        },
    }).json()
    if len(res["result"])==0:
        print("Could not find a card that contained ["+target_str+"]")
        return 1
    detail_res = requests.post(URL, json={
        'action': 'notesInfo',
        'version': 6,
        'params': {
            'notes': res['result']
        },
    }).json()
    pitchstr=decorate_pitchtags(hyougen,yomikata)
    noteID = ((detail_res["result"])[0])["noteId"]
    old_yomikata=((detail_res["result"])[0])["fields"]["yomikata"]["value"]
    old_reiyomi=((detail_res["result"])[0])["fields"]["reibun_yomikata"]["value"]
    AC_utils.SelectCard(0) # DEselects cards; prevents http conflict
    modification_res = requests.post(URL,json={
    "action": "updateNoteFields",
    "version": 6,
    "params": {
        "note": {
            "id": noteID,
            "fields": {
                "yomikata": old_yomikata.replace(target_str,pitchstr),
                "reibun_yomikata": old_reiyomi.replace(target_str,pitchstr),
            },
        }
    }
    })
    AC_utils.SelectCard(noteID) # snap back to the modified card
    print(str(modification_res)=="<Response [200]>")

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("-x", "--hyougen",
            help="hyougen")
    parser.add_argument("-y", "--yomikata",
            help="yomikata")
    args=parser.parse_args()
    sync_to_anki(args.hyougen,args.yomikata)
    