#%%
import AC_utils as AC
import subprocess
import re
import os
treated_tag="g_"
source_folder="~/grego/AppData/Roaming/Anki2/User\ 1/collection.media/"
output_folder="~/grego/AppData/Roaming/Anki2/User\ 1/collection.media/"
suppress_bash=True
threshold=-30
def ffmpeg_command(filename):
    command=f"""ffmpeg -i {source_folder}{filename} -y -af silenceremove=start_periods=1"""+\
        """:start_silence=0.1:start_threshold=-30dB,areverse,silenceremove=start_periods"""+\
        f"""=1:start_silence=0.1:start_threshold=-30dB,areverse {output_folder}/{treated_tag}{filename}"""
    #if suppress_bash:
        #command+=" |& :"
    return command
#%%
def extract_names(input_string):
    pattern = r'\[sound:(.*?)\]'
    matches= re.findall(pattern, input_string)
    return matches
def update_one(indict):
    output=""
    audio_files=extract_names(indict["audio"])

    for filename in audio_files:
        output+="[sound:"
        if filename.startswith(treated_tag):
            #already treated
            return None
        os.system(ffmpeg_command(filename))
        output+=treated_tag+filename
        output+="]"
    return {"audio":output}
#%%
"""
if __name__=="__main__":
    AC.update_all(update_one)"""
# %%
if __name__=="__main__":
    import AC_utils as AC
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("-x", "--hyougen",
            help="hyougen")
    args=parser.parse_args()
    AC.update_one(args.hyougen,update_one)

# %%
