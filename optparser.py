import sys

# An opt string consists of, in order:
#
# 1. Zero or more "pre-flags" which start with the -- sequence
# 2. One or more command words with no -- sequence
# 3. Zero or more parameter groups
#
# A parameter group begins with a flag and is followed by zero or more non-flag items.
#
#
# This function returns a tuple (preflags, cmdwords, groups)
# preflags and cmdwords are both lists of strings.
# groups is a dictionary mapping group names to lists of strings.
def parse(args):
  PRE = 0
  CMD = 1
  GRP = 2
  stage = PRE
  
  preflags = []
  cmdwords = []
  groups = {}
  for a in args:

    # Pre-flag stage
    if stage == PRE:
      if a.startswith('--'):
	preflags.append(a)
      else:
	stage = CMD
    
    # Command word stage
    if stage == CMD:
      if not a.startswith('--'):
	cmdwords.append(a)
      else:
	stage = GRP
	
    # Group stage
    if stage == GRP:
      if a.startswith('--'):
	group = a
	groups.setdefault(group, [])
      else:
	groups[group].append(a)
	
  return preflags, cmdwords, groups