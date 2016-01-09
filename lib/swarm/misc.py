# -*- coding: utf8 -*-

from base import SwarmClient
from utils import byteformat

class Version(object):
    """
    Similar to `docker version`
    """
    def __init__(self):
        self.swarm = SwarmClient()
        self.cli = self.swarm.client

    def __call__(self):
        if self.cli is not None:
            ret = self.cli.version()
            self.cli.close()
            string = ''
            if self.cli.version is not None:
                string = '''\
Client:
 API version:  {ApiVersion}\n
'''.format(ApiVersion=ret['ApiVersion'] if self.swarm.version == 'auto'\
                                                else self.swarm.version)
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
        self.cli = SwarmClient().client

    def __call__(self):
        if self.cli is not None:
            ret = self.cli.info()
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
