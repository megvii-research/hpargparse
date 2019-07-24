from hpman.m import _

# for more usecases, please refer to hpman's document


def add():
    # define a hyperparameter on-the-fly with defaults
    return _("a", 1) + _("b", 2)


def mult():
    # reuse a pre-defined hyperparameters
    return _("a") * _("b")
