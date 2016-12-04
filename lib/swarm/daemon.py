# -*- coding: utf8 -*-

from __future__ import print_function
from docker import errors
from swarm.client import SwarmClient
from swarm.utils import byteformat


class Version(object):

    def __init__(self):
        self.swarm = SwarmClient()

    def __call__(self):
        cli = self.swarm.client
        if cli is not None:
            string = ''     
            ret = cli.version()
            cli.close()
            if self.swarm.version is not None:
                apiversion = ret['ApiVersion'] if self.swarm.version == 'auto'\
                                               else self.swarm.version
                string += '''\
Client:
API version:  {ApiVersion}\n
'''.format(ApiVersion=apiversion)
            string += '''\
Server:
Version:      {Version}
API version:  {ApiVersion}
Go version:   {GoVersion}
Git commit:   {GitCommit}
Built:        {KernelVersion}
OS/Arch:      {Os}/{Arch}\
'''.format(
Version=ret['Version'],
ApiVersion=ret['ApiVersion'],
GoVersion=ret['GoVersion'],
GitCommit=ret['GitCommit'],
KernelVersion=ret['KernelVersion'],
Os=ret['Os'],
Arch=ret['Arch'])
            print(string)


class Info(object):

    def __init__(self):
        self.swarm = SwarmClient()

    def __call__(self):
        cli = self.swarm.client
        if cli is not None:
            ret = cli.info()
            cli.close()
            # DriverStatus is deprecated since api v1.23
            # Use SystemStatus instead
            if ret['DriverStatus'] is None:
                systemstatus = ret['SystemStatus']
            else:
                systemstatus = ret['DriverStatus']
            string = '''\
Containers: {Containers}
Images: {Images}
{SystemStatus}
CPUs: {NCPU}
Total Memory: {MemTotal}
Name: {Name}\
'''.format(
Containers=ret['Containers'],
Images=ret['Images'],
SystemStatus='\n'.join([': '.join((item[0].encode('utf8'), item[1].encode('utf8')))\
                                                          for item in SystemStatus]),
NCPU=ret['NCPU'],
MemTotal=byteformat(ret['MemTotal']),
Name=ret['Name'])
            print(string)


class Login(object):

    def __init__(self):
        self.swarm = SwarmClient()

    def __call__(self, *args, **kwargs):
        """
        :param username(str): The registry username
        :param password(str): The plaintext password
        :param email(str): The email for the registry account
        :param registry(str): URL to the registry
        :param reauth(bool): Whether refresh existing authentication on the docker server
        :param dockercfg_path(str): Use a custom path for the .dockercfg file (default $HOME/.dockercfg)
        """
        cli = self.swarm.client
        if cli is not None:
            try:
                return cli.login(*args, **kwargs)
            except (errors.APIError, errors.DockerException) as e:
                print(e.explanation)
            finally:
                cli.close()
