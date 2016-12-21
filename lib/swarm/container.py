# -*- coding: utf8 -*-

from __future__ import print_function
import six
import dockerpty
from docker import errors
from datetime import datetime
from fnmatch import fnmatch
from swarm.client import SwarmClient
from swarm.utils import timeformat, pyprint


class ContainerBase(object):

    def __init__(self):
        self.swarm = SwarmClient()
        self.containers = {}
        self.node_length = len('NODE')
        self.image_length = len('IMAGE')
        self.command_length = len('COMMAND')
        self.created_length = len('CREATED')
        self.status_length = len('STATUS')
        self.max_command_length = 20
        self.max_id_length = 12

    def _handle_wildcard(self, pattern):
        names = []
        cli = self.swarm.client
        if cli is not None:
            containers = cli.containers(all=True)
            containers_name = tuple((name.split('/')[2] for container in containers
                                                        for name in container['Names']
                                                        if name.count('/') == 2))
            for name in containers_name:
                if fnmatch(name, pattern):
                    names.append(name)
        return names

    def _handle_containers(self, command, container, **kwargs):
        """
        :param command(str): must be one of ['start', 'stop', 'restart', 'remove', 'kill']
        :param container_list(list): list containes container ids or names
        :param kwargs: optional keyword arguments
        """
        cli = self.swarm.client
        if cli is not None:
            handlers = {
                'start': cli.start,
                'stop': cli.stop,
                'restart': cli.restart,
                'remove': cli.remove_container,
                'kill': cli.kill
            }
            try:
                handlers[command](container, **kwargs)
            except (errors.NotFound, errors.APIError, errors.DockerException) as e:
                pyprint(e.explanation)
            finally:
                cli.close()


class Containers(ContainerBase):

    def __init__(self):
        super(Containers, self).__init__()

    def _get_containers(self, show_all=False, filters={}, limit=None, latest=None, since=None):
        """
        :param show_all(bool): Show all containers. Only running containers are shown by default
        :param filters(dict): Filters to be processed on the image list
        :parma limit(tuple or list): Filter containers by node name or node pattern
        :param latest(bool): Show only the latest created container, include non-running ones
        :param since(str): Show only containers created since Id or Name, include non-running containers
        """
        cli = self.swarm.client
        if cli is not None:
            try:
                ret = cli.containers(all=show_all, filters=filters, latest=latest, since=since)
            except (errors.NotFound, errors.APIError, errors.DockerException) as e:
                pyprint(e.explanation)
                return
            finally:
                cli.close()
            if ret:
                for container in ret:
                    # if limit is provide, then get containers against it
                    node = container['Names'][0].split('/', 2)[1]
                    if limit is not None:
                        if not node in limit:
                            continue
                    # 'Names' includes self container name as well as names of linked containers
                    # Filter name by checking '/'
                    for names in container['Names']:
                        if names.count('/') == 2:
                            name = names.split('/')[2]
                            break
                    # convert created timestamp to human-readable string
                    created_delta = datetime.now() - datetime.fromtimestamp(container['Created'])
                    if created_delta.days > 1:
                        created = '{day} days ago'.format(day=created_delta.days)
                    else:
                        created = timeformat(created_delta.seconds + created_delta.days * 86400)
                    # get the longest node/created/status field length for pretty print
                    self.node_length = len(node) if len(node) > self.node_length else self.node_length
                    self.image_length = len(container['Image']) if len(container['Image']) > self.image_length\
                                                                else self.image_length
                    if len(container['Command']) < self.command_length:
                        command = container['Command']
                    else:
                        command = container['Command'] if len(container['Command']) < self.max_command_length\
                                                       else container['Command'][:self.max_command_length]
                        self.command_length = len(container['Command']) if len(container['Command']) < self.max_command_length\
                                                                        else self.max_command_length
                    self.created_length = len(created) if len(created) > self.created_length else self.created_length
                    self.status_length = len(container['Status']) if len(container['Status']) > self.status_length else self.status_length
                     # (Id, Node, Image, Command, Created, Status, Names)
                    data = (container['Id'], node, container['Image'], command, created, container['Status'], name)
                    self.containers.setdefault(node, []).append(data)

    def _pretty_print(self):
        if self.containers:
            blank = 4
            # title: CONTAINER ID    IMAGE    COMMAND    NODE    CREATED    STATUS    NAMES
            s1 = ' ' * blank
            s2 = ' ' * (self.node_length+blank-len('NODE'))
            s3 = ' ' * (self.image_length+blank-len('IMAGE'))
            s4 = ' ' * (self.command_length+blank-len('COMMAND')+2)
            s5 = ' ' * (self.created_length+blank-len('CREATED'))
            s6 = ' ' * (self.status_length+blank-len('STATUS'))
            title = '\
CONTAINER ID{s1}NODE{s2}IMAGE{s3}COMMAND{s4}CREATED{s5}STATUS{s6}NAMES'.format(s1=s1,
                                                                               s2=s2,
                                                                               s3=s3,
                                                                               s4=s4,
                                                                               s5=s5,
                                                                               s6=s6)
            # pretty-print string defined by title
            string = ''
            for node in sorted(self.containers):
                for data in self.containers[node]:
                    cid, node, image, command, created, status, names = data
                    s1 = ' ' * blank
                    s2 = ' ' * (self.node_length+blank-len(node))
                    s3 = ' ' * (self.image_length+blank-len(image))
                    s4 = ' ' * (self.command_length+blank-len(command))
                    s5 = ' ' * (self.created_length+blank-len(created))
                    s6 = ' ' * (self.status_length+blank-len(status))
                    string += '\
{id}{s1}{node}{s2}{image}{s3}"{command}"{s4}{created}{s5}{status}{s6}{names}\n'.format(id=cid[:self.max_id_length],
                                                                                       s1=s1,
                                                                                       node=node,
                                                                                       s2=s2,
                                                                                       image=image,
                                                                                       s3=s3,
                                                                                       command=command,
                                                                                       s4=s4,
                                                                                       created=created,
                                                                                       s5=s5,
                                                                                       status=status,
                                                                                       s6=s6,
                                                                                       names=names)
            # print pretty-print string
            print('{title}\n{string}'.format(title=title,string=string.rstrip()))

    def __call__(self, **kwargs):
        self._get_containers(**kwargs)
        self._pretty_print()


