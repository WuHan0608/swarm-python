# -*- coding: utf8 -*-

def byteformat(size, unit='B'):
    """
    Convert byte to KiB / MiB / GiB / TiB if possible
    """
    units = ('B', 'KiB', 'MiB', 'GiB', 'TiB')
    if size < 1024:
        return '{s:.2f} {u}'.format(s=size,u=unit)
    return byteformat(size/1024.0, units[units.index(unit)+1])

def timeformat(time, unit='second'):
    """
    Convert second to minute / hour if possible
    """
    units = ('second', 'minute', 'hour')
    if time < 60:
        suffix = 's' if time > 1 else ''
        return '{t} {u}{s} ago'.format(t=time,u=unit,s=suffix)
    return timeformat(time/60, units[units.index(unit)+1])