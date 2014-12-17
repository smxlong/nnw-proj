import sys
import chunkparser
import unittest

input_data_emptystring = ''
input_data_test = 'test'
input_data_test_nl = 'test\n'

input_data_testtesttest = '''test
test
test'''

input_data_testtesttest_nl = '''test
test
test
'''

input_data_proj1 = '''# --== proj begin test ==--
test
test
# --== proj end test ==--'''

input_data_proj2 = '''# --== proj begin test ==--
test
test
# --== proj end test ==--
'''

input_data_proj3 = '''

# --== proj begin test ==--
test
test
# --== proj end test ==--
'''

input_data_proj4 = '''# --== proj begin test ==--
test
test
# --== proj end test ==--


'''

input_data_proj5 = '''a
# --== proj begin b ==--
c
# --== proj end b ==--
d
# --== proj begin e ==--
f
# --== proj end e ==--
g
'''

input_data_proj6 = '''a
# --== proj begin b ==--
c
# --== proj begin d ==--
e
# --== proj end d ==--
# --== proj end b ==--
f
'''

input_baddata_1 = '''# --== proj begin a ==--
# --== proj end b ==--
'''

class test_chunkparser_parse(unittest.TestCase):
  def test_empty_input(self):
    result = chunkparser.parse(input_data_emptystring)
    self.assertEqual([''], result)
    
  def test_single_line_input_no_final_newline(self):
    result = chunkparser.parse(input_data_test)
    self.assertEqual(['test'], result)

  def test_single_line_input_with_final_newline(self):
    result = chunkparser.parse(input_data_test_nl)
    self.assertEqual(['test\n'], result)
    
  def test_multi_line_input_no_final_newline(self):
    result = chunkparser.parse(input_data_testtesttest)
    self.assertEqual(['test\ntest\ntest'], result)

  def test_multi_line_input_with_final_newline(self):
    result = chunkparser.parse(input_data_testtesttest_nl)
    self.assertEqual(['test\ntest\ntest\n'], result)
    
  def test_everything_in_one_chunk_no_final_newline(self):
    result = chunkparser.parse(input_data_proj1)
    self.assertEqual([('test', ['test\ntest'])], result)

  def test_everything_in_one_chunk_with_final_newline(self):
    result = chunkparser.parse(input_data_proj2)
    self.assertEqual([('test', ['test\ntest']), ''], result)

  def test_everything_in_one_chunk_leading_blank_lines(self):
    result = chunkparser.parse(input_data_proj3)
    self.assertEqual(['\n', ('test', ['test\ntest']), ''], result)
    
  def test_everything_in_one_chunk_trailing_blank_lines(self):
    result = chunkparser.parse(input_data_proj4)
    self.assertEqual([('test', ['test\ntest']), '\n\n'], result)
    
  def test_sequence_of_chunks(self):
    result = chunkparser.parse(input_data_proj5)
    self.assertEqual(['a', ('b', ['c']), 'd', ('e', ['f']), 'g\n'], result)

  def test_nested_chunks(self):
    result = chunkparser.parse(input_data_proj6)
    self.assertEqual(['a', ('b', ['c', ('d', ['e'])]), 'f\n'], result)
    
  def test_regeneration(self):
    for name, val in globals().items():
      if name.startswith('input_data_'):
	result = chunkparser.generate(chunkparser.parse(val))
	self.assertEqual(val, result)
	
  def test_bad(self):
    for name, val in globals().items():
      if name.startswith('input_baddata_'):
	self.assertRaises(Exception, lambda: chunkparser.parse(val))
    
if __name__ == '__main__':
    unittest.main()