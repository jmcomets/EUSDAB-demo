# -*- coding: utf-8 -*-

def enum(*sequential, **named):
    """Enumerated type constructor, found on SO."""
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)
