# Samaritan: Arthur Claypool's vision

---

Samaritan is a python-based artificially intelligent agent inspired by The Machine and Samaritan From Person of Interest.

The system consists of two main files; the `Samaritan.py` file, which serves as the 'brian' of the system, and the `Athena.py` file, which is the proxy through which the user communicated with the 'brain'.

## Features

The 'brain' is where the heavy processing and deep learning models are used. It uses PyTorch for intent recognition.

The proxy/client Uses the Vosk speech recognition models and the Pvporcupine wakeword detection engine.

Communication between the two systems is achieved through message passing using RabbitMQ.

## Installation

1. Install RabbitMQ for your operating system.
2. Download a vosk speech recognition model [here](https://alphacephei.com/vosk/models).
3. Extract the model and place it in `skills/model` directory.

```
git clone https://github.com/Isaac-Smith-369/Samaritan.git

cd Samaritan

pip install -r requirements.txt
```

## Contributing

Contributions for improving Samaritan is welcome. To get started, simply fork the repository, make your changes, and submit a pull request.

## Contact

If you have any questions or concerns about Samaritan, please feel free to contact me at `isaack.bsmith@gmail.com`.

## Reddit

[r/PersonOfInterest](https://www.reddit.com/r/PersonOfInterest/)

> Looking forward to your contributions!
