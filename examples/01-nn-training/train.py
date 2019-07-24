#!/usr/bin/env python3
from tqdm import tqdm
import functools
import numpy as np
import argparse
import torch
import yaml
import os
from torch import optim

from hpman.m import _
import hpargparse


BASE_DIR = os.path.dirname(os.path.realpath(__file__))


def main():
    parser = argparse.ArgumentParser()
    _.parse_file(BASE_DIR)
    hpargparse.bind(parser, _)
    parser.parse_args()  # we need not to use args

    # print all hyperparameters
    print("-" * 10 + " Hyperparameters " + "-" * 10)
    print(yaml.dump(_.get_values()))

    optimizer_cls = {
        "adam": optim.Adam,
        "sgd": functools.partial(optim.SGD, momentum=0.9),
    }[
        _("optimizer", "adam")  # <-- hyperparameter
    ]

    import model

    net = model.get_model()
    if torch.cuda.is_available():
        net.cuda()

    optimizer = optimizer_cls(
        net.parameters(),
        lr=_("learning_rate", 1e-3),  # <-- hyperparameter
        weight_decay=_("weight_decay", 1e-5),  # <-- hyperparameter
    )

    import dataset

    train_ds = dataset.get_data_and_labels("train")
    test_ds = dataset.get_data_and_labels("test")
    if torch.cuda.is_available():
        # since mnist is a small dataset, we store the test dataset all in the
        # gpu memory
        test_ds = {k: v.cuda() for k, v in test_ds.items()}

    rng = np.random.RandomState(_("seed", 42))  # <-- hyperparameter

    for epoch in range(_("num_epochs", 30)):  # <-- hyperparameter
        net.train()
        tq = tqdm(
            enumerate(
                dataset.iter_dataset_batch(
                    rng,
                    train_ds,
                    _("batch_size", 256),  # <-- hyperparameter
                    cuda=torch.cuda.is_available(),
                )
            )
        )
        for step, minibatch in tq:
            optimizer.zero_grad()

            Y_pred = net(minibatch["data"])
            loss = model.compute_loss(Y_pred, minibatch["labels"])

            loss.backward()
            optimizer.step()

            metrics = model.compute_metrics(Y_pred, minibatch["labels"])
            metrics["loss"] = loss.detach().cpu().numpy()
            tq.desc = "e:{} s:{} {}".format(
                epoch,
                step,
                " ".join(["{}:{}".format(k, v) for k, v in sorted(metrics.items())]),
            )

        net.eval()

        # since mnist is a small dataset, we predict all values at once.
        Y_pred = net(test_ds["data"])
        metrics = model.compute_metrics(Y_pred, test_ds["labels"])
        print(
            "eval: {}".format(
                " ".join(["{}:{}".format(k, v) for k, v in sorted(metrics.items())])
            )
        )

        # Save the model. We intentionally not saving the model here for
        # tidiness of the example
        # torch.save(net, "model.pt")


if __name__ == "__main__":
    main()
