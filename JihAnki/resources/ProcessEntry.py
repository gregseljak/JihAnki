#%%
import pandas as pd
import MeCab
import os

import LangUtils
tagger = MeCab.Tagger()


df = pd.read_excel("./ExampleBook.xlsx",header=0)
df.fillna("", inplace=True)


# %%
import MeCab
tagger = MeCab.Tagger()
import os

#debug
import numpy as np

import LangUtils as LU
import ProcessEntry

tagger = MeCab.Tagger()
### User override tag:
# <!--user-->
overrideTag= "<!--user-->"

df = pd.read_excel("./ExampleBook.xlsx",header=0)
df.fillna("", inplace=True)

#debug
df2 = pd.DataFrame(data=np.zeros((10,len(df.columns))),\
                    columns=df.columns.values)
# %%
### TODO: check if item should be treated

#def process_entry(entry):
idx = 2
output = dict.fromkeys(df.columns.values)
myentry = df.iloc[idx]


output["imi"] = df.at[idx, "imi"]


# tag pattern by line:
# 0. identified piece ver batim
# 1. ID'd piece phonetic (WITH - )
# 2. ID'd piece root phonetic
# 3. ID'd piece dictionary form (kanji)
# 4. Type of word
# 5. ???
# 6. (int) ???



#%%
def create_hyougen(idx:int):
    kirei_hyougen =""
    entry = df.iloc[idx].values
    hyougen_yomikata=""
    cleanHyou=entry[1].strip().strip("。")
    EntryParse = tagger.parse(cleanHyou).split("\n")
    for line in EntryParse:
        LineParse = line.split("\t")
        if LineParse[0]=="EOS" or LineParse[0]==[""]:
            break
        # special exception for some katakana words (ex. パンク)
        if len(LineParse)>=4:
            if "-" in LineParse[3]:
                LineParse[3]=LineParse[3][:LineParse[3].find("-")]
        # add pronounciation to the card face
        kirei_hyougen+="<br><b>"\
            +LineParse[3]+"    --    "\
            +LU.standardize_phonetic(LineParse[2])\
            +"</b>"

    kirei_hyougen="<b>"+cleanHyou+"</b><br>"+kirei_hyougen
    return(kirei_hyougen)

# %%
