from libhpman.m import _


def add():
    return _("a", 1) + _("b", 2)


def mult():
    return _("a") * _("b")
