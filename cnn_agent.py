import random
from collections import deque

from keras.models import Sequential
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import Dense
from skimage.transform import resize
from skimage.color import rgb2grey
from skimage.exposure import rescale_intensity
from skimage import data
from skimage.viewer import ImageViewer
from agent import Agent
import numpy as np

batch_size = 3


class CnnAgent(Agent):

    def __init__(self, action_space, state_space, **kwargs):
        super().__init__(action_space, state_space)
        self.name          = kwargs.get("name", "agent snake")
        self.model         = create_model(self.state_space)
        self.mem_capacity  = kwargs.get("mem_capacity", 1000)
        self.memory        = deque(maxlen=kwargs.get("mem_capacity", 1000))
        self.learning_rate = kwargs.get("learning_rate", 0.01)
        self.epsilon       = kwargs.get("epsilon", 0.99)
        self.epsilon_decay = kwargs.get("epsilon_decay", 0.99)
        self.epsilon_min   = kwargs.get("epsilon_min", 0.005)
        self.gamma         = kwargs.get("gamma", 0.99)


    def store_memory(self, state, action, reward, next_state, done):
        state = preprocess_image(state)
        next_state = preprocess_image(next_state)
        self.memory.append((state, action, reward, next_state, done))
        print("reward - " + str(reward))


    def learn(self):

        if len(self.memory) < batch_size:
            return

        sample = random.sample(self.memory, batch_size)

        for memory in sample:
            state, action, reward, next_state, done = memory

            q_value = reward

            curr_preds = self.model.predict(state)[0]
            curr_value = curr_preds[self.action_space.index(action)]

            next_state_preds = self.model.predict(next_state)[0]
            if done:
                updated_value = q_value

            else:
                s1_max_ind = np.argmax(next_state_preds)
                updated_value = curr_value
                updated_value = updated_value + self.gamma * (next_state_preds[s1_max_ind] - updated_value)

            updated_values = curr_preds
            updated_values[self.action_space.index(action)] = updated_value
            self.model.fit(state, updated_values.reshape((1, 4)), epochs=1, verbose=0)

    def act(self, state):
        state = preprocess_image(state)

        if np.random.rand() < self.epsilon:
            action_index = random.randrange(len(self.action_space))
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay
            return self.action_space[action_index]
        else:
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay

            q_reward = self.model.predict(state)
            max_q = np.argmax(q_reward)
            return self.action_space[max_q]


def create_model(img_sample):
    global agent
    img_sample = preprocess_image(img_sample)
    img_sample = np.array(img_sample)
    img_sample = np.reshape(img_sample, (80, 80, 1))

    return build_cnn(img_sample.shape)


def preprocess_image(img):
    img = rgb2grey(img)
    img = resize(img, (80, 80))
    img = np.reshape(img, (1, 80, 80, 1))
    return img


def build_cnn(shape):
    model = Sequential()
    model.add(Conv2D(filters=32, kernel_size=(8, 8), input_shape=(shape), activation='relu'))
    model.add(Flatten())

    model.add(Dense(units=42, activation='relu'))
    model.add(Dense(units=16, activation='relu'))

    model.add(Dense(4, activation='linear'))

    model.compile(optimizer='adam', loss='mse', metrics=['accuracy'])
    return model
