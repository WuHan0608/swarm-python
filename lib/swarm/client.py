# -*- coding: utf8 -*-

import json
from docker import Client, errors
from swarm.api import SwarmApi


class SwarmClient(object):

    def __init__(self):
        self._config = SwarmApi().config
        self.count = 0

    def _get_base_url(self):
        try:
            with open(self._config, 'r') as fp:
                data = json.load(fp)
            try:
                if data['current']:
                    return data['apis'][data['current']]
                return
            except KeyError:
                return
        except IOError:
            print('No available swarm api')
            exit(1)
        except OSError:
            raise

    def _get_version(self):
        try:
            with open(self._config, 'r') as fp:
                data = json.load(fp)
            try:
                if data['version']:
                    return data['version']
                return
            except KeyError:
                return
        except IOError as e:
            print(e)
            return
        except OSError:
            raise

    @property
    def client(self):
        base_url = self._get_base_url()
        if base_url is not None:
            try:
                cli = Client(base_url, version=self.version, timeout=3)
                # Hits the /_ping endpoint of the remote API and returns the result. 
                # An exception will be raised if the endpoint isn't responding.
                if cli.ping() == 'OK':
                    cli.close()
                    return Client(base_url, version=self.version, timeout=600)
                return
            except errors.DockerException as e:
                print(e)
                return
        print('No available swarm api')
        return
    
    @property
    def version(self):
        return self._get_version()
    