# -*- coding: utf8 -*-

from docker import errors
from datetime import datetime
from base import Docker
from utils import timeformat, byteformat

class Images(object):
    """
    Similar to `docker images`
    """
    def __init__(self):
        self.cli = Docker().client
        self.repo_length = 10    # `REPOSITORY` length
        self.tag_length = 3      # `TAG` length
        self.created_length = 7  # `CREATED` length
        self.images = set()

    def _get_images(self, name=None, show_all=False, filters={}, image_list=None):
        """
        :param name(str): Only show images belonging to the repository name
        :param show_all(bool):  Show all images (by default filter out the intermediate image layers)
        :parma filters(dict): Filters to be processed on the image list
        """
        if self.cli is not None:
            ret = self.cli.images(name=name,all=show_all,filters=filters)
            self.cli.close()
            for image in ret:
                # if image_list provide, then get images by it
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
        self._get_images(name=name,show_all=show_all,filters=filters)
        self._pretty_print()

class Tag(Images):
    """
    Similar to `docker tag`
    """
    def __init__(self):
        super(Tag, self).__init__()

    def __call__(self, image, repo, tag):
        if self.cli is not None:
            try:
                ret = self.cli.tag(image, repo, tag, force=True)
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

class RemoveImage(Images):
    """
    Similar to `docker rmi`
    """
    def __init__(self):
        super(RemoveImage, self).__init__()

    def __call__(self, image_list):
        if self.cli is not None:
            image_error = set()
            for image in image_list:
                try:
                    self.cli.remove_image(image)
                except errors.NotFound as e:
                    print(e.explanation)
                    image_error.add(image)
                except errors.APIError as e:
                    print(e.explanation)
                    image_error.add(image)
                except errors.DockeException as e:
                    print(e.explanation)
                    image_error.add(image)
                finally:
                    self.cli.close()
            # exclude images in image_error
            image_removed = tuple([image for image in image_list\
                                            if not image in image_error])
            self._get_images(image_removed)
            if not self.images and image_removed:
                print('Succeed to remove image {images}'.format(\
                                            images=', '.join(image_removed)))
