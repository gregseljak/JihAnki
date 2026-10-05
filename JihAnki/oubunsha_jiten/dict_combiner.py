#%%
dirpath="/home/greg/nihongo/JihAnki/oubunsha_jiten/"
import json
import pandas as pd

# %%

#[0]: word
#[1]: hiragana
#[5]: description
# %%

entries=[]
for ii in range(1,11):
    with open(dirpath+"term_bank_"+str(ii)+".json", "r") as file: 
        dict_json=json.load(file)
        for i in range(len(dict_json)):

            hg=dict_json[i][0]
            kana=dict_json[i][1]
            try:
                desc=dict_json[i][5][0].replace("\n","<br>").replace(",","&comma;")
            except:
                continue
            desc=entries.append({
                "hyougen":hg,
                "kana":kana,
                "description":desc
            })
df=pd.DataFrame(entries)
df.to_csv(dirpath+"oubunsha.csv",index=False)
# %%
