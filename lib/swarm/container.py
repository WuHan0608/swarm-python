# -*- coding: utf8 -*-

import json
from docker import errors
from datetime import datetime
from base import Docker
from utils import timeformat

class Containers(object):
    """
    Similar to `docker ps`
    """
    def __init__(self):
        self.cli = Docker().client
        self.nodes = {}
        self.node_length = 4     # `node` length
        self.created_length = 7  # `created` length
        self.status_length = 6   # `status` length

    def _get_containers(self, show_all=False, filters={}, limit=None, container_list=None):
        """
        :param show_all(bool): Show all containers. Only running containers are shown by default
        :param filters(dict): Filters to be processed on the image list
        :parma limit(tuple or list): Filter containers by node
        :param container_list(tuple): Filter containers by container id
        """
        if self.cli is not None:
            ret = cli.containers(all=show_all,filters=filters)
            self.cli.close()
            for container in ret:
                # if container_list provide, then get containers by it
                if container_list is not None:
                    if not container['Id'].startswith(container_list):
                        continue
                node = container['Names'][0].split('/', 2)[1]
                # if limit is given, then get containers by it
                if limit is not None:
                    if not node in limit:
                        continue
                # all containers links with this one is present in 'Names'
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
                self.status_length = len(container['Status']) if len(container['Status']) > self.status_length else self.status_length
                 # (Id, Node, Created, Status, Names)
                data = (container['Id'], node, created, container['Status'], names)
                self.nodes.setdefault(node, []).append(data)

    def _pretty_print(self):
        if self.nodes:
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

    def __call__(self, show_all=False, filters={},limit=None):
        self._get_containers(show_all=show_all,filters=filters,limit=limit)
        self._pretty_print()

class StartContainer(Containers):
    """
    Similar to `docker start`
    """
    def __init__(self):
        super(StartContainer, self).__init__()

    def __call__(self, container_list):
        if self.cli is not None:
            for container_id in container_list:
                try:
                    self.cli.start(container_id)
                except errors.NotFound as e:
                    print(e.explanation)
                except errors.APIError as e:
                    print(e.explanation)
                except errors.DockerException:
                    print(e.explanation)
                finally:
                    self.cli.close()
            # print container status
            self._get_containers(container_list=container_list)
            if self.nodes:
                self._pretty_print()

class StopContainer(Containers):
    """
    Similar to `docker stop`
    """
    def __init__(self):
        super(StopContainer, self).__init__()

    def __call__(self, container_list):
        if self.cli is not None:
            for container_id in container_list:
                try:
                    self.cli.stop(container_id)
                except errors.NotFound as e:
                    print(e.explanation)
                except errors.APIError as e:
                    print(e.explanation)
                except errors.DockerException as e:
                    print(e.explanation)
                finally:
                    self.cli.close()
            # print container status
            self._get_containers(filters={'status': 'exited'},\
                                    container_list=container_list)
            if self.nodes:
                self._pretty_print()

class RestartContainer(Containers):
    """
    Similar to `docker restart`
    """
    def __init__(self):
        super(RestartContainer, self).__init__()

    def __call__(self, container_list):
        if self.cli is not None:
            for container_id in container_list:
                try:
                    self.cli.restart(container_id)
                except errors.NotFound as e:
                    print(e.explanation)
                except errors.APIError as e:
                    print(e.explanation)
                except errors.DockerException as e:
                    print(e.explanation)
                finally:
                    self.cli.close()
            # print container status
            self._get_containers(container_list=container_list)
            if self.nodes:
                self._pretty_print()

class RemoveContainer(Containers):
    """
    Similar to `docker rm`
    """
    def __init__(self):
        super(RemoveContainer, self).__init__()

    def __call__(self, container_list):
        if self.cli is not None:
            container_error = set()
            for container_id in container_list:
                try:
                    self.cli.remove_container(container_id)
                except errors.NotFound as e:
                    print(e.explanation)
                    container_error.add(container_id)
                except errors.APIError as e:
                    print(e.explanation)
                    container_error.add(container_id)
                except errors.DockerException as e:
                    print(e.explanation)
                    container_error.add(container_id)
                finally:
                    self.cli.close()
            # exclude containers in container_error
            container_removed = tuple([container_id for container_id in container_list\
                                                if not container_id in container_error])
            self._get_containers(container_list=container_removed)
            if not self.nodes and container_removed:
                print('Succeed to remove container {containers}'.format(\
                                                containers=', '.join(container_removed)))

class CreateContainer(Containers):
    """
    Similar to `docker run`
    """
    def __init__(self):
        super(CreateContainer, self).__init__()

    def _create_container(self, image, command=None, hostname=None, user=None,
                          detach=False, stdin_open=False, tty=False,
                          mem_limit=None, ports=None, environment=None,
                          dns=None, volumes=None, volumes_from=None,
                          network_disabled=False, name=None, entrypoint=None,
                          cpu_shares=None, working_dir=None, domainname=None,
                          memswap_limit=None, cpuset=None, host_config=None,
                          mac_address=None, labels=None, volume_driver=None,
                          stop_signal=None):
        try:
            self.cli.create_container(image, command, hostname, user, detach, stdin_open,\
                                      tty, mem_limit, ports, environment, dns, volumes,\
                                      volumes_from, network_disabled, name, entrypoint,\
                                      cpu_shares, working_dir, domainname, memswap_limit,\
                                      cpuset, host_config, mac_address, labels, volume_driver,\
                                      stop_signal)
        except errors.APIError as e:
            print(e.explanation)
        except errors.DockerException as e:
            print(e.explanation)

