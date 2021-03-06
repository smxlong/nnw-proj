#!/usr/bin/env python

import chunkparser
import optparser
import templates
import os
import sys
import re
import itertools

def usage(exitcode=0):
  print \
'''Possible commands:

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

For more detailed help, consult the manual.'''
  sys.exit(exitcode)

# Internal functions

def _confirm_overwrite(filename):
  if os.path.exists(filename):
    if not os.path.isfile(filename):
      print '%s already exists and is not a file' % filename
      raise Exception('will not overwrite %s' % filename)
    sys.stdout.write('Overwrite %s y/n? ' % filename)
    response = sys.stdin.readline()
    if len(response) < 1 or str.upper(response[0]) != 'Y':
      raise Exception('will not overwrite %s' % filename)

def _find_preflag(preflags, flag):
  for k in preflags:
    if k == flag:
      return True
    leader = '%s=' % flag
    if k.startswith(leader):
      return k[len(leader):]
  return False

def _get_cmakelists(preflags):
  cmakelists = _find_preflag(preflags, '--cmakelists')
  # The following line looks odd, but it means that if --cmakelists is given without the =filename part,
  # we fall back to CMakeLists.txt as the name.
  if cmakelists == True or cmakelists == False:
    return 'CMakeLists.txt'
  return cmakelists

def _find_chunk(chunks, name):
  c = _find_chunk_recursive(chunks, name)
  if c is None:
    raise Exception('couldn\'t find \'%s\' chunk' % name)
  return c
  
def _find_chunk_recursive(chunks, name):
  for c in chunks:
    if type(c) == type([]):
      if c[0] == name:
	return c
      c = _find_chunk_recursive(c[1], name)
      if c != None:
	return c
  return None

def _is_plain_chunk(chunk):
  return type(chunk) != type([])

# Safely add items to the chunk, avoiding duplicates and ignoring whitespace
def _add_to_chunk(chunk, items, adding):
  # Get current list of items in the chunk, stripping surrounding whitespace.
  # Use filter to ignore sub-chunks
  currentitems = map(str.strip, filter(_is_plain_chunk, chunk[1]))

  if adding:
    for i in map(str.strip, items):
      if i not in currentitems:
	chunk[1].append(i)
	currentitems.append(i)

  else:
    outitems = []
    cmpitems = map(str.strip, items)
    for i in currentitems:
      if i not in cmpitems:
	outitems.append(i)
    chunk[1] = outitems

_define = re.compile(r'\s*target_compile_definitions\s*\(\s*(\S+)\s+(PUBLIC|PRIVATE|INTERFACE)\s+-D([0-9a-zA-Z_]+)(=(\S+))?\s*\)\s*')
def _add_or_modify_define(chunk, target, define, kind, adding):
  # Split the define into name and value. Keep the = character in the value, we'll make use of it later
  eq = define.find('=')
  if eq >= 0:
    name = define[:eq]
    value = define[eq:]
  else:
    name = define
    value = ''

  if adding:
    # Scan the chunk looking for an existing definition of this symbol
    for i in xrange(len(chunk)):
      c = chunk[i]
      if _is_plain_chunk(c):
	m = _define.match(c)
	if m:
	  existingtarget = m.group(1)
	  existingkind = m.group(2)
	  existingsymbol = m.group(3)
	  if existingtarget == target and existingsymbol == name and existingkind == kind:
	    # Found it
	    chunk[i] = 'target_compile_definitions(%s %s -D%s%s)' % (target, kind, name, value)
	    return
    chunk.append('target_compile_definitions(%s %s -D%s%s)' % (target, kind, name, value))

  else:
    outitems = []
    for i in chunk:
      if _is_plain_chunk(i):
	m = _define.match(i)
	if m:
	  existingtarget = m.group(1)
	  existingkind = m.group(2)
	  existingsymbol = m.group(3)
	  if existingtarget == target and existingsymbol == name and existingkind == kind:
	    # This is the matching one, skip it
	    continue
      outitems.append(i)
    # Replace chunk contents with new list
    chunk[:] = outitems

