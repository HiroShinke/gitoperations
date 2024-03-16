

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

    def test_basec1(self):
        make_file("hello.txt","hello world")
        cmd_stdout("git add hello.txt")
        ret = cmd_stdout("git status")
        self.assertTrue(re.search("No commits yet",ret))

    def test_basec2(self):
        make_file("hello.txt","hello world")
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m "add hello.txt" hello.txt')
        ret = cmd_stdout("git status")
        self.assertTrue( re.search("nothing to commit, working tree clean",ret) )

    def test_basec3(self):
        make_file("hello.txt","hello world\n")
        cmd_stdout("git add hello.txt")
        ret = cmd_stdout("git ls-files -s")
        self.assertEqual('100644 3b18e512dba79e4c8300dd08aeb37f8e728b8dad 0\thello.txt\n',ret)

    def test_basec4(self):
        make_file("hello.txt","hello world\n")
        cmd_stdout("git add hello.txt")
        ret = cmd_stdout("git write-tree")
        self.assertEqual('68aba62e560c0ebc3396e8ae9335232cd93a3f60\n',ret)

    def test_basec5(self):
        make_file("hello.txt","hello world\n")
        ret = hexdigest("hello.txt","blob")
        self.assertEqual('3b18e512dba79e4c8300dd08aeb37f8e728b8dad',ret)

    def test_basec6(self):
        make_file("hello.txt","hello world\n")
        cmd_stdout("git add hello.txt")
        cmd_stdout("git write-tree")
        ret = cmd_stdout("git cat-file -p 3b18e5")
        self.assertEqual("hello world\n",ret)

        ret2 = cmd_stdout("git cat-file -p 68aba6")
        self.assertEqual('100644 blob 3b18e512dba79e4c8300dd08aeb37f8e728b8dad\thello.txt\n',
                         ret2)
        ret3 = cmd_stdout("git ls-files -s")
        self.assertEqual('100644 3b18e512dba79e4c8300dd08aeb37f8e728b8dad 0\thello.txt\n',
                         ret3)


    def test_diff1(self):
        make_file("hello1.txt","""\
hello, world
"""
                  )
        cmd_stdout('git add *')
        cmd_stdout('git commit -m A')                  

        make_file("hello1.txt","""\
hello, world
hello, japan
"""
                  )
        make_file("hello2.txt","""\
hello, world
"""
                  )
        cmd_stdout('git add *')
        cmd_stdout('git commit -m B')

        self.assertEqual("""\
hello1.txt
hello2.txt
"""
                         ,cmd_stdout('git diff --name-only HEAD~1 HEAD'))


    def test_rebase1(self):

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
        

    def test_sparse1(self):

        os.chdir(DIR_ORG)
        if os.path.exists("testgitdir.git"): shutil.rmtree("testgitdir.git")
        if os.path.exists("testgitdir2"): shutil.rmtree("testgitdir2")
        if os.path.exists("testgitdir3"): shutil.rmtree("testgitdir3")
            
        cmd_stdout("git clone --bare testgitdir testgitdir.git")
        cmd_stdout("git clone testgitdir.git testgitdir2")

        os.chdir("testgitdir2")
        make_file("xxx/hello1.txt","hello world")
        make_file("xxx/hello2.txt","hello world")        
        make_file("goodbye1.txt","goodbye world")
        make_file("goodbye2.txt","goodbye world")
        cmd_stdout("git add *")
        cmd_stdout('git commit -m "add all"')
        cmd_stdout("git push origin")

        os.mkdir("../testgitdir3")
        os.chdir("../testgitdir3")
        cmd_stdout("git init")
        cmd_stdout("git config core.sparsecheckout true")
        cmd_stdout("git remote add origin ../testgitdir.git")
        make_file(".git/info/sparse-checkout","xxx\n")
        cmd_stdout("git pull origin master")

        self.assertEqual("xxx\n",cmd_stdout("ls"))
        self.assertEqual("""\
goodbye1.txt
goodbye2.txt
xxx/hello1.txt
xxx/hello2.txt
"""
                         ,cmd_stdout("git ls-files"))


if __name__ == "__main__":
    unittest.main()


    
