

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

        commit_file("A")
        commit_file("B")        
        commit_file("C")
        
        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
* b8324b8 C
* 0441581 B
* 2dd0306 A
"""
                         ,ret)

        cmd_stdout("git checkout -b new-topic")

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
        
        cmd_stdout("git checkout master")

        commit_file("F")

        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
* 8f4e340 F
* b8324b8 C
* 0441581 B
* 2dd0306 A
"""
                         ,ret)

        cmd_stdout("git rebase new-topic")

        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
* 8b27ada F
* 4f26866 E
* 3af0be2 D
* b8324b8 C
* 0441581 B
* 2dd0306 A
"""
                         ,ret)

        ret = cmd_stdout("git show-branch --more=5")
        self.assertEqual("""\
* [master] F
 ! [new-topic] E
--
*  [master] F
*+ [new-topic] E
*+ [new-topic^] D
*+ [new-topic~2] C
*+ [new-topic~3] B
*+ [new-topic~4] A
"""
                         ,ret)


    def test_rebase2(self):

        commit_file("A")
        commit_file("B")        
        commit_file("C")
        
        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
* b8324b8 C
* 0441581 B
* 2dd0306 A
"""
                         ,ret)

        cmd_stdout("git checkout -b new-topic")

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
        
        cmd_stdout("git checkout master")

        commit_file("F")

        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
* 8f4e340 F
* b8324b8 C
* 0441581 B
* 2dd0306 A
"""
                         ,ret)

        cmd_stdout("git rebase --onto new-topic master~ master")
        
        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
* 8b27ada F
* 4f26866 E
* 3af0be2 D
* b8324b8 C
* 0441581 B
* 2dd0306 A
"""
                         ,ret)

        ret = cmd_stdout("git show-branch --more=5")
        self.assertEqual("""\
* [master] F
 ! [new-topic] E
--
*  [master] F
*+ [new-topic] E
*+ [new-topic^] D
*+ [new-topic~2] C
*+ [new-topic~3] B
*+ [new-topic~4] A
"""
                         ,ret)



    def test_rebase3(self):

        commit_file("A")
        commit_file("B")        
        commit_file("C")
        
        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
