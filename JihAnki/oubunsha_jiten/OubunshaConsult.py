# Requires (oubunsha_jiten venv)
#%%
import pandas as pd
def construct_dict():
    dictpath="/home/greg/nihongo/JihAnki/resources/oubunsha.csv"
    df=None
    try:
        df=pd.read_csv(dictpath)
    except:
        print("OubunshaLookup didn't find "+dictpath)
        pass
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
        dn=["①","②","③","④"]
        headword="<u><strong>"+desc[:desc.find("】")]+"</u></strong>"
        desc=desc[desc.find("】"):]
        sections=desc.split("<br>")[1:]
        # sections[0] superfluous information (?)
        # sections[1:] different definitions
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
                outstr+=section
        return headword+"】<br>"+outstr



    def lookup(hyougen):
        outstr=""
        if df is None:
            print(" Need the Oubunsha df")
            return ""
        search_results=df[df["hyougen"]==hyougen]
        if len(search_results)==1:
            search_results=[search_results]
        for result in search_results:
            try:
                yomi=result.kana.values[0]
            except:
                return ""
            desc=result.description.values[0]
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
    
    oubunsha_dict={}
    words=df["hyougen"].values
    n=len(words)
    for i in range(len(words)):
        if not isinstance(words[i], str):
            continue
        oubunsha_dict[words[i]]=increase_font(lookup(words[i]))
        if i%1000==0:
            print(f"Oubunsha : {i}/{len(words)}")
#%%

"""from IPython.core.display import display, HTML
display(HTML(lookup("相合い傘")))
#%%
print("-"*30)
display(HTML(increase_font(lookup("触発"))))
#%%"""

import json
from mdict_utils.base.writemdict import MDictWriter
with open("oubunshadict.txt") as tweetfile:
    oubunsha_dict = json.loads(tweetfile.read().replace("30px","9px")) 
#%%
writer = MDictWriter(
        oubunsha_dict,
        title="Greg's OubunshaJiten",
        description="please work!",
    )
with open(f"oubunsha_boox.mdx", "wb") as wf:
    writer.write(wf)



# %%
