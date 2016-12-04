# -*- coding: utf8 -*-

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
    
    def get_api(self, name):
        if self._has_config():
            try:
                with open(self._config, 'r') as fp:
                    data = json.load(fp)
                    if name in data['apis']:
                        print(name + ': ' + data['apis'][name])
                    elif name == 'current':
                        try:
                            current = data['current']
                            print('{name}: {api}'.format(name=current, api=data['apis'][current]))
                        except KeyError:
                            print('No swarm api in use')
                    elif name == 'all':
                        for name in sorted(data['apis']):
                            print('{name}: {api}'.format(name=name,\
                                                          api=data['apis'][name]))
                    else:
                        args = ','.join(data['apis'].keys() + ['current', 'all'])
                        print('Error: `{name}` is unset. Available arguments: {args}'.format(name=name,
                                                                                             args=args))
            except IOError as e:
                print(e)
            except OSError:
                raise

    def update_api(self, name, api):
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

    def remove_api(self, name):
        if self._has_config():
            try:
                with open(self._config, 'r') as fp:
                    data = json.load(fp)
                    if name in data['apis']:
                        data['apis'].pop(name)
                        if 'current' in data and name == data['current']:
                            data['current'] = ''
                    elif name == 'current':
                        try:
                            data['apis'].pop(data['current'])
                        except KeyError:
                            print('No swarm api in use')
                            return
                        data['current'] = ''
                    elif name == 'all':
                        data = {
                            'current': '',
                            'apis': {}
                        }
                    else:
                        args = ','.join(data['apis'].keys() + ['current', 'all'])
                        print('Error: `{name}` is unset. Available arguments: {args}'.format(name=name,
                                                                                             args=args))
                        return
                with open(self._config, 'w') as fp:
                    fp.write(json.dumps(data, indent=4))
            except IOError as e:
                print(e)
            except OSError:
                raise

    def use_api(self, name):
        if self._has_config():
            try:
                with open(self._config, 'r') as fp:
                    data = json.load(fp)
                if name in data['apis']:
                    data['current'] = name
                else:
                    if data['apis'].keys():
                        args = ','.join(data['apis'].keys())
                        print('Error: `{name}` not exist. Available arguments: {args}'.format(name=name,
                                                                                              args=args))
                    else:
                        print('No available swarm api')
                    return
                with open(self._config, 'w') as fp:
                    fp.write(json.dumps(data, indent=4))
            except IOError as e:
                print(e)
            except OSError:
                raise

    def use_version(self, version):
        if self._has_config():
            try:
                if version == 'auto' or float(version) >= 1.10:
                    with open(self._config, 'r') as fp:
                        data = json.load(fp)
                    data['version'] = version
                    with open(self._config, 'w') as fp:
                        fp.write(json.dumps(data, indent=4))
                else:
                    print('Error: {version} is not numeric or greater than 1.10'.format(version=version))
            except ValueError:
                print('Error: {version} is not numeric or greater than 1.10'.format(version=version))
            except IOError as e:
                print(e)
            except OSError:
                raise
