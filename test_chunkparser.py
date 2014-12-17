import chunkparser
import unittest

class test_chunkparser_parse(unittest.TestCase):
  def test_empty_input(self):
    input_data = ''
    result = chunkparser.parse(input_data)
    self.assertEqual([''], result)
    
  def test_single_line_input_no_final_newline(self):
    input_data = 'test'
    result = chunkparser.parse(input_data)
    self.assertEqual(['test'], result)

  def test_single_line_input_with_final_newline(self):
    input_data = 'test\n'
    result = chunkparser.parse(input_data)
    self.assertEqual(['test\n'], result)
    
  def test_multi_line_input_no_final_newline(self):
    input_data = '''test
test
test'''
    result = chunkparser.parse(input_data)
    self.assertEqual(['test\ntest\ntest'], result)

  def test_multi_line_input_with_final_newline(self):
    input_data = '''test
test
test
'''
    result = chunkparser.parse(input_data)
    self.assertEqual(['test\ntest\ntest\n'], result)
    
  def test_everything_in_one_chunk_no_final_newline(self):
    input_data = '''# --== proj begin test ==--
test
test
# --== proj end test ==--'''
    result = chunkparser.parse(input_data)
    self.assertEqual([('test', ['test\ntest'])], result)

  def test_everything_in_one_chunk_with_final_newline(self):
    input_data = '''# --== proj begin test ==--
test
test
# --== proj end test ==--
'''
    result = chunkparser.parse(input_data)
    self.assertEqual([('test', ['test\ntest']), ''], result)

  def test_everything_in_one_chunk_leading_blank_lines(self):
    input_data = '''

# --== proj begin test ==--
test
test
# --== proj end test ==--
'''
    result = chunkparser.parse(input_data)
    self.assertEqual(['\n', ('test', ['test\ntest']), ''], result)
    
  def test_everything_in_one_chunk_trailing_blank_lines(self):
    input_data = '''# --== proj begin test ==--
test
test
# --== proj end test ==--


'''
    result = chunkparser.parse(input_data)
    self.assertEqual([('test', ['test\ntest']), '\n\n'], result)
    
  def test_sequence_of_chunks(self):
    input_data = '''a
# --== proj begin b ==--
c
# --== proj end b ==--
d
# --== proj begin e ==--
f
# --== proj end e ==--
g
'''

    result = chunkparser.parse(input_data)
    self.assertEqual(['a', ('b', ['c']), 'd', ('e', ['f']), 'g\n'], result)

  def test_nested_chunks(self):
    input_data = '''a
# --== proj begin b ==--
c
# --== proj begin d ==--
e
# --== proj end d ==--
# --== proj end b ==--
f
'''

    result = chunkparser.parse(input_data)
    self.assertEqual(['a', ('b', ['c', ('d', ['e'])]), 'f\n'], result)
    
if __name__ == '__main__':
    unittest.main()