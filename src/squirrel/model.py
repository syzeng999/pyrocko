from __future__ import absolute_import, print_function

import numpy as num

from pyrocko import util
from pyrocko.guts import Object, String, Timestamp, Float, Int, Unicode
from pyrocko.guts_array import Array

separator = '\t'

g_content_kinds = [
    'undefined',
    'waveform',
    'station',
    'channel',
    'response',
    'event']

g_content_kind_ids = (
    UNDEFINED, WAVEFORM, STATION, CHANNEL, RESPONSE, EVENT) = range(
        len(g_content_kinds))

g_tmin = int(util.str_to_time('1900-01-01 00:00:00'))
g_tmax = int(util.str_to_time('2100-01-01 00:00:00'))


def to_kind(kind_id):
    return g_content_kinds[kind_id]


def to_kinds(kind_ids):
    return [g_content_kinds[kind_id] for kind_id in kind_ids]


def to_kind_id(kind):
    return g_content_kinds.index(kind)


def to_kind_ids(kinds):
    return [g_content_kinds.index(kind) for kind in kinds]


def str_or_none(x):
    if x is None:
        return None
    else:
        return str(x)


def float_or_none(x):
    if x is None:
        return None
    else:
        return float(x)


def int_or_none(x):
    if x is None:
        return None
    else:
        return int(x)


def int_or_g_tmin(x):
    if x is None:
        return g_tmin
    else:
        return int(x)


def int_or_g_tmax(x):
    if x is None:
        return g_tmax
    else:
        return int(x)


def tsplit(t):
    if t is None:
        return None, 0.0

    seconds = num.floor(t)
    offset = t - seconds
    return int(seconds), float(offset)


def tjoin(seconds, offset, deltat):
    if seconds is None:
        return None

    if deltat is not None and deltat < 1e-3:
        return util.hpfloat(seconds) + util.hpfloat(offset)
    else:
        return seconds + offset


tscale_min = 1
tscale_max = 365 * 24 * 3600  # last edge is one above
tscale_logbase = 20

tscale_edges = [tscale_min]
while True:
    tscale_edges.append(tscale_edges[-1]*tscale_logbase)
    if tscale_edges[-1] >= tscale_max:
        break


tscale_edges = num.array(tscale_edges)


def tscale_to_kscale(tscale):

    # 0 <= x < tscale_edges[1]: 0
    # tscale_edges[1] <= x < tscale_edges[2]: 1
    # ...
    # tscale_edges[len(tscale_edges)-1] <= x: len(tscale_edges)

    return int(num.searchsorted(tscale_edges, tscale))


class Content(Object):
    '''
    Base class for content types in the Squirrel framework.
    '''

    @property
    def scodes(self):
        return '.'.join(self.codes)


class Waveform(Content):
    '''
    A continuous seismic waveform snippet.
    '''

    agency = String.T(default='', help='Agency code (2-5)')
    network = String.T(default='', help='Deployment/network code (1-8)')
    station = String.T(default='', help='Station code (1-5)')
    location = String.T(default='', help='Location code (0-2)')
    channel = String.T(default='', help='Channel code (3)')
    extra = String.T(default='', help='Extra/custom code')

    tmin = Timestamp.T()
    tmax = Timestamp.T()

    deltat = Float.T(optional=True)

    data = Array.T(
        shape=(None,),
        dtype=num.float32,
        serialize_as='base64',
        serialize_dtype=num.dtype('<f4'),
        help='numpy array with data samples')

    @property
    def codes(self):
        return (
            self.agency, self.network, self.station, self.location,
            self.channel, self.extra)


class Station(Content):
    '''
    A seismic station.
    '''

    agency = String.T(default='', help='Agency code (2-5)')
    network = String.T(default='', help='Deployment/network code (1-8)')
    station = String.T(default='', help='Station code (1-5)')
    location = String.T(default='', optional=True, help='Location code (0-2)')

    tmin = Timestamp.T(optional=True)
    tmax = Timestamp.T(optional=True)

    lat = Float.T()
    lon = Float.T()
    elevation = Float.T(optional=True)
    depth = Float.T(optional=True)

    description = Unicode.T(optional=True)

    @property
    def codes(self):
        return (self.agency, self.network, self.station, self.location)

    def get_pyrocko_station(self):
        from pyrocko import model
        return model.Station(
            network=self.network,
            station=self.station,
            location=self.location,
            lat=self.lat,
            lon=self.lon,
            elevation=self.elevation,
            depth=self.depth)


