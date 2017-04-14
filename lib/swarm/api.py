# -*- coding: utf8 -*-

from __future__ import print_function
import os
import json


class SwarmApi(object):

    def __init__(self):
        # config: $HOME/.swarm/config.json
        self._config = os.path.join(os.environ['HOME'], '.swarm', 'config.json')
        if not os.path.exists(os.path.dirname(self._config)):
            os.mkdir(os.path.dirname(self._config))

    def _has_config(self, warning=True):
        if not os.path.exists(self._config):
            if warning:
                print('No available swarm api')
            return False
        return True

    @property
    def config(self):
        return self._config
    
    def list_api(self):
        if self._has_config():
            try:
                with open(self._config, 'r') as fp:
                    data = json.load(fp)
                    if data['apis']:
                        for name in data['apis']:
                            tag = ' \033[32m*\033[0m' if name == data.get('current', '') else ''
                            print('{name}: {api}{tag}'.format(name=name, api=data['apis'][name], tag=tag))
            except IOError as e:
                print(e)
            except OSError:
                raise

    def add_api(self, name, api):
        if self._has_config(warning=False):
            try:
                with open(self._config, 'r') as fp:
                    data = json.load(fp)
                    data['apis'][name] = api
                with open(self.config, 'w') as fp:
                    fp.write(json.dumps(data, indent=4))
            except OSError as e:
                print(e)
        else:
            data = {'apis': {}}
            data['apis'][name] = api
            with open(self._config, 'w') as fp:
                fp.write(json.dumps(data, indent=4))

    def unset_api(self, name):
        if self._has_config():
            try:
                with open(self._config, 'r') as fp:
                    data = json.load(fp)
                    if name in data['apis']:
                        data['apis'].pop(name)
                        if name == data.get('current', ''):
                            data['current'] = ''
                    elif name == 'all':
                        data = {
                            'current': '',
                            'apis': {}
                        }
                    else:
                        args = ', '.join(data['apis'].keys() + ['all'])
                        print('Error: `{name}` is unset. Available arguments: {args}'.format(name=name, args=args))
                        return
                with open(self._config, 'w') as fp:
                    fp.write(json.dumps(data, indent=4))
            except IOError as e:
                print(e)
            except OSError:
                raise

    def set_api(self, name):
        if self._has_config():
            try:
                with open(self._config, 'r') as fp:
                    data = json.load(fp)
                if name in data['apis']:
                    data['current'] = name
                else:
                    if data['apis'].keys():
                        args = ','.join(data['apis'].keys())
                        print('Error: `{name}` is not available. Available arguments: {args}'.format(name=name, args=args))
                    else:
                        print('No available swarm api')
                    return
                with open(self._config, 'w') as fp:
                    fp.write(json.dumps(data, indent=4))
            except IOError as e:
                print(e)
            except OSError:
                raise

    def set_version(self, version):
        if self._has_config():
            try:
                if version == 'auto' or float(version) >= 1.10:
                    with open(self._config, 'r') as fp:
                        data = json.load(fp)
                    data['version'] = version
                    with open(self._config, 'w') as fp:
                        fp.write(json.dumps(data, indent=4))
                else:
                    print('Error: {version} is not numeric or less than 1.10'.format(version=version))
            except ValueError:
                print('Error: {version} is not numeric or less than 1.10'.format(version=version))
            except IOError as e:
                print(e)
            except OSError:
                raise

    def set_tls(self, value):
        if self._has_config():
            try:
                if value in ('0', '1'):
                    with open(self._config, 'r') as fp:
                        data = json.load(fp)
                    current = data['current']
                    tlsconfig =  data.get('tlsconfig', {}).get(current, {})
                    if tlsconfig.get('tlscert') and tlsconfig.get('tlskey'):
                        tlsconfig['tls'] = value
                        with open(self._config, 'w') as fp:
                            fp.write(json.dumps(data, indent=4))
                    else:
                        print('Error: no specified tlscert/tlskey') 
                else:
                    print('Error: tls must be set either 0 or 1')
            except IOError as e:
                print(e)
            except OSError:
                raise

    def set_tlsverify(self, value):
        if self._has_config():
            try:
                if value in ('0', '1'):
                    with open(self._config, 'r') as fp:
                        data = json.load(fp)
                    current = data['current']
                    tlsconfig =  data.get('tlsconfig', {}).get(current, {})
                    if tlsconfig.get('tlscert') and tlsconfig.get('tlskey'):
                        tlsconfig['tlsverify'] = value
                        with open(self._config, 'w') as fp:
                            fp.write(json.dumps(data, indent=4))
                    else:
                        print('Error: no specified tlscert/tlskey')
                else:
                    print('Error: tlsverify must be set either 0 or 1')
            except IOError as e:
                print(e)
            except OSError:
                raise

    def set_tlscacert(self, tlscacert):
        if self._has_config():
            try:
                if os.path.exists(tlscacert):
                    with open(self._config, 'r') as fp:
                        data = json.load(fp)
                    current = data['current']
                    tlsconfig = data.setdefault('tlsconfig', {}).setdefault(current, {})
                    tlsconfig['tlscacert'] = tlscacert
                    with open(self._config, 'w') as fp:
                        fp.write(json.dumps(data, indent=4))
                else:
                    print('Specified tlscacert is not found.')
            except IOError as e:
                print(e)
            except OSError:
                raise

    def set_tlscert(self, tlscert):
        if self._has_config():
            try:
                if os.path.exists(tlscert):
                    with open(self._config, 'r') as fp:
                        data = json.load(fp)
                    current = data['current']
                    tlsconfig = data.setdefault('tlsconfig', {}).setdefault(current, {})
                    tlsconfig['tlscert'] = tlscert
                    with open(self._config, 'w') as fp:
                        fp.write(json.dumps(data, indent=4))
                else:
                    print('Specified tlscert is not found.')
            except IOError as e:
                print(e)
            except OSError:
                raise

    def set_tlskey(self, tlskey):
        if self._has_config():
            try:
                if os.path.exists(tlskey):
                    with open(self._config, 'r') as fp:
                        data = json.load(fp)
                    current = data['current']
                    tlsconfig = data.setdefault('tlsconfig', {}).setdefault(current, {})
                    tlsconfig['tlskey'] = tlskey
                    with open(self._config, 'w') as fp:
                        fp.write(json.dumps(data, indent=4))
                else:
                    print('Specified tlskey is not found.')
            except IOError as e:
                print(e)
            except OSError:
                raise

    def get_tlsconfig(self):
        if self._has_config():
            try:
                with open(self._config, 'r') as fp:
                    data = json.load(fp)
                current = data['current']
                tlsconfig = data.get('tlsconfig', {}).get(current, {})
                if tlsconfig:
                    for name in ('tls', 'tlscacert', 'tlscert', 'tlskey', 'tlsverify'):
                        if tlsconfig.get(name):
                            print('{name}: {value}'.format(name=name, value=tlsconfig.get(name)))
            except IOError as e:
                print(e)
            except OSError as e:
                raise
