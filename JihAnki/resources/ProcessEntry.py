#%%
import pandas as pd
import MeCab
import LangUtils
tagger = MeCab.Tagger()


df = pd.read_excel("./ExampleBook.xlsx",header=0)
df.fillna("", inplace=True)

tagger = MeCab.Tagger()

#debug
import numpy as np
import LangUtils as LU
tagger = MeCab.Tagger()
### User override tag:
# <!--user-->
overrideTag= "<!--user-->"

df = pd.read_excel("./ExampleBook.xlsx",header=0)
df.fillna("", inplace=True)

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


#%%
def create_hyougen(idx:int, debug=""):
    # pass this dict to reibun creator for highlighting
    reibunResource={
        "hyougen"   : None,
        "idx"       : idx,
        "fragments" : []
    }
    kirei_hyougen =""
    entry = df.iloc[idx].values
    if debug != "":
        entry=[None, debug]
        print("ProcessEntry.create_hyougen warning - arg idx "+str(idx)+\
              " overridden in favour of debug '"+debug+"'")
        reibunResource["idx"]=None
    cleanHyou=entry[1].strip().strip("。")
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
            kirei_hyougen+="<br><b>"\
                +LineParse[3]+"    --    "\
                +LU.standardize_phonetic(LineParse)\
                +"</b>"

    kirei_hyougen="<b>"+cleanHyou+"</b><br>"+kirei_hyougen

    return kirei_hyougen, reibunResource






def create_reibun(hyougenDict:dict, debug=""):
    kirei_hyougen =""
    entry = df.iloc[hyougenDict["idx"]].values
    if hyougenDict["idx"] is None:
        entry=[None, debug]
        print("ProcessEntry.create_reibun warning - arg idx "+str(idx)+\
              " overridden in favour of debug '"+debug+"'")
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
        if outsentence.endswith("</b>"):
            return True
        return False

    phrase=df.iloc[hyougenDict["idx"]].values[4]
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
            Kakikata = "<b>"+Kakikata+"</b>"
            Yomikata = "<b>"+Yomikata+"</b>"
            # stronger condition to add to recap

            if recapcriteria(LineParse,hyougenDict):
                recap+="<br><b>"+LineParse[3]\
                    +"    --    "\
                    +LU.standardize_phonetic(LineParse)\
                    +r"<\b>"
            else:
                pass
                #print(LineParse[0]+"failed to be interesting")
        # always true
        outsentence   +=Kakikata
        pronounciation+=Yomikata
    outsentence+="<br>"
    outstring = outsentence+"<br>\n"+pronounciation+"<br>\n"+recap
    outstring = outstring.replace("<b></b>","").replace("</b><b>","")
    return outstring

def ProcessEntry(idx:int):
    hyougenface, HGdict = create_hyougen(773)
    reibunface = create_reibun(HGdict)
    return hyougenface, reibunface

if __name__=="__main__":
    cardface, HGdict = create_hyougen(773)
    print(HGdict)
    print(create_reibun(HGdict))
