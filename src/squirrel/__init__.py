'''Prompt seismological data access with a fluffy tail.

Usage
-----

.. code::

    from pyrocko import squirrel as psq

    sq = psq.Squirrel()
    sq.add(files)


Concepts
--------

* squirrel
* nut
* database

Reference
---------
'''

from __future__ import absolute_import, print_function


from . import base, model, io

from .base import *  # noqa
from .model import *  # noqa
from .io import *  # noqa
from .client import *  # noqa

__all__ = base.__all__ + model.__all__ + io.__all__ + client.__all__
