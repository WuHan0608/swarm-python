# -*- coding: utf8 -*-

import json
from docker import Client
from config import ApiConfig

class Docker(object):
    def __init__(self):
        self._config = ApiConfig().config

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
        except IOError as e:
            print('No available swarm api')
            exit(1)
        except OSError as e:
            print(e)
            exit(2)

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
            return
        except OSError:
            return

    @property
    def client(self):
        base_url = self._get_base_url()
        if base_url is not None:
            return Client(base_url, version=self._get_version())
        print('No available swarm api')
        return
        