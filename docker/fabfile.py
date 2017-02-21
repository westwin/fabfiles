#!/usr/bin/env python
# encoding: utf-8
'''
fabfile -- automation deployment docker tools.

@author:     FengXi

USAGE:
    fab -H xf5,xf6,xf8 --user=root --password='your_password' --parallel --pool-size=8 install
'''
import os

from fabric.api import sudo, local, run, put, env, cd, settings
from fabric.contrib.files import append, exists

def install_yum_repo():
    """install docker-engine yum repo"""
    run("yum-config-manager --add-repo https://docs.docker.com/engine/installation/linux/repo_files/centos/docker.repo")

def install():
    """
    install docker engine rather than docker which is maintained by ubuntu
    see the difference https://www.quora.com/What-is-the-difference-between-docker-engine-and-docker-io-packages
    """
    install_yum_repo()

    run("yum install -y docker-engine")
    run("yum update -y ")

    config_registry_mirror(restart=False)
    config_storage(restart=False)

    #start docker
    run("systemctl enable docker")
    run("systemctl start docker")

def install_compose():
    #cmd = """curl -L "https://github.com/docker/compose/releases/download/1.8.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose"""

    cmd = """curl -L "https://github.com/docker/compose/releases/download/1.11.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose"""
    run(cmd)
    run("chmod +x /usr/local/bin/docker-compose")

    #docker compose completion
    cmd = """curl -L https://raw.githubusercontent.com/docker/compose/$(docker-compose version --short)/contrib/completion/bash/docker-compose -o /etc/bash_completion.d/docker-compose"""
    run(cmd)

def uninstall():
    """
    try to uninstall docker
    """
    with settings(warn_only=True):
        installed = run("rpm -q docker")
        if installed.succeeded:
            sudo("systemctl stop docker")
            sudo("yum -y remove docker")
            sudo("yum -y remove docker-selinux")
            sudo("rm -rf /var/lib/docker")

def config_registry_mirror(restart=True):
    #docker mirror
    #mirror = "http://146f0d71.m.daocloud.io"
    #cmd = """sed -i "s|OPTIONS='|OPTIONS='--registry-mirror=http://146f0d71.m.daocloud.io |g" /etc/sysconfig/docker"""
    cmd = """curl -sSL https://get.daocloud.io/daotools/set_mirror.sh | sh -s http://146f0d71.m.daocloud.io """
    sudo(cmd)
    _restart(restart)

def _restart(restart=True):
    #restart docker
    if restart:
        with settings(warn_only=True):
            sudo("systemctl enable docker")
            sudo("systemctl restart docker")

def config_storage(restart=True):
    """
    TODO: config docker storage
    """
    pass

