# cue2tracks

This program uses a .cue file to guide it in splitting a single audio file with many tracks into individual files, each with one track. 

## Features
* works with any audio format supported by ffmpeg
* parses very very quickly
* conversion is lossless since no reencoding takes place
* conversion is also very quick for the same reason, only limited in speed by the amount of data being "converted"

## Known limitations
### To be patched in upcoming versions
* Has some issues with non-UTF-8 encodings
* Does not work on multi-file cue/audio combinations (e.g., album-name-part1.flac, album-name-part2.flac)
* Does not automatically write album cover to each file
  * while we work on this issue, you can use tools such as [puddletag](https://docs.puddletag.net/) for batch-writing of album covers

### Unlikely to ever be patched
* Can only convert formats supported by your compilation of ffmpeg


## Installation
This package requires almost no installation since all the code is contained in one file which can be linked or moved to a directory in $PATH, or simply executed in a normal directory. It does, however, have a couple of dependencies:

* ffmpeg
  * Installation instructions for every common operating system can be found [here](https://ffmpeg.org/download.html)
  * most Linux systems will have it already installed since it is a dependency for many packages
  * even more Linux users will find it very easy to install as it is many distributions' default package manager repositories
* metaflac
  * this should come with an installation of FLAC
  * And what kind of CUE/image isn't in flac?

## Usage
This command should be executed using Python 3:
* If your system has the `python3` command:  
`ptyhon3 c2t.py [PATH_TO_DIRECTORY_CONTAINING_CUE_AND_ALBUM]`
* If your system uses `python` to invoke the Python 3 interpreter:  
`python c2t.py [PATH_TO_DIRECTORY_CONTAINING_CUE_AND_ALBUM]`
* Give your user group permission to execute it and then do so (Linux):  
`chmod u+x c2t.py`  
`./c2t.py [PATH_TO_DIRECTORY_CONTAINING_CUE_AND_ALBUM]`
