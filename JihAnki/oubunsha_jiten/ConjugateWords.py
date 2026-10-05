#%%
import re
import MeCab
tagger = MeCab.Tagger()
import pandas as pd
# %%

jpob = "（"
jpcb = "）"
a_ends="あかがさたなばまら"
i_ends="いきぎしちにびみり"
e_ends="えけげせてねべめれ"
u_ends="うくぐすつぬぶむる"
o_ends="おこごそとのぼもろ"

katakana_a = "aァャヵアカガサザタダナハバパマヤラワ"
phonetic_a=katakana_a+""
#12449 to 
katakana_i = "iイキギシジチヂニヒビピミリヰ"
katakana_u = "uゥュウクグスズツヅヌフブプムユル"
katakana_e = "eェヶエケゲセゼテデネヘベペメレヱ"
katakana_o = "oォョオコゴソゾトドノホボポモヨロヲ"
#%%
def generate_forms(root,endings):
    possibilities=[]
    for ending in endings:
        for i in range(1,(len(ending))+1):
            possibility=root+ending[:i]
            if possibility not in possibilities:
                possibilities.append(possibility)
    return possibilities
def i_adjective(pieces):
    root=pieces[0][:-1]
    endings=["い","くて","かった"]
    possibilities=generate_forms(root, endings)
    return possibilities
def godan_verb(pieces):
    ending=pieces[0][-1]
    root=pieces[0][:-1]
    conjugations=[]
    base=[]
    # four groups of godan:
    if ending in ["く"]:
        base="いて"
    elif ending in ["す"]:
        base="して"
    elif ending in ["ぐ","む","ぬ","ぶ"]:
        base="んで"
    else:
        base="って"
    times=["い"]#["いる","いた", "いて"]
    conjugations=[base+time for time in times]
    if base=="んで":
        conjugations.append("んだ")
    else:
        conjugations.append(base[0]+"た")
    ### common trunk
    idx=u_ends.find(ending)
    conjugations.append(ending)
    conjugations.append(a_ends[idx]+"ない")
    conjugations.append(a_ends[idx]+"なく")
    conjugations.append(a_ends[idx]+"れた")
    conjugations.append(a_ends[idx]+"れば")
    conjugations.append(i_ends[idx])
    conjugations.append(e_ends[idx]+"る")
    conjugations.append(u_ends[idx])
    conjugations.append(o_ends[idx]+"う")
    return generate_forms(root, conjugations)
def ichidan_verb(pieces):
    root=pieces[0][:-1]
    conjugations=[]
    conjugations.append("れば")
    conjugations.append("られた")
    conjugations.append("さ")
    conjugations.append("て")
    conjugations.append("た")
    conjugations.append("る")
    return generate_forms(root, conjugations)

def generate(hyougen):
    pieces=tagger.parse(hyougen).split("\n")[0]
    pieces=pieces.split("\t")
    if '形容詞' in pieces[5] and pieces[0].endswith("い"):
        return i_adjective(pieces)
    elif '五段' in pieces[5] and (pieces[0][-1] in u_ends):
        return godan_verb(pieces)
    elif '一段' in pieces[5] and pieces[0][-1]=="る":
        return ichidan_verb(pieces)
    else:
        return [hyougen]