class StartContainer(ContainerBase):

    def __init__(self):
        super(StartContainer, self).__init__()

    def __call__(self, container_list):
        """
        :param container_list(list): List of container id or name
        """
        for container in container_list:
            if container.count('*') > 0: # wildcard name
                containers = self._handle_wildcard(container)
                for _container in containers:
                    self._handle_containers('start', _container)
                    print(_container)
            else:
                self._handle_containers('start', container)
                print(container)


class StopContainer(ContainerBase):

    def __init__(self):
        super(StopContainer, self).__init__()

    def __call__(self, container_list, timeout):
        """
        :param container_list(list): List of container id or name
        :param timeout(int): Timeout in seconds to wait for the container to stop before sending a SIGKIL
        """
        for container in container_list:
            if container.count('*') > 0: # wildcard name
                containers = self._handle_wildcard(container)
                for _container in containers:
                    self._handle_containers('stop', _container, timeout=timeout)
                    print(_container)
            else:
                self._handle_containers('stop', container, timeout=timeout)
                print(container)


class RestartContainer(ContainerBase):

    def __init__(self):
        super(RestartContainer, self).__init__()

    def __call__(self, container_list, timeout=10):
        """
        :param container_list(list): List of container id or name
        :param timeout(int): Timeout in seconds to wait for the container to stop before sending a SIGKIL
        """
        for container in container_list:
            if container.count('*') > 0: # wildcard name
                containers = self._handle_wildcard(container)
                for _container in containers:
                    self._handle_containers('restart', _container, timeout=timeout)
                    print(_container)
            else:
                self._handle_containers('restart', container, timeout=timeout)
                print(container)


class RemoveContainer(ContainerBase):

    def __init__(self):
        super(RemoveContainer, self).__init__()

    def __call__(self, container_list, **kwargs):
        """
        :param container_list(list): List of container ids
        :param v(bool): Remove the volumes associated with the container
        :param force(bool): Force the removal of a running container (uses SIGKILL)
        :param: link(bool): Remove the specified link and not the underlying container
        """
        for container in container_list:
            if container.count('*') > 0: # wildcard name
                containers = self._handle_wildcard(container)
                for _container in containers:
                    self._handle_containers('remove', _container, **kwargs)
                    print(_container)
            else:
                self._handle_containers('remove', container, **kwargs)
                print(container)


class CreateContainer(ContainerBase):

    def __init__(self):
        super(CreateContainer, self).__init__()

    def __call__(self, *args, **kwargs):
        cli = self.swarm.client
        if cli is not None:
            rm_flag = kwargs.pop('rm')
            logs = kwargs.pop('logs')
            try:
                ret = cli.create_container(*args, **kwargs)
                if ret.get('Warnings') is not None:
                    print('[Warning] {message}'.format(message=ret['Warnings']))
                # try to start created container
                if ret.get('Id') is not None:
                    if kwargs['stdin_open'] and kwargs['tty']:
                        dockerpty.start(cli, ret['Id'], logs=logs)
                    else:
                        cli.start(ret['Id'])
                        print(ret['Id'])
                    if rm_flag:
                        cli.remove_container(ret['Id'])
            except (errors.NotFound, errors.APIError, errors.DockerException) as e:
                pyprint(e.explanation)
            # volumes_from and dns arguments raise TypeError exception 
            # if they are used against v1.10 and above of the Docker remote API
            except TypeError as e:
                pyprint(e)
            finally:
                cli.close()


