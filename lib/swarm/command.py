# -*- coding: utf8 -*-

import argparse
from config import ApiConfig
from misc import Version, Info
from container import Containers, StartContainer, StopContainer, RestartContainer, RemoveContainer, CreateContainer
from image import Images, Tag, RemoveImage
from utils import base_url_found, current_url_found

class SwarmCommand(object):
    def __init__(self):
        self._config = ApiConfig().config
        self._parser = argparse.ArgumentParser()
        self._subparsers = self._parser.add_subparsers()
        self._commands = {
            'api': self._swarm_api(),
            'version': self._swarm_version(),
            'info': self._swarm_info(),
            'ps': self._swarm_ps(),
            'run': self._swarm_run(),
            'start': self._swarm_start(),
            'stop': self._swarm_stop(),
            'restart': self._swarm_restart(),
            'rm': self._swarm_rm(),
            'images': self._swarm_images(),
            'rmi': self._swarm_rmi(),
            'tag': self._swarm_tag(),
        }

    def _add_subparsers(self):
        self._add_parser_api()
        if base_url_found:
            self._add_parser_version()
            self._add_parser_info()
            self._add_parser_ps()
            self._add_parser_start()
            self._add_parser_stop()
            self._add_parser_restart()
            self._add_parser_rm()
            self._add_parser_run()
            self._add_parser_images()

    def _add_parser_api(self):
        parser_api = self._subparsers.add_parser('api', help='\
Config Swarm API arguments, Otherwise no further command')
        parser_api.add_argument('command', choices=('get','update','remove','use'),help='\
Available comamnd: get, update, remove, use')
        parser_api.add_argument('argument', type=str, help='\
a comma-separated list for `get`(i.e. name1,name2); \
a comma-separated list for `update`(i.e. name1=api1,name2=api2); \
a comma-separated list for `remove`(i.e. name1,name2); \
set one name as current Swarm API for `use`')
        parser_api.set_defaults(func=ApiConfig())

    def _add_parser_version(self):
        parser_version = self._subparsers.add_parser('version', help='\
Show the Docker version information.')
        parser_version.set_defaults(func=Version())

    def _add_parser_info(self):
        parser_info = self._subparsers.add_parser('info', help='\
Display system-wide information')
        parser_info.set_defaults(Info())

    def _add_parser_ps(self):
        parser_ps = self._subparsers.add_parser('ps', help='List containers')
        parser_ps.add_argument('-a', '--all', action='store_true', help='\
Show all containers (default shows just running)')
        parser_ps.add_argument('-f', '--filter', type=str, help='\
Filter output based on conditions provide, a comma-separated list')
        parser_ps.add_argument('-l', '--limit', type=str, help='\
Show containers on nodes provide, a comma-separated list')
        parser_ps.set_defaults(func=Containers())

    def _add_parser_start(self):
        parser_start = self._subparsers.add_parser('start', help='\
Start one or more stopped containers')
        parser_start.add_argument('CONTAINER', nargs='+', help='\
Container ID')
        parser_start.set_defaults(func=StartContainer())

    def _add_parser_stop(self):
        parser_stop = self._subparsers.add_parser('stop', help='\
Stop a running container by sending SIGTERM and then SIGKILL after a grace period')
        parser_stop.add_argument('CONTAINER',nargs='+', help='\
Container ID')
        parser_stop.set_defaults(func=StopContainer())

    def _add_parser_restart(self):
        parser_restart = self._subparsers.add_parser('restart', help='\
Restart a running container')
        parser_restart.add_argument('CONTAINER',nargs='+', help='\
Container ID')
        parser_restart.set_defaults(func=RestartContainer())

    def _add_parser_rm(self):
        # add subparser for `swarm rm`
        parser_rm = self._subparsers.add_parser('rm', help='\
Remove one or more containers')
        parser_rm.add_argument('CONTAINER',nargs='+', help='\
CONTAINER ID')
        parser_rm.set_defaults(func=RemoveContainer())

    def _add_parser_run(self):
        parser_run = self._subparsers.add_parser('run', help='\
Run a command in a new container')
        parser_run.add_argument('--cpuset-cpus', dest='cpuset', type=str, help='\
CPUs in which to allow execution (0-3, 0,1)')
        parser_run.add_argument('-e', '--environment', type=str, help='\
Set environment variables, a comma-separated list')
        parser_run.add_argument('--entrypoint', type=str, help='\
Overwrite the default ENTRYPOINT of the image')
        parser_run.add_argument('--hostname', type=str, help='\
Container host name')
        parser_run.add_argument('-l', '--label', type=str, help='\
Set meta data on a container')
        parser_run.add_argument('--link', type=str, help='\
Add link to another container')
        parser_run.add_argument('-m', '--memory', type=str, help='\
Memory limit')
        parser_run.add_argument('--name', type=str, help='\
Assign a name to the container')
        parser_run.add_argument('--net', type=str, help='\
Set the Network mode for the container')
        parser_run.add_argument('-P', '--publish-all', action='store_true', help='\
Publish all exposed ports to random ports')
        parser_run.add_argument('-p', '--publish', type=str, help='\
Publish a container\'s port(s) to the host\
(format: ip:hostPort:containerPort | ip::containerPort | hostPort:containerPort | containerPort),\
a comma-separated list')
        parser_run.add_argument('--privileged', action='store_true', help='\
Give extended privileges to this container')
        parser_run.add_argument('--restart', type=str, help='\
Restart policy to apply when a container exits')
        parser_run.add_argument('--rm', action='store_true', help='\
Automatically remove the container when it exits')
        parser_run.add_argument('-u', '--user', type=str, help='\
Username or UID')
        parser_run.add_argument('-v', '--volume', type=str, help='\
Bind mount a volume, a comma-separated list')
        parser_run.add_argument('--volumes-from', dest='volumes_from', type=str, help='\
Mount volumes from the specified container(s), a comma-separated list')
        parser_run.set_defaults(func=CreateContainer())

    def _add_parser_images(self):
        parser_images = self._subparsers.add_parser('images', help='\
List images')
        parser_images.add_argument('REPOSITORY', nargs='?', default=None, help='\
Only show images belonging to the repository name')
        parser_images.add_argument('-a', '--all', action='store_true', help='\
Show all images (default hides intermediate images)')
        parser_images.add_argument('-f','--filter',type=str, help='\
Filter output based on conditions provided, a comma-separated list')
        parser_images.set_defaults(func=Images())

    def _add_parser_rmi(self):
        parser_rmi = self._subparsers.add_parser('rmi', help='\
Remove one or more images')
        parser_rmi.add_argument('IMAGE', nargs='+', help='\
IMAGE[:TAG]')
        parser_rmi.set_defaults(func=RemoveImage())

    def _add_parser_tag(self):
        parser_tag = self._subparsers.add_parser('tag', help='Tag an image into a repository')
        parser_tag.add_argument('IMAGE', type=str, help='IMAGE[:TAG]')
        parser_tag.add_argument('REPOTAG', type=str, help='[REGISTRYHOST/][USERNAME/]NAME[:TAG]')
        parser_tag.set_defaults(func=Tag())

    def _swarm_api(self):
        notice = '[Notice] No swarm api in use'
        args = self._parser.parse_args()
        if args.command == 'get':
            if not current_url_found(self._config):
                print(notice)
            for name in args.argument.split(','):
                args.func.get_api(name.strip())
        elif args.command == 'update':
            if not current_url_found(self._config):
                print(notice)
            for item in args.argument.split(','):
                name, api = item.strip().split('=')
                args.func.update_api(name, api)
        elif args.command == 'remove':
            if not current_url_found(self._config):
                print(notice)
            for name in args.argument.split(','):
                args.func.remove_api(name.strip())
        elif args.command == 'use':
            args.func.use_api(args.argument)

    def _swarm_version(self):
        args = self._parser.parse_args()
        args.func()

    def _swarm_info(self):
        args = self._parser.parse_args()
        args.func()

    def _swarm_ps(self):
        args = self._parser.parse_args()
        filters = {}
        if args.filter:
            for item in args.filter.split(','):
                k, v = item.strip().split('=')
                filters[k] = v
        if args.limit:
            limit = tuple([n.strip() for n in args.limit.split(',')])
        else:
            limit = None
        args.func(show_all=args.all,filters=filters,limit=limit)

    def _swarm_run(self):
        pass

    def _swarm_start(self):
        args = self._parser.parse_args()
        args.func(tuple(args.CONTAINER))

    def _swarm_stop(self):
        args = self._parser.parse_args()
        args.func(tuple(args.CONTAINER))

    def _swarm_restart(self):
        args = self._parser.parse_args()
        args.func(tuple(args.CONTAINER))

    def _swarm_rm(self):
        args = self._parser.parse_args()
        args.func(tuple(args.CONTAINER))

    def _swarm_images(self):
        args = self._parser.parse_args()
        filters = {}
        if args.filter:
            for item in args.filter.split(','):
                k, v = item.strip().split('=')
                filters[k] = v
        args.func(name=args.REPOSITORY,show_all=args.all,filters=filters)

    def _swarm_rmi(self):
        args = self._parser.parse_args()
        images = set()
        for image_name in args.IMAGE:
            # tag defaults to 'latest' if not provide
            if len(image_name.split(':')) == 1:
                image = ''.join((image_name.split(':')[0], ':', 'latest'))
            else:
                image = image_name
            images.add(image)
        args.func(tuple(images))

    def _swarm_tag(self):
        args = self._parser.parse_args()
        repo_name = args.REPOTAG.split(':', 1)
        # tag defaults to 'latest' if not provide
        if len(repo_name) == 1:
            repo = repo_name[0]
            tag = 'latest'
        else:
            repo, tag = repo_name
        args.func(args.IMAGE, repo, tag)

    def run(self):
        self._add_subparsers()
        args = self._parser.parse_args()
        self._commands[args.func.__class__.__name__]
