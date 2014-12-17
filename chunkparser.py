import re

_beg = re.compile(r'# --== proj begin (.+) ==--\s*')
_end = re.compile(r'# --== proj end (.+) ==--\s*')

def parse(data):
  return _parse((l for l in data.split('\n')), None)
    
def _parse(lines, currname):
  # List of subchunks to return
  chunks = []
  
  # Line buffer
  buf = []
  
  # For each line...
  line = next(lines, None)
  while line is not None:
    matchbegin = _beg.match(line)
    matchend = _end.match(line)
    if not matchbegin and not matchend:
      buf.append(line)
    else:
      if buf:
	chunks.append(str.join('\n', buf))
	buf = []
      if matchbegin:
	name = matchbegin.group(1)
	subchunk = _parse(lines, name)
	chunks.append((name, subchunk))
      else:
	name = matchend.group(1)
	if name != currname:
	  raise Exception('unexpected chunk close marker \'%s\' (expected \'%s\')' % (name, currname))
	break
    line = next(lines, None)
  
  if buf:
    chunks.append(str.join('\n', buf))
  return chunks

def generate(chunks):
  return str.join('\n', map(_gen, chunks))

def _gen(chunk):
  if type(chunk) == type(()):
    name = chunk[0]
    return '# --== proj begin %s ==--\n%s\n# --== proj end %s ==--' % (name, generate(chunk[1]), name)
  return chunk