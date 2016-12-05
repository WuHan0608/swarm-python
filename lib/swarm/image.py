# -*- coding: utf8 -*-

from __future__ import print_function
from sys import stdout
from docker import errors
from datetime import datetime
from swarm.client import SwarmClient
from swarm.utils import timeformat, byteformat, pyprint


class Images(object):

    def __init__(self):
        self.swarm = SwarmClient()
        self.repo_length = len('REPOSITORY')
        self.tag_length = len('TAG')
        self.created_length = len('CREATED')
        self.images = set()

    def _get_images(self, name=None, show_all=False, filters={}, image_list=None):
        """
        :param name(str): Only show images belonging to the repository name
        :param show_all(bool):  Show all images (by default filter out the intermediate image layers)
        :parma filters(dict): Filters to be applied on the image list
        :param image_list(list): List of image id or name
        """
        cli = self.swarm.client
        if cli is not None:
            try:
                ret = cli.images(name=name,all=show_all,filters=filters)
            except (errors.NotFound, errors.APIError, errors.DockerException) as e:
                pyprint(e.explanation)
                return
            finally:
                cli.close()
            if ret:
                for image in ret:
                    # if image_list provide, then get images against it
                    if image_list is not None:
                        if not image['Id'].startswith(image_list)\
                          and not image['RepoTags'].startswith(image_list):
                            continue
                    image_id = image['Id'][:12]
                    # convert created timestamp to human-readable string
                    created_delta = datetime.now() - datetime.fromtimestamp(image['Created'])
                    if created_delta.days > 1:
                        created = '{day} days ago'.format(day=created_delta.days)
                    else:
                        created = timeformat(created_delta.seconds + created_delta.days * 86400)
                    # convert virtual size to human-readable string
                    virtual_size = byteformat(image['VirtualSize'], base=1000)
                    # get the longest created field length for pretty print
                    self.created_length = len(created) if len(created) > self.created_length\
                                                       else self.created_length
                    for repotag in image['RepoTags']:
                        repo, tag = repotag.split(':')
                        data = (repo, tag, image_id, created, virtual_size)
                        self.images.add(data)
                        # get the longest repo/tag field length for pretty print
                        self.repo_length = len(repo) if len(repo) > self.repo_length else self.repo_length
                        self.tag_length = len(tag) if len(tag) > self.tag_length else self.tag_length
 
    def _pretty_print(self):
        if self.images:
            blank = 4
            # title: CONTAINER ID    NODE    CREATED    STATUS    NAMES
            s1 = ' ' * (self.repo_length+blank-len('REPOSITORY'))
            s2 = ' ' * (self.tag_length+blank-len('TAG'))
            s3 = ' ' * (blank+4)
            s4 = ' ' * (self.created_length+blank-len('CREATED'))
            title = 'REPOSITORY{s1}TAG{s2}IMAGE ID{s3}CREATED{s4}VIRTUAL SIZE'.format(s1=s1,
                                                                                      s2=s2,
                                                                                      s3=s3,
                                                                                      s4=s4)
            # pretty-print string defined by title
            string = ''
            for node in self.images:
                repo, tag, image_id, created, virtual_size = node
                s1 = ' ' * (self.repo_length+blank-len(repo))
                s2 = ' ' * (self.tag_length+blank-len(tag))
                s3 = ' ' * blank
                s4 = ' ' * (self.created_length+blank-len(created))
                string += '{repo}{s1}{tag}{s2}{image_id}{s3}{created}{s4}{virtual_size}\n'.format(repo=repo,
                                                                                                  s1=s1,
                                                                                                  tag=tag,
                                                                                                  s2=s2,
                                                                                                  image_id=image_id,
                                                                                                  s3=s3,
                                                                                                  created=created,
                                                                                                  s4=s4,
                                                                                                  virtual_size=virtual_size)
            # print pretty-print string
            print('{title}\n{string}'.format(title=title,string=string.rstrip()))

    def __call__(self, **kwargs):
        self._get_images(**kwargs)
        self._pretty_print()


class RemoveImage(Images):

    def __init__(self):
        super(RemoveImage, self).__init__()

    def __call__(self, image_list):
        """
        :param image_list(list): List of image id or name
        """
        cli = self.swarm.client
        if cli is not None:
            images_err = set()
            for image in image_list:
                try:
                    cli.remove_image(image)
                except (errors.NotFound, errors.APIError, errors.DockerException) as e:
                    pyprint(e.explanation)
                    images_err.add(image)
            cli.close()
            # exclude images in image_error
            images_removed = tuple((image for image in image_list if not image in images_err))
            if images_removed:
                print('Succeed to remove image {images}'.format(images=', '.join(images_removed)))


