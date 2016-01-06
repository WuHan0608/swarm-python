# -*- coding: utf8 -*-

from docker import Client, errors
from datetime import datetime
from utils import timeformat

class Containers(object):
    """
    Similar to `docker ps -a`
    """
    def __init__(self, base_url, version=None):
        self.cli = Client(base_url,version=version)
        self.nodes = {}
        self.node_length = 0     # node field length
        self.created_length = 0  # created field length
        self.status_length = 0   # status field length

    def _get_containers(self, container_list=None):
        """
        :param container_list: list containing coantainer ids to filter
        """
        ret = self.cli.containers(all=True)
        self.cli.close()
        for item in ret:
            # if container_list is given
            # then get containers whose ids are in container_list
            if container_list is not None:
                if not item['Id'].startswith(container_list):
                    continue
            node = item['Names'][0].split('/', 2)[1]
            # all containers links with this one is present in 'Names'
            names = ','.join([name.split('/', 2)[2] for name in item['Names']])
            # convert created timestamp to string such as '3 hours ago'
            created_delta = datetime.now() - datetime.fromtimestamp(item['Created'])
            if created_delta.days > 1:
                created = '{day} days ago'.format(day=created_delta.days)
            else:
                created = timeformat(created_delta.seconds + created_delta.days * 86400)
            # get the longest node/created/status length for pretty print
            self.node_length = len(node) if len(node) > self.node_length else self.node_length
            self.created_length = len(created) if len(created) > self.created_length else self.created_length
            self.status_length = len(item['Status']) if len(item['Status']) > self.status_length else self.status_length
             # (Id, Node, Created, Status, Names)
            data = (item['Id'], node, created, item['Status'], names)
            self.nodes.setdefault(node, []).append(data)

    def _pretty_print(self):
        s1 = ' ' * 4
        s2 = ' ' * (self.node_length+4-len('NODE'))
        s3 = ' ' * (self.created_length+4-len('CREATED'))
        s4 = ' ' * (self.status_length+4-len('STATUS'))
        title = 'CONTAINER ID{s1}NODE{s2}CREATED{s3}STATUS{s4}NAMES'.format(\
                                                                        s1=s1,\
                                                                        s2=s2,\
                                                                        s3=s3,\
                                                                        s4=s4)
        string = ''
        for node in sorted(self.nodes):
            for data in self.nodes[node]:
                cid, node, created, status, names = data
                s1 = ' ' * 4
                s2 = ' ' * (self.node_length+4-len(node))
                s3 = ' ' * (self.created_length+4-len(created))
                s4 = ' ' * (self.status_length+4-len(status))
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
        # return pretty-print string
        print('{title}\n{string}'.format(title=title,string=string).rstrip())

    def __call__(self):
        self._get_containers()
        self._pretty_print()

class Start(Containers):
    """
    Similar to `docker start`
    """
    def __init__(self, base_url, version=None):
        super(Start, self).__init__(base_url, version)

    def __call__(self, container_list):
        # exec `docker start`
        for container_id in container_list:
            try:
                self.cli.start(container_id)
            except errors.NotFound as e:
                print('{message} ({explanation})'.format(\
                                                message=e.message,\
                                                explanation=e.explanation))
            except errors.DockerException:
                print(e)
            finally:
                self.cli.close()
        # print container status
        self._get_containers(container_list)
        if self.nodes:
            self._pretty_print()

class Stop(Containers):
    """
    Similar to `docker stop`
    """
    def __init__(self, base_url, version=None):
        super(Stop, self).__init__(base_url, version)

    def __call__(self, container_list):
        # exec `docker stop`
        for container_id in container_list:
            try:
                self.cli.stop(container_id)
            except errors.NotFound as e:
                print('{message} ({explanation})'.format(\
                                                message=e.message,\
                                                explanation=e.explanation))
            except errors.DockerException as e:
                print(e)
            finally:
                self.cli.close()
        # print container status
        self._get_containers(container_list)
        if self.nodes:
            self._pretty_print()

class Restart(Containers):
    """
    Similar to `docker restart`
    """
    def __init__(self, base_url, version=None):
        super(Restart, self).__init__(base_url, version)

    def __call__(self, container_list):
        # exec `docker start`
        for container_id in container_list:
            try:
                self.cli.restart(container_id)
            except errors.NotFound as e:
                print('{message} ({explanation})'.format(\
                                                message=e.message,\
                                                explanation=e.explanation))
            except errors.DockerException as e:
                print(e)
            finally:
                self.cli.close()
        # print container status
        self._get_containers(container_list)
        if self.nodes:
            self._pretty_print()

if __name__ == '__main__':
    base_url = 'tcp://172.24.128.31:3375'
    version = '1.20'
    container_ids = ('0ca2f37ae038', '58b62c6cf7b0', '29d4c6b6ced9', 'c832fa5f3fdb')
    #containers = Containers(base_url, version)
    #containers()
    #stop = Stop(base_url, version)
    #stop(container_ids)
    #start = Start(base_url, version)
    #start(container_ids)
    restart = Restart(base_url, version)
    restart(container_ids)
