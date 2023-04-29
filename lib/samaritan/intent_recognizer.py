import os
import torch
from lib.samaritan.intent_neuralnet import NeuralNet
from lib.samaritan.nlp_toolkit import bag_of_words, tokenize


class IntentRecognizer:

    def __init__(self, base_dir) -> None:
        self.base_dir = base_dir
        self._device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")
        self._model_path = self.base_dir.joinpath('intel/skills/skills.pth')
        self._intents_path = self.base_dir.joinpath(
            'intel/skills/intents.json')
        self._data = torch.load(self._model_path)
        self._model_state = self._data["model_state"]
        self._input_size = self._data["input_size"]
        self._hidden_size = self._data["hidden_size"]
        self._output_size = self._data["output_size"]
        self._all_words = self._data["all_words"]
        self._groups = self._data["groups"]
        self._model = NeuralNet(
            self._input_size, self._hidden_size, self._output_size).to(self._device)
        self._model.load_state_dict(self._model_state)
        self._model.eval()

    def evaluate(self, text: str):
        words = tokenize(text)
        X = bag_of_words(words, self._all_words)
        X = X.reshape(1, X.shape[0])
        X = torch.from_numpy(X)
        result = self._model(X)
        _, predicted = torch.max(result, dim=1)
        group = self._groups[predicted.item()]

        # Calcluate the probability of the result
        prob = torch.softmax(result, dim=1)
        prob = prob[0][predicted.item()]
        return prob, group
