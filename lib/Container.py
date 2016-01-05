# -*- coding: utf8 -*-

from docker import Client
from datetime import datetime
from config import VERSION
from utils import timeformat

class Containers(object):
    """
    Equals to `docker ps -a`
    """
    def __init__(self, base_url):
        self.cli = Client(base_url,version=VERSION)

    def __call__(self):
        nodes = {}
        node_length = 0    # node name length
        created_length = 0 # created length
        status_length = 0  # status length
        ret = self.cli.containers(all=True)
        for item in ret:
            node = item['Names'][0].split('/', 2)[1]
            # all containers links with this one is present in 'Names'
            names = ','.join([name.split('/', 2)[2] for name in item['Names']])
            # convert created timestamp to string such as '3 hours ago'
            created_delta = datetime.now() - datetime.fromtimestamp(item['Created'])
            if created_delta.days > 1:
                created = '{day} days ago'.format(day=created_delta.days)
            elif created_delta.days == 1:
                created = '1 day ago'
            else:
                created = timeformat(created_delta.seconds)
            status = item['Status']
            # get the longest node/created/status length for pretty print
            node_length = len(node) if len(node) > node_length else node_length
            created_length = len(created) if len(created) > created_length else created_length
            status_length = len(status) if len(status) > status_length else status_length
             # (Id, Node, Created, Status, Names)
            data = (item['Id'], node, created, status, names)
            nodes.setdefault(node, []).append(data)
        # pretty print
        s1 = ' ' * 4
        s2 = ' ' * (node_length+4-len('NODE'))
        s3 = ' ' * (created_length+4-len('CREATED'))
        s4 = ' ' * (status_length+4-len('STATUS'))
        title = 'CONTAINER ID{s1}NODE{s2}CREATED{s3}STATUS{s4}NAMES'.format(\
                                                                        s1=s1,\
                                                                        s2=s2,\
                                                                        s3=s3,\
                                                                        s4=s4)
        string = ''
        for node in sorted(nodes):
            for data in nodes[node]:
                cid, node, created, status, names = data
                s1 = ' ' * 4
                s2 = ' ' * (node_length+4-len(node))
                s3 = ' ' * (created_length+4-len(created))
                s4 = ' ' * (status_length+4-len(status))
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

        print('{title}\n{string}'.format(title=title,string=string).rstrip())
        # close communication
        self.cli.close()

if __name__ == '__main__':
    base_url = 'tcp://172.24.128.31:3375'
    containers = Containers(base_url)
    containers()
