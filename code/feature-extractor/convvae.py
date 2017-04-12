import torch 
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.autograd import Variable


class ConvVAE(nn.Module):
    def __init__(self):
        super(ConvVAE, self).__init__()
        self.latent_vars = 150
        
        self.fc11 = nn.Linear(64*32*32, 300)
        self.fc12 = nn.Linear(128, 64)
        
        
        self.conv1 = nn.Conv2d(3, 16, 2, 2, 1, 1, 1, 1)
        self.conv2 = nn.Conv2d(16, 32, 2, 2, 1, 1, 1, 1)
        self.conv3 = nn.Conv2d(32, 64, 2, 2, 1, 1, 1, 1)
    
        self.dconv1 = nn.ConvTranspose2d(64, 32,2,2,1,1, 1,1)
        self.dconv2 = nn.ConvTranspose2d(32, 16,2,2,1,1)
        self.dconv3 = nn.ConvTranspose2d(16, 3,2,2)
	self.dconv4 = nn.ConvTranspose2d(3, 3,2,2)

        
        
        self.bn1 = nn.BatchNorm2d(16)
        self.bn2 = nn.BatchNorm2d(32)
	self.bn3 = nn.BatchNorm2d(3)
        
        self.fc3 = nn.Linear(150,  64*32*32)
        
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()


    def encode(self, x):
        x = self.relu(self.bn1(self.conv1(x)))
        x = F.max_pool2d(x, 2, 2)
        x = self.relu(self.bn2(self.conv2(x)))
        x = self.relu(self.conv3(x))
        x = x.view(-1, 64*32*32)
        z = self.fc11(x)
        mu = z[:, 0:self.latent_vars]
        log_sig = z[:, self.latent_vars:]
        return mu, log_sig

    def reparametrize(self, mu, logvar):
        eps = Variable(torch.randn(logvar.size()))
        z = mu + torch.exp(logvar / 2) * eps        
        return z

    def decode(self, x):
	x = F.relu(self.fc3(x))
        x = x.view(-1, 64, 32,32)
	x = self.relu(self.bn2(F.max_pool2d(self.dconv1(x), 1,1)))
        x = self.relu(self.bn1(self.dconv2(x)))
        x = self.relu(self.bn3(self.dconv3(x)))
        x = self.dconv4(x)
	return self.sigmoid(x)

    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparametrize(mu, logvar)
        return self.decode(z), mu, logvar

model = ConvVAE()
input = Variable(torch.Tensor(64,3,500,500))
output, _, _ = model(input)
print("Output size",  output.size())


