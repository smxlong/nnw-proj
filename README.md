proj, a CMake project management tool
========

This is proj.

Possible commands:

  new [rootproject | executable | library]
  add
  remove

Usage examples:

Create an executable project from all source files in the current directory
  proj.py new executable --name hello --sources *.cpp --headers *.h

Add things to a project
  proj.py add --sources another.cpp
  proj.py add --headers another.h
  proj.py add --defines MAX_CLIENTS=32

Remove things from a project
  proj.py remove --sources bad.cpp
  proj.py remove --headers bad.h
  proj.py remove --defines MAX_CLIENTS

For more detailed help, consult the manual.