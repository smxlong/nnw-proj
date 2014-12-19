import optparser
import unittest

class test_optparser(unittest.TestCase):
  def test_no_args(self):
    args = []
    (preflags, cmdwords, groups) = optparser.parse(args)
    self.assertEqual(0, len(preflags))
    self.assertEqual(0, len(cmdwords))
    self.assertEqual(0, len(groups))
    
  def test_preflag_only(self):
    args = ['--test']
    (preflags, cmdwords, groups) = optparser.parse(args)
    self.assertEqual(['--test'], preflags)
    self.assertEqual(0, len(cmdwords))
    self.assertEqual(0, len(groups))

  def test_preflag_multi_only(self):
    args = ['--test', '--test2', '--test3']
    (preflags, cmdwords, groups) = optparser.parse(args)
    self.assertEqual(['--test', '--test2', '--test3'], preflags)
    self.assertEqual(0, len(cmdwords))
    self.assertEqual(0, len(groups))
    
  def test_cmd_only(self):
    args = ['test']
    (preflags, cmdwords, groups) = optparser.parse(args)
    self.assertEqual(0, len(preflags))
    self.assertEqual(['test'], cmdwords)
    self.assertEqual(0, len(groups))

  def test_cmd_multi_only(self):
    args = ['test', 'test2']
    (preflags, cmdwords, groups) = optparser.parse(args)
    self.assertEqual(0, len(preflags))
    self.assertEqual(['test', 'test2'], cmdwords)
    self.assertEqual(0, len(groups))
    
  def test_preflags_and_cmd(self):
    args = ['--test', 'test1']
    (preflags, cmdwords, groups) = optparser.parse(args)
    self.assertEqual(['--test'], preflags)
    self.assertEqual(['test1'], cmdwords)
    self.assertEqual(0, len(groups))

  def test_preflags_and_cmd_multi_1(self):
    args = ['--test', '--test2', 'test1']
    (preflags, cmdwords, groups) = optparser.parse(args)
    self.assertEqual(['--test', '--test2'], preflags)
    self.assertEqual(['test1'], cmdwords)
    self.assertEqual(0, len(groups))

  def test_preflags_and_cmd_multi_2(self):
    args = ['--test', 'test1', 'test2']
    (preflags, cmdwords, groups) = optparser.parse(args)
    self.assertEqual(['--test'], preflags)
    self.assertEqual(['test1', 'test2'], cmdwords)
    self.assertEqual(0, len(groups))

  def test_preflags_and_cmd_multi_3(self):
    args = ['--test', '--test3', 'test1', 'test2']
    (preflags, cmdwords, groups) = optparser.parse(args)
    self.assertEqual(['--test', '--test3'], preflags)
    self.assertEqual(['test1', 'test2'], cmdwords)
    self.assertEqual(0, len(groups))
    
  def test_cmd_and_empty_group(self):
    args = ['test', '--test1']
    (preflags, cmdwords, groups) = optparser.parse(args)
    self.assertEqual([], preflags)
    self.assertEqual(['test'], cmdwords)
    self.assertEqual({'--test1': []}, groups)

  def test_cmd_and_empty_group_multi(self):
    args = ['test', '--test1', '--test2']
    (preflags, cmdwords, groups) = optparser.parse(args)
    self.assertEqual([], preflags)
    self.assertEqual(['test'], cmdwords)
    self.assertEqual({'--test1': [], '--test2': []}, groups)

  def test_cmd_multi_and_empty_group_multi(self):
    args = ['test', 'test3', '--test1', '--test2']
    (preflags, cmdwords, groups) = optparser.parse(args)
    self.assertEqual([], preflags)
    self.assertEqual(['test', 'test3'], cmdwords)
    self.assertEqual({'--test1': [], '--test2': []}, groups)

  def test_cmd_and_group(self):
    args = ['test', '--test1', 'test2']
    (preflags, cmdwords, groups) = optparser.parse(args)
    self.assertEqual([], preflags)
    self.assertEqual(['test'], cmdwords)
    self.assertEqual({'--test1': ['test2']}, groups)

  def test_cmd_and_group_many_1(self):
    args = ['test', '--test1', 'test2', 'test3']
    (preflags, cmdwords, groups) = optparser.parse(args)
    self.assertEqual([], preflags)
    self.assertEqual(['test'], cmdwords)
    self.assertEqual({'--test1': ['test2', 'test3']}, groups)

  def test_cmd_and_group_many_2(self):
    args = ['test', '--test1', 'test3', 'test2']
    (preflags, cmdwords, groups) = optparser.parse(args)
    self.assertEqual([], preflags)
    self.assertEqual(['test'], cmdwords)
    self.assertEqual({'--test1': ['test3', 'test2']}, groups)

  def test_cmd_and_group_multi(self):
    args = ['test', '--test1', 'test2', '--test3', 'test4']
    (preflags, cmdwords, groups) = optparser.parse(args)
    self.assertEqual([], preflags)
    self.assertEqual(['test'], cmdwords)
    self.assertEqual({'--test1': ['test2'], '--test3': ['test4']}, groups)

  def test_cmd_and_group_merge(self):
    args = ['test', '--test1', 'test2', '--test1', 'test4']
    (preflags, cmdwords, groups) = optparser.parse(args)
    self.assertEqual([], preflags)
    self.assertEqual(['test'], cmdwords)
    self.assertEqual({'--test1': ['test2', 'test4']}, groups)

  def test_preflag_and_cmd_and_group_merge(self):
    args = ['--preflag', 'test', '--test1', 'test2', '--test1', 'test4']
    (preflags, cmdwords, groups) = optparser.parse(args)
    self.assertEqual(['--preflag'], preflags)
    self.assertEqual(['test'], cmdwords)
    self.assertEqual({'--test1': ['test2', 'test4']}, groups)
    
  def test_big(self):
    args = ['--noninteractive', 'new', 'executable', '--sources', 'a.cpp', 'b.cpp', 'c.cpp', '--headers', 'a.h', 'b.h', 'c.h', '--sources', 'd.cpp']
    (preflags, cmdwords, groups) = optparser.parse(args)
    self.assertEqual(['--noninteractive'], preflags)
    self.assertEqual(['new', 'executable'], cmdwords)
    self.assertEqual({'--sources': ['a.cpp', 'b.cpp', 'c.cpp', 'd.cpp'], '--headers': ['a.h', 'b.h', 'c.h']}, groups)
    
if __name__ == '__main__':
    unittest.main()