class Channel(Content):
    '''
    A channel of a seismic station.
    '''

    agency = String.T(default='', help='Agency code (2-5)')
    network = String.T(default='', help='Deployment/network code (1-8)')
    station = String.T(default='', help='Station code (1-5)')
    location = String.T(default='', help='Location code (0-2)')
    channel = String.T(default='', help='Channel code (3)')

    tmin = Timestamp.T(optional=True)
    tmax = Timestamp.T(optional=True)

    lat = Float.T()
    lon = Float.T()
    elevation = Float.T(optional=True)
    depth = Float.T(optional=True)

    dip = Float.T(optional=True)
    azimuth = Float.T(optional=True)
    deltat = Float.T(optional=True)

    @property
    def codes(self):
        return (
            self.agency, self.network, self.station, self.location,
            self.channel)

    def get_pyrocko_channel(self):
        from pyrocko import model
        return model.Channel(
            name=self.channel,
            azimuth=self.azimuth,
            dip=self.dip)


class Response(Content):
    '''
    The instrument response of a seismic station channel.
    '''

    pass


class Event(Content):
    '''
    A seismic event.
    '''

    name = String.T(optional=True)
    time = Timestamp.T()
    duration = Float.T(optional=True)

    lat = Float.T()
    lon = Float.T()
    elevation = Float.T(optional=True)
    depth = Float.T(optional=True)

    magnitude = Float.T(optional=True)


