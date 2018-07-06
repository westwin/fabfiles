#!/usr/bin/env python
# encoding: utf-8
'''
fabfile -- automation deployment tools.

@author:     FengXi

USAGE:
    fab -H xf5,xf6,xf8 --user=root --password='your_password' --parallel --pool-size=8 setup_env

'''
import os
from StringIO import StringIO
import tempfile

from fabric.api import sudo, local, run, get, put, env, cd, settings
from fabric.contrib.files import append, exists
#import logging

#logging.basicConfig()

def setup_env(update=False,jdk=False):
    """
    setup centos environments
    """
    #with settings(warn_only=True):
    ssh_no_pwd()
    create_ssh_key()
    #install_gfw_hosts()
    install_epel_repo()
    if update:
        update_os()
    #install_centos_release_scl_repo()
    install_basic_tools()
    install_python_lib()
    install_dotfiles()
    motd()
    #install_dockerize()
    if jdk:
        install_jdk()
    create_me

def install_jdk():
    """ install jdk """
    sudo("yum install -y java-1.8.0-openjdk")

def create_me():
    """
    create me
    """
    me = "xifeng"
    password = "xifeng"

    with settings(warn_only=True):
        run("groupadd %s" % me)

        user_add = """useradd -m -d /home/%s -g %s -G wheel -s "/bin/bash" %s  """ % (me, me, me)
        run(user_add)

        #set password
        set_pwd = """echo -e '%s' | sudo passwd '%s' --stdin""" % (password, me)
        run(set_pwd)

def ssh_no_pwd(local_key_file='~/.ssh/id_rsa.pub', remote_key_dir='~root'):
    """
    push ssh public key to remote server(s).
    """
    remote_authorized_keys = "%s/.ssh/authorized_keys" % remote_key_dir

    with settings(warn_only=True):
        run("mkdir -p %s/.ssh" % remote_key_dir)
    if exists(remote_authorized_keys) is None:
        run("touch %s " % remote_authorized_keys)


    def _read_local_key_file(local_key_file):
        local_key_file = os.path.expanduser(local_key_file)
        with open(local_key_file) as f:
            return f.read()

    key = _read_local_key_file(local_key_file)

    with settings(warn_only=True):
        # check if the public exists on remote server.
        #ret = run("grep -q '%s' '%s'" %  (key, remote_authorized_keys))
        #if ret.return_code == 0:
        #    print "existed"
        #    pass
        #else:
        append(remote_authorized_keys, key)
        run("chmod 600 %s" % remote_authorized_keys)

def create_ssh_key():
    """
    create local ssh keys
    """
    local_key_dir = '/root/.ssh/id_rsa'
    run("echo -e 'y\n' | ssh-keygen -t rsa -N '' -f %s" % local_key_dir)

def download_ssh_keys():
    """
    ssh wo passwod between remote servers.
    """
    # read remote keys to local
    local_temp_file = "/tmp/.id_rsa.pub.%s" % env.host
    with settings(warn_only=True):
        local("rm -rf %s" % local_temp_file)
        get(local_path=local_temp_file, remote_path="/root/.ssh/id_rsa.pub")

def copy_ssh_keys():
    """
    copy all ssh keys to remote
    """
    for host in env.hosts:
        if host != env.host:
            with settings(warn_only=True):
                local_temp_file = "/tmp/.id_rsa.pub.%s" % host
                ssh_no_pwd(local_key_file=local_temp_file, remote_key_dir='/root')

def update_os():
    """
    yum update -y os
    """
    sudo("yum upgrade -y")
    sudo("yum update -y")

def install_basic_tools():
    """
    install some basic tools
    """
    sudo("yum install -y yum-utils vim git rsync unzip wget telnet bind-utils bash-completion fabric ")

def install_python_lib():
    """
    install python tools and libs.
    """
    with settings(warn_only=True):
        sudo("yum install -y python-ldap python-pip")
        sudo("pip install --upgrade pip")
        sudo("pip install requests")

def install_epel_repo():
    """
    install yum epel release repo
    """
    sudo("yum install -y epel-release")

def install_centos_release_scl_repo():
    """
    install yum centos release scl repo
    """
    sudo("yum install -y centos-release-scl")

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


def motd():
    """
    motd text
    """
    run("echo %s >/etc/motd" % "I LOVE YOU, AGNES !")

def install_dockerize(version="v0.3.0"):
    """
    install dockerize
    """
    cmd = """curl --insecure --retry 5 -L https://github.com/jwilder/dockerize/releases/download/%s/dockerize-linux-amd64-%s.tar.gz | tar -C /usr/local/bin -xz""" % (version,version)
    sudo(cmd)

def stop_firewall():
    """
    shutdown firewall
    """
    with settings(warn_only=True):
        sudo("systemctl stop firewalld")
        sudo("systemctl disable firewalld")
