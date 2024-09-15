#! /usr/bin/env python
import sys
import os
import argparse
from os.path import splitext
from decimal import *
from pprint import pp



# helper functoins
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

    """
    subtracts two times passed as CUE-syle timestamps and returns
    their difference in seconds
    """
    
    return abs(convert_to_seconds(time_one)
             - convert_to_seconds(time_two))

def parse_args():

    """returns ArgumentParser for cue2tracks. 'c2t --help' for more info"""
    
    parser = argparse.ArgumentParser(
    		  prog='cue2tracks',
                  description='A small Python program for converting ' \
                            + 'single-file albums to one file for each' \
                            + 'track using a CUE sheet as reference')

    parser.add_argument('cue_path')
    parser.add_argument('-y',
                        action='store_true',
                        help='approve any requests for your approbation')

    if len(sys.argv) > 1:
        return parser.parse_args()
    else:
        parser.parse_args(['-h'])

        
class cue2tracks:

    def __init__(self, y=False):
        self.y = y
        
    """
    Methods used for parsing and conversion are found below. These are
    all holdovers from before they were methods of a class, but I've
    kept them since the devision seems logical to me
    """    
    def parse_cue_file(self, cue_path: str) -> list[dict, list, str, str]:
        """
        Parses a CUE file and returns a dictionary containing metadata
        and a list of track dictionarie.

        Args:
            cue_path (str): Path to the CUE file.

        Returns:
            dict: Dictionary containing *album* metad.
            list: List of dictionaries containing *track* information.
        """

        print(f"Parsing file: {cue_path}...")
        track_list = []
        # ffmpeg will try to guess some tags
        # we like to think we're smarter than ffmpeg
        album_flags = "--remove-all-tags "
        tag_setting_flag = "--set-tag="

        with open(cue_path, errors='backslashreplace') as cue:
            
            print("Parsing album data...")
            
            for line in cue:
                # if we've reached the end of the album-specific metadata
                if not line or line.startswith("FILE"):
                    break

                # sometimes the first character in a file is a zero-width
                # space, which can mess up a remarkable number of things
                if line[0] == '​': line = line[1:]
                
                if line.startswith("REM"):
                    field = line.split()[1]
                    value = line.removeprefix(f"REM {field} ").strip("\" \n")
                else:
                    field = line.split()[0]
                    value = line.removeprefix(field).strip("\" \n")
                    
                if field == "PERFORMER": # flacs uses this term differetnly
                    album_flags += f" {tag_setting_flag}"\
                                 + f"\"album_artist={value}\" "
                elif field == "TITLE": # this one, too
                    album_flags += f" {tag_setting_flag}"\
                                 + f"\"ALBUM={value}\" "
                else: 
                    album_flags += f"{tag_setting_flag}"\
                                 + f"\"{field}={value}\" "
                            
                    print(f"{field}: {value:>{60-len(field)}}")

            audio_file = line.removeprefix("FILE ").rsplit(' ', 1)[0]
            audio_file = audio_file.strip("\"")
            file_extension = splitext(audio_file)[1]
            print(f"CD image: {audio_file:>52}")
            print(f"File extension: {file_extension:>46}")
            
            # Read each track's specific metadata
            for track in cue:
                track_number = track.strip().split()[1]
                track_flags = f"{tag_setting_flag}"\
                            + f"\"TRACK={track_number}\" "
                track_timestamp = ""
                
                for field in cue:
                    field_name = field.strip().split()[0]
                    if field_name == "INDEX":
                        if field.split()[1] == "01":
                            # Indices are only used for splitting the image
                            # We only need INDEX 01
                            # And the others (just 00, really) always come last
                            # in a list of a track's data
                            track_timestamp = field.split()[2]
                            track_list.append([track_flags, track_timestamp])
                            break
                        else:
                            continue
                        
                    field_value = field.strip().removeprefix(field_name + " ")

                    if field_name == "PERFORMER":
                        field_name = "ARTIST"
                        
                    # metaflac only needs quotes around entire "A=B" exp
                    field_value = field_value.strip("\"'")
                    track_flags += f"{tag_setting_flag}"\
                                 + f"\"{field_name}={field_value}\" "

            print(f"Parsed {len(track_list)} tracks")

            album_flags += f"{tag_setting_flag}"\
                         + f"\"TOTALTRACKS={len(track_list)}\" "
            
            return album_flags, track_list, file_extension, audio_file

        
    def convert_tracks(self,
                       album_flags,
                       track_list,
                       file_extension,
                       audio_file):
        """
        Uses system's ffmpeg installation in path to convert a flac file
        into individual tracks, then uses system's id3v2 installation to
        tag them according to the track_list.

        Args:
            metadata (dict): a dictionary containing metadat about the album
            track_list (dict): a dictionary containing metadata about the
                               tracks
            audio_file (string): the name of the audio file to be split
        Returns:
            nothing
        """
        
        for index, current_track in enumerate(track_list):
            current_track_file_name = f"Track {index}{file_extension}"
            current_track_index01 = convert_to_seconds(track_list[index][1])
            
            # the last track needs a separate command since it can't use
            # the next track's index as reference
            if index == len(track_list)-1:
                ffmpeg_command = f"ffmpeg"\
                               + f" -ss {current_track_index01}"\
                               + f" -i \"{audio_file}\" -map_metadata -1"\
                               + f" -c:a copy"\
                               + f" \"{current_track_file_name}\""\
                               + " -y"
            else:
                next_track_index01 = convert_to_seconds(track_list[index+1][1])
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

            # tag each file right after it's reated
            metaflac_command = f"metaflac {album_flags} {current_track[0]} \"{current_track_file_name}\""
            print(metaflac_command)
            os.system(metaflac_command)


    def main(self, cue_path):
        """
        Directs the execution of the script
        """
        
        [album_flags,
         track_list,
         file_extension,
         audio_file] = self.parse_cue_file(cue_path)

        if self.y: 
            self.convert_tracks(album_flags,
                                track_list,
                                file_extension,
                                audio_file)
        else:
            try:
                confirmation = input("Convert tracks now? [Y/n]:") or 'y'
            except:
                confirmation = 'n'
            if confirmation[0].lower() == 'n':
                print("\nExiting...")
                exit()
            else:
                self.convert_tracks(album_flags,
                                    track_list,
                                    file_extension,
                                    audio_file)

                
if __name__ == "__main__":
    
    parser = parse_args()
    if len(sys.argv) < 2:
        sys.exit(1)
        
    c2t = cue2tracks(y=parser.y)

    c2t.main(parser.cue_path)
    
