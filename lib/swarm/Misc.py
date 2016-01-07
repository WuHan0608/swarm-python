# -*- coding: utf8 -*-

from docker import Client
from utils import byteformat

class Version(object):
    """
    Similar to `docker version`
    """
    def __init__(self, base_url, version=None):
        self.cli = Client(base_url, version=version)

    def __call__(self):
        ret = self.cli.version()
        string = '''\
Server
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
        # close session
        self.cli.close()

class Info(object):
    """
    Similar to `docker info`
    """
    def __init__(self, base_url, version=None):
        self.cli = Client(base_url, version=version)

    def __call__(self):
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
        # close session
        self.cli.close()