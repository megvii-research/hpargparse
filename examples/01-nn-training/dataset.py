from torchvision.datasets import MNIST
import torch
import functools
import numpy as np


@functools.lru_cache(maxsize=2)
def get_mnist_dataset(train):
    return MNIST("../data", train=train, download=True)


def get_data_and_labels(dataset_type):
    """
    :param dataset_type: train or test
    :return: a dict of
        {
            'data': X,
            'labels': Y,
        }
    """
    mnist = get_mnist_dataset(dataset_type == "train")  # False for test dataet

    X = mnist.data
    Y = mnist.targets

    X = X.reshape(-1, 1, 28, 28)
    return {"data": X, "labels": Y}


def iter_dataset_batch(rng, dct, batch_size, loop=False, cuda=False):
    """
    :param rng: random number generator, a np.random.RandomState object
    :param dct: data dict. values must be torch tensors
    :param batch_size: batch size
    :param loop: whether to loop forever
    :param cuda: whether to use cuda tensor
    """

    # sanity check
    assert len(dct) > 0, len(dct)

    n = None
    for k, v in dct.items():
        assert isinstance(v, torch.Tensor), type(v)
        if n is None:
            n = v.shape[0]
        else:
            assert v.shape[0] == n, (n, v.shape)

    idx = np.arange(n)

    def run():
        rng.shuffle(idx)

        for i in range(0, n, batch_size):
            j = min(n, i + batch_size)
            mb = {k: v[idx[i:j]] for k, v in dct.items()}
            if cuda:
                mb = {k: v.cuda() for k, v in mb.items()}
            yield mb

    if loop:
        while True:
            yield from run()
    else:
        yield from run()
