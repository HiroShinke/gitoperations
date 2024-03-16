

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
        
    def test_remote1(self):
        make_file("hello.txt","hello world")
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m "add hello.txt" hello.txt')
        
        os.chdir(DIR_ORG)
        if os.path.exists("testgitdir2"):
            shutil.rmtree("testgitdir2")
        cmd_stdout("cp -r testgitdir testgitdir2")
        
        os.chdir("testgitdir2")
        cmd_stdout("git remote add first ../testgitdir")
        ret = cmd_stdout("git remote")
        self.assertEqual("first\n",ret)
        cmd_stdout("git remote update first")
        ret = cmd_stdout("git branch -a")
        self.assertEqual('* master\n' + 
                         '  remotes/first/master\n',
                         ret)
        
        os.chdir("../testgitdir")
        make_file("hello1.txt","hello world")
        cmd_stdout("git add hello1.txt")
        ret = cmd_stdout('git commit -m "add hello1.txt" hello1.txt')
        
        os.chdir("../testgitdir2")
        cmd_stdout("git remote update")
        cmd_stdout("git merge first/master")
        ret = cmd_stdout("ls")
        self.assertEqual('hello.txt\nhello1.txt\n',ret)

    def test_remote2(self):
        make_file("hello.txt","hello world")
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m "add hello.txt" hello.txt')
        
        os.chdir(DIR_ORG)
        if os.path.exists("testgitdir2"):
            shutil.rmtree("testgitdir2")
        cmd_stdout("cp -r testgitdir testgitdir2")
        
        os.chdir("testgitdir2")
        cmd_stdout("git remote add first ../testgitdir")
        ret = cmd_stdout("git remote")
        self.assertEqual("first\n",ret)
        cmd_stdout("git remote update first")
        ret = cmd_stdout("git branch -a")
        self.assertEqual('* master\n' + 
                         '  remotes/first/master\n',
                         ret)
        
        os.chdir("../testgitdir")
        make_file("hello1.txt","hello world")
        cmd_stdout("git add hello1.txt")
        ret = cmd_stdout('git commit -m "add hello1.txt" hello1.txt')
        
        os.chdir("../testgitdir2")
        cmd_stdout("git pull first master")
        ret = cmd_stdout("ls")
        self.assertEqual('hello.txt\nhello1.txt\n',ret)


    def test_remote2_2(self):
        make_file("hello.txt","hello world")
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m "add hello.txt" hello.txt')
        
        os.chdir(DIR_ORG)
        if os.path.exists("testgitdir2"):
            shutil.rmtree("testgitdir2")
        cmd_stdout("cp -r testgitdir testgitdir2")
        
        os.chdir("testgitdir2")
        cmd_stdout("git remote add first ../testgitdir")
        ret = cmd_stdout("git remote")
        self.assertEqual("first\n",ret)
        cmd_stdout("git remote update first")
        ret = cmd_stdout("git branch -a")
        self.assertEqual('* master\n' + 
                         '  remotes/first/master\n',
                         ret)
        cmd_stdout("git branch --set-upstream-to=first/master master")
        
        os.chdir("../testgitdir")
        make_file("hello1.txt","hello world")
        cmd_stdout("git add hello1.txt")
        ret = cmd_stdout('git commit -m "add hello1.txt" hello1.txt')
        
        os.chdir("../testgitdir2")
        cmd_stdout("git pull")
        ret = cmd_stdout("ls")
        self.assertEqual('hello.txt\nhello1.txt\n',ret)


    def test_remote3(self):
        make_file("hello.txt","hello world")
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m "add hello.txt" hello.txt')
        
        os.chdir(DIR_ORG)
        if os.path.exists("testgitdir2"):
            shutil.rmtree("testgitdir2")
        cmd_stdout("cp -r testgitdir testgitdir2")
        
        os.chdir("testgitdir2")
        cmd_stdout("git remote add first ../testgitdir")
        ret = cmd_stdout("git remote")
        self.assertEqual("first\n",ret)
        cmd_stdout("git remote update first")
        ret = cmd_stdout("git branch -a")
        self.assertEqual('* master\n' + 
                         '  remotes/first/master\n',
                         ret)
        
        os.chdir("../testgitdir")
        make_file("hello1.txt","hello world")
        cmd_stdout("git add hello1.txt")
        ret = cmd_stdout('git commit -m "add hello1.txt" hello1.txt')
        
        os.chdir("../testgitdir2")
        cmd_stdout("git pull first master")
        ret = cmd_stdout("ls")
        self.assertEqual('hello.txt\nhello1.txt\n',ret)
        
        make_file("hello2.txt","hello world2")
        cmd_stdout("git add hello2.txt")
        ret = cmd_stdout('git commit -m "add hello2.txt" hello2.txt')
        
        os.chdir("../testgitdir")

        cmd_stdout("git remote add second ../testgitdir2")
        ret = cmd_stdout("git remote")
        self.assertEqual("second\n",ret)
        cmd_stdout("git remote update second")
        ret = cmd_stdout("git branch -a")
        self.assertEqual('* master\n' + 
                         '  remotes/second/master\n',
                         ret)

        cmd_stdout("git pull second master")
        ret = cmd_stdout("ls")
        self.assertEqual("""\
hello.txt
hello1.txt
hello2.txt
"""
                         ,ret)


if __name__ == "__main__":
    unittest.main()


    
