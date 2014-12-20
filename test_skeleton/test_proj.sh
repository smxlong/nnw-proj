# Make sure we're in the right place, otherwise we could blow away a real set of makelists
CURDIR=`pwd`
if [ `basename $CURDIR` != test_skeleton ]; then
  echo You need to be in the test_skeleton directory to run this script.
  exit 1
fi

# Delete all old CMakeLists.txt
find . -name CMakeLists.txt -exec rm {} \;

# Make the executable project first
proj.py new executable --name main --sources main.cpp

# Create the hello project
cd hello
proj.py new library --name hello --sources hello.cpp --headers hello.h
cd ..

# Add hello subdir to main project
proj.py add --subdirs hello

# Add hello as linklib
proj.py add --libs hello

# Try to build it
mkdir -p b
cd b
rm -rf *
cmake ..
make
./main
