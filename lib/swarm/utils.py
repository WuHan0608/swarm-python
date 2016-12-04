# -*- coding: utf8 -*-

import json
import string


def byteformat(size, base=1024, unit='B'):
    """
    Convert byte to KiB / MiB / GiB / TiB if possible
    """
    units = ('B', 'KB', 'MB', 'GB', 'TB')
    if size < base:
        return '{s:.2f} {u}'.format(s=size,u=unit)
    return byteformat(size/float(base), base, units[units.index(unit)+1])


def timeformat(time, unit='second'):
    """
    Convert second to minute / hour if possible
    """
    units = ('second', 'minute', 'hour')
    if time < 60:
        suffix = 's' if time > 1 else ''
        return '{t:.0f} {u}{s} ago'.format(t=time,u=unit,s=suffix)
    return timeformat(time/60, units[units.index(unit)+1])


def base_url_found(config):
    try:
        with open(config, 'r') as fp:
            data = json.load(fp)
        try:
            if data['apis'][data['current']]:
                return True
        except KeyError:
            return False
    except IOError:
        return False


def current_url_found(config):
    try:
        with open(config, 'r') as fp:
            data = json.load(fp)
        try:
            if data['current']:
                return True
        except KeyError:
            return False
    except IOError:
        return False


# The following helper functions are copied from Ansible.
# Thanks the ansible team for the awesome codes.
# Now range such as db[01:10].example.com is avaliable.
def detect_range(line = None):
    '''
    A helper function that checks a given host line to see if it contains
    a range pattern described in the docstring above.

    Returnes True if the given line contains a pattern, else False.
    '''
    if '[' in line:
        return True
    else:
        return False


def expand_hostname_range(line = None):
    '''
    A helper function that expands a given line that contains a pattern
    specified in top docstring, and returns a list that consists of the
    expanded version.

    The '[' and ']' characters are used to maintain the pseudo-code
    appearance. They are replaced in this function with '|' to ease
    string splitting.

    References: http://ansible.github.com/patterns.html#hosts-and-groups
    '''
    all_hosts = []
    if line:
        # A hostname such as db[1:6]-node is considered to consists
        # three parts:
        # head: 'db'
        # nrange: [1:6]; range() is a built-in. Can't use the name
        # tail: '-node'

        # Add support for multiple ranges in a host so:
        # db[01:10:3]node-[01:10]
        # - to do this we split off at the first [...] set, getting the list
        #   of hosts and then repeat until none left.
        # - also add an optional third parameter which contains the step. (Default: 1)
        #   so range can be [01:10:2] -> 01 03 05 07 09

        (head, nrange, tail) = line.replace('[','|',1).replace(']','|',1).split('|')
        bounds = nrange.split(":")
        if len(bounds) != 2 and len(bounds) != 3:
            raise ValueError("host range must be begin:end or begin:end:step")
        beg = bounds[0]
        end = bounds[1]
        if len(bounds) == 2:
            step = 1
        else:
            step = bounds[2]
        if not beg:
            beg = "0"
        if not end:
            raise ValueError("host range must specify end value")
        if beg[0] == '0' and len(beg) > 1:
            rlen = len(beg) # range length formatting hint
            if rlen != len(end):
                raise ValueError("host range must specify equal-length begin and end formats")
            fill = lambda _: str(_).zfill(rlen)  # range sequence
        else:
            fill = str

        try:
            i_beg = string.ascii_letters.index(beg)
            i_end = string.ascii_letters.index(end)
            if i_beg > i_end:
                raise ValueError("host range must have begin <= end")
            seq = list(string.ascii_letters[i_beg:i_end+1:int(step)])
        except ValueError:  # not an alpha range
            seq = range(int(beg), int(end)+1, int(step))

        for rseq in seq:
            hname = ''.join((head, fill(rseq), tail))

            if detect_range(hname):
                all_hosts.extend( expand_hostname_range( hname ) )
            else:
                all_hosts.append(hname)

        return all_hosts
