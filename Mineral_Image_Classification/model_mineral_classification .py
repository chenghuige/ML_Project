from google.colab import drive
drive.mount('/content/drive') #to load model.state_dict()

import torch
import torch.nn as nn
from torchvision import transforms
import numpy as np
from PIL import Image
import requests
from io import BytesIO
import matplotlib.pyplot as plt

#only predict for this classes
target_label = ['biotite', 'bornite', 'chrysocolla', 'malachite', 
                'muscovite', 'pyrite', 'quartz']

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class Mineral_1(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(3, 48, 11, stride=3, padding=0),
            nn.ReLU(),
            nn.MaxPool2d(3, 1), #out 70x70

            nn.Conv2d(48, 128, 5, stride=1, padding=0),
            nn.ReLU(),
            nn.MaxPool2d(3, 1),#out 64x64

            nn.Conv2d(128, 128, 4, stride=1, padding=0),
            nn.ReLU(),
            nn.MaxPool2d(4, 3),#out 20x20

            nn.Conv2d(128, 64, 3, stride=1, padding=0),
            nn.ReLU(),
            nn.MaxPool2d(3, 3),#out 20x20

            nn.Flatten(),
            nn.Linear(64*6*6, 512),
            nn.ReLU(),
            nn.Dropout(p=0.3),
            nn.Linear(512, 7),
            nn.LogSoftmax(dim=1),
            )
        
    def forward(self, x):
        out = self.net(x)
        return out


def load_model(fpath):
    check = torch.load(fpath)
    model = check['model']
    model.load_state_dict(check['state_dict'])
   
    return model

def predict_img(model, image):
    model.eval()
    model.to(device)

    imsize = (224, 224)
    loader = transforms.Compose([transforms.Resize(imsize), 
                                 transforms.ToTensor(),
                                 transforms.Normalize(mean = [0.485, 0.456, 0.406],
                                                      std = [0.229, 0.224, 0.225])])
    image = loader(image)
    image = image.unsqueeze(0) 
    
    image = image.to(device); 
    out = model(image)
    ps = torch.exp(out)
    _, top_class = torch.max(ps , 1)
    preds = np.squeeze(top_class.cpu().numpy())

    return target_label[preds]

#load trained model
model_mineral = load_model('/content/drive/My Drive/Colab Notebooks/mineral/minet/mineral_seq_own.pth') #model file
model_vgg = load_model('/content/drive/My Drive/Colab Notebooks/mineral/minet/mineral_vgg.pth') #model file

#input picture has to be at least 224x224 to avoid size mismatch
url = input('picture link:')
response = requests.get(url)
img = Image.open(BytesIO(response.content))
plt.axis('off')
plt.imshow(img)

#print prediction
print('Predicted label VGG Model: ', predict_img(model_vgg, img)) #vgg pretrained
print('Predicted label My Model: ', predict_img(model_mineral, img)) #my model