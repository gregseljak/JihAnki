#%%
godan_ends = list("うくぐすつぬふぶむる")
jpob = "（"
jpcb = "）"

katakana_a = "aァャヵアカガサザタダナハバパマヤラワ"
phonetic_a=katakana_a+""
#12449 to 
katakana_i = "iイキギシジチヂニヒビピミリヰ"
katakana_u = "uゥュウクグスズツヅヌフブプムユル"
katakana_e = "eェヶエケゲセゼテデネヘベペメレヱ"
katakana_o = "oォョオコゴソゾトドノホボポモヨロヲ"


intMIN_KATA=12448


"""def standardize_parsed(inentry):
    if "-" in inentry:
        entry = inentry[:inentry.find("-")]
    else:
        entry = inentry
    entry = entry.replace("為る", "する")"""

def sym_to_dec(inchar:str):
    # from symbolic char to dec representation of unicode #
    # ex. あ -> 12354
    if len(inchar) > 1:
        return None
    return int(str(inchar.encode("unicode_escape"))[5:-1], base=16)

def dec_to_sym(unidec:int):
    # ex. 12354 ->　あ
    return ("\\u"+str(hex(unidec))[2:]).encode("utf-8").decode("unicode_escape")

def just_kanji(inword:str):
    outlist = []
    for character in list(inword):
        if sym_to_dec(character) > 19968:
            outlist.append(character)
    return outlist

def is_kanji(inword:str):
    for char in inword:
        if sym_to_dec(char)<=19968:
            return False
    return True

def is_hiragana(word:str, allow_white=True):
    # check if each char in string is hiragana
    for character in word:
        if character.isspace() and (allow_white is True):
            continue
        kanadec = sym_to_dec(character)
        if kanadec < 12354 or kanadec>12435:
            return False
    return True
#%%
def is_katakana(word:str, allow_white=True):
    # check if each char in string is katakana
    for char in word:
        try:
            if char.isspace() and (allow_white is True):
                continue
            kanadec = sym_to_dec(char)
            if kanadec < 12448 or kanadec > 12543:
                return False
        except ValueError: # not even kana
            return False    
    return True


#%%
def to_hiragana(inword:str):
    # like tolower(), but with hiragana
    outword = ""
    for inkana in inword:
        if inkana=="ー":
            outword+="ー"
            continue
        if not inkana.isascii():
            inkana_dec=sym_to_dec(inkana)
            #inkana_dec >= 12448 and inkana_dec <= 12534
            if is_katakana(inkana):
                outword += dec_to_sym(inkana_dec-96)
            else:
                outword += inkana
        else:
            outword += inkana
    return outword

def to_katakana(inword:str):
    # like toupper(), but with katakana
    outword = ""
    for inkana in inword:
        if not inkana.isascii():
            inkana_dec=sym_to_dec(inkana)
            #inkana_dec >= 12448 and inkana_dec <= 12534
            if is_hiragana(inkana):
                outword += dec_to_sym(inkana_dec+96)
            else:
                outword += inkana
        else:
            outword += inkana
    return outword



def standardize_phonetic(entry):
    # returns the dictionary-form yomikata[hiragana]
    # of the POS
    outParse=entry[1]
    while "ー" in outParse:
        d = outParse.find("ー")
        if len(entry[2])>=len(outParse):
            insertChar=entry[2][d]
        # the only known exception is "~yo <-> you"
        elif to_katakana(outParse[d-1]) in katakana_u:
            insertChar="う"
        elif to_katakana(outParse[d-1]) in katakana_o:
            insertChar="う"
        elif to_katakana(outParse[d-1]) in katakana_i:
            insertChar="い"
        elif to_katakana(outParse[d-1]) in katakana_e:
            insertChar="い"
        elif to_katakana(outParse[d-1]) in katakana_a:
            insertChar="あ"
        try:
            outParse=outParse[:d]+insertChar+outParse[d+1:]
        except UnboundLocalError:
            print("LangUtils unable to parse the entry ")
            print("  ::  ".join(entry))
            quit()
    outParse=to_hiragana(outParse)
    return outParse

def guessOnyomi(instr:str):
    if is_katakana(instr):
        return True
    if is_kanji(instr) and len(instr)>1:
        return True
    return False

boring_elements=[
    "助詞-接続助詞"  # te/ta
    "助詞",         # particles
    "助詞-終助詞",  # sentence-ending na
    "助動詞",       # desu,...
    "格助詞"        # other particles (de, no)
    "助動詞-ダ",    # MeCab-superfluous -da
    "助詞-接続助詞",# object particles (ga,ni,wo)
    "御",           # o-, go- honorofics
    #"動詞-非自立可能", # suffix verbs
]
def bool_Interesting(entry, verbose=False):
    element = " ".join(entry)
    
    for boring in boring_elements:
        if boring in element:
            #print(entry[0] +" was boring by "+boring)
            return False
    if("格助詞" in element):
        # can't tell why this is necessary
        return False

    if("動詞-非自立可能") in element:
        # suffix verbs are usually interesting
        if entry[3]=="有る": # aru
            return False
        if entry[3]=="為る": # suru
            return False
        if entry[3]=="居る": # iru
            return False
    return True

def deconjugate(inword:str):
    #TODO implement; probably its own class
    pass
# %%
