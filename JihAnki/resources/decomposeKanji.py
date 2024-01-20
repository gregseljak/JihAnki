#%%
import pandas as pd
with open("./kanjidic2.xml","r") as file:
    kanjidic = file.read()
with open("./KRad/kradfile","r") as file:
    KRad=file.read()
# %%
def decompose(target):
    stroke_count=""
    pieceEntry=""
    radical=""
    header = "<!-- Entry for Kanji: "+target+" -->"
    headerIdx = kanjidic.find(header)
    footer = "</character>"
    footerIdx = kanjidic[headerIdx:].find(footer)+headerIdx

    KDentry = kanjidic[headerIdx:footerIdx].split("\n")
    stroke_count=""
    stcTag = "<stroke_count>"
    steTag = "</stroke_count>"
    radTag = "<rad_value"
    rdeTag = "</rad_value>"
    mngTag = "<meaning>"
    mneTag = "</meaning>"
    meanings = []
    radicalList = "一丨丶丿乙亅二亠人儿入八冂冖冫几凵刂力勹匕匚匸十卜卩厂厶又口囗土士夂夊夕大女子宀寸小尢尸屮山川巛工己巾干幺广廴廾弋弓彡彳心戈戸扌支攴文斗斤方无日曰月木欠止歹殳毋比毛氏气氵灬爫父爻爿片牙牜犭玄玉瓜瓦甘生用田疋疒癶白皮皿目矛矢石礻禸禾穴立竹米糸缶网羊羽老而耒耳聿肉臣自至臼舌舛舟艮色艸虍虫血行衤襾見角言谷豆豕豸貝赤走足車辛辰辵邑酉釆金镸門阜隶隹雨青非面革韋韭音頁風飛食首香馬骨高髟鬥鬯鬲鬼魚鳥鹵鹿麥麻黄黍黒黹黽鼎鼓鼠鼻齊齒龍龜龠"
    for line in KDentry:
        if line.startswith(stcTag):
            stroke_count = (line[len(stcTag):])[:-len(steTag)]
        if line.startswith(mngTag):
            meanings.append((line[len(mngTag):])[:-len(mneTag)])
        if line.startswith(radTag):
            stTag = 'classical">'
            stIdx = line.find(stTag)
            seIdx = line.find(rdeTag)
            radval = int(line[stIdx+len(stTag):seIdx])
            radical = radicalList[radval-1]

    pieceIdx = KRad.find(target)
    endline = KRad[pieceIdx:].find("\n")
    pieceEntry = KRad[pieceIdx:endline+pieceIdx]
    return stroke_count, radical, pieceEntry, meanings

#%%
def createFooter(target):
    stroke_count, radical, pieceEntry, meanings = decompose(target)
    mstr = ""
    if len(meanings)>0:
        mstr = meanings[0]
        if len(meanings)>1:
            mstr += ", "
            mstr += meanings[1]
    outLine = "<strong>"+pieceEntry[0]+"</strong>  ("+stroke_count+"):  <strong>"\
        +radical+"</strong> "+pieceEntry[3:].replace(radical,"")+"\n"+" "*8+mstr
    return outLine

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("-k", "--kanji",
            help="kanji")
    args=parser.parse_args()
    print(decompose(args.kanji))
    print()
    print(createFooter(args.kanji))