class Nut(Object):
    '''Container for elementary content meta-information.

    So-called *nuts* are used in Pyrocko's Squirrel framework to hold common
    meta-information about individual pieces of waveforms, stations, channels,
    etc. together with the information where it was found or generated.
    '''

    file_path = String.T(optional=True)
    file_format = String.T(optional=True)
    file_mtime = Timestamp.T(optional=True)
    file_size = Int.T(optional=True)

    file_segment = Int.T(optional=True)
    file_element = Int.T(optional=True)

    kind_id = Int.T()
    codes = String.T()

    tmin_seconds = Timestamp.T()
    tmin_offset = Float.T(default=0.0, optional=True)
    tmax_seconds = Timestamp.T()
    tmax_offset = Float.T(default=0.0, optional=True)

    deltat = Float.T(optional=True)

    content = Content.T(optional=True)

    content_in_db = False

    def __init__(
            self,
            file_path=None,
            file_format=None,
            file_mtime=None,
            file_size=None,
            file_segment=None,
            file_element=None,
            kind_id=0,
            codes='',
            tmin_seconds=None,
            tmin_offset=0.0,
            tmax_seconds=None,
            tmax_offset=0.0,
            deltat=None,
            content=None,
            tmin=None,
            tmax=None,
            values_nocheck=None):

        if values_nocheck is not None:
            (self.file_path, self.file_format, self.file_mtime, self.file_size,
             self.file_segment, self.file_element,
             self.kind_id, self.codes,
             self.tmin_seconds, self.tmin_offset,
             self.tmax_seconds, self.tmax_offset,
             self.deltat) = values_nocheck

            self.content = None
        else:
            if tmin is not None:
                tmin_seconds, tmin_offset = tsplit(tmin)

            if tmax is not None:
                tmax_seconds, tmax_offset = tsplit(tmax)

            self.kind_id = int(kind_id)
            self.codes = str(codes)
            self.tmin_seconds = int_or_g_tmin(tmin_seconds)
            self.tmin_offset = float(tmin_offset)
            self.tmax_seconds = int_or_g_tmax(tmax_seconds)
            self.tmax_offset = float(tmax_offset)
            self.deltat = float_or_none(deltat)
            self.file_path = str_or_none(file_path)
            self.file_segment = int_or_none(file_segment)
            self.file_element = int_or_none(file_element)
            self.file_format = str_or_none(file_format)
            self.file_mtime = float_or_none(file_mtime)
            self.file_size = int_or_none(file_size)
            self.content = content

        Object.__init__(self, init_props=False)

    def __eq__(self, other):
        return (isinstance(other, Nut) and
                self.equality_values == other.equality_values)

    def __ne__(self, other):
        return not (self == other)

    def get_io_backend(self):
        from . import io
        return io.get_backend(self.file_format)

    def file_modified(self):
        return self.get_io_backend().get_stats(self.file_path) \
            != (self.file_mtime, self.file_size)

    @property
    def key(self):
        return (
            self.file_path,
            self.file_segment,
            self.file_element,
            self.file_mtime)

    @property
    def equality_values(self):
        return (
            self.file_segment, self.file_element,
            self.kind_id, self.codes,
            self.tmin_seconds, self.tmin_offset,
            self.tmax_seconds, self.tmax_offset, self.deltat)

    @property
    def tmin(self):
        return tjoin(self.tmin_seconds, self.tmin_offset, self.deltat)

    @property
    def tmax(self):
        return tjoin(self.tmax_seconds, self.tmax_offset, self.deltat)

    @property
    def kscale(self):
        if self.tmin_seconds is None or self.tmax_seconds is None:
            return 0
        return tscale_to_kscale(self.tmax_seconds - self.tmin_seconds)

    @property
    def waveform_kwargs(self):
        agency, network, station, location, channel, extra = \
            self.codes.split(separator)

        return dict(
            agency=agency,
            network=network,
            station=station,
            location=location,
            channel=channel,
            extra=extra,
            tmin=self.tmin,
            tmax=self.tmax,
            deltat=self.deltat)

    @property
    def station_kwargs(self):
        agency, network, station, location = self.codes.split(separator)
        return dict(
            agency=agency,
            network=network,
            station=station,
            location=location,
            tmin=self.tmin,
            tmax=self.tmax)

    @property
    def channel_kwargs(self):
        agency, network, station, location, channel \
            = self.codes.split(separator)

        return dict(
            agency=agency,
            network=network,
            station=station,
            location=location,
            channel=channel,
            tmin=self.tmin,
            tmax=self.tmax,
            deltat=self.deltat)

    @property
    def event_kwargs(self):
        return dict(
            name=self.codes,
            time=self.tmin,
            duration=(self.tmax - self.tmin) or None)


def make_waveform_nut(
        agency='', network='', station='', location='', channel='', extra='',
        **kwargs):

    codes = separator.join(
        (agency, network, station, location, channel, extra))

    return Nut(
        kind_id=WAVEFORM,
        codes=codes,
        **kwargs)


def make_station_nut(
        agency='', network='', station='', location='', **kwargs):

    codes = separator.join((agency, network, station, location))

    return Nut(
        kind_id=STATION,
        codes=codes,
        **kwargs)


def make_channel_nut(
        agency='', network='', station='', location='', channel='', **kwargs):

    codes = separator.join((agency, network, station, location, channel))

    return Nut(
        kind_id=CHANNEL,
        codes=codes,
        **kwargs)


def make_event_nut(name='', **kwargs):

    codes = name

    return Nut(
        kind_id=EVENT, codes=codes,
        **kwargs)


def group_channels(nuts):
    by_ansl = {}
    for nut in nuts:
        if nut.kind_id != CHANNEL:
            continue

        ansl = nut.codes[:4]

        if ansl not in by_ansl:
            by_ansl[ansl] = {}

        group = by_ansl[ansl]

        k = nut.codes[4][:-1], nut.deltat, nut.tmin, nut.tmax

        if k not in group:
            group[k] = set()

        group.add(nut.codes[4])

    return by_ansl


__all__ = [
    'to_kind',
    'to_kinds',
    'to_kind_id',
    'to_kind_ids',
    'Content',
    'Waveform',
    'Station',
    'Channel',
    'Nut',
]
