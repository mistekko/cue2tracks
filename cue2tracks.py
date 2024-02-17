#! /usr/bin python
import sys, os

          #this program assumes CUE files provided as input will be (computer generated) of standard structure:
          #- INDEX 01 is the last track field
          #- the tracks metadata is the last set of fields
          #it also assumes that the CUE only references one audio file. 
          
metadata = [] #this is all the album metadata
audio_file = [] #rather than have the user supply the CUE's corresponding audio file, let's detect it outomatically


track_list = [] #will contain dictionaries


#track metadata
track = ""
title = ""
isrc = ""
performer = "" #this is what CUE calls the artist! 
index00 = "" #timestamp of previos track's end in MM:SS:mS... convert this later becaus ffmpeg uses HH:MM:SS. May not be used
index01 = "" #timestamp of this track's beginning.


with open(sys.argv[1], 'r') as cue:
    #store the album metadata data in a list and grab the audio file's name
    line = cue.readline()
    while line.strip()[0:4] != "FILE": 
        metadata.append(line.strip()) #will probably change this in the future; right now, it's just there becuase I want to store this data, but I'm not sure how it's going to be used exactly yet
        line = cue.readline()

    audio_file = line[6:-7] #the last 7 characters are " WAVE, which we don't care about. The first 6, FILE ", are similarly irrelevant
    print(f"Converting file:{audio_file:>60}") 
          
    #the above works properly; trust me; trust yourself

    #grab the file extension for later use
    for n in range(1,len(audio_file)):
        if audio_file[-n] == ".":
            file_extension = audio_file[-n:]
            print(f"Detected file extension:{file_extension:>52}")

    track = cue.readline()
    while track != "":
        track = track.strip().split(' ')[1] #grabs the second word in the line after FILE. This should be something like "TRACK 01 AUDIO", meaning the track number should be the second word
        print("track: " + track) #works up to this point
        while line != "":
            line = cue.readline()
            if line.find("PERFORMER") > -1:
                performer = line.split("PERFORMER ")[1].strip('\"')[0:-2] #assumes the artist's name does not start with a space
                print(f"\tparsed performer {performer}")
            elif line.find("TITLE") > -1:
                title = line.strip().strip("TITLE ").strip("\"")
                print(f"\tparsed title {title}")
            elif line.find("ISRC") > -1:
                isrc = line.split("ISRC ")[1].strip()
                print(f"\tparsed irsc {isrc}")
            elif line.find("INDEX 00") > -1:
                index00 = line.split("INDEX 00 ")[1].strip()
                print(f"\tparsed index00 {index00}")
            elif line.find("INDEX 01") > -1:
                index01 = line.split("INDEX 01 ")[1].strip()
                #construct a dictionary of the just-parsed tracked and append it to track_list
                print(f"\tparsed index01 {index01}")
                track_list.append({"track" : track,
                                    "title" : title,
                                    "performer" : performer,
                                    "isrc" : isrc,
                                    "index00" : index00,
                                    "index01" : index01})
                print()
                break

        track = cue.readline() #this line is down here so the value in 'track' can be used to detect the end of the file and end iteration accordingly. This requires it to get its value BEFORE each iteration in which said value is used. Either that or check it each iteration, which is an extra conditional every iteration. Not the end of the world, but it is bloat that doesn't geatly improve the readability or intelligibility of my code (or so I think...)
            
    print(metadata, file_extension)         
    
#when the 'tracks' section is reached, create a dictionary for each track and a list containing each track

#dict: {n : {"track" : %track%, "title" : %title%, "performer" : %artist%, "index" : timestamp


#finally:
# for a in track_list[0:(len(track_list)-1)]: #the last track won't needs a different command since it won't have a track after in from which the track's end index can be extracted
#     current_track = track_list[a]
#     next_track = track_list[a+1]
#     current_track["track"] + ". " + current_track["title"] + "." + file_extension
#     ffmpeg_command = "ffmpeg -i " + audio_file + " -ss " + current_track["index"] + " -to " + next_track["index"] + " -c:a copy " + file_name
