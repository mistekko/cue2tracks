# cue2tracks

This program uses a .cue file to guide it in splitting a single audio file with many tracks into individual files, each with one track. 

## Features
* works with any audio format supported by ffmpeg

## Installation
This package requires almost no installation since all the code is contained in one file which can be linked or moved to a directory in $PATH or simply executed in a normal directory. It does, however, have a couple of dependencies:

* ffmpeg
* * Installation instructions for every common operating system can be found [here](https://ffmpeg.org/download.html)
* * most Linux systems will have it already installed since it is a dependency for many packages
* * even more Linux users will find it very easy to install as it is many distributions' default package manager repositories
* id3v2
* * [Available](https://sourceforge.net/projects/id3v2/) for Unix-like systems and found in some distributions' default package manager repositories
* * this dependency is, in theory, easily changeable since it is only used twice (as of 15/05/24) in the code
