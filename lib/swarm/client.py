# -*- coding: utf8 -*-

from __future__ import print_function
import json
from docker import Client, errors
from docker.tls import TLSConfig
from swarm.api import SwarmApi
from swarm.utils import pyprint


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
            pyprint(e)
            return
        except OSError:
            raise

    def _get_tlsconfig(self):
        try:
            with open(self._config, 'r') as fp:
                data = json.load(fp)
            current = data['current']
            tlsconfig = data.get('tlsconfig', {}).get(current, {})
            return tlsconfig if tlsconfig else None
        except IOError as e:
            pyprint(e)
            return
        except OSError:
            raise

    @property
    def client(self):
        base_url = self._get_base_url()
        if base_url is not None:
            try:
                tls = False
                _tlsconfig = self._get_tlsconfig()
                if _tlsconfig is not None:
                    client_cert = (_tlsconfig.get('tlscert'), _tlsconfig.get('tlskey'))
                    ca_cert = _tlsconfig.get('tlscacert')
                    verify = True if  _tlsconfig.get('tlsverify') == '1' else False
                    tls = TLSConfig(client_cert=client_cert, ca_cert=ca_cert, verify=verify)
                cli = Client(base_url, version=self.version, timeout=3, tls=tls)
                # Hits the /_ping endpoint of the remote API and returns the result. 
                # An exception will be raised if the endpoint isn't responding.
                if cli.ping() == 'OK':
                    cli.close()
                    return Client(base_url, version=self.version, timeout=600, tls=tls)
                return
            except errors.DockerException as e:
                pyprint(e)
                return
        print('No available swarm api')
        return
    
    @property
    def version(self):
        return self._get_version()
