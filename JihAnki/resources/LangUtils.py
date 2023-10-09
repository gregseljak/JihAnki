godan_ends = list("うくぐすつぬふぶむる")
jpob = "（"
jpcb = "）"

katakana_a = "aアカガサザタダナハバパマヤラワ"
katakana_i = "iイキギシジチヂニヒビピミリヰ"
katakana_u = "uウクグスズツヅヌフブプムユル"
katakana_e = "eエケゲセゼテデネヘベペメレヱ"
katakana_o = "oオコゴソゾトドノホボポモヨロヲ"

def standardize_parsed(inentry):
    if "-" in inentry:
        entry = inentry[:inentry.find("-")]
    else:
        entry = inentry
    entry = entry.replace("為る", "する")

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

def is_hiragana(word:str, allow_white=True):
    # check if each char in string is hiragana
    for character in word:
        if character.isspace() and (allow_white is True):
            continue
        kanadec = sym_to_dec(character)
        if kanadec < 12354 or kanadec>12435:
            return False
    return True

def to_hiragana(inword:str):
    # like tolower(), but with hiragana
    outword = ""
    for inkana in inword:
        if not inkana.isascii():
            inkana_dec =sym_to_dec(inkana)
            if inkana_dec >= 12448 and inkana_dec <= 12534:
                outword += dec_to_sym(inkana_dec-96)
            else:
                outword += inkana
        else:
            outword += inkana
    return outword

def standardize_phonetic(_inParse):
    outParse=to_hiragana(_inParse)
    while "ー" in outParse:
        d = outParse.find("ー")
        if d == 0:
            print("bad d found at "+str(d))
            insertChar="$"
        elif outParse[d-1]=="お":
            insertChar="う"
        else:
            insertChar=outParse[d-1]
        outParse=outParse[:d]+insertChar+outParse[d+1:]
    return outParse
standardize_phonetic("おじいーさん")

def deconjugate(inword:str):
    #TODO implement; probably its own class
    pass