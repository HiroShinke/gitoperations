

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


    def test_rebase1(self):

        make_file("hello.txt","""\
hello, world
"""
                  )
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m A')

        
        make_file("hello.txt","""\
hello, world
goodby japan
"""
                  )
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m B')

        cmd_stdout('git branch new-topic 70809e4')
        cmd_stdout('git checkout new-topic')

        make_file("hello.txt","""\
hello, world
goodby america
"""
                  )
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m C')


        make_file("hello.txt","""\
hello, world
goodby america
goodby europe
"""
                  )

        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m D')


        self.assertEqual("""\
* 5b91415 D
* b0fad3f C
* 70809e4 A
"""
                         ,cmd_stdout("git log --graph --abbrev-commit --oneline"))

        with self.assertRaises(subprocess.SubprocessError) as cm:
            cmd_stdout('git rebase master')

        self.assertEqual("""\
hello, world
<<<<<<< HEAD
goodby japan
=======
goodby america
>>>>>>> b0fad3f (C)
"""
                         ,cmd_stdout("cat hello.txt"))

        make_file("hello.txt","""\
hello, world
goodby japan
goodby america
"""
                  )

        cmd_stdout("git add hello.txt")
        ptyexec.pty_exec('git rebase --continue',
                         b"ixxx\n\x1b:wq\n",
                         stdout=io.BytesIO())
                         
        self.assertEqual("""\
hello, world
goodby japan
goodby america
goodby europe
"""
                         ,cmd_stdout("cat hello.txt"))

        self.assertEqual("""\
* a81a685 D
* bbc93fc xxx C
* b3db10b B
* 70809e4 A
"""
                         ,cmd_stdout("git log --graph --abbrev-commit --oneline"))


    def test_rebase2(self):

        make_file("hello.txt","""\
hello, world
"""
                  )
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m A')

        make_file("hello.txt","""\
hello, world
goodby japan
"""
                  )
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m B')

        make_file("hello.txt","""\
hello, world
goodby japan
goodby america
"""
                  )

        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m C')


        make_file("hello.txt","""\
hello, world
goodby japan
goodby america
goodby europe
"""
                  )

        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m D')

        self.assertEqual("""\
* 36da5b2 D
* 40c9072 C
* b3db10b B
* 70809e4 A
"""
                         ,cmd_stdout("git log --graph --abbrev-commit --oneline"))

        cmd_stdout('git branch new-topic 70809e4')
        cmd_stdout('git checkout new-topic')

        with self.assertRaises(subprocess.SubprocessError) as cm:
            cmd_stdout('git cherry-pick 40c9072 36da5b2')

        self.assertEqual("""\
hello, world
<<<<<<< HEAD
=======
goodby japan
goodby america
>>>>>>> 40c9072 (C)
"""
                         ,cmd_stdout("cat hello.txt"))

        make_file("hello.txt","""\
hello, world
goodby japan
goodby america
"""
                  )

        cmd_stdout("git add hello.txt")
        ptyexec.pty_exec("git cherry-pick --continue",
                         b"ixxx\n\x1b:wq\n",
                         stdout=io.BytesIO())

        self.assertEqual("""\
* d8b0b40 D
* 4d5d473 xxx C
* 70809e4 A
"""
                         ,cmd_stdout("git log --graph --abbrev-commit --oneline"))


        self.assertEqual("""\
hello, world
goodby japan
goodby america
goodby europe
"""
                         ,cmd_stdout("cat hello.txt"))
        


    def test_rebase3(self):

        make_file("hello.txt","""\
hello, world
xxx        
"""
                  )
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m A')

        cmd_stdout('git branch new-topic')

        make_file("hello.txt","""\
hello, world
xxx
goodby japan
yyy
"""
                  )
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m B')

        make_file("hello.txt","""\
hello, world
xxx
goodby japan
yyy
goodby america
zzz
"""
                  )

        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m C')


        make_file("hello.txt","""\
hello, world
xxx
goodby japan
yyy
goodby america
zzz
goodby europe
www
"""
                  )

        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m D')

        self.assertEqual("""\
* d60c2fe D
* 2513e3a C
* 89d63cd B
* 19cb86d A
"""
                         ,cmd_stdout("git log --graph --abbrev-commit --oneline"))

        cmd_stdout('git branch new-topic 19cb86d')
        cmd_stdout('git checkout new-topic')

        with self.assertRaises(subprocess.SubprocessError) as cm:
            cmd_stdout('git cherry-pick 2513e3a d60c2fe')

        self.assertEqual("""\
hello, world
<<<<<<< HEAD
xxx        
=======
xxx
goodby japan
yyy
goodby america
zzz
>>>>>>> 2513e3a (C)
"""
                         ,cmd_stdout("cat hello.txt"))

        make_file("hello.txt","""\
hello, world
xxx
yyy
goodby america
zzz
"""
                  )

        cmd_stdout("git add hello.txt")
        ptyexec.pty_exec("git cherry-pick --continue",
                         b"ixxx\n\x1b:wq\n",
                         stdout=io.BytesIO())

        self.assertEqual("""\
hello, world
xxx
yyy
goodby america
zzz
goodby europe
www
"""
                         ,cmd_stdout("cat hello.txt"))

        self.assertEqual("""\
* 0673ec1 D
* ecfb82d xxx C
* 19cb86d A
"""
                         ,cmd_stdout("git log --graph --abbrev-commit --oneline"))

        
if __name__ == "__main__":
    unittest.main()


    
