# -*- coding: utf8 -*-

from docker import Client
from api import SwarmApi
from utils import current_url_found, detect_range, expand_hostname_range
from pprint import pprint

class SwarmCommand(object):
    def __init__(self, args):
        self._config = SwarmApi().config
        self._args = args
        self._commands = {
            'api': self._swarm_api,
            'version': self._swarm_version,
            'info': self._swarm_info,
            'ps': self._swarm_ps,
            'run': self._swarm_run,
            'start': self._swarm_start,
            'stop': self._swarm_stop,
            'restart': self._swarm_restart,
            'rm': self._swarm_rm,
            'exec': self._swarm_exec,
            'top': self._swarm_top,
            'inspect': self._swarm_inspect,
            'images': self._swarm_images,
            'rmi': self._swarm_rmi,
            'tag': self._swarm_tag,
            'pull': self._swarm_pull,
            'build': self._swarm_build,
        }

    def __call__(self):
        self._commands[self._args.cmd]()

    def _swarm_api(self):
        notice = '[Notice] No swarm api in use'
        if self._args.command == 'get':
            if not current_url_found(self._config):
                print(notice)
            for name in self._args.argument:
                self._args.func.get_api(name)
        elif self._args.command == 'set':
            if not current_url_found(self._config):
                print(notice)
            for item in self._args.argument:
                name, api = item.split('=')
                self._args.func.update_api(name, api)
        elif self._args.command == 'unset':
            if not current_url_found(self._config):
                print(notice)
            for name in self._args.argument:
                self._args.func.remove_api(name)
        elif self._args.command == 'version':
            self._args.func.use_version(self._args.argument[0])
        elif self._args.command == 'use':
            self._args.func.use_api(self._args.argument[0])

    def _swarm_version(self):
        self._args.func()

    def _swarm_info(self):
        self._args.func()

    def _swarm_ps(self):
        filters = {}
        if self._args.filter is not None:
            for item in self._args.filter:
                if item.count('=') == 1:
                    k, v = item.split('=')
                    filters[k] = v
                else:
                    print('bad format of filter (expected name=value)')
                    exit(1)
        if self._args.limit is not None:
            limit = []
            for node in self._args.limit:
                if detect_range(node):
                    limit.extend(expand_hostname_range(node))
                else:
                    limit.append(node)
            limit = tuple(limit)
        else:
            limit = None
        self._args.func(show_all=self._args.all,filters=filters,limit=limit)

    def _swarm_run(self):
        labels = None
        links = None
        ports = None
        port_bindings = None
        volumes = None
        # handle container lables
        if self._args.label is not None:
            labels = {}
            for item in self._args.label:
                if item.count('=') == 1:
                    name, value = item.split('=')
                    labels[name] = value
                else:
                    print('bad format of label (expected name=value)')
                    exit(1)
        # handle container link
        if self._args.link is not None:
            links = {}
            for item in self._args.link:
                if item.count(':') == 0:
                    name = alias = item
                elif item.count(':') == 1:
                    name, value = item.split(':')
                else:
                    print('bad format for link (expected name:alias)')
                    exit(1)
                links[name] = alias
        # handle published ports
        if self._args.publish is not None:
            ports = []
            port_bindings = {}
            for item in self._args.publish:
                # expected format: ip:hostPort:containerPort | ip::containerPort | hostPort:containerPort | containerPort
                if item.count(':') == 0:
                    containerPort = item
                    port_bindings[containerPort] = None
                elif item.count(':') == 1:
                    hostPort, containerPort = item.split(':')
                    port_bindings[containerPort] = hostPort
                elif item.count(':') == 2:
                    hostIp, hostPort, containerPort = item.split(':')
                    port_bindings[containerPort] = (hostIp, hostPort) if hostPort else (hostIp,)
                else:
                    print('bad format of publish \
(expected ip:hostPort:containerPort | ip::containerPort | hostPort:containerPort | containerPort')
                    exit(1)
                if containerPort.find('/udp') > 0:
                    containerPort, protocol = containerPort.split('/')
                    ports.append((containerPort, protocol))
                else:
                    ports.append(containerPort)
        # handler container volumes
        if self._args.volume is not None:
            volumes = []
            for item in self._args.volume:
                # expected format: containerPath | hostPath:containerPath | hostPath:containerPath:[ro|rw]
                if item.count(':') == 0:
                    volumes.append(item)
                elif item.count(':') == 1:
                    volumes.append(item[1])
                elif item.count(':') == 2:
                    volumes.append(item[1])
                else:
                    print('bad format of volume \
(expected containerPath | hostPath:containerPath | hostPath:containerPath:[ro|rw]')
        # handle command
        _command = []
        if self._args.COMMAND is not None:
            _command.append(self._args.COMMAND)
        if self._args.ARG is not None:
            _command.extend(self._args.ARG)
        command = _command if _command else None
        # create host config
        host_config = Client().create_host_config(binds=self._args.volume,\
                                                  port_bindings=port_bindings,\
                                                  publish_all_ports=self._args.publish_all,\
                                                  links=links,\
                                                  privileged=self._args.privileged,\
                                                  volumes_from=self._args.volumes_from,\
                                                  network_mode=self._args.net,\
                                                  restart_policy={'Name': self._args.restart},\
                                                  mem_limit=self._args.memory)
        # build kwargs
        #print(host_config)
        image = self._args.IMAGE
        kwargs = {
            'command': command,
            'hostname': self._args.hostname,
            'user': self._args.user,
            'detach': self._args.detach,
            'stdin_open': self._args.interactive,
            'tty': self._args.tty,
            'rm': self._args.rm,
            'ports': ports,
            'environment': self._args.environment,
            'dns': None,
            'volumes': volumes,
            'network_disabled': False,
            'name': self._args.name,
            'entrypoint': self._args.entrypoint,
            'cpu_shares': None,
            'working_dir': None,
            'domainname': None,
            'memswap_limit': None,
            'cpuset': self._args.cpuset_cpus,
            'host_config': host_config,
            'mac_address': None,
            'labels': labels,
            'volume_driver': None,
            'stop_signal': None,
        }
        self._args.func(image, command=kwargs['command'], hostname=kwargs['hostname'],\
                        user=kwargs['user'],detach=kwargs['detach'],stdin_open=kwargs['stdin_open'],\
                        tty=kwargs['tty'],rm=kwargs['rm'],mem_limit=None,ports=kwargs['ports'],\
                        environment=kwargs['environment'],dns=kwargs['dns'],volumes=kwargs['volumes'],\
                        volumes_from=None,network_disabled=kwargs['network_disabled'],\
                        name=kwargs['name'],entrypoint=kwargs['entrypoint'],\
                        cpu_shares=kwargs['cpu_shares'],working_dir=kwargs['working_dir'],\
                        domainname=kwargs['domainname'],memswap_limit=kwargs['memswap_limit'],\
                        cpuset=kwargs['cpuset'],host_config=kwargs['host_config'],\
                        mac_address=kwargs['mac_address'],labels=kwargs['labels'],\
                        volume_driver=kwargs['volume_driver'],stop_signal=kwargs['stop_signal'])

    def _swarm_start(self):
        self._args.func(tuple(self._args.CONTAINER))

    def _swarm_stop(self):
        self._args.func(tuple(self._args.CONTAINER), self._args.time)

    def _swarm_restart(self):
        self._args.func(tuple(self._args.CONTAINER), self._args.time)

    def _swarm_rm(self):
        self._args.func(tuple(self._args.CONTAINER), self._args.volumes,\
                                        self._args.force, self._args.link)

    def _swarm_exec(self):
        command = []
        if self._args.COMMAND is not None:
            command.append(self._args.COMMAND)
        if self._args.ARG is not None:
            command.extend(self._args.ARG)
        self._args.func(self._args.CONTAINER, command, self._args.detach,\
                                self._args.interactive, self._args.tty, self._args.user)

    def _swarm_top(self):
        self._args.func(self._args.CONTAINER, self._args.ps_args)

    def _swarm_inspect(self):
        # print container or image inspect if type is provide
        if self._args.type is not None:
            if self._args.type == 'container':
                ret = self._args.inspect_container(self._args.OBJECT)
            elif self._args.type == 'image':
                ret = self._args.inspect_image(self._args.OBJECT)
            if ret is not None:
                pprint(ret)
        else:
        # print both otherwise
            ret = []
            for data in (self._args.inspect_container(self._args.OBJECT),\
                            self._args.inspect_image(self._args.OBJECT)):
                if data is not None:
                    ret.extend(data)
            pprint(ret)

    def _swarm_images(self):
        filters = {}
        if self._args.filter:
            for item in self._args.filter.split(','):
                if item.count('=') == 1:
                    k, v = item.split('=')
                    filters[k] = v
                else:
                    print('bad format for filter (expected name=value)')
                    exit(1)
        self._args.func(name=self._args.REPOSITORY,show_all=self._args.all,filters=filters)

    def _swarm_rmi(self):
        images = set()
        for image_name in self._args.IMAGE:
            images.add(image_name)
        self._args.func(tuple(images))

    def _swarm_tag(self):
        repo_name = self._args.REPOTAG.split(':', 1)
        # tag defaults to 'latest' if not provide
        if len(repo_name) == 1:
            repo = repo_name[0]
            tag = None
        else:
            repo, tag = repo_name
        self._args.func(self._args.IMAGE, repo, tag, self._args.force)

    def _swarm_pull(self):
        auth_config = None
        repo_name = self._args.REPOTAG.split(':', 1)
        if len(repo_name) == 1:
            repo = repo_name[0]
            tag = None
        else:
            repo, tag = repo_name
        if self._args.auth is not None:
            if self._args.auth.count(':') == 1:
                username, password = self._args.auth.split(':')
            else:
                print('bad format for auth (expected username:password)')
                exit(1)
            auth_config = {
                'username': username,
                'password': password
            }
        self._args.func(repo, tag, self._args.insecure, auth_config)

    def _swarm_build(self):
        container_limits = {}
        if self._args.cpu_shares is not None:
            container_limits['cpushares'] = self._args.cpu_shares
        if self._args.cpuset_cpus is not None:
            container_limits['cpusetcpus'] = self._args.cpuset_cpus
        if self._args.memory is not None:
            container_limits['memory'] = self._args.memory
        if self._args.memory_swap is not None:
            container_limits['memswap'] = self._args.self._args.memory_swap
        self._args.func(path=self._args.PATH, tag=self._args.tag, quiet=self._args.quiet,\
                        nocache=self._args.no_cache, rm=self._args.rm, pull=self._args.pull,\
                        forcerm=self._args.force_rm, dockerfile=self._args.file,\
                        container_limits=container_limits, decode=True)

