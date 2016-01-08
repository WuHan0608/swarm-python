# -*- coding: utf8 -*-

import json

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
        return '{t} {u}{s} ago'.format(t=time,u=unit,s=suffix)
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