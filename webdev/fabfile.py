#!/usr/bin/env python
# encoding: utf-8
'''
fabfile -- automation setup webui dev env on node

@author:     FengXi

USAGE:
    fab -H xf5,xf6,xf8 --user=root --password='your_password' --parallel --pool-size=8 install

'''

from fabric.api import sudo, local, run, get, put, env, cd, settings
from fabric.contrib.files import append, exists

def install():
    """
    setup centos environments
    """
    with settings(warn_only=True):
        run("yum install -y nodejs")

        # use taobao npm reg
        use_taobao_npm_reg()

        install_ncu()

def use_taobao_npm_reg():
    sudo("npm config -g set registry https://registry.npm.taobao.org")

def install_ncu():
    run("npm install -g npm-check-updates")
