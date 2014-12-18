#!/usr/bin/env python

import chunkparser
import optparser
import templates
import os
import sys
import re

def usage(exitcode=0):
  print 'usage: unknown'
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
  namechunk[1] = ['    project(proj_%s)' % name]
  _save_chunks(preflags, chunks)

_extract_projname = re.compile(r'\s*project\(proj_(.*)\)')
def _get_name(chunks):
  name = _find_chunk(chunks, 'projectname')
  m = _extract_projname.match(name[1][0])
  if not m:
    raise Exception('corrupted or missing project name')
  return m.group(1)

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

# Command implementations.

def cmd_help(preflags, groups):
  usage()

def cmd_new_project(preflags, groups):
  _init_from_template(templates.rootproject, preflags, groups)

def cmd_new_executable(preflags, groups):
  _init_from_template(templates.executable, preflags, groups)
  chunks = _load_chunks(preflags)
  name = _get_name(chunks)
  exename = _find_chunk(chunks, 'exename')
  exename[1] = [name]
  _save_chunks(preflags, chunks)
  
def cmd_add(preflags, groups):
  sources = None
  headers = None
  if '--sources' in groups:
    sources = groups['--sources']
  if '--headers' in groups:
    headers = groups['--headers']
  if sources is None and headers is None:
    # Nothing was asked of us, don't touch the file at all
    return
  chunks = _load_chunks(preflags)
  if sources is not None:
    c = _find_chunk(chunks, 'sources')
    for s in sources:
      c[1].append('    %s' % s)
  if headers is not None:
    c = _find_chunk(chunks, 'headers')
    for h in headers:
      c[1].append('    %s' % h)
  _save_chunks(preflags, chunks)

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

#try:
process_cmdline(sys.argv[1:])
#except Exception as e:
#  print 'ERROR: %s' % str(e)