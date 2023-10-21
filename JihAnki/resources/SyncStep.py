#%%
import requests
import AC_utils as AC

URL=AC.URL
#%%
import pandas as pd
import numpy as np

colnames=AC.colnames
userColnames=AC.userColnames


### Make a DF for existing collection, a DF for new entries
import os
from datetime import datetime
datestr = datetime.today().strftime('%Y_%m_%d')

existingCollection=AC.load("JihAnki")["result"]
existingDF=AC.AnkiConnect_to_Pandas(existingCollection,colnames)

takobotoCollection=AC.load("Takoboto")["result"]
userDF = pd.DataFrame(data=np.empty((len(takobotoCollection),
                                     len(colnames)),dtype=str),
                columns=colnames)
for i in range(len(takobotoCollection)):
    note = takobotoCollection[i]["fields"]
    userDF.at[i,"hyougen"]=note["Japanese"]["value"]
    userDF.at[i,"imi"]=note["Meaning"]["value"]
    userDF.at[i,"reibun"]=note["Sentence"]["value"]
    userDF.at[i,"reibun_imi"]=note["SentenceMeaning"]["value"]
    userDF.at[i,"source_tag"]="takoboto"


#%%
### Read the excel sheet for novel entries
localxl = "/home/greg/nihongo/JihAnki/resources/_jihanki.xlsx"
os.popen("cp ~/grego/Desktop/JihAnki.xlsx "\
            +localxl)
XLuserDF=pd.read_excel(localxl,sheet_name="userSheet",header=0)
XLuserDF.fillna("", inplace=True)
def filter_rows_by_values(df, col, values):
    return df[~df[col].isin(values)]
#%%
# entries from excel take priority over entries from takoboto
userDF=filter_rows_by_values(userDF, "hyougen", XLuserDF.hyougen.values)
userDF = pd.concat([userDF,XLuserDF])
userDF=filter_rows_by_values(userDF, "hyougen", existingDF.hyougen.values)

### Fill out the entries
#%%
prevMax = 0
for value in existingDF.entryID.values:
    if int(value)>prevMax:
        prevMax=int(value)
userDF["entryID"]=prevMax+1
userDF["entryID"]+=np.arange(0,len(userDF))
userDF["audio"]=""
userDF["hyougen_yomikata"]=""
userDF["reibun_yomikata"]=""
import ProcessEntry as pe

for j in range(len(userDF)):
    i=userDF.index.values[j]
    userDF.at[i, "hyougen"]=userDF.at[i, "hyougen"].replace(" ","")
    HGback, RBback = pe.parseEntry(userDF.at[i, "hyougen"],
                    userDF.at[i, "reibun"])
    userDF.at[i,"yomikata"]=HGback
    userDF.at[i,"reibun_yomikata"]=RBback
#%%
addRes = AC.AddFromDF(userDF)

#%%

### Back up and Flush
existingDF = pd.concat([existingDF, userDF])
existingDF.to_excel("~/grego/Documents/Nihongo/backend_JihAnki.xlsx",
                     sheet_name="backend_sheet",
                     columns=colnames,
                     index=False,
                     header=True
                     )
BKuserDF=pd.DataFrame(data=np.empty((1,len(userColnames)),dtype=str),
                      columns=userColnames)
BKuserDF.to_excel("~/grego/Desktop/JihAnki.xlsx",
                sheet_name="userSheet",
                index=False,
                header=userColnames,
                )
path_to_outcsv="~/nihongo/JihAnki/outputCsv/out_"+datestr
BKuserDF.to_csv(path_to_outcsv,
                index=False,
                header=userColnames,
                )
res = requests.post(URL,json={
    "action": "sync",
    "version": 6
})
AC.flushNotes("Takoboto")

# %%
