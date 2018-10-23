# -*- coding: utf-8 -*-
"""keras cbow

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1bcGEl24veoNgjlo-wV9cv8O1G7W8G5NA
"""

# IMPORTS AND PREPARATION
#!pip install -U -q PyDrive
#from pydrive.auth import GoogleAuth
#from pydrive.drive import GoogleDrive
#from google.colab import auth, files
#from oauth2client.client import GoogleCredentials
import pandas as pd

# Authenticate and create the PyDrive client.
#def authenticate():
#    auth.authenticate_user()
#    gauth = GoogleAuth()
#    gauth.credentials = GoogleCredentials.get_application_default()
#    return GoogleDrive(gauth)

#drive = authenticate()

# Load the dataset as .csv
#download = drive.CreateFile({'id': '1MSwZRm3toMCyNrOQ0HbqIhCO1_eYUl5N'})
#download.GetContentFile('dataset.csv')

df = pd.read_csv('COMBINED dataset.csv', index_col=None)
NUM_SENTENCES = len(df['0'])
sentences = df['0'].astype(str)

import string
translation = str.maketrans(string.ascii_letters, string.ascii_letters, string.digits)

f = lambda x : x.translate(translation)
sentences = sentences.apply(f)

def raw_words(corpus):
  stop_words = ['is','a', 'will', 'be']
  words = []
  for sentence in corpus:
    sentence = sentence.split()
    words.extend(sentence)
  words =set(words)
  for stop in stop_words:
    if stop in words:
      words.remove(stop)
  words = list(words)
  wordToint = {}
  for (index,word) in enumerate(words):
    wordToint[word] = index
    
  return wordToint

wordToint = raw_words(sentences)
NUM_OF_WORDS = len(wordToint)

NUM_OF_WORDS

def remove_stop_words(corpus):
  stop_words = ['is','a', 'will', 'be']
  clean_data = []
  for sentence in corpus: 
    sen = sentence.split()
    for word in stop_words:
        while word in sen:
          sen.remove(word)
      
    clean_data.append(sen)
  return clean_data

def generate_data(sentences):
  data = []
  for sentence in sentences:
    for i in range(2, len(sentence) - 2):
      try:
        context = [wordToint[sentence[i - 2]], wordToint[sentence[i - 1]],  wordToint[sentence[i + 1]],  wordToint[sentence[i + 2]]]
        target = wordToint[sentence[i]]
        data.append((context, target))
      except:
        print(sentence)
      
  return data

VOCAB_SIZE = len(wordToint)
NUM_LABELS = 2
EMDEDDING_DIM = 24

sentences = remove_stop_words(sentences)
data  = generate_data(sentences)

import numpy as np

data  = generate_data(sentences)
data  =np.array(data)

x = [context for (context,target) in data]
y = [target for (context,target) in data]
x = np.array(x)
y = np.array(y)

from keras.models import Sequential
from keras.layers import Embedding,Lambda
from keras.layers import Dense, Activation, Flatten
from keras.utils import np_utils
from keras import optimizers
from keras import backend as K

x = x[0:-1:4]
y = y[0:-1:4]

dim_embedddings = 8
model = Sequential()
model.add(Embedding(VOCAB_SIZE,dim_embedddings , input_shape=(4,)))
model.add(Lambda(lambda x : K.sum(x,axis=1),output_shape=(dim_embedddings,)))
model.add(Dense(VOCAB_SIZE,activation='softmax'))

opt = optimizers.Adam(lr=0.1)

model.compile(optimizer=opt,
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.summary()

model.fit(x,y,epochs=500, batch_size=1024)

f = open('vectors.txt' ,'w')
f.write('{} {}\n'.format(NUM_OF_WORDS, dim_embedddings))
vectors = model.get_weights()[0]
for word, i in wordToint.items():
    f.write('{} {}\n'.format(word, ' '.join(map(str, list(vectors[i, :])))))
f.close()

#!pip install gensim
import gensim
w2v = gensim.models.KeyedVectors.load_word2vec_format('./vectors.txt', binary=False)

files.download("vectors.txt")

w2v.similar_by_vector("la")
