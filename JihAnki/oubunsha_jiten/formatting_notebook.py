
#%%
import re
import MeCab
tagger = MeCab.Tagger()
import pandas as pd
dictpath="/home/greg/nihongo/JihAnki/resources/oubunsha.csv"
df=None
#%%
try:
    df=pd.read_csv(dictpath)
except FileNotFoundError:
    print("OubunshaLookup didn't find "+dictpath)
    pass
df.dropna(inplace=True)
#%%
def list_examples(example_section):
    outstr="<ul><li>"
    rei=example_section.replace("<br>","")
    rei=rei.replace("」","」</li><li>")
    rei=rei[:-4]
    outstr+=rei+"</ul>"
    return outstr

def beautify_description(desc):
    
    outstr=""
    SplitCharacters=["①","②","③","④","🈩","🈔"]
    posChar=["（副）","（名・自スル）","（名・自他スル）","｟俗｠","（副・形動ダ）"]

    titleidx=desc.find("】")+1

    if titleidx==0: #not found
        titleidx=desc.find("<br>")
    titleidx=min(titleidx,desc.find("<br>"))
    if titleidx==-1:
        return desc # just give up
    headword="<u><strong>"+desc[:titleidx]+"</u></strong>"
    desc=desc[titleidx:]

    sections=desc.split("<br>")[1:]

    # sections[0] superfluous information (?)
    # part-of-speech information

    # terrible logic for some pretty insane edge cases (see わんわん)
    try:
        posidx=-1
        for char in SplitCharacters:
            if sections[0].find(char)>-1:
                posidx=max(posidx,sections[0].find(char)+len(char))
        if(posidx==-1 or posidx>=len(sections[0])):
            posSection=sections[0]
        else:
            posSection=sections[0][:posidx]
        # move pos tags into the title line
        for char in posChar:
            if char in posSection:
                headword+=char
                sections[0]=sections[0][:sections[0].find(char)]+\
                    sections[0][sections[0].find(char)+len(char):]
    except:
        print(posidx)
    # actual list of definitions/uses
    for section in sections:
        if str.isspace(section) or len(section)==0:
                continue
        ex_idx=section.find("―")
        if ex_idx>-1:
            # find the closest quote mark to the left:
            # this allows headers to contain quotes
            deltaL=(section[:ex_idx])[::-1].find("「")+1
            deltaR=section[ex_idx:].find("」")
            header=section[:ex_idx-deltaL]
            examples=section[len(header):].split("」")
            outstr+="<br><br>"+header+"<ul>"
            for example in examples:
                if str.isspace(example) or len(example)==0:
                    continue
                outstr+="<li>"+example+"」</li>"
            outstr+="</ul>"
        else:
            outstr+=section+"<br>"*2
    
    return headword+"<br>"+outstr



def lookup(hyougen):
    outstr=""
    if df is None:
        print(" Need the Oubunsha df")
        return ""
    search_results=df[df["hyougen"]==hyougen].to_numpy()
    if len(search_results)==0:
        print("not results found for "+hyougen)
    for result in search_results:
        desc=result[2]
        desc=beautify_description(desc)
        #coutstr+="<strong>"+hyougen+"</strong>    "+yomi
        outstr+=desc+"<br><br><br>"
    while outstr.startswith('<br>'):
        outstr = outstr[4:]
    while outstr.endswith('<br>'):
        outstr = outstr[:-4]
    return outstr

def increase_font(lookup):
    style=''' <body style="margin: 20px;"><span style="font-size:30px">'''
    return style+lookup+"</span></body> "
from IPython.display import display, HTML

#%%
target="あたって砕けろ"
print(df[df["hyougen"]==target])
print(lookup(target))
display(HTML(lookup(target)))

#%%
### Lemmatizer section

#%%
target="綺麗"
print(tagger.parse(target).split("\t"))
display(HTML(lookup(target)))
# %%
import numpy as np
pos=[]
for target in df["hyougen"].values:
    try:
        _pos=tagger.parse(target).split("\n")[0].split("\t")[4]
    except TypeError:
        print("TypeError: "+str(target))
    if _pos not in pos:
        pos.append(_pos)

# %%
