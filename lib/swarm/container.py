# -*- coding: utf8 -*-

import dockerpty
from docker import errors
from datetime import datetime
from client import SwarmClient
from utils import timeformat

class ContainerBase(object):
    """
    Containers Base Class
    """
    def __init__(self):
        self.swarm = SwarmClient()
        self.containers = {}
        self.node_length = len('NODE')
        self.image_length = len('IMAGE')
        self.command_length = len('COMMAND')
        self.created_length = len('CREATED')
        self.status_length = len('STATUS')
        self.max_command_length = 20

    def _handle_containers(self, command, container_list, **kwargs):
        """
        :param command(str): must be one of ['start', 'stop', 'restart', 'remove']
        :container_list(list): list containes container ids
        :kwargs: optional keyword arguments
        """
        cli = self.swarm.client
        if cli is not None:
            handlers = {
                'start': cli.start,
                'stop': cli.stop,
                'restart': cli.restart,
                'remove': cli.remove_container,
            }
            if not command in handlers:
                return
            containers_id = tuple((container['Id'] for container in cli.containers(all=True)))
            containers_err = set()
            for container_id in container_list:
                # try find container_id in the containers_id:
                matched = False
                for full_container_id in containers_id:
                    if full_container_id.startswith(container_id):
                        matched = True
                        break
                if not matched:
                    print('Container ID `{container_id}` is missing'.format(container_id=container_id))
                    containers_err.add(container_id)
                    continue
                # handler container is container id is ok
                try:
                    handlers[command](container_id, **kwargs)
                except errors.NotFound as e:
                    print(e.explanation)
                    containers_err.add(container_id)
                except errors.APIError as e:
                    print(e.explanation)
                    containers_err.add(container_id)
                except errors.DockerException:
                    print(e.explanation)
                    containers_err.add(container_id)
            cli.close()
            return tuple((container_id for container_id in container_list\
                                            if not container_id in containers_err))

    def _get_containers(self, show_all=False, filters={}, limit=None, latest=None, since=None,\
                                                                            container_list=None):
        """
        :param show_all(bool): Show all containers. Only running containers are shown by default
        :param filters(dict): Filters to be processed on the image list
        :parma limit(tuple or list): Filter containers by node name or node pattern
        :param latest(bool): Show only the latest created container, include non-running ones
        :param since(str): Show only containers created since Id or Name, include non-running ones
        :param container_list(list): List containes container ids
        """
        cli = self.swarm.client
        if cli is not None:
            try:
                ret = cli.containers(all=show_all, filters=filters, latest=latest, since=since)
            except errors.NotFound as e:
                print(e.explanation)
                return
            except errors.APIError as e:
                print(e.explanation)
                return
            except errors.DockerException:
                print(e.explanation)
                return
            finally:
                cli.close()
            if ret:
                for container in ret:
                    # if container_list provide, then get containers against it
                    # name and id are both allowed for query from api version '1.20'
                    if container_list is not None:
                        if not container['Id'].startswith(container_list):
                            continue
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
                    self.created_length = len(created) if len(created) > self.created_length\
                                                                        else self.created_length
                    self.status_length = len(container['Status']) if len(container['Status']) > self.status_length\
                                                                        else self.status_length
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
CONTAINER ID{s1}NODE{s2}IMAGE{s3}COMMAND{s4}CREATED{s5}STATUS{s6}NAMES'.format(\
                                                                        s1=s1,\
                                                                        s2=s2,\
                                                                        s3=s3,\
                                                                        s4=s4,\
                                                                        s5=s5,\
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
{id}{s1}{node}{s2}{image}{s3}"{command}"{s4}{created}{s5}{status}{s6}{names}\n'.format(\
                                                                            id=cid[:12],\
                                                                            s1=s1,\
                                                                            node=node,\
                                                                            s2=s2,\
                                                                            image=image,\
                                                                            s3=s3,\
                                                                            command=command,\
                                                                            s4=s4,\
                                                                            created=created,\
                                                                            s5=s5,\
                                                                            status=status,\
                                                                            s6=s6,\
                                                                            names=names)
            # print pretty-print string
            print('{title}\n{string}'.format(title=title,string=string.rstrip()))

class Containers(ContainerBase):
    """
    Similar to `docker ps`
    """
    def __init__(self):
        super(Containers, self).__init__()

    def __call__(self, **kwargs):
        self._get_containers(**kwargs)
        self._pretty_print()

class StartContainer(ContainerBase):
    """
    Similar to `docker start`
    """
    def __init__(self):
        super(StartContainer, self).__init__()

    def __call__(self, container_list):
        """
        :param container_list(list): List of container ids
        """
        containers_start = self._handle_containers('start', container_list)
        if containers_start is not None:
            # print container status
            self._get_containers(show_all=True, container_list=containers_start)
            self._pretty_print()

