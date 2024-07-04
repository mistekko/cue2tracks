#! /usr/bin/env python
import sys
import os
import argparse
from os.path import splitext
from decimal import *
from pprint import pp



"""Helper functions """
def convert_to_seconds(time):
    """
    Converts a colon-separated CUE-style time (MM:SS:cS) into the the
    fully numerical unit of seconds
    """

    # times is a list containing HH, MM, SS.mS... extracted from time
    times = time.split(':') 
    seconds = int(int(times[0])*60 + int(times[1]) + Decimal(times[2])/100)
    return seconds

def subtract_times(time_one, time_two):

    """subtracts two times passed as CUE-syle timestamps and returns their difference in seconds"""
    
    return (abs(int(convert_to_seconds(time_one))
            - int(convert_to_seconds(time_two))))

def parse_args():

    """returns ArgumentParser for cue2tracks. 'c2t --help' for more info"""
    
    parser = argparse.ArgumentParser(
    		  prog='cue2tracks',
                  description='A small Python program for converting single-file albums to one file for each track using a CUE sheet as reference')

    parser.add_argument('cue_path')
    parser.add_argument('-y', action='store_true', help='approve any requests for your approbation, i.e., before conversion')

    if len(sys.argv) > 1:
        return parser.parse_args()
    else:
        parser.parse_args(['-h'])



"""Main class containing methods for cue-2-track-ing"""
class cue2tracks:

    def __init__(self):
        print("object created")

        
    """
    Methods used for parsing and conversion are found below. These are
    all holdovers from before they were methods of a class, but I've
    kept them since the devision seems logical to me
    """    
    def parse_cue_file(self, cue_path):
        """
        Parses a CUE file and returns a dictionary containing metadata
        and a list of track dictionaries.

        Args:
            cue_path (str): Path to the CUE file.

        Returns:
            dict: Dictionary containing *album* metadata.
            list: List of dictionaries containing *track* information.
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
                    num = 28-len(key)
                    print(f"{key}: {metadata[key]:>{28-len(key)}}")
                else:
                    key = line.split()[0]
                    metadata[key] = line.removeprefix(key + " ").strip("\"")
                    print(f"{key}: {metadata[key]:>{28-len(key)}}")

                
            """Parse audio file's name and extension"""            
            audio_file = line.split()
            # gets rid of first and last word and first and last character of middle section
            audio_file = " ".join(audio_file[1:-1])[1:-1] 
            file_extension = splitext(audio_file)[1]
            print(f"Detected file extension: {file_extension:>5}")
            metadata["file extension"] = file_extension

            # Read each track's specific metadata
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
                            "index01": index01,})
                        break

            return metadata, track_list, audio_file

    def convert_tracks(self, metadata, track_list, audio_file):
        """
        Uses system's ffmpeg installation in path to convert a flac file
        into individual tracks, then uses system's id3v2 installation to
        tag them according to the track_list.

        Args:
            metadat (dict): a dictionary containing metadat about the album
            track_list (dict): a dictionary containing metadata about the tracks
            audio_file (string): the name of the audio file to be split
        Returns:
            nothing
        """

        tags_keys = [['-A','TITLE'],
                     ['-c','COMMENT'],
                     ['-g','GENRE'],
                     ['-y','DATE']]
        
        for a in range(0,len(track_list)):
            current_track = track_list[a]
            file_extension = metadata["file extension"]
            current_track_file_name = f"{current_track['track']}."\
                                    + f" {current_track['title']}"\
                                    + f"{file_extension}"
            current_track_index01 = convert_to_seconds(current_track['index01'])

            # the last track needs a separate command since it can't use
            # the next track's index as reference
            if a == len(track_list)-1:
                ffmpeg_command = f"ffmpeg"\
                               + f" -ss {current_track_index01}"\
                               + f" -i \"{audio_file}\" -map_metadata -1"\
                               + f" \"{current_track_file_name}\""\
                               + " -y"
            else:
                next_track_index01 = convert_to_seconds(track_list[a+1]['index01'])
                duration = current_track_index01 - next_track_index01
                ffmpeg_command = f"ffmpeg"\
                               + f" -ss {current_track_index01}"\
                               + f" -to {next_track_index01}"\
                               + f" -i \"{audio_file}\""\
                               + f" -map_metadata -1"\
                               + f" -c:a copy"\
                               + f" \"{current_track_file_name}\""\
                               + f" -y"
            print(ffmpeg_command)
            os.system(ffmpeg_command + " 2> /dev/null")

            #The following code tags each file right after its been converted
            id3_command = f"id3v2"

            for pair in tags_keys:
                try:
                    id3_command +=f" {pair[0]} \"{metadata[pair[1]]}\"" 
                except KeyError:
                    print(f"{pair[1]} not specificed... skipping")

            id3_command += f" -t \"{current_track['title']}\""\
                         + f" -a \"{current_track['performer']}\""\
                         + f" -T \"{current_track['track']}\""\
              		 + f" \"{current_track_file_name}\""
            print(id3_command)
            os.system(id3_command)


    def main(self):
        """
        Directs the execution of the script
        """

        """
        in a very-soon-to-be-released update, we'll have a more proper
        way of determining the passed cue file. Both in this iteration
        AND in the just mentioned one, we'll determine cue_path outside
        of the parsing function. It will almost definitely end up being
        an instance variable since it'll be sorted from the rest of the
        elements in sys.argv at the same time as instance variable
        assignment.
        """
        cue_path = sys.argv[1]
        
        metadata, track_list, audio_file = self.parse_cue_file(cue_path)
        print("Cue parsed")

        self.convert_tracks(metadata, track_list, audio_file)


if __name__ == "__main__":


    parser = parse_args()
    if len(sys.argv) < 2:
        sys.exit(1)
        
    object = cue2tracks()

    object.main()
    
