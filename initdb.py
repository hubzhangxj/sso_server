#!/bin/bash
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import shutil


def list_dirs(parent):
    """clear migrations"""
    dirs = os.listdir(parent)
    for i in range(0, len(dirs)):
        path = os.path.join(parent, dirs[i])
        if os.path.isfile(path):
            continue
        if os.path.isdir(path) and dirs[i][0] != '.':
            if 'migrations' == dirs[i]:
                shutil.rmtree(path)
                print 'delete ', path
            else:
                list_dirs(path)


print 'clear migrations start =================='
list_dirs(os.getcwd())
print 'clear migrations end ==================\nclear db start =================='

os.system('mysql -uroot -p1qaz2wsx~ -e "DROP DATABASE IF EXISTS uams; create database uams;"')
print 'clear db end =================='