_subdir = re.compile(r'\s*add_subdirectory\s*\(\s*(\S+)\s*\)\s*')
def _add_subdir(chunk, subdir, adding):
  if adding:
    for i in chunk:
      if _is_plain_chunk(i):
	m = _subdir.match(i)
	if m:
	  if m.group(1) == subdir:
	    # Already added, do not add it again
	    return
    chunk.append('add_subdirectory(%s)' % subdir)

  else:
    outitems = []
    for i in chunk:
      if _is_plain_chunk(i):
	m = _subdir.match(i)
	if m:
	  if m.group(1) == subdir:
	    # This is the one, don't add it to the output
	    continue
      outitems.append(i)
    chunk[:] = outitems

_linklib = re.compile(r'\s*target_link_libraries\s*\(\s*(\S+)\s+(debug|optimized|general)\s+(\S+)\s*\)\s*')
def _add_lib(chunk, target, lib, kind, adding):
  if adding:
    for i in chunk:
      if _is_plain_chunk(i):
	m = _linklib.match(i)
	if m:
	  existingtarget = m.group(1)
	  existingkind = m.group(2)
	  existinglib = m.group(3)
	  if existingtarget == target and existingkind == kind and existinglib == lib:
	    # Already added, do not add it again
	    return
    chunk.append('target_link_libraries(%s %s %s)' % (target, kind, lib))

  else:
    outitems = []
    for i in chunk:
      if _is_plain_chunk(i):
	m = _linklib.match(i)
	if m:
	  existingtarget = m.group(1)
	  existingkind = m.group(2)
	  existinglib = m.group(3)
	  if existingtarget == target and existingkind == kind and existinglib == lib:
	    # This is the one, don't add it to the output
	    continue
      outitems.append(i)
    chunk[:] = outitems

def _load_chunks(preflags):
  filename = _get_cmakelists(preflags)
  f = open(filename, 'r')
  data = f.read()
  f.close()
  return chunkparser.parse(data)

def _save_chunks(preflags, chunks):
  filename = _get_cmakelists(preflags)
  data = chunkparser.generate(chunks)
  f = open(filename, 'w')
  f.write(data)
  f.close()

def _set_name(preflags, name):
  chunks = _load_chunks(preflags)
  namechunk = _find_chunk(chunks, 'projectname')
  namechunk[1] = ['project(proj_%s)' % name]
  _save_chunks(preflags, chunks)

_extract_projname = re.compile(r'\s*project\(proj_(.*)\)')
def _get_name(chunks):
  name = _find_chunk(chunks, 'projectname')
  m = _extract_projname.match(name[1][0])
  if not m:
    raise Exception('corrupted or missing project name')
  return m.group(1)

def _get_type(chunks):
  possibilities = ['rootproject', 'executable', 'library']
  for p in possibilities:
    try:
      _find_chunk(chunks, p)
      return p
    except:
      pass
  raise Exception('project doesn\'t seem to be managed by proj')

def _init_from_template(template, preflags, groups):
  # All things initialized from template must be given a name
  if '--name' not in groups or groups['--name'] == []:
    raise Exception('no name specified')
  if len(groups['--name']) > 1:
    raise Exception('name must be given exactly once')
  name = groups['--name'][0]
  # To create new, we start with the template and then do an 'add'
  filename = _get_cmakelists(preflags)
  _confirm_overwrite(filename)
  f = open(filename, 'w')
  f.write(template)
  f.close()
  _set_name(preflags, name)
  cmd_add(preflags, groups)

