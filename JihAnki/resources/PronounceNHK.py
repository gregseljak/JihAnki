#%%
import LangUtils as LU
import pandas as pd
import json
import os
filePath="./nhkPronunciations/nhk_2016_pronunciations_index-main"
mediafolderPath="~/grego/AppData/Roaming/Anki2/User\ 1/collection.media"

with open(filePath+"/index.json", 'r') as file:
    content = json.load(file)
# Extract the "data" section
content = content.get("headwords", {})
lean_content = {key: values[0] if values else None for key, values in content.items()}
del content
#%%
df=pd.DataFrame(list(lean_content.items()), columns=["hyougen","filename"])

# %%
def update_one(indict):
    # try to add an audio field to the indict dict, based on the hyougen
    # input: indict dict with at least a hyougen field
    # output: indict dict with an audio field added, if found in nhkDF
    lookup=df[df["hyougen"]==indict["hyougen"]]
    if len(lookup)==0:
        print(" "+indict['hyougen']+" not found in nhkDF")
        return None
    nhkAudioFile=lookup["filename"].values[0]
    filetype=nhkAudioFile[-4:]
    newName="nhk"+indict["hyougen"]+"_pronounce"+filetype
    command=f"cp {filePath}/media/{nhkAudioFile} {mediafolderPath}/{newName}" 
    os.system(command)
    audiofield={"audio":f"[sound:{newName}]"}
    return audiofield
def alt_lookup(indict, lookupterm):
    # this allows the nhkDF lookup term to differ from the card hyougen
    argdict=indict.copy()
    argdict["hyougen"]=lookupterm
    return update_one(argdict)

if __name__=="__main__":
    import AC_utils as AC
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("-x", "--hyougen",
            help="hyougen")
    parser.add_argument("-y", "--yomikata",
            help="alt lookup in nhk json (presumably yomikata)",default=None)
    args=parser.parse_args()
    if args.yomikata is None:
        AC.update_one(args.hyougen,update_one)
    else:
        AC.update_one(args.hyougen, lambda x:alt_lookup(x,args.yomikata))

# %%
