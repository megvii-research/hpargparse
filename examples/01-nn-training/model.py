import torch
from torch import nn
from torch.nn import functional as F
from hpman.m import _


class EnsureFloat(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, x):
        return x.float()


class GlobalAveragePooling(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, x):
        assert len(x.shape) == 4, x.shape
        h, w = x.shape[2], x.shape[3]
        v = F.avg_pool2d(x, (h, w))
        return v.reshape(v.shape[:2])


def ConvBNReLU(in_channels, out_channels, *args, **kwargs):
    return nn.Sequential(
        nn.Conv2d(in_channels, out_channels, *args, **kwargs),
        nn.BatchNorm2d(out_channels),
        nn.ReLU(inplace=True),
    )


def get_model():
    base_channel = _("base_channel", 32)  # <-- hyperparameter
    in_channels = 1  # _('input_channels', 1)

    return nn.Sequential(
        EnsureFloat(),
        ConvBNReLU(in_channels, base_channel, 3, stride=2, padding=1),
        ConvBNReLU(base_channel, base_channel * 2, 3, stride=2, padding=1),
        ConvBNReLU(base_channel * 2, base_channel * 4, 3, stride=2, padding=1),
        GlobalAveragePooling(),
        nn.Linear(base_channel * 4, 10),
    )


def compute_loss(y_pred, y_gt):
    return F.cross_entropy(y_pred, y_gt)


def compute_metrics(y_pred, y_gt):
    return {
        "misclassify": (y_pred.argmax(dim=1) != y_gt)
        .detach()
        .float()
        .mean()
        .cpu()
        .numpy()
    }