# adding==True adds the information, adding==False deletes it
def _add_or_remove(preflags, groups, adding):
  sources = []
  headers = []
  defines = []
  publicdefines = []
  interfacedefines = []
  subdirs = []
  libs = []
  if '--sources' in groups:
    sources += groups['--sources']
  if '--headers' in groups:
    headers += groups['--headers']
  if '--defines' in groups:
    defines += groups['--defines']
  if '--private-defines' in groups:
    defines += groups['--private-defines']
  if '--public-defines' in groups:
    publicdefines += groups['--public-defines']
  if '--interface-defines' in groups:
    interfacedefines += groups['--interface-defines']
  if '--subdirs' in groups:
    subdirs += groups['--subdirs']
  if '--libs' in groups:
    libs += groups['--libs']

  # Load in the chunks
  chunks = _load_chunks(preflags)

  # Do some sanity checking based on project type
  projtype = _get_type(chunks)
  if projtype == 'rootproject':
    if sources or headers:
      raise Exception('sources and headers can\'t be added to a rootproject')

  # Add sources
  if sources:
    c = _find_chunk(chunks, 'sources')
    _add_to_chunk(c, sources, adding)

  # Add headers
  if headers:
    c = _find_chunk(chunks, 'headers')
    _add_to_chunk(c, headers, adding)

  # Add defines
  if defines:
    name = _get_name(chunks)
    c = _find_chunk(chunks, 'definitions')
    for d in defines:
      _add_or_modify_define(c[1], name, d, 'PRIVATE', adding)

  # Add publicdefines
  if publicdefines:
    name = _get_name(chunks)
    c = _find_chunk(chunks, 'definitions')
    for d in publicdefines:
      _add_or_modify_define(c[1], name, d, 'PUBLIC', adding)

  # Add interfacedefines
  if interfacedefines:
    name = _get_name(chunks)
    c = _find_chunk(chunks, 'definitions')
    for d in interfacedefines:
      _add_or_modify_define(c[1], name, d, 'INTERFACE', adding)

  # Add subdirs
  if subdirs:
    c = _find_chunk(chunks, 'subdirs')
    for d in subdirs:
      _add_subdir(c[1], d, adding)

  # Add libs
  if libs:
    name = _get_name(chunks)
    c = _find_chunk(chunks, 'linklibs')
    for l in libs:
      _add_lib(c[1], name, l, 'general', adding)

  # Blow chunks
  _save_chunks(preflags, chunks)

# Command implementations.

def cmd_help(preflags, groups):
  usage()

def cmd_new_rootproject(preflags, groups):
  _init_from_template(templates.rootproject, preflags, groups)

def cmd_new_executable(preflags, groups):
  _init_from_template(templates.executable, preflags, groups)
  chunks = _load_chunks(preflags)
  name = _get_name(chunks)
  exename = _find_chunk(chunks, 'exename')
  exename[1] = [name]
  _save_chunks(preflags, chunks)

def cmd_new_library(preflags, groups):
  _init_from_template(templates.library, preflags, groups)
  chunks = _load_chunks(preflags)
  name = _get_name(chunks)
  libname = _find_chunk(chunks, 'libname')
  libname[1] = [name]
  exports = _find_chunk(chunks, 'exports')
  exports[1] = ['target_include_directories(%s INTERFACE ${CMAKE_CURRENT_SOURCE_DIR})' % name]
  _save_chunks(preflags, chunks)

def cmd_add(preflags, groups):
  _add_or_remove(preflags, groups, True)

def cmd_remove(preflags, groups):
  _add_or_remove(preflags, groups, False)

def process_cmdline(args):
  preflags, cmdwords, groups = optparser.parse(args)
  # TODO: validate all the stuff we just parsed:
  # * Only recognized preflags are allowed
  # * Only recognized commands are allowed
  # * Only recognized groups are allowed
  #
  # The individual commands can validate the specific usages of preflags and groups.
  
  if cmdwords == []:
    usage()

  # To add a command, just define a function named cmd_my_command. You don't need to
  # change anything down here.
  #
  # For example:
  #   "new project" is provided by cmd_new_project
  #   "list" is provided by cmd_list
    
  cmd = 'cmd_' + str.join('_', cmdwords)
  func = globals().get(cmd, None)
  if not func:
    print 'ERROR: unrecognized command \'%s\'' % str.join(' ', cmdwords)
    usage(1)
  func(preflags, groups)

try:
  process_cmdline(sys.argv[1:])
except Exception as e:
  print 'ERROR: %s' % str(e)
  sys.exit(1)