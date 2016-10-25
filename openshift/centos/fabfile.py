#!/usr/bin/env python
# encoding: utf-8
'''
fabfile -- automation deployment tools.

@author:     FengXi

USAGE:
    fab -H xf5,xf6,xf8 --user=root --password='your_password' --parallel --pool-size=8 install_openshift

'''
import os

from fabric.api import sudo, local, run, put, env, cd, settings
from fabric.contrib.files import append, exists

def install_openshift():
    """
    install openshift 
    """
    install_base_pkg()
    install_ansible()

    clone_openshift_ansible_repo()
    install_docker()


def install_base_pkg():
    """
    install base packages
    """
    sudo("yum install -y wget git net-tools bind-utils iptables-services bridge-utils bash-completion")
    sudo("yum update -y ")

def install_ansible():
    """
    install ansible ant its deps
    """
    sudo("yum install -y ansible pyOpenSSL")

def clone_openshift_ansible_repo():
    """
    clone openshift-ansible repository
    """

    local_repo_basedir = '/tmp/'
    local_repo_name = 'openshift-ansible'
    local_repo_dir = "%s/%s" % (local_repo_basedir, local_repo_name)

    if exists(local_repo_basedir) is None:
        run("mkdir -p %s" % local_repo_basedir)

    if exists(local_repo_dir) :
        run("rm -rf %s" % local_repo_dir)

    with cd(local_repo_basedir):
        run("git clone https://github.com/openshift/openshift-ansible %s" % local_repo_name)

def install_docker():
    """
    install docker 
    """
    def _config():
        """
        docker config
        """
        cmd = """sed -i '/OPTIONS=.*/c\OPTIONS="--selinux-enabled --insecure-registry 172.30.0.0/16"' \
/etc/sysconfig/docker"""
        run(cmd)

    run("yum install -y docker")
    _config()
