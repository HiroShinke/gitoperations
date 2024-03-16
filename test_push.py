

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


    def test_push1(self):

        os.chdir(DIR_ORG)
        if os.path.exists("testgitdir.git"): shutil.rmtree("testgitdir.git")
        if os.path.exists("testgitdir2"): shutil.rmtree("testgitdir2")
        if os.path.exists("testgitdir3"): shutil.rmtree("testgitdir3")
            
        cmd_stdout("git clone --bare testgitdir testgitdir.git")
        cmd_stdout("git clone testgitdir.git testgitdir2")
        cmd_stdout("git clone testgitdir.git testgitdir3")

        os.chdir("testgitdir2")
        make_file("hello1.txt","hello world")
        cmd_stdout("git add hello1.txt")
        cmd_stdout('git commit -m "add hello1.txt" hello1.txt')
        cmd_stdout("git push origin")

        os.chdir("../testgitdir3")
        cmd_stdout("git pull origin master")
        ret = cmd_stdout("ls")
        self.assertEqual("""\
hello1.txt
"""
                         ,ret)
        
    def test_push2(self):

        os.chdir(DIR_ORG)
        if os.path.exists("testgitdir.git"): shutil.rmtree("testgitdir.git")
        if os.path.exists("testgitdir2"): shutil.rmtree("testgitdir2")
        if os.path.exists("testgitdir3"): shutil.rmtree("testgitdir3")
            
        cmd_stdout("git clone --bare testgitdir testgitdir.git")
        cmd_stdout("git clone testgitdir.git testgitdir2")
        cmd_stdout("git clone testgitdir.git testgitdir3")

        os.chdir("testgitdir2")
        make_file("hello1.txt","hello world\n")
        cmd_stdout("git add hello1.txt")
        cmd_stdout('git commit -m "add hello1.txt" hello1.txt')
        make_file("hello1.txt","hello world\nhello world, again\n")
        cmd_stdout("git push origin")

        cmd_stdout("git checkout -b new-topic")
        cmd_stdout("git add hello1.txt")
        cmd_stdout('git commit -m "add hello1.txt" hello1.txt')        
        cmd_stdout("git push origin new-topic")

        os.chdir("../testgitdir3")
        cmd_stdout("git fetch origin")
        cmd_stdout("git checkout --track -b new-topic origin/new-topic")
        ret = cmd_stdout("git diff HEAD~1 HEAD")
        self.assertEqual("""\
diff --git a/hello1.txt b/hello1.txt
index 3b18e51..b652454 100644
--- a/hello1.txt
+++ b/hello1.txt
@@ -1 +1,2 @@
 hello world
+hello world, again
"""
              ,ret)

        cmd_stdout("git checkout master")
        cmd_stdout("git merge new-topic")
        cmd_stdout("git push origin master")

        os.chdir("../testgitdir2")
        cmd_stdout("git pull origin master")
        ret = cmd_stdout("git diff HEAD~1 HEAD")
        self.assertEqual("""\
diff --git a/hello1.txt b/hello1.txt
index 3b18e51..b652454 100644
--- a/hello1.txt
+++ b/hello1.txt
@@ -1 +1,2 @@
 hello world
+hello world, again
"""
                         ,ret)

        os.chdir("../testgitdir3")
        ret = cmd_stdout("git branch -a")
        self.assertEqual("""\
* master
  new-topic
  remotes/origin/master
  remotes/origin/new-topic
"""
              ,ret)
        cmd_stdout("git branch -d new-topic")
        cmd_stdout("git push origin --delete new-topic")
        ret = cmd_stdout("git branch -a")
        self.assertEqual("""\
* master
  remotes/origin/master
"""
              ,ret)


        os.chdir("../testgitdir2")
        cmd_stdout("git checkout master")        
        cmd_stdout("git pull origin master")
        cmd_stdout("git fetch --prune origin")
        cmd_stdout("git branch -d new-topic")
        ret = cmd_stdout("git branch -a")        
        self.assertEqual("""\
* master
  remotes/origin/master
"""
              ,ret)


if __name__ == "__main__":
    unittest.main()


    
