# -*- coding: utf8 -*-

from docker import errors
from datetime import datetime
from base import SwarmClient
from utils import timeformat

class ContainersBase(object):
    """
    Containers Base Class
    """
    def __init__(self):
        self.cli = SwarmClient().client
        self.containers = {}
        self.node_length = 4     # `node` length
        self.created_length = 7  # `created` length
        self.status_length = 6   # `status` length

    def _handle_containers(self, command, container_list, **kwargs):
        """
        :param command(str): must be one of ['start', 'stop', 'restart', 'remove']
        :container_list(list): list containes container ids
        :kwargs: optional keyword arguments
        """
        handlers = {
            'start': self.cli.start,
            'stop': self.cli.stop,
            'restart': self.cli.restart,
            'remove': self.cli.remove_container,
        }
        if not command in handlers:
            return
        containers_id = tuple((container['Id'] for container in self.cli.containers(all=True)))
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
        return tuple((container_id for container_id in container_list\
                                        if not container_id in containers_err))

    def _get_containers(self, show_all=False, filters={}, limit=None, latest=None, since=None,\
                                                                            container_list=None):
        """
        :param show_all(bool): Show all containers. Only running containers are shown by default
        :param filters(dict): Filters to be processed on the image list
        :parma limit(tuple or list): Filter containers by node
        :param latest(bool): Show only the latest created container, include non-running ones
        :param since(str): Show only containers created since Id or Name, include non-running ones
        :param container_list(list): List containes container ids
        """
        try:
            ret = self.cli.containers(all=show_all, filters=filters, latest=latest, since=since)
        except errors.NotFound as e:
            print(e.explanation)
            return
        except errors.APIError as e:
            print(e.explanation)
            return
        except errors.DockerException:
            print(e.explanation)
            return
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
                names = ','.join([name.split('/', 2)[2] for name in container['Names']])
                # convert created timestamp to human-readable string
                created_delta = datetime.now() - datetime.fromtimestamp(container['Created'])
                if created_delta.days > 1:
                    created = '{day} days ago'.format(day=created_delta.days)
                else:
                    created = timeformat(created_delta.seconds + created_delta.days * 86400)
                # get the longest node/created/status field length for pretty print
                self.node_length = len(node) if len(node) > self.node_length else self.node_length
                self.created_length = len(created) if len(created) > self.created_length else self.created_length
                self.status_length = len(container['Status']) if len(container['Status']) > self.status_length\
                                                                                        else self.status_length
                 # (Id, Node, Created, Status, Names)
                data = (container['Id'], node, created, container['Status'], names)
                self.containers.setdefault(node, []).append(data)

    def _pretty_print(self):
        if self.containers:
            blank = 4
            # title: CONTAINER ID    NODE    CREATED    STATUS    NAMES
            s1 = ' ' * blank
            s2 = ' ' * (self.node_length+blank-len('NODE'))
            s3 = ' ' * (self.created_length+blank-len('CREATED'))
            s4 = ' ' * (self.status_length+blank-len('STATUS'))
            title = 'CONTAINER ID{s1}NODE{s2}CREATED{s3}STATUS{s4}NAMES'.format(\
                                                                            s1=s1,\
                                                                            s2=s2,\
                                                                            s3=s3,\
                                                                            s4=s4)
            # pretty-print string defined by title
            string = ''
            for node in sorted(self.nodes):
                for data in self.nodes[node]:
                    cid, node, created, status, names = data
                    s1 = ' ' * blank
                    s2 = ' ' * (self.node_length+blank-len(node))
                    s3 = ' ' * (self.created_length+blank-len(created))
                    s4 = ' ' * (self.status_length+blank-len(status))
                    string += '{id}{s1}{node}{s2}{created}{s3}{status}{s4}{names}\n'.format(\
                                                                                id=cid[:12],\
                                                                                s1=s1,\
                                                                                node=node,\
                                                                                s2=s2,\
                                                                                created=created,\
                                                                                s3=s3,\
                                                                                status=status,\
                                                                                s4=s4,\
                                                                                names=names)
            # print pretty-print string
            print('{title}\n{string}'.format(title=title,string=string.rstrip()))

