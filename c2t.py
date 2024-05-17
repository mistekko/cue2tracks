#! /usr/bin/env python
import sys, os
from os.path import splitext
from decimal import * 


"""
Helper functions below
"""
def fix_time(input_time):
    """Converts a time from CUE format (MM:SS:cS) to ffmpeg format (HH:MM:SS.cS)
       Note that CUE files tend to limit our precision to hundredths of a seconds
    """

    return "00:"+input_time[0:-3]+"."+input_time[-2:]


def convert_to_seconds(time):
    """Converts a colon-separated time in ffmpeg format ino the number of seconds from epoch (i.e., 00:00:00)
    """
    
    times = time.split(':') #times is a list containing HH, MM, SS.mS... extracted from time
    seconds = int(int(times[0])*3600 + int(times[1]) * 60 + Decimal(times[2]))
    return seconds

def subtract_times(time_one, time_two):

    """subtracts two times passed as CUE-style timestamps and returns their difference in seconds
    """
    
    return abs(int(convert_to_seconds(time_one)) - int(convert_to_seconds(time_two)))


"""
code of substance below
"""
def parse_cue_file(cue_path):
    """Parses a CUE file and returns a dictionary containing metadata
    and a list of track dictionaries.

    Args:
        cue_path (str): Path to the CUE file.

    Returns:
        dict: Dictionary containing album metadata.
        list: List of track dictionaries, each containing track information.
    """

    print(f"parsing file: {cue_path}")

    metadata = {}
    audio_file = None
    track_list = []

    with open(cue_path, 'r') as cue:
        # Read album metadata
        for line in cue:
            line = line.strip()
            if not line or line.startswith("FILE"):
                break
            if line.startswith("REM"):
                key = line.split()[1]
                metadata[key] = line.removeprefix(f"REM {key} ").strip("\"")
                # print(f"\tkey: {key}\n\tvalue: {metadata[key]}")
                num = 28-len(key)
                print(f"{key}: {metadata[key]:>{28-len(key)}}")
                #second word equals the rest of the list/string
            else:
                key = line.split()[0]
                metadata[key] = line.removeprefix(key + " ").strip("\"")
                print(f"{key}: {metadata[key]:>{28-len(key)}}")
                #first word equals the rest of the list/strong

        # Parse audio file and extension
        audio_file = line.split()
        audio_file = " ".join(audio_file[1:-1])[1:-1] #gets rid of first and last work and first and last character of middle section
        file_extension = splitext(audio_file)[1]
        print(f"Detected file extension: {file_extension:>5}")
        metadata["file extension"] = file_extension

        # Read track information
                      
        for track in cue:
            track = track.strip().split(' ', 2)[1]
            performer, title, isrc, index00, index01 = "", "", "", "", ""

            for line in cue:
                line = line.strip()
                if line.startswith("PERFORMER"):
                    performer = line.split("PERFORMER ")[1].strip('\"')
                elif line.startswith("TITLE"):
                    title = line.strip().strip("TITLE ").strip("\"")
                elif line.startswith("ISRC"):
                    isrc = line.split("ISRC ")[1].strip()
                elif line.startswith("INDEX 00"):
                    index00 = line.split("INDEX 00 ")[1].strip()
                elif line.startswith("INDEX 01"):
                    index01 = line.split("INDEX 01 ")[1].strip()
                    track_list.append({
                        "track": track,
                        "title": title,
                        "performer": performer,
                        "isrc": isrc,
                        "index00": index00,
                        "index01": index01,
                    })
                    break

    return metadata, track_list, audio_file

def convert_tracks(metadata, track_list, audio_file):
    """Uses system calls to ffmpeg installation in path to convert a flac file into individual tracks according to track_list

    Args:
    	track_list (dict): a dictionary containing metadata about the tracks
    Returns:
   	nothing
    """


    for a in range(0,len(track_list)): #the last track will  need a different command since it won't have a track after it from which the track's end index can be extracted
        current_track = track_list[a]
        file_extension = metadata["file extension"]
        current_track_file_name = current_track["track"] + ". " + current_track["title"] + "." + file_extension
        current_track_index01 = fix_time(current_track['index01'])
        
        if a == len(track_list)-1:
            ffmpeg_command = f"ffmpeg -ss {current_track_index01} -i \"{audio_file}\" -map_metadata -1 \"{current_track_file_name}\" -y"
        else:
            next_track_index01 = fix_time(track_list[a+1]['index01'])
            duration = subtract_times(current_track_index01, next_track_index01)
            ffmpeg_command = f"ffmpeg -ss {current_track_index01} -t {duration} -i \"{audio_file}\" -map_metadata -1 \"{current_track_file_name}\" -y"
        print(ffmpeg_command)
        os.system(ffmpeg_command + " 2> /dev/null")

        #The following code tags each file right after its been converted
        id3_command = f"id3v2"
        tags_keys = [['-a','PERFORMER'], ['-A','TITLE'], ['-c','COMMENT'], ['-g','GENRE'], ['-y','DATE']]
        
        for pair in tags_keys:
            try:
                id3_command +=f" {pair[0]} \"{metadata[pair[1]]}\"" #the quotes are allowable by id3v2. If the tagging backend is switched, we may run into some type errors.
            except KeyError:
                print(f"{pair[1]} not specificed... skipping")

        id3_command += f" -t \"{current_track['title']}\" -T {current_track['track']} \"{current_track_file_name}\""
        print(id3_command)
        os.system(id3_command)
    
def main():
    """Main function that parses the CUE file and prints information."""

    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <CUE_file>")
        sys.exit(1)

    cue_path = sys.argv[1]
    metadata, track_list, audio_file = parse_cue_file(sys.argv[1])
    print("Cue parsed")
    convert_tracks(metadata, track_list, audio_file)


if __name__ == "__main__":
    main()
    
