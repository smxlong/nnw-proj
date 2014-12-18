#!/usr/bin/env python

import chunkparser
import optparser
import templates
import os
import sys


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

def _init_from_template(template, preflags, groups):
  # To create new, we start with the template and then do an 'add'
  filename = _get_cmakelists(preflags)
  _confirm_overwrite(filename)
  f = open(filename, 'w')
  f.write(template)
  f.close()
  cmd_add(preflags, groups)

# Command implementations.

def cmd_help(preflags, groups):
  usage()

def cmd_new_project(preflags, groups):
  _init_from_template(templates.rootproject, preflags, groups)

def cmd_new_executable(preflags, groups):
  _init_from_template(templates.executable, preflags, groups)

def cmd_add(preflags, groups):
  pass

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