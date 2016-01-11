# -*- coding: utf8 -*-

import json
from docker import errors
from datetime import datetime
from base import SwarmClient
from utils import timeformat, byteformat

class Images(object):
    """
    Similar to `docker images`
    """
    def __init__(self):
        self.cli = SwarmClient().client
        self.repo_length = len('REPOSITORY')
        self.tag_length = len('TAG')
        self.created_length = len('CREATED')
        self.images = set()

    def _get_images(self, name=None, show_all=False, filters={}, image_list=None):
        """
        :param name(str): Only show images belonging to the repository name
        :param show_all(bool):  Show all images (by default filter out the intermediate image layers)
        :parma filters(dict): Filters to be processed on the image list
        :param image_list(list): List of image id or name
        """
        try:
            ret = self.cli.images(name=name,all=show_all,filters=filters)
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
            for image in ret:
                # if image_list provide, then get images against it
                if image_list is not None:
                    if not image['Id'].startswith(image_list) and\
                      not image['RepoTags'].startswith(image_list):
                        continue
                image_id = image['Id'][:12]
                # convert created timestamp to human-readable string
                created_delta = datetime.now() - datetime.fromtimestamp(image['Created'])
                if created_delta.days > 1:
                    created = '{day} days ago'.format(day=created_delta.days)
                else:
                    created = timeformat(created_delta.seconds + created_delta.days * 86400)
                # convert virtual size to human-readable string
                virtual_size = byteformat(image['VirtualSize'],base=1000)
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
            title = 'REPOSITORY{s1}TAG{s2}IMAGE ID{s3}CREATED{s4}VIRTUAL SIZE'.format(\
                                                                                s1=s1,\
                                                                                s2=s2,\
                                                                                s3=s3,\
                                                                                s4=s4)
            # pretty-print string defined by title
            string = ''
            for node in self.images:
                repo, tag, image_id, created, virtual_size = node
                s1 = ' ' * (self.repo_length+blank-len(repo))
                s2 = ' ' * (self.tag_length+blank-len(tag))
                s3 = ' ' * blank
                s4 = ' ' * (self.created_length+blank-len(created))
                string += '{repo}{s1}{tag}{s2}{image_id}{s3}{created}{s4}{virtual_size}\n'.format(\
                                                                                        repo=repo,\
                                                                                        s1=s1,\
                                                                                        tag=tag,\
                                                                                        s2=s2,\
                                                                                        image_id=image_id,\
                                                                                        s3=s3,\
                                                                                        created=created,\
                                                                                        s4=s4,\
                                                                                        virtual_size=virtual_size)
            # print pretty-print string
            print('{title}\n{string}'.format(title=title,string=string.rstrip()))

    def __call__(self, name=None, show_all=False, filters={}):
        if self.cli is not None:
            self._get_images(name=name,show_all=show_all,filters=filters)
            self._pretty_print()

class RemoveImage(Images):
    """
    Similar to `docker rmi`
    """
    def __init__(self):
        super(RemoveImage, self).__init__()

    def __call__(self, image_list):
        if self.cli is not None:
            images_err = set()
            for image in image_list:
                try:
                    self.cli.remove_image(image)
                except errors.NotFound as e:
                    print(e.explanation)
                    images_err.add(image)
                except errors.APIError as e:
                    print(e.explanation)
                    images_err.add(image)
                except errors.DockeException as e:
                    print(e.explanation)
                    images_err.add(image)
            # exclude images in image_error
            images_removed = tuple((image for image in image_list\
                                            if not image in images_err))
            self._get_images(images_removed)

            if not self.images and images_removed:
                print('Succeed to remove image {images}'.format(\
                                            images=', '.join(images_removed)))
            self.cli.close()

class Tag(Images):
    """
    Similar to `docker tag`
    """
    def __init__(self):
        super(Tag, self).__init__()

    def __call__(self, image, repo, tag, force):
        """
        :param image(str): The image to tag
        :param repo(str): The repository to set for the tag
        :param tag(str): The tag name
        :param force(bool): Force
        """
        if self.cli is not None:
            try:
                ret = self.cli.tag(image, repo, tag, force)
            except errors.NotFound as e:
                print(e.explanation)
            except errors.APIError as e:
                print(e.explanation)
            except errors.DockeException as e:
                print(e.explanation)
            finally:
                self.cli.close()
            status = 'Succeed' if ret else 'Fail'
            print('{status} to tag {image} into {repo}:{tag}'.format(\
                                                            status=status,\
                                                            image=image,\
                                                            repo=repo,\
                                                            tag=tag))

class InspectImage(Images):
    """
    Similar to `docker inspect`, but only for images
    """
    def __init__(self):
        super(InspectImage, self).__init__()

    def __call__(self, image_list):
        """
        :param image_list(list): List of image id or names
        """
        if self.cli is not None:
            ret = []
            for image in image_list:
                try:
                    ret.append(self.cli.inspect_image(image))
                except errors.NotFound as e:
                    print(e.explanation)
                except errors.APIError as e:
                    print(e.explanation)
                except errors.DockerException as e:
                    print(e.explanation)
            self.cli.close()
            return ret if ret else None

class Pull(Images):
    """
    Similar to `docker pull`
    """
    def __init__(self):
        super(Pull, self).__init__()

    def __call__(self, repo, tag, insecure_registry, auth_config):
        """
        :param repo(str): The repository to pull
        :param tag(str): The tag to pull
        :param insecure_registry(bool): Use an insecure registry
        :param auth_config(dict):  Override the credentials that Client.login has set for this request auth_config should contain the username and password keys to be valid
        """
        if self.cli is not None:
            try:
                for line in self.cli.pull(repo, tag=tag, stream=True,\
                                        insecure_registry=insecure_registry,\
                                        auth_config=auth_config):
                    ret = json.loads(line)
                    print('[{id}] {status}'.format(id=ret['id'],\
                                                  status=ret['status']))
            except errors.NotFound as e:
                print(e.explanation)
            except errors.APIError as e:
                print(e.explanation)
            except errors.DockerException as e:
                print(e.explanation)
            finally:
                self.cli.close()