* b8324b8 C
* 0441581 B
* 2dd0306 A
"""
                         ,ret)

        cmd_stdout("git checkout -b new-topic")

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
        
        cmd_stdout("git checkout master")

        commit_file("F")

        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
* 8f4e340 F
* b8324b8 C
* 0441581 B
* 2dd0306 A
"""
                         ,ret)

        cmd_stdout("git rebase --onto master new-topic")
        
        ret = cmd_stdout("git show-branch --more=5")
        self.assertEqual("""\
* [master] F
 ! [new-topic] E
--
 + [new-topic] E
 + [new-topic^] D
*  [master] F
*+ [new-topic~2] C
*+ [new-topic~3] B
*+ [new-topic~4] A
"""
                         ,ret)

        cmd_stdout("git checkout master")
        cmd_stdout("git merge new-topic")

        ret = cmd_stdout("git show-branch --more=5")
        self.assertEqual("""\
* [master] Merge branch 'new-topic'
 ! [new-topic] E
--
-  [master] Merge branch 'new-topic'
*+ [new-topic] E
*+ [new-topic^] D
*  [master^] F
*+ [master~2] C
*+ [master~3] B
*+ [master~4] A
"""
                         ,ret)



    def test_rebase4(self):

        commit_file("A")
        commit_file("B")
        commit_file("C")
        commit_file("D")
        commit_file("E")

        
        self.assertEqual("""\
* 4f26866 E
* 3af0be2 D
* b8324b8 C
* 0441581 B
* 2dd0306 A
"""
                         ,cmd_stdout("git log --graph --abbrev-commit --oneline"))

        cmd_stdout("git branch maint 0441581")
        cmd_stdout("git checkout maint")

        commit_file("W")
        commit_file("X")
        commit_file("Y")
        commit_file("Z")

        self.assertEqual("""\
* 46f4fb0 Z
* c88d99e Y
* d1bb43e X
* 8467c6b W
* 0441581 B
* 2dd0306 A
"""
                         ,cmd_stdout("git log --graph --abbrev-commit --oneline"))

        cmd_stdout("git branch feature c88d99e")
        cmd_stdout("git checkout feature")

        commit_file("P")
        commit_file("Q")

        self.assertEqual("""\
* 763c98d Q
* 7850129 P
* c88d99e Y
* d1bb43e X
* 8467c6b W
* 0441581 B
* 2dd0306 A
"""
                         ,cmd_stdout("git log --graph --abbrev-commit --oneline"))


        cmd_stdout("git rebase --onto master maint~ feature")
        
        self.assertEqual("""\
* d994301 Q
* 6ce9ab1 P
* 4f26866 E
* 3af0be2 D
* b8324b8 C
* 0441581 B
* 2dd0306 A
"""
                         ,cmd_stdout("git log --graph --abbrev-commit --oneline"))


        
        self.assertEqual("""\
* [feature] Q
 ! [maint] Z
  ! [master] E
---
 +  [maint] Z
 +  [maint^] Y
 +  [maint~2] X
 +  [maint~3] W
*   [feature] Q
*   [feature^] P
* + [master] E
* + [master^] D
* + [master~2] C
*++ [maint~4] B
*++ [maint~5] A
"""
                         ,cmd_stdout("git show-branch --more=5"))

        
        
    def test_rebase4(self):

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


    def helper_rebase5(self):

        commit_file("A")
        commit_file("B")
        commit_file("C")
        commit_file("D")

        self.assertEqual("""\
* 3af0be2 D
* b8324b8 C
* 0441581 B
* 2dd0306 A
"""
                         ,cmd_stdout("git log --graph --abbrev-commit --oneline"))
        
        cmd_stdout("git branch dev master~3")
        cmd_stdout("git checkout dev")

        commit_file("X")
        commit_file("Y")
        commit_file("Z")
        
        self.assertEqual("""\
* f7491ed Z
* 174d94d Y
* 7e3b2a3 X
* 2dd0306 A
"""
                         ,cmd_stdout("git log --graph --abbrev-commit --oneline"))

        cmd_stdout("git branch dev2 dev~")
        cmd_stdout("git checkout dev2")
        
        commit_file("P")
        commit_file("Q")

        self.assertEqual("""\
* aa352cf Q
* 283ec77 P
* 174d94d Y
* 7e3b2a3 X
* 2dd0306 A
"""
                         ,cmd_stdout("git log --graph --abbrev-commit --oneline"))

        cmd_stdout("git rebase master dev")

        self.assertEqual("""\
* da1e91a Z
* ccdbf92 Y
* c682392 X
* 3af0be2 D
* b8324b8 C
* 0441581 B
* 2dd0306 A
"""
                         ,cmd_stdout("git log --graph --abbrev-commit --oneline"))

        
        self.assertEqual("""\
* [dev] Z
 ! [dev2] Q
  ! [master] D
---
 +  [dev2] Q
 +  [dev2^] P
 +  [dev2~2] Y
 +  [dev2~3] X
*   [dev] Z
*   [dev^] Y
*   [dev~2] X
* + [master] D
* + [master^] C
* + [master~2] B
*++ [dev2~4] A
"""
                         ,cmd_stdout("git show-branch"))


    def test_rebase5_1(self):

        self.helper_rebase5()
        
        cmd_stdout("git rebase dev~ dev2")        
        
        self.assertEqual("""\
! [dev] Z
 * [dev2] Q
  ! [master] D
---
 *  [dev2] Q
 *  [dev2^] P
+   [dev] Z
+*  [dev2~2] Y
+*  [dev2~3] X
+*+ [master] D
+*+ [master^] C
+*+ [master~2] B
+*+ [master~3] A
"""
                         ,cmd_stdout("git show-branch --more=5"))


    def test_rebase5_2(self):

        self.helper_rebase5()
        
        cmd_stdout("git rebase --onto dev~ dev2~3 dev2")        
        
        self.assertEqual("""\
! [dev] Z
 * [dev2] Q
  ! [master] D
---
 *  [dev2] Q
 *  [dev2^] P
+   [dev] Z
+*  [dev2~2] Y
+*  [dev2~3] X
+*+ [master] D
+*+ [master^] C
+*+ [master~2] B
+*+ [master~3] A
"""
                         ,cmd_stdout("git show-branch --more=5"))


    def helper_rebase6(self):

        commit_file("A")
        commit_file("B")
        commit_file("C")
        commit_file("D")

        self.assertEqual("""\
* 3af0be2 D
* b8324b8 C
* 0441581 B
* 2dd0306 A
"""
                         ,cmd_stdout("git log --graph --abbrev-commit --oneline"))
        
        cmd_stdout("git branch dev master~2")
        cmd_stdout("git checkout dev")

        commit_file("X")
        commit_file("Y")
        commit_file("Z")

        self.assertEqual("""\
* [dev] Z
 ! [master] D
--
 + [master] D
 + [master^] C
*  [dev] Z
*  [dev^] Y
*  [dev~2] X
*+ [master~2] B
*+ [master~3] A
"""
                     ,cmd_stdout("git show-branch --more=5"))


        
        cmd_stdout("git branch dev2 dev~1")
        cmd_stdout("git checkout dev2")

        commit_file("P")

        self.assertEqual("""\
* a1dca86 P
* 3de9d62 Y
* 4405c30 X
* 0441581 B
* 2dd0306 A
"""
        ,cmd_stdout("git log --graph --abbrev-commit --oneline"))

        cmd_stdout("git checkout dev")
        cmd_stdout("git merge dev2")

        commit_file("N")

        self.assertEqual("""\
* [dev] N
 ! [dev2] P
  ! [master] D
---
  + [master] D
  + [master^] C
*   [dev] N
*+  [dev2] P
*   [dev~2] Z
*+  [dev~3] Y
*+  [dev~4] X
*++ [master~2] B
*++ [master~3] A
"""
                         ,cmd_stdout("git show-branch --more=5"))

        self.assertEqual(
r"""* 07d853e N
*   eb7aeba Merge branch 'dev2' into dev
|\  
| * a1dca86 P
* | 1ee5867 Z
|/  
* 3de9d62 Y
* 4405c30 X
* 0441581 B
* 2dd0306 A
"""
        ,cmd_stdout("git log --graph --abbrev-commit --oneline"))


    def test_rebase6_1(self):

        self.helper_rebase6()

        cmd_stdout("git rebase master dev")

        
        self.assertEqual("""\
* [dev] N
 ! [dev2] P
  ! [master] D
---
 +  [dev2] P
 +  [dev2^] Y
 +  [dev2~2] X
*   [dev] N
*   [dev^] P
*   [dev~2] Z
*   [dev~3] Y
*   [dev~4] X
* + [master] D
* + [master^] C
*++ [dev2~3] B
*++ [dev2~4] A
"""
                         ,cmd_stdout("git show-branch --more=5"))

        self.assertEqual("""\
* 43439fb N
* e331821 P
* da1e91a Z
* ccdbf92 Y
* c682392 X
* 3af0be2 D
* b8324b8 C
* 0441581 B
* 2dd0306 A
"""
        ,cmd_stdout("git log --graph --abbrev-commit --oneline"))
        


    def test_rebase6_2(self):

        self.helper_rebase6()

        cmd_stdout("git checkout dev")
#       ptyexec.pty_exec("git rebase --rebase-merges master -i",
#                        keyseq=b":wq\r")
        cmd_stdout("git rebase --rebase-merges master")
        
        self.assertEqual("""\
* [dev] N
 ! [dev2] P
  ! [master] D
---
 +  [dev2] P
 +  [dev2^] Y
 +  [dev2~2] X
*   [dev] N
*   [dev^^2] P
*   [dev~2] Z
*   [dev~3] Y
*   [dev~4] X
* + [master] D
* + [master^] C
*++ [dev2~3] B
*++ [dev2~4] A
"""
                         ,cmd_stdout("git show-branch --more=5"))

        self.assertEqual(
r"""* b6f4097 N
*   7a72e89 Merge branch 'dev2' into dev
|\  
| * cfbab7c P
* | da1e91a Z
|/  
* ccdbf92 Y
* c682392 X
* 3af0be2 D
* b8324b8 C
* 0441581 B
* 2dd0306 A
"""
        ,cmd_stdout("git log --graph --abbrev-commit --oneline"))

        
        
    def test_rebase_txt1(self):

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


    def test_rebase_txt1_1(self):

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


    def test_rebase_txt2(self):

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

        

        
if __name__ == "__main__":
    unittest.main()


    
