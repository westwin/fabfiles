#!/usr/bin/env python
# encoding: utf-8
'''
fabfile -- automation deployment tools.

@author:     FengXi

USAGE:
    fab -H xf5,xf6,xf8 --user=root --password='your_password' --parallel --pool-size=8 setup_env

'''
import os

from fabric.api import sudo, local, run, put, env, cd, settings
from fabric.contrib.files import append, exists

def setup_env():
    """
    setup centos environments
    """
    #with settings(warn_only=True):
    push_public_key()
    update_os()
    install_basic_tools()
    install_dotfiles()
    install_gfw_hosts()

def push_public_key(local_key_file='~/.ssh/id_rsa.pub', remote_key_dir='~root'):
    """
    push ssh public key to remote server(s).
    """
    remote_authorized_keys = "%s/.ssh/authorized_keys" % remote_key_dir

    with settings(warn_only=True):
        run("mkdir -p %s 2>/dev/null" % remote_key_dir)
    if exists(remote_authorized_keys) is None:
        run("touch %s " % remote_authorized_keys)


    def _read_local_key_file(local_key_file):
        local_key_file = os.path.expanduser(local_key_file)
        with open(local_key_file) as f:
            return f.read()

    key = _read_local_key_file(local_key_file)

    with settings(warn_only=True):
        # check if the public exists on remote server.
        ret = run("grep -q '%s' '%s'" %  (key, remote_authorized_keys))
        if ret.return_code == 0:
            pass
        else:
            append(remote_authorized_keys, key)
            run("chmod 600 %s" % remote_authorized_keys)

def update_os():
    """
    yum update -y os
    """
    sudo("yum update -y")

def install_basic_tools():
    """
    install some basic tools
    """
    sudo("yum install -y vim git rsync unzip wget net-tools telnet")

def install_dotfiles():
    """
    install my dotfiles from github
    """
    tmp_dir = "/tmp/"

    with settings(warn_only=True):
        with cd(tmp_dir):
            run("git clone https://github.com/westwin/dotfiles.git dotfiles")
            run("bash %s/dotfiles/install.sh" % tmp_dir)

        run("rm -rf %s/dotfiles" % tmp_dir)

def install_gfw_hosts():
    """
    install GFW hosts file
    """
    put(local_path="./hosts", remote_path="/etc/hosts", mirror_local_mode=True)
