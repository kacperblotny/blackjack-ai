#from multiprocessing.dummy import active_children
import numpy as np
import keras
import tensorflow as tf


def initAI():
  # import danych
  punktyGracza = open('./data/base/punktyGracza.txt').readlines()
  punktyKrupiera = open('./data/base/punktyKrupiera.txt').readlines()
  ruchyGracza = open('./data/base/ruchyGracza.txt').readlines()

  listaPunktyGracza = []
  listaPunktyKrupiera = []
  listaRuchyGracza = []

  punkty = []
  ruchy = []
  
  
  for i in range(len(punktyGracza)):
    listaPunktyGracza.append(punktyGracza[i].rstrip())

  for i in range(len(punktyKrupiera)):
    listaPunktyKrupiera.append(punktyKrupiera[i].rstrip())

  for i in range(len(ruchyGracza)):
    listaRuchyGracza.append(ruchyGracza[i].rstrip())


  # czyszczenie danych
  for i in range(len(punktyGracza)):
    rozdzielonePunktyGracza = punktyGracza[i].split(' ')
    rozdzielonePunktyKrupiera = punktyKrupiera[i].split(' ')

    for j in range(len(rozdzielonePunktyGracza)-2):
      punkty.append([int(rozdzielonePunktyGracza[j].strip()), int(rozdzielonePunktyKrupiera[j].strip())])

  for i in range(len(listaRuchyGracza)):
    rozdzieloneRuchy = listaRuchyGracza[i].split(' ')
    for ruch in rozdzieloneRuchy:
      if ruch.strip() == 'H':
        ruchy.append([1.0])
      else:
        ruchy.append([0.0])

  # podział na listy testowe i ćwiczeniowe
  size = int(len(punktyGracza) * (0.75))


  train_punkty = np.array( punkty[1:size] )
  train_ruchy = np.array( ruchy[1:size] )
  test_punkty = np.array( punkty[size:] )
  test_ruchy = np.array( ruchy[size:] )

  # Sieć neuronowa
  model = keras.Sequential()
  model.add( keras.layers.Dense(16, input_dim=2) )
  model.add( keras.layers.Dense(2, activation=tf.nn.softmax) )
  model.compile(optimizer='nadam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy'])
  model.fit(train_punkty, train_ruchy, epochs=100)
  test_loss, test_acc = model.evaluate(test_punkty, test_ruchy)
  print('Test accuracy:', test_acc)


  model_json = model.to_json()
  with open('./models/blackjackmodel.json', 'w') as json_file:
    json_file.write(model_json)
  model.save_weights("./weights/blackjackmodel.h5")
  print( "Model saved" )
  
  json_file = open('./models/blackjackmodel.json', 'r')
  loaded_model_json = json_file.read()
  json_file.close()
  model = keras.models.model_from_json( loaded_model_json, custom_objects={"GlorotUniform": tf.keras.initializers.glorot_uniform} )
  model.load_weights( "./weights/blackjackmodel.h5" )
  print( "Model loaded from disk" )
  return model



