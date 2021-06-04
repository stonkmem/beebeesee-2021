# FACE

![logo](assets/logo.png?raw=true)

- **F**ace-recognition
- **A**I for
- **C**ommunicating
- **E**motions

This is an AI Project for visual sentiment analysis based on audiences' **Face**.

This application will be an indispensable tool for movie-makers *FACE*ing problems with getting honest feedback about thier productions through text.
With **FACE**, they will be able to view thier audience's audiences reactions and will get essential information to improve thier movie production, using deep learning!


## Our Idea
The theme we have chosen is “Inspired by Hollywood”. This project aims to enable our program to detect the target's feelings, and gauge their satisfaction when watching a film. This will allow the film directors to know how the audience is taking the film. For example, when watching a film, a director can quickly know the audience's engagement and feeling. This allows him to be able to see how his or her film is in the eyes of the audience. With this program, through facial expressions, the director can quickly receive feedback, allowing for more accurate and quick feedback on the emotional rollercoaster that the audience is in. With our Face-recognition AI for Communicating Emotions (FACE), you will never have to FACE this problem again!


## To Run
To run, please run `face-tkinter/main.py` using the python interpreter.

```sh
pip install -r requirements.txt
```

### Options

```sh
python facetk/main.py
```

or

```sh
py facetk/main.py
```

or

```sh
/path/to/python/interpreter/python.exe facetk/main.py
```



## But How does it work?
We are using a Tensorflow Convolutional Neural Network with labels for the emotions.

## Trained Model Details
 - Convolutional Neural Network
 - 20 epochs with 448 steps per epoch
 - training accuracy: 0.8702
 - validation accuracy: 0.6283


## Technical Specifics
## Clone with

```bash
git clone git@github.com:RenoirTan/beebeesee-2021.git
```

## Setup using

**NOTE: Dlib uses a lot of resources for compilation and might crash your computer.**

### Unix (SU)

```bash
bash ./setup.sh
```

### Windows (SU)

```shell
./setup.cmd
```

## Running the website in debug mode

### Unix (RWDM)

```bash
bash ./debug.sh
```

### Windows (RWDM)

```shell
./debug.cmd
```
