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
    config_container_logs()


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

def config_firewall_on_master():
    """
    config firewall on master node.
    """
    sudo("systemctl start firewalld")
    sudo("systemctl enable firewalld")

    sudo("firewall-cmd --zone=public --add-port=53/tcp --permanent")
    sudo("firewall-cmd --zone=public --add-port=8053/tcp --permanent")
    sudo("firewall-cmd --zone=public --add-port=8443/tcp --permanent")
    sudo("firewall-cmd --zone=public --add-port=443/tcp --permanent")
    sudo("firewall-cmd --zone=public --add-port=10250/tcp --permanent")
    sudo("firewall-cmd --zone=public --add-port=4789/udp --permanent")
    sudo("firewall-cmd --zone=public --add-port=8053/udp --permanent")
    sudo("firewall-cmd --zone=public --add-port=53/udp --permanent")
    sudo("firewall-cmd --reload")

    run ("echo listing current firewall rules...")
    run("firewall-cmd --list-all")

def shutdown_firewall():
    """
    shutdown firewall for easier debug.
    """
    with settings(warn_only=True):
        sudo("systemctl stop firewalld")
        sudo("systemctl disable firewalld")

def pull_images():
    """
    pull openshift related images manually.
    """
    run("docker pull openshift/origin-deployer:v1.3.1")
    run("docker pull openshift/origin-docker-registry:v1.3.1")
    run("docker pull openshift/origin-metrics-deployer:latest")
