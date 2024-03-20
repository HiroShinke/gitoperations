

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
goodby europe
goodby america
"""
                  )
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m D')

        make_file("hello.txt","""\
hello, world
goodby japan
goodby europe
goodby america
goodby world
"""
                  )
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m E')
        
        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
* 91ed2a5 E
* 967e46b D
* 40c9072 C
* b3db10b B
* 70809e4 A
"""
                         ,ret)
        
        cmd_stdout("git checkout master")

        make_file("hello.txt","""\
hello, world
goodby japan
goodby america
goodby africa
"""
                  )
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m F')

        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
* 65baea3 F
* 40c9072 C
* b3db10b B
* 70809e4 A
"""
                         ,ret)

        with self.assertRaises(subprocess.SubprocessError) as cm:
            cmd_stdout("git rebase new-topic")

        self.assertEqual("""\
hello, world
goodby japan
goodby europe
goodby america
<<<<<<< HEAD
goodby world
=======
goodby africa
>>>>>>> 65baea3 (F)
"""
                         ,cmd_stdout("cat hello.txt"))

        self.assertEqual("""\
interactive rebase in progress; onto 91ed2a5
Last command done (1 command done):
   pick 65baea3 F
No commands remaining.
You are currently rebasing branch 'master' on '91ed2a5'.
  (fix conflicts and then run "git rebase --continue")
  (use "git rebase --skip" to skip this patch)
  (use "git rebase --abort" to check out the original branch)

Unmerged paths:
  (use "git restore --staged <file>..." to unstage)
  (use "git add <file>..." to mark resolution)
	both modified:   hello.txt

no changes added to commit (use "git add" and/or "git commit -a")
"""
                         ,cmd_stdout("git status"))

        make_file("hello.txt","""\
hello, world
goodby japan
goodby europe
goodby america
goodby africa
goodby world
"""
                  )
        cmd_stdout("git add hello.txt")
        cmd_stdout("git commit -m \"F'\"")
        cmd_stdout("git rebase --continue")
        
        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
* e316ff3 F'
* 91ed2a5 E
* 967e46b D
* 40c9072 C
* b3db10b B
* 70809e4 A
"""
                         ,ret)

        ret = cmd_stdout("git show-branch")
        self.assertEqual("""\
* [master] F'
 ! [new-topic] E
--
*  [master] F'
*+ [new-topic] E
"""
                         ,ret)

        ret = cmd_stdout("cat hello.txt")
        self.assertEqual("""\
hello, world
goodby japan
goodby europe
goodby america
goodby africa
goodby world
"""
                         ,ret)


    def test_rebase1_1(self):

        """ use ptyexec for continue """
        

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

        cmd_stdout('git branch new-topic b3db10b')
        cmd_stdout('git checkout new-topic')


        make_file("hello.txt","""\
hello, world
goodby japan
goodby africa
"""
                  )
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m E')

        cmd_stdout('git branch new-topic2')
        cmd_stdout('git checkout new-topic2')
        
        make_file("hello.txt","""\
hello, world
goodby japan
goodby africa
goodby china
"""
                 )
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m F')
                  
        self.assertEqual("""\
! [master] D
 ! [new-topic] E
  * [new-topic2] F
---
  * [new-topic2] F
 +* [new-topic] E
+   [master] D
+   [master^] C
++* [new-topic^] B
"""
                         ,cmd_stdout("git show-branch"))

        with self.assertRaises(subprocess.SubprocessError) as cm:
            cmd_stdout("git rebase new-topic new-topic2 --onto master")

        self.assertEqual("""\
hello, world
goodby japan
<<<<<<< HEAD
goodby america
goodby europe
=======
goodby africa
goodby china
>>>>>>> 3399f7b (F)
"""
                         ,cmd_stdout("cat hello.txt"))


        make_file("hello.txt","""\
hello, world
goodby japan
goodby america
goodby europe
goodby china
"""
                 )

        cmd_stdout("git add hello.txt")
        cmd_stdout("git commit -m \"F'\"")
        cmd_stdout("git rebase --continue")

        self.assertEqual("""\
! [master] D
 ! [new-topic] E
  * [new-topic2] F'
---
  * [new-topic2] F'
+ * [master] D
+ * [master^] C
 +  [new-topic] E
++* [master~2] B
"""
                         ,cmd_stdout("git show-branch"))

        
    def test_rebase3(self):

        commit_file("E")
        commit_file("F")
        commit_file("G")
        commit_file("H")
        commit_file("I")
        commit_file("J")        

        self.assertEqual("""\
* 39f824d J
* 15755eb I
* ca7cd2f H
* 98b455d G
* 57eb397 F
* ae463d8 E
"""
                         ,cmd_stdout("git log --graph --abbrev-commit --oneline"))
        
        cmd_stdout('git rebase --onto master~5 master~3 master')


        self.assertEqual("""\
* 65e2642 J
* 351ed9c I
* 3552661 H
* ae463d8 E
"""
                         ,cmd_stdout("git log --graph --abbrev-commit --oneline"))

        
if __name__ == "__main__":
    unittest.main()


    
