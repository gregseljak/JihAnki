#%%
import pandas as pd
import MeCab

tagger = MeCab.Tagger()



tagger = MeCab.Tagger()

#debug
import numpy as np
import LangUtils as LU
tagger = MeCab.Tagger()
### User override tag:
# <!--user-->
overrideTag= "<!--user-->"



# tag pattern by line:
# 0. identified piece ver batim
# 1. ID'd piece phonetic (WITH - )
# 2. ID'd piece root phonetic
# 3. ID'd piece dictionary form (kanji)
# 4. Type of word
# 5. ???
# 6. (int) ???
def recapcriteria(entry, hgDict=None):
    # detect if the word is worth putting in the recap
    if not LU.bool_Interesting(entry):
        return False
    if hgDict is not None:
        if entry[3] in hgDict["fragments"]:
            return True
        else:
            return False
    return True


def ExceptionFilter(entry):
    # replacing MeCab's ideosyncracies with my own
    # wo/o should show as wo during pronounciations
    if entry[0]=="を":
        entry[1]="を"
        entry[2]="を"
    # same with ha/wa
    if entry[0]=="は":
        entry[1]="は"
        entry[2]="は"
    return entry

def decomposeKanji(kanji:str):
    """ take a kanji; return its 1.components 2. base translation
        This stuff rules!
    """
    #TODO
    pass


#%%
def create_hyougen(hyougenStr):
    # pass this dict to reibun creator for highlighting
    reibunResource={
        "hyougen"   : None,
        "fragments" : []
    }
    kirei_hyougen =""
    cleanHyou=hyougenStr.strip().strip("。")
    reibunResource["hyougen"]=cleanHyou
    EntryParse = tagger.parse(cleanHyou).split("\n")
    for line in EntryParse:
        LineParse = line.split("\t")
        if LineParse[0]=="EOS" or LineParse[0]==[""] or len(LineParse)<5:
            break
        # for recognition in 
        reibunResource["fragments"].append(LineParse[3])
        # special exception for some katakana words (ex. パンク)
        if len(LineParse)>=4:
            if "-" in LineParse[3]:
                LineParse[3]=LineParse[3][:LineParse[3].find("-")]
        # add pronounciation to the card face
        if recapcriteria(LineParse):
            kirei_hyougen+="<br><strong>"\
                +LineParse[3]+"    --    "\
                +LU.standardize_phonetic(LineParse)\
                +"</strong>"

    kirei_hyougen="<strong>"+cleanHyou+"</strong><br>"+kirei_hyougen

    return kirei_hyougen, reibunResource






def create_reibun(phraseStr, hyougenDict:dict):
    outsentence=""
    pronounciation=""
    recap=""
    def hilitecriteria(entry,hgDict):
        # guess-style
        # 1. False in general
        # 2. Interesting fragments are interesting
        # 3. If a particle is in fragments and is right-adjacent
        # to another highlight, then it's probably hyougen. 
        if not entry[3] in hgDict["fragments"]:
            return False
        if LU.bool_Interesting(entry):
            return True
        if outsentence.endswith("</strong>"):
            return True
        return False

    phrase=phraseStr
    if phrase=="":
        return ""
    EntryParse=tagger.parse(phrase)

    for line in EntryParse.split("\n"):
        LineParse=line.split("\t")
        if LineParse[0]=="EOS" or LineParse[0]==[""] or len(LineParse)<5:
            break
        LineParse=ExceptionFilter(LineParse)
        Kakikata=LineParse[0]
        if LU.is_katakana(LineParse[0]):
            Yomikata=LineParse[1]
        #if LU.guessOnyomi(LineParse[0]):
            # Reasonable guess if it's onyomi
            #Yomikata=LU.to_katakana(LU.standardize_phonetic(LineParse))
        else:
            # kunyomi
            Yomikata=LU.standardize_phonetic(LineParse)
            #print("yomikata = "+Yomikata)
        
        if hilitecriteria(LineParse,hyougenDict):
            Kakikata = "<strong>"+Kakikata+"</strong>"
            Yomikata = "<strong>"+Yomikata+"</strong>"
            # stronger condition to add to recap

            if recapcriteria(LineParse,hyougenDict):
                recap+="<br><strong>"+LineParse[3]\
                    +"    --    "\
                    +LU.standardize_phonetic(LineParse)\
                    +"</strong>"
            else:
                pass
                #print(LineParse[0]+"failed to be interesting")
        # always true
        outsentence   +=Kakikata
        pronounciation+=Yomikata
    outsentence+="<br>"
    outstring = outsentence+"<br>\n"+pronounciation+"<br>\n"+recap
    outstring = outstring.replace("<strong></strong>","").replace("</strong><strong>","")
    return outstring

def parseEntry(hyougen, phrase):
    hyougenface, HGdict = create_hyougen(hyougen)
    reibunface = create_reibun(phrase, HGdict)
    return hyougenface, reibunface

def sync_to_anki(hyougen, rei_face, rei_back):
    import requests
    import AC_utils
    # New method since WSL2 2.0.0
    # Requires windowsIP mirroring

    URL="http://127.0.0.1:8765"
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
    noteID = ((detail_res["result"])[0])["noteId"]
    AC_utils.SelectCard(0) # DEselects cards; prevents http conflict
    modification_res = requests.post(URL,json={
    "action": "updateNoteFields",
    "version": 6,
    "params": {
        "note": {
            "id": noteID,
            "fields": {
                "reibun": rei_face,
                "reibun_yomikata": rei_back,
                "reibun_imi":"",
                "source_tag":"gpt",
            },
        }
    }
    })
    AC_utils.SelectCard(noteID) # snap back to the modified card
    print(str(modification_res)=="<Response [200]>")



def simple_print(args):
    hg=parseEntry(args.hyougen,args.sentence)
    print("HGf: "+args.hyougen)
    print("HGb: "+hg[0])
    print()
    print("RBf: "+args.sentence)
    print("RBb: "+hg[1])

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("-x", "--hyougen",
            help="hyougen")
    parser.add_argument("-s", "--sentence",
            help="sentence")
    parser.add_argument("-a", "--anki", default=True)
    #parser.add_argument("-h", "--help", default=False)
    args=parser.parse_args()
    
    if args.anki:
        if False:
            print(' -x : hyougen (should be a str directly in kanji/kana, surrounded with "")'+\
                  "\n -s : sentence (should be in same format as hyougen)"+\
                  "\n -a : bool, default=True; Updates Anki directly")
        else:
            hg=parseEntry(args.hyougen,args.sentence)
            sync_to_anki(args.hyougen,args.sentence,hg[1])
    else:
        simple_print(args)
# %%
