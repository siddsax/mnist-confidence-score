import torch
import torchvision
#import matplotlib.pyplot as plt
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import argparse
import os
import numpy as np

from utils import *
from classifier import *

parser = argparse.ArgumentParser()
parser.add_argument('--n_epochs', type=int, default=100)
parser.add_argument('--logInt', type=int, default=10)
parser.add_argument('--momentum', type=float, default=.5)
parser.add_argument('--lr', type=float, default=1e-2)
parser.add_argument('--batchSize', type=int, default=64)
parser.add_argument('--dataPath', type=str, default="data")
parser.add_argument('--msp', dest = 'modelStorePath', type=str, default="savedModels")

args = parser.parse_args()
print(args)

random_seed = 1
torch.manual_seed(random_seed)

if not os.path.exists(args.modelStorePath):
    os.makedirs(args.modelStorePath)

train_loader, test_loader = getData(args)

network = Net()
optimizer = optim.SGD(network.parameters(), lr=args.lr, momentum=args.momentum)

train_losses, train_counter, test_losses, test_counter = [], [], [], []


def train(epoch):
  network.train()
  for batch_idx, (data, target) in enumerate(train_loader):

    output = network(data)
    loss = F.nll_loss(output, target)
    loss.backward()
    optimizer.step()
    optimizer.zero_grad()

    if batch_idx % args.logInt == 0:
      prettyPrint(epoch, batch_idx, len(data), train_loader, loss.item())
      train_losses.append(loss.item())
      train_counter.append((batch_idx*args.batchSize) + ((epoch-1)*len(train_loader)))

def test(epoch):
  network.eval()
  test_loss, correct, outputAll, targetAll = 0, 0, [], []
  with torch.no_grad():
    for data, target in test_loader:
      output = network(data)
      test_loss += F.nll_loss(output, target, size_average=False).item()
      pred = output.data.max(1, keepdim=True)[1]
      correct += pred.eq(target.data.view_as(pred)).sum()

      outputAll.append(predHot(output))
      targetAll.append(np.eye(10)[target.data.cpu().numpy()])

  test_loss /= len(test_loader.dataset)
  prettyPrint2(test_loss, correct, len(test_loader.dataset), np.concatenate(outputAll, axis=0), np.concatenate(targetAll, axis=0))
  test_losses.append(test_loss)
  test_counter.append(epoch*len(train_loader.dataset))

for epoch in range(1, args.n_epochs + 1):
  train(epoch)
  test(epoch)
  #genMyPlots(train_losses, test_losses, train_counter, test_counter)

