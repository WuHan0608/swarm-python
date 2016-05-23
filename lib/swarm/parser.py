# -*- coding: utf8 -*-

import argparse
from api import SwarmApi
from daemon import Version, Info, Login
from container import Containers, StartContainer, StopContainer, RestartContainer,\
                      RemoveContainer, CreateContainer, InspectContainer, Top, Exec,\
                      Kill
from image import Images, RemoveImage, Tag, InspectImage, Pull, Push, Build
from utils import base_url_found

class SwarmArgumentParser(object):
    """
    ArgumentParser for swarm command
    """
    def __init__(self):
        self._config = SwarmApi().config
        self._parser = argparse.ArgumentParser()
        self._subparsers = self._parser.add_subparsers(title='Commands')
        self._usage = {
            'api': 'swarm api COMMAND ARG [ARG...]',
            'version': 'swarm version [OPTIONS]',
            'info': 'swarm info [OPTIONS]',
            'login': 'docker login [OPTIONS] [SERVER]',
            'ps': 'swarm ps [OPTIONS]',
            'start': 'swarm start [OPTIONS] CONTAINER [CONTAINER...]',
            'stop': 'swarm stop [OPTIONS] CONTAINER [CONTAINER...]',
            'restart': 'swarm restart [OPTIONS] CONTAINER [CONTAINER...]',
            'rm': 'swarm rm [OPTIONS] CONTAINER [CONTAINER...]',
            'run': 'swarm run [OPTIONS] IMAGE [COMMAND] [ARG...]',
            'exec': 'swarm exec [OPTIONS] CONTAINER COMMAND [ARG...]',
            'top': 'swarm top [OPTIONS] CONTAINER [ps OPTIONS]',
            'kill': 'docker kill [OPTIONS] CONTAINER [CONTAINER...]',
            'inspect': 'swarm inspect [OPTIONS] CONTAINER|IMAGE [CONTAINER|IMAGE...]',
            'images': 'swarm images [OPTIONS] [REPOSITORY]',
            'rmi': 'swarm rmi [OPTIONS] IMAGE [IMAGE...]',
            'tag': 'swarm tag [OPTIONS] IMAGE[:TAG] [REGISTRYHOST/][USERNAME/]NAME[:TAG]',
            'pull': 'swarm pull [OPTIONS] NAME[:TAG]',
            'push': 'swarm push [OPTIONS] NAME[:TAG]',
            'build': 'swarm build [OPTIONS] PATH | URL | -',
        }
        self._help = {
            'api': 'Config Swarm API, otherwise no further command is available',
            'version': 'Show the Docker version information.',
            'info': 'Display system-wide information',
            'login': 'Register or log in to a Docker registry server, if no server is\
specified "https://index.docker.io/v1/" is the default.',
            'ps': 'List containers',
            'start': 'Start one or more stopped containers',
            'stop': 'Stop a running container by sending SIGTERM and then SIGKILL after a grace period',
            'restart': 'Restart a running container',
            'rm': 'Remove one or more containers',
            'run': 'Run a command in a new container',
            'exec': 'Run a command in a running container',
            'top': 'Display the running processes of a container',
            'kill': 'Kill a running container using SIGKILL or a specified signal',
            'inspect': 'Return low-level information on a container or image',
            'images': 'List images',
            'rmi': 'Remove one or more images',
            'tag': 'Tag an image into a repository',
            'pull': 'Pull an image or a repository from a registry',
            'push': 'Push an image or a repository to a registry',
            'build': 'Build a new image from the source code at PATH',
        }

    def parse_args(self):
        self._add_parser_api()
        if base_url_found(self._config):
            self._add_parser_version()
            self._add_parser_info()
            self._add_parser_login()
            self._add_parser_ps()
            self._add_parser_start()
            self._add_parser_stop()
            self._add_parser_restart()
            self._add_parser_rm()
            self._add_parser_run()
            self._add_parser_exec()
            self._add_parser_images()
            self._add_parser_inspect()
            self._add_parser_top()
            self._add_parser_kill()
            self._add_parser_rmi()
            self._add_parser_tag()
            self._add_parser_pull()
            self._add_parser_push()
            self._add_parser_build()
        return self._parser.parse_args()

    def _add_parser_api(self):
        choices = ('get', 'set', 'unset', 'use', 'version')
        parser_api = self._subparsers.add_parser('api', description=self._help['api'],\
help=self._help['api'], usage=self._usage['api'], formatter_class=argparse.RawTextHelpFormatter)
        parser_api.add_argument('command', choices=choices, metavar='COMMAND', help='\
Available comamnd: {commands}'.format(commands=', '.join(choices)))
        parser_api.add_argument('argument', nargs='+', metavar='ARG', help='\
format:\n\
set [ name1=tcp://ip:port name2=tcp://ip:port ... ]\n\
get [ name1 name2 ... | all | current ]\n\
unset [ name1 name2 ... | all | current ]\n\
use name1\n\
version [ x.xx | auto ]')
        parser_api.set_defaults(func=SwarmApi())
        parser_api.set_defaults(cmd='api')

    def _add_parser_version(self):
        parser_version = self._subparsers.add_parser('version', description=self._help['version'],\
help=self._help['version'], usage=self._usage['version'])
        parser_version.set_defaults(func=Version())
        parser_version.set_defaults(cmd='version')

    def _add_parser_info(self):
        parser_info = self._subparsers.add_parser('info', description=self._help['info'],\
help=self._help['info'], usage=self._usage['info'])
        parser_info.set_defaults(func=Info())
        parser_info.set_defaults(cmd='info')

    def _add_parser_login(self):
        parser_login = self._subparsers.add_parser('login', description=self._help['login'],\
help=self._help['login'], usage=self._usage['login'])
        parser_login.add_argument('-e', '--email', type=str, help='\
Email')
        parser_login.add_argument('-p', '--password', type=str, help='\
Password')
        parser_login.add_argument('-u', '--username', type=str, help='\
Username')
        parser_login.add_argument('SERVER', type=str, nargs='?', help='\
URL to the registry. Ex:https://index.docker.io/v1/')
        parser_login.set_defaults(func=Login())
        parser_login.set_defaults(cmd='login')

    def _add_parser_ps(self):
        parser_ps = self._subparsers.add_parser('ps', description=self._help['ps'],\
help=self._help['ps'], usage=self._usage['ps'], formatter_class=argparse.RawTextHelpFormatter)
        parser_ps.add_argument('-a', '--all', action='store_true', help='\
Show all containers (default shows just running)')
        parser_ps.add_argument('-f', '--filter', action='append', help='\
Filter output based on the conditions provide', metavar='name=value')
        parser_ps.add_argument('-l', '--limit', action='append', metavar='NODE', help='\
Show containers of the specific nodes\n\
e.g. -l web.example.com -l mail.example.com\n\
     -l db[01:08].example.com -l db10.example.com')
        parser_ps.set_defaults(func=Containers())
        parser_ps.set_defaults(cmd='ps')

    def _add_parser_start(self):
        parser_start = self._subparsers.add_parser('start', description=self._help['start'],\
help=self._help['start'], usage=self._usage['start'])
        parser_start.add_argument('CONTAINER', nargs='+', help='\
Container ID')
        parser_start.set_defaults(func=StartContainer())
        parser_start.set_defaults(cmd='start')

    def _add_parser_stop(self):
        parser_stop = self._subparsers.add_parser('stop', description=self._help['stop'],\
help=self._help['stop'], usage=self._usage['stop'])
        parser_stop.add_argument('-t', '--time', type=int, default=10, help='\
Seconds to wait for stop before killing it (Default 10 seconds)')
        parser_stop.add_argument('CONTAINER',nargs='+', help='\
Container ID')
        parser_stop.set_defaults(func=StopContainer())
        parser_stop.set_defaults(cmd='stop')

    def _add_parser_restart(self):
        parser_restart = self._subparsers.add_parser('restart', description=self._help['restart'],\
help=self._help['restart'], usage=self._usage['restart'])
        parser_restart.add_argument('-t', '--time', type=int, default=10, help='\
Seconds to wait for stop before killing it (Default 10 seconds)')
        parser_restart.add_argument('CONTAINER',nargs='+', help='\
Container ID')
        parser_restart.set_defaults(func=RestartContainer())
        parser_restart.set_defaults(cmd='restart')

    def _add_parser_rm(self):
        # add subparser for `swarm rm`
        parser_rm = self._subparsers.add_parser('rm', description=self._help['rm'],\
help=self._help['rm'], usage=self._usage['rm'])
        parser_rm.add_argument('-f', '--force', action='store_true', help='\
Force the removal of a running container (uses SIGKILL)')
        parser_rm.add_argument('-l', '--link', action='store_true', help='\
Remove the specified link')
        parser_rm.add_argument('-v', '--volumes', action='store_true', help='\
Remove the volumes associated with the container')
        parser_rm.add_argument('CONTAINER',nargs='+', help='\
Container ID')
        parser_rm.set_defaults(func=RemoveContainer())
        parser_rm.set_defaults(cmd='rm')

    def _add_parser_run(self):
        parser_run = self._subparsers.add_parser('run', description=self._help['run'],\
help=self._help['run'], usage=self._usage['run'])
        group = parser_run.add_mutually_exclusive_group()
        group.add_argument('-d', '--detach', action='store_true', help='\
Run container in background')
        group.add_argument('--rm', action='store_true', help='\
Automatically remove the container when it exits')
        parser_run.add_argument('--cpuset-cpus', type=str, help='\
CPUs in which to allow execution (0-3, 0,1)')
        parser_run.add_argument('--dns', action='append', help='\
Set custom DNS servers')
        parser_run.add_argument('-e', '--environment', action='append', help='\
Set environment variables')
        parser_run.add_argument('--entrypoint', type=str, help='\
Overwrite the default ENTRYPOINT of the image')
        parser_run.add_argument('--hostname', type=str, help='\
Container host name')
        parser_run.add_argument('-i', '--interactive', action='store_true', help='\
Keep STDIN open even if not attached')
        parser_run.add_argument('-l', '--label', action='append', help='\
Set meta data on a container')
        parser_run.add_argument('--link', action='append', help='\
Add link to another container')
        parser_run.add_argument('--log-driver',type=str,help='\
Logging driver for container')
        parser_run.add_argument('--log-opt',action='append',help='\
Log driver options')
        parser_run.add_argument('-m', '--memory', type=str, help='\
Memory limit')
        parser_run.add_argument('--name', type=str, help='\
Assign a name to the container')
        parser_run.add_argument('--net', type=str, help='\
Set the Network mode for the container')
        parser_run.add_argument('-P', '--publish-all', action='store_true', help='\
Publish all exposed ports to random ports')
        parser_run.add_argument('-p', '--publish', action='append', help='\
Publish a container\'s port(s) to the host')
        parser_run.add_argument('--privileged', action='store_true', help='\
Give extended privileges to this container')
        parser_run.add_argument('--restart', choices=('on-failure', 'always'), help='\
Restart policy to apply when a container exits')
        parser_run.add_argument('-t', '--tty', action='store_true', help='\
Allocate a pseudo-TTY')
        parser_run.add_argument('-u', '--user', type=str, help='\
Username or UID')
        parser_run.add_argument('-v', '--volume', action='append', help='\
Bind mount a volume')
        parser_run.add_argument('--volumes-from', action='append', help='\
Mount volumes from the specified container(s)')
        parser_run.add_argument('IMAGE', type=str, help='\
Image name to run')
        parser_run.add_argument('COMMAND', nargs='?', help='\
The command to be run in the container')
        parser_run.add_argument('ARG', nargs=argparse.REMAINDER, help='\
Command arguments')
        parser_run.set_defaults(func=CreateContainer())
        parser_run.set_defaults(cmd='run')

    def _add_parser_exec(self):
        parser_exec = self._subparsers.add_parser('exec', description=self._help['exec'],\
help=self._help['exec'], usage=self._usage['exec'])
        parser_exec.add_argument('-d', '--detach', action='store_true', help='\
Detached mode: run command in the background')
        parser_exec.add_argument('-i', '--interactive', action='store_true', help='\
Keep STDIN open even if not attached')
        parser_exec.add_argument('-t', '--tty', action='store_true', help='\
Allocate a pseudo-TTY')
        parser_exec.add_argument('-u', '--user', type=str, help='\
Username or UID (format: <name|uid>[:<group|gid>])')
        parser_exec.add_argument('CONTAINER', type=str, help='\
Container ID')
        parser_exec.add_argument('COMMAND', type=str, help='\
Command to be executed')
        parser_exec.add_argument('ARG', nargs=argparse.REMAINDER, help='\
Command arguments')
        parser_exec.set_defaults(func=Exec())
        parser_exec.set_defaults(cmd='exec')

    def _add_parser_top(self):
        parser_top = self._subparsers.add_parser('top', description=self._help['top'],\
help=self._help['top'], usage=self._usage['top'])
        parser_top.add_argument('CONTAINER', type=str, help='\
Container ID')
        parser_top.add_argument('ps_args', nargs='?', metavar='ps OPTIONS', help='\
e.g., aux')
        parser_top.set_defaults(func=Top())
        parser_top.set_defaults(cmd='top')

    def _add_parser_kill(self):
        parser_kill = self._subparsers.add_parser('kill', description=self._help['kill'],\
help=self._help['kill'], usage=self._usage['kill'])
        parser_kill.add_argument('-s', '--signal', help='\
Signal to send to the container (Defaults to SIGKILL')
        parser_kill.add_argument('CONTAINER', nargs='+', help='\
Contaner ID')
        parser_kill.set_defaults(func=Kill())
        parser_kill.set_defaults(cmd='kill')

    def _add_parser_inspect(self):
        parser_inspect = self._subparsers.add_parser('inspect', description=self._help['inspect'],\
help=self._help['inspect'], usage=self._usage['inspect'])
        parser_inspect.add_argument('--type', choices=('image', 'container'), help='\
Return JSON for specified type, (e.g image or container)')
        parser_inspect.add_argument('OBJECT', nargs='+', metavar='CONTAINER|IMAGE', help='\
id or name of container|image')
        parser_inspect.set_defaults(inspect_container=InspectContainer())
        parser_inspect.set_defaults(inspect_image=InspectImage())
        parser_inspect.set_defaults(cmd='inspect')

    def _add_parser_images(self):
        parser_images = self._subparsers.add_parser('images', description=self._help['images'],\
help=self._help['images'], usage=self._usage['images'], formatter_class=argparse.RawTextHelpFormatter)
        parser_images.add_argument('REPOSITORY', nargs='?', default=None, help='\
Only show images belonging to the repository name')
        parser_images.add_argument('-a', '--all', action='store_true', help='\
Show all images (default hides intermediate images)')
        parser_images.add_argument('-f','--filter',type=str, help='\
Filter output based on conditions provided\n\
Use \'[-f|--filter] node=<nodename>\' to show images of the specific node')
        parser_images.set_defaults(func=Images())
        parser_images.set_defaults(cmd='images')

    def _add_parser_rmi(self):
        parser_rmi = self._subparsers.add_parser('rmi', description=self._help['rmi'],\
help=self._help['rmi'], usage=self._usage['rmi'])
        parser_rmi.add_argument('IMAGE', nargs='+', help='\
IMAGE[:TAG]')
        parser_rmi.set_defaults(func=RemoveImage())
        parser_rmi.set_defaults(cmd='rmi')

    def _add_parser_tag(self):
        parser_tag = self._subparsers.add_parser('tag', description=self._help['tag'],\
help=self._help['tag'], usage=self._usage['tag'])
        parser_tag.add_argument('-f', '--force', action='store_true', help='\
Force')
        parser_tag.add_argument('IMAGE', type=str, help='\
IMAGE[:TAG]')
        parser_tag.add_argument('REPOTAG', type=str, help='\
[REGISTRYHOST/][USERNAME/]NAME[:TAG]')
        parser_tag.set_defaults(func=Tag())
        parser_tag.set_defaults(cmd='tag')

    def _add_parser_pull(self):
        parser_pull = self._subparsers.add_parser('pull', description=self._help['pull'],\
help=self._help['pull'], usage=self._usage['pull'])
        parser_pull.add_argument('--insecure', action='store_true', help='\
Use an insecure registry')
        parser_pull.add_argument('--auth', type=str, metavar='username:password', help='\
Override credentials for client login')
        parser_pull.add_argument('REPOTAG', type=str, metavar='NAME[:TAG]', help='\
Image name with optional tag')
        parser_pull.set_defaults(func=Pull())
        parser_pull.set_defaults(cmd='pull')

    def _add_parser_push(self):
        parser_push = self._subparsers.add_parser('push', description=self._help['push'],\
help=self._help['push'], usage=self._usage['push'])
        parser_push.add_argument('--insecure', action='store_true', help='\
Use http:// to connect to the registry')
        parser_push.add_argument('REPOTAG', type=str, metavar='NAME[:TAG]')
        parser_push.set_defaults(func=Push())
        parser_push.set_defaults(cmd='push')

    def _add_parser_build(self):
        parser_build = self._subparsers.add_parser('build', description=self._help['build'],\
help=self._help['build'], usage=self._usage['build'])
        parser_build.add_argument('--build-arg', type=str, action='append', help='\
Set build-time variables')
        parser_build.add_argument('-c', '--cpu-shares', type=int, help='\
CPU shares (relative weight)')
        parser_build.add_argument('--cpuset-cpus', type=str, help='\
CPUs in which to allow execution (0-3, 0,1)')
        parser_build.add_argument('-f', '--file', type=str, help='\
Name of the Dockerfile (Default is \'PATH/Dockerfile\')')
        parser_build.add_argument('--force-rm', action='store_true', help='\
Always remove intermediate containers')
        parser_build.add_argument('-m', '--memory', type=int, help='\
Memory limit')
        parser_build.add_argument('--memory-swap', type=int, help='\
Total memory (memory + swap), \'-1\' to disable swap')
        parser_build.add_argument('--no-cache', action='store_true', help='\
Do not use cache when building the image')
        parser_build.add_argument('--pull', action='store_true', help='\
Always attempt to pull a newer version of the image')
        parser_build.add_argument('-q', '--quiet', action='store_true', help='\
Suppress the verbose output generated by the containers')
        parser_build.add_argument('--rm', choices=(True, False), default=True, help='\
Remove intermediate containers after a successful build')
        parser_build.add_argument('-t', '--tag', type=str, default='latest', help='\
Repository name (and optionally a tag) for the image')
        parser_build.add_argument('PATH', type=str, metavar='PATH | URL | -')
        parser_build.set_defaults(func=Build())
        parser_build.set_defaults(cmd='build')
