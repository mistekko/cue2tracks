# cue2tracks

This program uses a .cue file to guide it in splitting a single audio file with many tracks into individual files, each with one track. 

## Features
* works with any audio format supported by ffmpeg
* parses very very quickly
* conversion is lossless since no reencoding takes place
* conversion is also very quick for the same reason, only limited in speed by the amount of data being "converted"

## Known limitations
### To be patched in upcoming versions
* Does not work on non-UTF-8 cue files. This is often an issue for me, so expect it to be fixed rather soon
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
* id3v2
  * [Available](https://sourceforge.net/projects/id3v2/) for Unix-like systems and found in some distributions' default package manager repositories
  * this dependency is, in theory, easily changeable since it is only used twice (as of 15/05/24) in the code

## Usage
This command should be executed using Python 3:
* If your system has the <code>python3</code> command:  
<code>ptyhon3 c2t.py [PATH_TO_DIRECTORY_CONTAINING_CUE_AND_ALBUM]</code>
* If your system uses <code>python</code> to invoke the Python 3 interpreter:  
<code>ptyhon c2t.py [PATH_TO_DIRECTORY_CONTAINING_CUE_AND_ALBUM]</code>
* Give your user group permission to execute it and then do so (Linux):  
<code>chmod u+x c2t.py
./c2t.py [PATH_TO_DIRECTORY_CONTAINING_CUE_AND_ALBUM]<code>
