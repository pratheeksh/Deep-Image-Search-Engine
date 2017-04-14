import torch
import torch.nn as nn
from torchvision import models

# From https://discuss.pytorch.org/t/how-to-extract-features-of-an-image-from-a-trained-model/119/3
def load_model():
    model = models.alexnet(pretrained=True)
    # remove last fully-connected layer
    new_classifier = nn.Sequential(*list(model.classifier.children())[:-1])
    model.classifier = new_classifier
    model = model.float()
    print(model)
    return model