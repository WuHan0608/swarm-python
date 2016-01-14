# -*- coding: utf8 -*-

from docker import errors
from client import SwarmClient
from utils import byteformat

class Version(object):
    """
    Similar to `docker version`
    """
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
'''.format(\
Version=ret['Version'],\
ApiVersion=ret['ApiVersion'],\
GoVersion=ret['GoVersion'],\
GitCommit=ret['GitCommit'],\
KernelVersion=ret['KernelVersion'],\
Os=ret['Os'],\
Arch=ret['Arch'])
            print(string)


class Info(object):
    """
    Similar to `docker info`
    """
    def __init__(self):
        self.swarm = SwarmClient()

    def __call__(self):
        cli = self.swarm.client
        if cli is not None:
            ret = cli.info()
            cli.close()
            string = '''\
Containers: {Containers}
Images: {Images}
{DriverStatus}
CPUs: {NCPU}
Total Memory: {MemTotal}
Name: {Name}\
'''.format(\
Containers=ret['Containers'],\
Images=ret['Images'],\
DriverStatus='\n'.join([ ': '.join((item[0].encode('utf8'), item[1].encode('utf8')))\
                                                for item in ret['DriverStatus']]),\
NCPU=ret['NCPU'],\
MemTotal=byteformat(ret['MemTotal']),\
Name=ret['Name'])
            print(string)

class Login(object):
    """
    Similar to `docker login`
    """
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
                ret = cli.login(*args, **kwargs)
            except errors.APIError as e:
                print(e.explanation)
            except errors.DockerException as e:
                print(e.explanation)
            else:
                print(ret['Status'])
            finally:
                cli.close()
