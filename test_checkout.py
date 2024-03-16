

import unittest
import subprocess
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

    def test_checkout1(self):

        os.environ["GIT_AUTHOR_DATE"] = "Fri May 5 20:30:55 2023 +0900"
        os.environ["GIT_COMMITTER_DATE"] = "Fri May 5 20:30:55 2023 +0900"
        
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

        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
* 40c9072 C
* b3db10b B
* 70809e4 A
"""
                         ,ret)

        cmd_stdout("git branch new-topic")

        make_file("hello.txt","""\
hello, world
goodby japan
goodby europe
goodby america
"""
                  )
        cmd_stdout("git checkout new-topic")

        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m D')

        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
* 967e46b D
* 40c9072 C
* b3db10b B
* 70809e4 A
"""
                         ,ret)


    def test_checkout2(self):

        os.environ["GIT_AUTHOR_DATE"] = "Fri May 5 20:30:55 2023 +0900"
        os.environ["GIT_COMMITTER_DATE"] = "Fri May 5 20:30:55 2023 +0900"
        
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

        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
* 40c9072 C
* b3db10b B
* 70809e4 A
"""
                         ,ret)

        cmd_stdout("git checkout -b new-topic")

        make_file("hello.txt","""\
hello, world
goodby japan
goooby world
goodby america
"""
                  )

        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m E')

        cmd_stdout("git checkout master")
        
        make_file("hello.txt","""\
hello, world
goodby japan
goodby europe
goodby america
"""
                  )
        
        cmd_stdout("git checkout -m new-topic")
        self.assertEqual("""\
hello, world
goodby japan
<<<<<<< new-topic
goooby world
=======
goodby europe
>>>>>>> local
goodby america
"""
                         ,cmd_stdout("cat hello.txt"))

        make_file("hello.txt","""\
hello, world
goodby japan
goodby europe
goooby world
goodby america
"""
                  )

        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m D')

        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
* 2a28b8c D
* 1683878 E
* 40c9072 C
* b3db10b B
* 70809e4 A
"""
                         ,ret)

    def test_checkout3(self):

        os.environ["GIT_AUTHOR_DATE"] = "Fri May 5 20:30:55 2023 +0900"
        os.environ["GIT_COMMITTER_DATE"] = "Fri May 5 20:30:55 2023 +0900"
        
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

        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
* 40c9072 C
* b3db10b B
* 70809e4 A
"""
                         ,ret)

        cmd_stdout("git checkout b3db10b")
        self.assertEqual("""\
hello, world
goodby japan
"""
                         ,cmd_stdout("cat hello.txt"))

        self.assertEqual("""\
* (HEAD detached at b3db10b)
  master
"""
                         ,cmd_stdout("git branch -a"))

        cmd_stdout("git checkout master")
        self.assertEqual("""\
hello, world
goodby japan
goodby america
"""
                         ,cmd_stdout("cat hello.txt"))

        self.assertEqual("""\
* master
"""
                         ,cmd_stdout("git branch -a"))


    def test_checkout4(self):

        os.environ["GIT_AUTHOR_DATE"] = "Fri May 5 20:30:55 2023 +0900"
        os.environ["GIT_COMMITTER_DATE"] = "Fri May 5 20:30:55 2023 +0900"
        
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
goodby america
"""
                  )

        make_file("hello.txt","""\
hello, world
goodby japan
goodby america
"""
                  )
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m C')


        cmd_stdout("git merge HEAD")
        cmd_stdout("cat hello.txt",print_=True)

        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
* 40c9072 C
* b3db10b B
* 70809e4 A
"""
                         ,ret)


        cmd_stdout("git checkout b3db10b")
        self.assertEqual("""\
hello, world
goodby japan
"""
                         ,cmd_stdout("cat hello.txt"))

        self.assertEqual("""\
* (HEAD detached at b3db10b)
  master
"""
                         ,cmd_stdout("git branch -a"))


        make_file("hello.txt","""\
hello, world
goodby japan
goodby england
"""
                  )

        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m C2')

        cmd_stdout("git branch c2")
        cmd_stdout("git checkout c2")        
        self.assertEqual("""\
* c2
  master
"""
                        ,cmd_stdout("git branch -a"))


        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
* 249145c C2
* b3db10b B
* 70809e4 A
"""
                         ,ret)


if __name__ == "__main__":
    unittest.main()


    