class StopContainer(ContainerBase):
    """
    Similar to `docker stop`
    """
    def __init__(self):
        super(StopContainer, self).__init__()

    def __call__(self, container_list, timeout):
        """
        :param container_list(list): List of container ids
        :param timeout(int): Timeout in seconds to wait for the container to stop before sending a SIGKIL
        """
        containers_stop = self._handle_containers('stop', container_list, timeout=timeout)
        if containers_stop is not None:
            # print container status
            self._get_containers(filters={'status': 'exited'}, container_list=container_list)
            self._pretty_print()

class RestartContainer(ContainerBase):
    """
    Similar to `docker restart`
    """
    def __init__(self):
        super(RestartContainer, self).__init__()

    def __call__(self, container_list, timeout=10):
        """
        :param container_list(list): List of container ids
        :param timeout(int): Timeout in seconds to wait for the container to stop before sending a SIGKIL
        """
        containers_restart = self._handle_containers('restart', container_list, timeout=timeout)
        if containers_restart is not None:
            # print container status
            self._get_containers(show_all=True, container_list=containers_restart)
            self._pretty_print()

class RemoveContainer(ContainerBase):
    """
    Similar to `docker rm`
    """
    def __init__(self):
        super(RemoveContainer, self).__init__()

    def __call__(self, container_list, **kwargs):
        """
        :param container_list(list): List of container ids
        :param v(bool): Remove the volumes associated with the container
        :param force(bool): Force the removal of a running container (uses SIGKILL)
        :param: link(bool): Remove the specified link and not the underlying container
        """
        containers_removed = self._handle_containers('remove', container_list, **kwargs)
        if containers_removed:
            print('Succeed to remove container {containers}'.format(\
                            containers=', '.join(containers_removed)))

class CreateContainer(ContainerBase):
    """
    Similar to `docker run`
    """
    def __init__(self):
        super(CreateContainer, self).__init__()

    def __call__(self, *args, **kwargs):
        cli = self.swarm.client
        if cli is not None:
            rm_flag = kwargs.pop('rm')
            try:
                ret = cli.create_container(*args, **kwargs)
                if ret.get('Warnings') is not None:
                    print('[Warning] {message}'.format(message=ret['Warnings']))
                # try to start created container
                if ret.get('Id') is not None:
                    if kwargs['stdin_open'] and kwargs['tty']:
                        dockerpty.start(cli, ret['Id'])
                    else:
                        cli.start(ret['Id'])
                        # try to get the latest container
                        # check if container id is matched
                        # otherwise search containers since=self.container['Id']
                        latest_container = cli.containers(latest=True)[0]
                        if ret['Id'] == latest_container['Id']:
                            self._get_containers(latest=True)
                        else:
                            self._get_containers(since=ret['Id'], container_list=(ret['Id'],))
                        self._pretty_print()                     
                    if rm_flag:
                        cli.remove_container(ret['Id'])
            except errors.NotFound as e:
                print(e.explanation)
            except errors.APIError as e:
                print(e.explanation)
            except errors.DockerException as e:
                print(e.explanation)
            # volumes_from and dns arguments raise TypeError exception 
            # if they are used against v1.10 and above of the Docker remote API
            except TypeError as e:
                print(e)
            finally:
                cli.close()

class InspectContainer(ContainerBase):
    """
    Similar to `docker inspect`, but only for containers
    """
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
                except errors.NotFound as e:
                    print(e.explanation)
                except errors.APIError as e:
                    print(e.explanation)
                except errors.DockerException as e:
                    print(e.explanation)
            cli.close()
            return ret if ret else None

class Top(ContainerBase):
    """
    Similar to `docker top`
    """
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
            except errors.NotFound as e:
                print(e.explanation)
            except errors.APIError as e:
                print(e.explanation)
            except errors.DockerException as e:
                print(e.explanation)
            finally:
                cli.close()
            self._pretty_print()

class Exec(ContainerBase):
    """
    Similar to `docker exec`
    """
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
                    ret = cli.exec_create(container, command, stdin=True, stdout=True,\
                                                        stderr=True, tty=True, user=user)
                    #dockerpty.exec_start(cli, ret['Id'])
                    print('Not implement with `swarm exec -it`')
                else:
                    ret = cli.exec_create(container, command, user=user)
                    for line in cli.exec_start(ret['Id'], detach=detach, stream=True):
                        print(line.strip())                     
            except errors.NotFound as e:
                print(e.explanation)
            except errors.APIError as e:
                print(e.explanation)
            except errors.DockerException as e:
                print(e.explanation)
            finally:
                cli.close()
