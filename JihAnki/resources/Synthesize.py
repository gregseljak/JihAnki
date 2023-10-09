#%%
import pandas as pd

#%%

#%%
for i in range(len(df2)):#range(len(df)):
    df2.iloc[i]=process_entry(df.iloc[i])

path_to_debug = "/mnt/c/Users/greg/Desktop/debugfile.csv"
debugCSV = df2.to_csv(path_or_buf=None, header=False, index=False)
with open(path_to_debug, 'w') as debugCSVfile: debugCSVfile.write(debugCSV)
# %%