class InspectContainer(ContainerBase):

    def __init__(self):
        super(InspectContainer, self).__init__()

    def __call__(self, container_list):
        """
        :param container_list(list): List of container ids or names
        """
        cli = self.swarm.client
        if cli is not None:
            ret = []
            for container in container_list:
                try:
                    ret.append(cli.inspect_container(container))
                except (errors.NotFound, errors.APIError, errors.DockerException):
                    pass 
            cli.close()
            return ret if ret else None


class Top(ContainerBase):

    def __init__(self):
        super(Top, self).__init__()

    def _pretty_print(self):
        string = ''
        length = []
        for title in self.ret['Titles']:
            length.append(len(title))
        for process in self.ret['Processes']:
            for value in process:
                i = process.index(value)
                if len(value) > length[i]:
                    length[i] = len(value)
        for title in self.ret['Titles']:
            i = self.ret['Titles'].index(title)
            string += title + ' ' * (length[i]-len(title)+4)
        string += '\n'
        for process in self.ret['Processes']:
            for value in process:
                i = process.index(value)
                string += value + ' ' * (length[i]-len(value)+4)
            string += '\n'
        print(string.strip())

    def __call__(self, container, ps_args):
        """
        :param container(str): The container to inspect
        :param ps_args(str): An optional arguments passed to ps (e.g., aux)
        """
        cli = self.swarm.client
        if cli is not None:
            try:
                self.ret = cli.top(container, ps_args)
            except (errors.NotFound, errors.APIError, errors.DockerException) as e:
                pyprint(e.explanation)
            finally:
                cli.close()
            self._pretty_print()


class Exec(ContainerBase):

    def __init__(self):
        super(Exec, self).__init__()

    def __call__(self, container, command, detach, stdin, tty, user):
        """
        :param container(str): Target container where exec instance will be created
        :param command(str or list): Command to be executed
        :param detach(bool): If true, detach from the exec command
        :param stdin(bool): Keep stdin open even if not attached
        :param tty(bool): Allocate a pseudo-TTY
        :param user(str): User to execute command as
        """
        cli = self.swarm.client
        if cli is not None:
            try:
                if stdin and tty:
                    ret = cli.exec_create(container, command, stdin=True, stdout=True,
                                          stderr=True, tty=True, user=user)
                    dockerpty.start_exec(cli, ret['Id'])
                else:
                    ret = cli.exec_create(container, command, user=user)
                    for line in cli.exec_start(ret['Id'], detach=detach, stream=True):
                        print(line.strip())                     
            except (errors.NotFound, errors.APIError, errors.DockerException) as e:
                pyprint(e.explanation)
            finally:
                cli.close()


class Kill(ContainerBase):

    def __init__(self):
        super(Kill, self).__init__()

    def __call__(self, container_list, signal):
        """
        :param container(str): The container id to kill
        :param signal(str or int):  The signal to send. Defaults to SIGKILL
        """
        containers_killed = self._handle_containers('kill', container_list, signal=signal)
        if containers_killed:
            print('\n'.join(containers_killed))


class Rename(ContainerBase):

    def __init__(self):
        super(Rename, self).__init__()

    def __call__(self, container, name):
        """
        :param container(str): ID of the container to rename
        :param name(str): New name for the container
        """
        cli = self.swarm.client
        if cli is not None:
            try:
                cli.rename(container, name)
            except (errors.NotFound, errors.APIError, errors.DockerException) as e:
                pyprint(e.explanation)
            finally:
                cli.close()


class Logs(ContainerBase):

    def __init__(self):
        super(Logs, self).__init__()

    def __call__(self, container, **kwargs):
        """
        :param container(str): The container to get logs from
        :param timestamps(bool): Show timestamps
        :param tail(str or int): Output specified number of lines at the end of logs: "all" or number
        :param since(int): Show logs since a given datetime or integer epoch (in seconds)
        :param follow(bool): Follow log output
        """
        cli = self.swarm.client
        if cli is not None:
            kwargs['stdout'] = kwargs['stderr'] = True
            kwargs['stream'] = True
            try:
                for line in cli.logs(container, **kwargs):
                    if six.PY3:
                        line = line.decode('utf8')
                    print(line, end='')
            except (errors.NotFound, errors.APIError, errors.DockerException) as e:
                pyprint(e.explanation)
            finally:
                cli.close()
