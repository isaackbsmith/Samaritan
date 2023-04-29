import json
import numpy as np
from nlp import tokenize, stem, bag_of_words

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, dataset

from model import NeuralNet

with open('intents.json', 'r') as f:
    intents = json.load(f)


all_words = []
groups = []
xy = []

for intent in intents['intents']:
    group = intent['group']
    groups.append(group)
    for pattern in intent['patterns']:
        w = tokenize(pattern)
        all_words.extend(w)
        xy.append((w, group))


# ignore_words = ['?', '!', '.', ',']
all_words = [stem(w) for w in all_words]
all_words = sorted(set(all_words))
groups = sorted(set(groups))


X_train = []
y_train = []

for (pattern_sentence, group) in xy:
    bow = bag_of_words(pattern_sentence, all_words)
    X_train.append(bow)

    label = groups.index(group)
    y_train.append(label)

X_train = np.array(X_train)
y_train = np.array(y_train)


class SkillDataset(Dataset):
    def __init__(self) -> None:
        self.n_samples = len(X_train)
        self.x_data = X_train
        self.y_data = y_train

    def __getitem__(self, index):
        return self.x_data[index], self.y_data[index]

    def __len__(self):
        return self.n_samples

#  Hyperparameters
batch_size = 8
hidden_size = 8
output_size = len(groups)
input_size = len(X_train[0])
learning_rate = 0.001
num_epochs = 1000


dataset = SkillDataset()
trian_loader = DataLoader(dataset=dataset, batch_size=batch_size, shuffle=True, num_workers=0)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model = NeuralNet(input_size, hidden_size, output_size).to(device)

# loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)


for epoch in range(num_epochs):
    for (words, labels) in trian_loader:
        words = words.to(device)
        labels = labels.to(dtype=torch.long).to(device)

        # forward
        outputs = model(words)
        loss = criterion(outputs, labels)

        # backward and optimizer step
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    if (epoch + 1) % 100 == 0:
        print(f'epoch {epoch + 1}/{num_epochs}, loss={loss.item():.4f}')


print(f'final loss, loss={loss.item():.4f}')

data = {
    "model_state": model.state_dict(),
    "input_size": input_size,
    "output_size": output_size,
    "hidden_size": hidden_size,
    "all_words": all_words,
    "groups": groups
}

FILE = "skills.pth"
torch.save(data, FILE)

print(f'training complete. file saved to {FILE}')
