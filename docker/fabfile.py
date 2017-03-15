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
    sudo("yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo")

def install():
    """
    install docker engine rather than docker which is maintained by ubuntu
    see the difference https://www.quora.com/What-is-the-difference-between-docker-engine-and-docker-io-packages
    """
    install_yum_repo()

    sudo("yum install -y docker-ce")
    #sudo("yum update -y ")

    #config_registry_mirror(restart=False)

    use_bj_registry()

    #start docker
    _restart()

def install_compose():
    #cmd = """curl -L "https://github.com/docker/compose/releases/download/1.8.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose"""

    cmd = """curl -L "https://github.com/docker/compose/releases/download/1.11.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose"""
    sudo(cmd)
    sudo("chmod +x /usr/local/bin/docker-compose")

    #docker compose completion
    cmd = """curl -L https://raw.githubusercontent.com/docker/compose/$(docker-compose version --short)/contrib/completion/bash/docker-compose -o /etc/bash_completion.d/docker-compose"""
    sudo(cmd)

def config_registry_mirror(restart=True):
    #docker mirror
    #mirror = "http://146f0d71.m.daocloud.io"
    #cmd = """sed -i "s|OPTIONS='|OPTIONS='--registry-mirror=http://146f0d71.m.daocloud.io |g" /etc/sysconfig/docker"""
    cmd = """curl -sSL https://get.daocloud.io/daotools/set_mirror.sh | sh -s http://146f0d71.m.daocloud.io """
    sudo(cmd)
    _restart(restart)

def use_bj_registry():
    """install beijing internal docker registry """
    dns_resolve()
    install_bj_cert()
    config_bj_registry()

def install_bj_cert(registry="registry.nscloud.local:5005", cert_name="esdp_bj_registry.crt"):
    """
    install registry ssl certificate. the registry do not starts with scheme
    """
    scheme,fqdn = _parse_scheme(registry)
    sudo("openssl s_client -connect %s <<<'' | openssl x509 -out /etc/pki/ca-trust/source/anchors/%s" % (fqdn, cert_name))
    sudo("update-ca-trust enable")
    sudo("systemctl restart docker")

def config_bj_registry(pull_registry="https://registry.nscloud.local:5005",push_registry="https://registry.nscloud.local:5006", user="admin", password="admin123"):
    """
    config registry pull and push registry. suppose pull/push registry use same cert and same auth info.
    """
    basic_auth = ""
    if user and password:
        basic_auth = "%s:%s@" % (user, password)

    scheme,fqdn = _parse_scheme(pull_registry)

    registry_with_auth = "%s//%s%s" % (scheme, basic_auth, fqdn)
    cmd = """curl -sSL https://get.daocloud.io/daotools/set_mirror.sh | sh -s %s""" % registry_with_auth
    sudo(cmd)

    #perform a docker login for push
    cmd = """docker login %s -u %s -p %s""" % (push_registry, user, password)
    sudo(cmd)

    _restart()

def dns_resolve(fqdn="registry.nscloud.local", ip="172.16.10.231"):
    """
    config registry fqdn and ip mapping in case of dns can not resolve
    NOTE: the dns server 192.168.30.202 in bj can resolve this fqdn
    """
    with settings(warn_only=True):
        ping = """ping -c 3 %s""" %  fqdn
        ret = run(ping)
        if ret.return_code ==0:
            print "yes. dns can resolve."
        else:
            print "no. dns can no resolve."
            sudo("echo %s   %s >> /etc/hosts" % (ip,fqdn))

def _parse_scheme(url):
    """
    parse an url to return scheme and remaining part.
    """
    splits = url.split("""//""")
    if len(splits) == 2:
        return splits[0], splits[1]
    else:
        return "https:", splits[0]
def _restart(restart=True):
    #restart docker
    if restart:
        with settings(warn_only=True):
            sudo("systemctl daemon-reload")
            sudo("systemctl enable docker")
            sudo("systemctl restart docker")
