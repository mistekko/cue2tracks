#! /usr/bin python
import sys, os

          #this program assumes CUE files provided as input will be (computer generated) of standard structure:
          #- INDEX 01 is the last track field
          #- the track metadata is the last set of fields
          #it also assumes that the CUE only references one audio file. 
          
metadata = [] #this is all the album metadata
audio_file = [] #rather than have the user supply the CUE's corresponding audio file, let's detect it outomatically


track_list = [] #contains dictionaries


#track metadata
track = ""
title = ""
isrc = ""
performer = "" #this is what CUE calls the artist! Why!
index00 = "" #timestamp of previos track's end in MM:SS:mS... convert this later becaus ffmpeg uses HH:MM:SS. May not be used
index01 = "" #timestamp of this track's beginning.


with open(sys.argv[1], 'r') as cue:
    #store the album metadata data in a list and grab the audio file's name
    line = cue.readline()
    while line.strip()[0:4] != "FILE": 
        metadata.append(line.strip()) #will probably change this in the future; right now, it's just there becuase I want to store this data, but I'm not sure how it's going to be used exactly yet
        line = cue.readline()

    audio_file = line[6:-7]
    print(f"Converting file: {audio_file:>60}")
          
    #the above works properly; trust me

    #grab the file extension for later use
    for n in range(1,len(audio_file)):
        if audio_file[-n] == ".":
            file_extension = audio_file[-n:]
            print("Detected file extension:\t" + file_extension)
            n = len(audio_file)
            break


    while True:
        track = cue.readline().strip().split(' ')[1]
        print("track: " + track)
        line = cue.readline()
        while line != "":
            if line.find("TITLE") > -1:
                title = line.strip("TITLE ").strip("\"")
            elif line.find("PERFORMER") > -1:
                title = line.split("PERFORMER ")[1].strip('\"')[0] #assumes the artist's name does not start with a space
            elif line.find("ISRC") > -1:
                isrc = line.split("ISRC ")[1].strip()
            elif line.find("INDEX 00") > -1:
                index00 = line.split("INDEX 00 ")[1].strip()
            elif line.find("INDEX 01") > -1:
                index01 = line.split("INDEX 01 ")[1].strip()
                #construct a dictionary of the just-parsed tracked and append it to track_list
                track_list.append({"track" : track,
                                    "title" : title,
                                    "performer" : performer,
                                    "isrc" : isrc,
                                    "index00" : index00,
                                    "index01" : index01})
                print(track_list)
                print()
                

            

            
    print(metadata, file_extension)         
    
#when the 'tracks' section is reached, create a dictionary for each track and a list containing each track

#dict: {n : {"track" : %track%, "title" : %title%, "performer" : %artist%, "index" : timestamp


#finally:
# for a in track_list[0:(len(track_list)-1)]: #the last track won't needs a different command since it won't have a track after in from which the track's end index can be extracted
#     current_track = track_list[a]
#     next_track = track_list[a+1]
#     current_track["track"] + ". " + current_track["title"] + "." + file_extension
#     ffmpeg_command = "ffmpeg -i " + audio_file + " -ss " + current_track["index"] + " -to " + next_track["index"] + " -c:a copy " + file_name
