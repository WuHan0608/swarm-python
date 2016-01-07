# -*- coding: utf8 -*-

import os
import json

class ApiConfig(object):
    """
    Get swarm config
    """
    def __init__(self):
        # config: $HOME/.swarm/config.json
        self.config = os.path.join(os.environ['HOME'], '.swarm', 'config.json')
        if not os.path.exists(os.path.dirname(self.config)):
            os.mkdir(os.path.dirname(self.config))

    def _has_config(self, warning=True):
        if not os.path.exists(self.config):
            if warning:
                print('Config not found. Please add config first')
            return False
        return True

    def get_api(self, name):
        if self._has_config():
            try:
                with open(self.config, 'r') as fp:
                    data = json.load(fp)
                    if name in data['apis']:
                        print(name + ': ' + data['apis'][name])
                    elif name == 'current':
                        try:
                            current = data['current']
                            print('{name}: {api}'.format(name=current,\
                                                         api=data['apis'][current]))
                        except KeyError:
                            print('Current Swarm API is unset')
                    elif name == 'all':
                        for name in sorted(data['apis']):
                            print('{name}: {api}'.format(name=name,\
                                                          api=data['apis'][name]))
                    else:
                        args = ','.join(data['apis'].keys() + ['current', 'all'])
                        print('Error: `{name}` not exist. Available arguments: {args}'.format(\
                                                                                    name=name,\
                                                                                    args=args))
            except OSError as e:
                print(e)

    def update_api(self, name, api):
        if self._has_config(warning=False):
            try:
                with open(self.config, 'r') as fp:
                    data = json.load(fp)
                    data['apis'][name] = api
                with open(self.config, 'w') as fp:
                    fp.write(json.dumps(data, indent=4))
            except OSError as e:
                print(e)
        else:
            data = {'apis': {}}
            data['apis'][name] = api
            with open(self.config, 'w') as fp:
                fp.write(json.dumps(data, indent=4))

    def remove_api(self, name):
        if self._has_config():
            try:
                with open(self.config, 'r') as fp:
                    data = json.load(fp)
                    if name in data['apis']:
                        data['apis'].pop(name)
                        if 'current' in data and name == data['current']:
                            data['current'] = ''
                    elif name == 'current':
                        try:
                            data['apis'].pop(data['current'])
                        except KeyError:
                            print('Current Swarm API is unset')
                            return
                        data['current'] = ''
                    elif name == 'all':
                        data = {
                            'current': '',
                            'apis': {}
                        }
                    else:
                        args = ','.join(data['apis'].keys() + ['current', 'all'])
                        print('Error: `{name}` not exist. Available arguments: {args}'.format(\
                                                                                    name=name,\
                                                                                    args=args))
                        return
                with open(self.config, 'w') as fp:
                    fp.write(json.dumps(data, indent=4))
            except OSError as e:
                print(e)

    def use_api(self, name):
        if self._has_config():
            try:
                with open(self.config, 'r') as fp:
                    data = json.load(fp)
                    if name in data['apis']:
                        data['current'] = name
                    else:
                        if data['apis'].keys():
                            args = ','.join(data['apis'].keys())
                            print('Error: `{name}` not exist. Available arguments: {args}'.format(\
                                                                                        name=name,\
                                                                                        args=args))
                        else:
                            print('Config not found. Please add config first')
                        return
                with open(self.config, 'w') as fp:
                    fp.write(json.dumps(data, indent=4))
            except OSError as e:
                print(e)