class Tag(Images):

    def __init__(self):
        super(Tag, self).__init__()

    def __call__(self, *args, **kwargs):
        """
        :param image(str): The image to tag
        :param repo(str): The repository to set for the tag
        :param tag(str): The tag name
        :param force(bool): Force
        """
        cli = self.swarm.client
        if cli is not None:
            ret = None
            try:
                ret = cli.tag(*args, **kwargs)
            except (errors.NotFound, errors.APIError, errors.DockerException) as e:
                pyprint(e.explanation)
            finally:
                cli.close()
            if ret is not None:
                status = 'Succeed' if ret else 'Fail'
                image, repo = args
                tag = kwargs['tag'] if kwargs.get('tag') is not None else 'latest'
                print('{status} to tag {image} into {repo}:{tag}'.format(status=status,
                                                                         image=image,
                                                                         repo=repo,
                                                                         tag=tag))


class InspectImage(Images):

    def __init__(self):
        super(InspectImage, self).__init__()

    def __call__(self, image_list):
        """
        :param image_list(list): List of image id or name
        """
        cli = self.swarm.client
        if cli is not None:
            ret = []
            for image in image_list:
                try:
                    ret.append(cli.inspect_image(image))
                except (errors.NotFound, errors.APIError, errors.DockerException):
                    pass
            cli.close()
            return ret if ret else None


class Pull(Images):

    def __init__(self):
        super(Pull, self).__init__()

    def __call__(self, *args, **kwargs):
        """
        :param repo(str): The repository to pull
        :param tag(str): The tag to pull
        :param insecure_registry(bool): Use an insecure registry
        :param auth_config(dict):  Override the credentials that Client.login has set for this request \
auth_config should contain the username and password keys to be valid
        """
        cli = self.swarm.client
        if cli is not None:
            try:
                kwargs['stream'] = True
                kwargs['decode'] = True
                for line in cli.pull(*args, **kwargs):
                    if line.get('id') is not None:
                        print('[{id}] {status}'.format(id=line['id'], status=line['status']))
                    elif line.get('error') is not None:
                        print(line['error'])
            except (errors.NotFound, errors.APIError, errors.DockerException) as e:
                pyprint(e.explanation)
            finally:
                cli.close()


class Push(Images):

    def __init__(self):
        super(Push, self).__init__()

    def _display(self, msg):
        endl = ''
        if msg.get("progressDetail") is not None:
            # <ESC>[2K = erase entire current line
            print('{esc:c}[2K\r'.format(esc=27), end='')
            endl = '\r'
        if msg.get('id'):
            print('{id}: '.format(id=msg['id']), end='')
        if msg.get('progressDetail') is not None:
            progress = msg['progress'] if msg['progressDetail'] else ''
            print('{status} {progress}'.format(status=msg['status'],progress=progress), end=endl)
        else:
            print('{status}{endl}'.format(status=msg['status'],endl=endl))
        stdout.flush() # flush stdout otherwise display may be broken

    def _display_JSONMessages(self, stream):
        ids = {}  # map[string]int
        for msg in stream:
            #print('<' + repr(msg) + '>')
            #continue
            if msg.get('aux') is not None:
                continue
            diff = 0
            if msg.get('id'): #and msg.get('progress') is not None:
                line = ids.get(msg['id'])
                if line is None:
                    line = len(ids)
                    ids[msg['id']] = line
                    print()
                diff = len(ids) - line
                if diff > 0:
                    print('{esc:c}[{row:d}A'.format(esc=27,row=diff), end='')
            else:
                ids = {}
            self._display(msg)
            if msg.get('id') and diff > 0:
                print('{esc:c}[{row:d}B'.format(esc=27,row=diff), end='')

    def __call__(self, *args, **kwargs):
        """
        :param repo(str): The repository to push to
        :param tag(str): An optional tag to push
        :param insecure_registry(bool): Use http:// to connect to the registry
        """
        cli = self.swarm.client
        if cli is not None:
            kwargs['stream'] = True
            kwargs['decode'] = True
            try:
                self._display_JSONMessages(cli.push(*args, **kwargs))
            except (errors.NotFound, errors.APIError, errors.DockerException) as e:
                pyprint(e.explanation)
            finally:
                cli.close()


class Build(Images):

    def __init__(self):
        super(Build, self).__init__()

    def __call__(self, **kwargs):
        cli = self.swarm.client
        if cli is not None:
            try:
                for line in cli.build(**kwargs):
                    if line.get('stream') is not None:
                        print(line['stream']),
                    elif line.get('error') is not None:
                        print(line['error'])
                    stdout.flush()
            except (errors.NotFound, errors.APIError, errors.DockerException) as e:
                pyprint(e.explanation)
            except TypeError as e:
                pyprint(e)
            finally:
                cli.close()
