import torch
import torch.nn as nn
from importlib.resources import files

class Block(nn.Module):
    def __init__(self, c_in, c_out, pool=True):
        super().__init__()
        self.conva = nn.Conv2d(c_in, c_in, 1, padding=0)
        self.conv  = nn.Conv2d(c_in, c_out, 3, padding=1)
        self.bn    = nn.BatchNorm2d(c_out)
        self.relu  = nn.ReLU()
        self.pool  = nn.MaxPool2d(2,2) if pool else None

    def forward(self, x):
        x = self.conva(x)
        x = self.conv(x)
        x = self.bn(x)
        x = self.relu(x)
        return self.pool(x) if self.pool else x

class FaseNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1   = nn.Conv2d(3,64,7,stride=2,padding=3)
        self.pool    = nn.MaxPool2d(3,2,padding=1)
        self.bn1     = nn.BatchNorm2d(64)
        self.relu    = nn.ReLU()
        self.block2  = Block(64, 192)
        self.block3  = Block(192,384)
        self.block4  = Block(384,256, pool=False)
        self.block5  = Block(256,256, pool=False)
        self.block6  = Block(256,256, pool=False)
        self.linear1 = nn.Linear(50176,128)
        self.linear2 = nn.Linear(128,128)

    def forward(self, x):
        x = self.conv1(x); x = self.pool(x)
        x = self.bn1(x);   x = self.relu(x)
        x = self.block2(x); x = self.block3(x)
        x = self.block4(x); x = self.block5(x); x = self.block6(x)
        x = torch.flatten(x,1)
        x = self.linear1(x); return self.linear2(x)


def getFaseNet():
    model = FaseNet()
    weight_path = files('cat_feeder').joinpath('weight.pt')
    model.load_state_dict(torch.load(weight_path, map_location='cpu', weights_only=True))
    
    return model
