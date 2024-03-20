

import unittest
import os
import shutil
import sys
import re
import hashlib
import ptyexec
import io
from datetime import datetime
from testutil import *

class GitTest(unittest.TestCase):

    def setUp(self):
        os.chdir(DIR_ORG)
        if os.path.exists("testgitdir"):
            shutil.rmtree("testgitdir")
        os.mkdir("testgitdir")
        os.chdir("testgitdir")
        cmd_stdout("git init")
        cmd_stdout("git config user.name HirofumiShinke")
        cmd_stdout("git config user.email hiro.shinke@gmail.com")



    def test_revert1(self):

        commit_file("A")
        commit_file("B")        
        commit_file("C")
        commit_file("D")
        commit_file("E")
                
        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
* 4f26866 E
* 3af0be2 D
* b8324b8 C
* 0441581 B
* 2dd0306 A
"""
                         ,ret)
        
        ptyexec.pty_exec("git revert HEAD~2",
                         keyseq=b"ixxx\n\x1b:wq\n")

        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
* 5d2ba48 xxx Revert "C"
* 4f26866 E
* 3af0be2 D
* b8324b8 C
* 0441581 B
* 2dd0306 A
"""
                         ,ret)


        self.assertEqual("""\
A.txt
B.txt
D.txt
E.txt
"""
                         ,cmd_stdout("git ls-files"))

        
if __name__ == "__main__":
    unittest.main()


    
