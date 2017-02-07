#!/usr/bin/env python
# encoding: utf-8
'''
fabfile -- setup a NFS server on CentOS.

@author:     FengXi

USAGE:
    fab -H xf5,xf6,xf8 --user=root --password='your_password' --parallel --pool-size=8 install_nfs

'''
import os
from StringIO import StringIO
import tempfile

from fabric.api import sudo, local, run, get, put, env, cd, settings
from fabric.contrib.files import append, exists

def install_nfs(mount="/home/data"):
    """
    setup nfs server
    """
    sudo("yum install -y nfs-utils")

    sudo("systemctl enable rpcbind")
    sudo("systemctl enable nfs-server")
    sudo("systemctl enable nfs-lock")
    sudo("systemctl enable nfs-idmap")
    sudo("systemctl start rpcbind")
    sudo("systemctl start nfs-server")
    sudo("systemctl start nfs-lock")
    sudo("systemctl start nfs-idmap")

    sudo("firewall-cmd --permanent --zone=public --add-service=nfs")
    sudo("firewall-cmd --reload")

    #easier debug to disable firewalld
    sudo("systemctl stop firewalld")
    sudo("systemctl disable firewalld")

    #allow all ip access
    exports = """%s ""(rw,sync,no_root_squash,no_all_squash)""" % (mount)
    run("""echo  '%s' >> /etc/exports""" % exports)
    sudo("systemctl restart nfs-server")

    #create several clusters
    with settings(warn_only=True):
        clusters = ("dev1", "dev2", "qa1", "qa2", "xf1", )
        for cluster in clusters:
            create_cluster(cluster, mount)

def create_cluster(cluster,mount="/home/data"):
    """create a folder for one cluster"""
    with settings(warn_only=True):
        cluster_dir = "%s/%s" % (mount, cluster)
        sudo("mkdir -p %s" % cluster_dir)
        sudo("chmod -R 777 %s" % cluster_dir)
