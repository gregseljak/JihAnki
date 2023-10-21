# INPUT  : Partially complete entry from the excel sheet that matches based on hyougen
# EFFECT : Fills out the rest of the entry; sends the updated fields to anki
# Returns: Error code
import os
import pandas as pd
import AC_utils as AC

colnames=AC.colnames
userColnames=AC.userColnames

localxl = "/home/greg/nihongo/JihAnki/resources/_jihanki.xlsx"
os.popen("cp ~/grego/Desktop/JihAnki.xlsx "\
            +localxl)
XLuserDF=pd.read_excel(localxl,sheet_name="userSheet",header=0)
XLuserDF.fillna("", inplace=True)
def keepOverlappingRows(df, col, values):
    return df[df[col].isin(values)]
existingCollection=AC.load("JihAnki")["result"]
existingDF=AC.AnkiConnect_to_Pandas(existingCollection,colnames)
XLuserDF=keepOverlappingRows(XLuserDF, "hyougen", existingDF.hyougen.values)