class Containers(ContainersBase):
    """
    Similar to `docker ps`
    """
    def __init__(self):
        super(Containers, self).__init__()

    def __call__(self, show_all=False, filters={},limit=None):
        if self.cli is not None:
            self._get_containers(show_all=show_all,filters=filters,limit=limit)
            self._pretty_print()
            self.cli.close()

class StartContainer(ContainersBase):
    """
    Similar to `docker start`
    """
    def __init__(self):
        super(StartContainer, self).__init__()

    def __call__(self, container_list):
        """
        :param container_list(list): List of container ids
        """
        if self.cli is not None:
            containers_start = self._handle_containers('start', container_list)
            if containers_start is not None:
                # print container status
                self._get_containers(show_all=True,\
                                     container_list=containers_start)
                self._pretty_print()
            self.cli.close()

class StopContainer(ContainersBase):
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
        if self.cli is not None:
            containers_stop = self._handle_containers('stop', container_list,\
                                                                timeout=timeout)
            if containers_stop is not None:
                # print container status
                self._get_containers(filters={'status': 'exited'},\
                                     container_list=container_list)
                self._pretty_print()
            self.cli.close()

class RestartContainer(ContainersBase):
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
        if self.cli is not None:
            containers_restart = self._handle_containers('restart', container_list,\
                                                                        timeout=timeout)
            if containers_restart is not None:
                # print container status
                self._get_containers(show_all=True,\
                                     container_list=containers_restart)
                self._pretty_print()
            self.cli.close()

class RemoveContainer(ContainersBase):
    """
    Similar to `docker rm`
    """
    def __init__(self):
        super(RemoveContainer, self).__init__()

    def __call__(self, container_list, v, force, link):
        """
        :param container_list(list): List of container ids
        :param v(bool): Remove the volumes associated with the container
        :param force(bool): Force the removal of a running container (uses SIGKILL)
        :param: link(bool): Remove the specified link and not the underlying container
        """
        if self.cli is not None:
            containers_removed = self._handle_containers('remove', container_list,\
                                                        v=v, force=force, link=link)
            if containers_removed is not None:
                self._get_containers(show_all=True,\
                                     container_list=containers_removed)
                if not self.nodes and containers_removed:
                    print('Succeed to remove container {containers}'.format(\
                                            containers=', '.join(containers_removed)))
            self.cli.close()

class CreateContainer(ContainersBase):
    """
    Similar to `docker run`
    """
    def __init__(self):
        super(CreateContainer, self).__init__()

    def _create_container(self, *args, **kwargs):
        ret = self.cli.create_container(*args, **kwargs)
        self.container_id, self.warning = ret.get('Id'), ret.get('Warnings')

    def _print_created_container(self):
        # try to get the latest container
        # check if container id is matched
        # otherwise search containers since=self.container_id
        latest_container = self.cli.containers(latest=True)[0]
        if self.container_id == latest_container['Id']:
            self._get_containers(latest=True)
        else:
            self._get_containers(since=self.container_id,\
                                 container_list=(self.container_id,))
        self._pretty_print()

    def __call__(self, *args, **kwargs):
        if self.cli is not None:
            try:
                self._create_container(*args, **kwargs)
                if self.warning is not None:
                    print('[Warning] {message}'.format(message=self.warning))
                # try to start created container
                if self.container_id is not None:
                    self.cli.start(self.container_id)
                    self._print_created_container()
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
                self.cli.close()

class InspectContainer(ContainersBase):
    """
    Similar to `docker inspect`, but only for containers
    """
    def __init__(self):
        super(InspectContainer, self).__init__()

    def __call__(self, container_list):
        """
        :param container_list(list): List of container ids or names
        """
        if self.cli is not None:
            ret = []
            for container in container_list:
                try:
                    ret.append(self.cli.inspect_container(container))
                except errors.NotFound as e:
                    print(e.explanation)
                except errors.APIError as e:
                    print(e.explanation)
                except errors.DockerException as e:
                    print(e.explanation)
            self.cli.close()
            return ret if ret else None
