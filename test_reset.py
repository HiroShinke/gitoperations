

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


    def test_reset1(self):

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

        self.assertEqual("""\
diff --git a/hello.txt b/hello.txt
index 47ca7f2..d3bbad9 100644
--- a/hello.txt
+++ b/hello.txt
@@ -1,2 +1,3 @@
 hello, world
 goodby japan
+goodby america
"""
                         ,cmd_stdout("git diff"))
                         
        cmd_stdout("git add hello.txt")
        cmd_stdout("git reset --hard")

        self.assertEqual("""\
hello, world
goodby japan
"""
                         ,cmd_stdout("cat hello.txt"))

        self.assertEqual("",
                         cmd_stdout("git diff"))


    def test_reset2(self):

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
        cmd_stdout("git reset --mixed")

        self.assertEqual("""\
hello, world
goodby japan
goodby america
"""
                         ,cmd_stdout("cat hello.txt"))

        self.assertEqual("""\
diff --git a/hello.txt b/hello.txt
index 47ca7f2..d3bbad9 100644
--- a/hello.txt
+++ b/hello.txt
@@ -1,2 +1,3 @@
 hello, world
 goodby japan
+goodby america
"""
                         ,cmd_stdout("git diff"))



    def test_reset3(self):

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
        cmd_stdout('git reset b3db10b --hard')

        self.assertEqual("""\
hello, world
goodby japan
"""
                         ,cmd_stdout("cat hello.txt"))

        self.assertEqual(""
                         ,cmd_stdout("git diff"))

        self.assertEqual("""\
* b3db10b B
* 70809e4 A
"""
                         ,cmd_stdout("git log --graph --abbrev-commit --oneline"))


    def test_reset4(self):

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

        self.assertEqual("""\
* 40c9072 C
* b3db10b B
* 70809e4 A
"""
                         ,cmd_stdout("git log --graph --abbrev-commit --oneline"))


        cmd_stdout('git reset b3db10b --hard')

        self.assertEqual("""\
hello, world
goodby japan
"""
                         ,cmd_stdout("cat hello.txt"))

        self.assertEqual(""
                         ,cmd_stdout("git diff"))

        self.assertEqual("""\
* b3db10b B
* 70809e4 A
"""
                         ,cmd_stdout("git log --graph --abbrev-commit --oneline"))


        make_file("hello.txt","""\
hello, world
goodby japan
goodby europe
"""
                  )

        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m D')

        self.assertEqual("""\
* b33898f D
* b3db10b B
* 70809e4 A
"""
                         ,cmd_stdout("git log --graph --abbrev-commit --oneline"))


        cmd_stdout('git reset 40c9072 --hard')

        self.assertEqual("""\
* 40c9072 C
* b3db10b B
* 70809e4 A
"""
                         ,cmd_stdout("git log --graph --abbrev-commit --oneline"))


if __name__ == "__main__":
    unittest.main()


    
