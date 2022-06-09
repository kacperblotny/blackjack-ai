from pydoc import doc
import random
from multiprocessing.dummy import active_children
from turtle import end_fill
import numpy as np
import keras
import tensorflow as tf

from AI import initAI

for i in range(400):
    try:
        json_file = open('./models/blackjackmodel.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        model = keras.models.model_from_json( loaded_model_json, custom_objects={"GlorotUniform": tf.keras.initializers.glorot_uniform} )
        model.load_weights( "./weights/blackjackmodel.h5" )
        print( "Model loaded from disk" )
    except:
        model = initAI()

    wyniki = []

    punktyGracza = open('./data/punktyGracza.txt', 'a')
    punktyKrupiera = open('./data/punktyKrupiera.txt', 'a')
    ruchyGracza = open('./data/ruchyGracza.txt', 'a')
    wr = open('./data/wr.txt', 'r')
    lastWR = wr.readlines()
    tab = []
    for k in range(len(lastWR)):
        tab.append(float(lastWR[k].rstrip()))
    lastWR = max(tab)
    wr.close()
    wr = open('./data/wr.txt', 'a')

    # Definicja klasy karty
    class Card:
        def __init__(self, color, value, card_value):

            # Kolor (pik, kier, trefl, karo)
            self.color = color
    
            # Oznaczenie karty, np A dla asa
            self.value = value
    
            # Wartość karty, np 10 dla króla
            self.card_value = card_value

    # Rodzaje kolorów
    colors = ["Pik", "Kier", "Trefl", "Karo"]
    
    # Znaki kolorów
    colors_values = {"Pik":"\u2664", "Kier":"\u2661", "Trefl": "\u2667", "Karo": "\u2662"}

    # Rodzaje kart
    cards = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    
    # Wartości kart
    cards_values = {"A": 11, "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "10":10, "J":10, "Q":10, "K":10}


    # Funkcja do wyświetlania kart
    def print_cards(cards, player, score):
        if player == "gracz":
            print("KARTY GRACZA (", score,"): ", end='')
        else:
            print("KARTY KRUPIERA (", score,"): ", end='')

        for card in cards:
            print("[",card.value, card.color,"]", end='')
        print("")

    # Funkcja pojedynczej gry
    def blackjack_game():

        pG, pK, rG = [], [], []

        print("\n-------------------------- Nowa gra! --------------------------\n")
    
        global cards_values, deck
    
        player_cards = []
        dealer_cards = []
    
        player_score = 0
        dealer_score = 0

        # Rozdawanie kart krupierowi i graczowi
        while len(player_cards) < 2:
            # Gracz
            player_card = random.choice(deck)
            player_cards.append(player_card)
            deck.remove(player_card)
        
            player_score += player_card.card_value
        
            # Jeśli as
            if len(player_cards) == 2:
                if player_cards[0].card_value == 11 and player_cards[1].card_value == 11:
                    player_cards[0].card_value = 1
                    player_score -= 10
        
            # Krupier
            dealer_card = random.choice(deck)
            dealer_cards.append(dealer_card)
            deck.remove(dealer_card)
        
            dealer_score += dealer_card.card_value
        
            # Jeśli as
            if len(dealer_cards) == 2:
                if dealer_cards[0].card_value == 11 and dealer_cards[1].card_value == 11:
                    dealer_cards[1].card_value = 1
                    dealer_score -= 10
        
        # Wyświetlenie kart 
        print_cards(player_cards, "gracz", player_score)

        # Nie wyswietlaj uykrytej karty dla standa
        print("KARTY KRUPIERA (", dealer_score - dealer_cards[-1].card_value,"): ", end='')
        for card in dealer_cards[:-1]:
            print("[",card.value, card.color,"]", end='')
        print("")

        # Jeśli blackjack 
        if player_score == 21:
            wyniki.append('W')
            return None

        pG.append(str(player_score))
        pK.append(str(dealer_score - dealer_cards[-1].card_value))


        # Ruch gracza
        while player_score < 21:
            prediction = model.predict( np.array([ [player_score, dealer_score - dealer_cards[-1].card_value] ]) )
            if prediction[0][0] > prediction[0][1]:
                choice = 'S'
            else:
                choice = 'H'
            # Poprawność danych
            if len(choice) != 1 or (choice.upper() != 'H' and choice.upper() != 'S'):
                print("Wrong choice!! Try Again")
        
            rG.append(choice)
            # Hit
            if choice.upper() == 'H':
                player_card = random.choice(deck)
                player_cards.append(player_card)
                deck.remove(player_card)
        
                player_score += player_card.card_value
        
                # Jeśli jest as
                c = 0
                while player_score > 21 and c < len(player_cards):
                    if player_cards[c].card_value == 11:
                        player_cards[c].card_value = 1
                        player_score -= 10
                        c += 1
                    else:
                        c += 1 
            
                print_cards(player_cards, "gracz", player_score)
                print("KARTY KRUPIERA (", dealer_score - dealer_cards[-1].card_value,"): ", end='')
                for card in dealer_cards[:-1]:
                    print("[",card.value, card.color,"]", end='')
                print("")
                pG.append(str(player_score))
                pK.append(str(dealer_score - dealer_cards[-1].card_value))

            # Stand
            if choice.upper() == 'S':
                print_cards(player_cards, "gracz", player_score)
                print_cards(dealer_cards, "krupier", dealer_score)
                print("")
                pG.append(str(player_score))
                pK.append(str(dealer_score - dealer_cards[-1].card_value))
                break
                
        # Blackjack
        if player_score == 21:
            print("_______________________ Gracz wygrywa _______________________\n")
            for l in range(len(rG)):
                punktyGracza.write(str(pG[l]) + ' ')
                punktyKrupiera.write(str(pK[l]) + ' ')
                ruchyGracza.write(str(rG[l]) + ' ')
            if len(pG) > 0:
                punktyGracza.write('\n')
                punktyKrupiera.write('\n')
                ruchyGracza.write('\n')

            wyniki.append('W')
            return None
        
        # Jeśli bust
        if player_score > 21:
            print("______________________ Krupier wygrywa ______________________\n")
            wyniki.append('L')
            return None

        # Ruch krupiera
        #input()
        while dealer_score < 17:
        
            dealer_card = random.choice(deck)
            dealer_cards.append(dealer_card)
            deck.remove(dealer_card)
        

            dealer_score += dealer_card.card_value
        
            # Jeśli as
            c = 0
            while dealer_score > 21 and c < len(dealer_cards):
                if dealer_cards[c].card_value == 11:
                    dealer_cards[c].card_value = 1
                    dealer_score -= 10
                    c += 1
                else:
                    c += 1

            print_cards(player_cards, "gracz", player_score)
            print_cards(dealer_cards, "krupier", dealer_score)
            print("")

        # Bust krupiera
        if dealer_score > 21:        
            print("_______________________ Gracz wygrywa _______________________\n")
            for l in range(len(rG)):
                punktyGracza.write(str(pG[l]) + ' ')
                punktyKrupiera.write(str(pK[l]) + ' ')
                ruchyGracza.write(str(rG[l]) + ' ')
            if len(pG) > 0:
                punktyGracza.write('\n')
                punktyKrupiera.write('\n')
                ruchyGracza.write('\n')
            
                wyniki.append('W')
            return None
        
        # Blackjack krupiera
        if dealer_score == 21:
            print("______________________ Krupier wygrywa ______________________\n")
            wyniki.append('L')
            return None
        
        # Push
        if dealer_score == player_score:
            print("__________________________ Remis __________________________ \n")
            wyniki.append('D')
            return None
        
        # Gracz wygrywa
        elif player_score > dealer_score:
            print("_______________________ Gracz wygrywa _______________________\n")
            for l in range(len(rG)):
                punktyGracza.write(str(pG[l]) + ' ')
                punktyKrupiera.write(str(pK[l]) + ' ')
                ruchyGracza.write(str(rG[l]) + ' ')
            if len(pG) > 0:
                punktyGracza.write('\n')
                punktyKrupiera.write('\n')
                ruchyGracza.write('\n')
            
                wyniki.append('W')
            return None            
        
        # Krupier wygrywa
        else:
            print("______________________ Krupier wygrywa ______________________\n")
            wyniki.append('L')
            return None
        
        
    roundsLimiter = 0
    roundsLimitedTo = 25

    while roundsLimiter<roundsLimitedTo: 
        deck = []

        for color in colors:
            for card in cards:
                deck.append(Card(colors_values[color], card, cards_values[card]))
        blackjack_game()
        roundsLimiter += 1
    
    rozegraneGry = open('./data/gamesPlayed.txt', 'r')
    lengthOfGamesPlayedFile = len(rozegraneGry.readlines())
    rozegraneGry = open('./data/gamesPlayed.txt', 'a')
    x = lengthOfGamesPlayedFile*roundsLimitedTo
    rozegraneGry.write(str(x) + "\n")

    rozegraneGry.close()
    punktyGracza.close()
    punktyKrupiera.close()
    ruchyGracza.close()

    #clear()
    print("Zagrano ", roundsLimiter, " gier.")
    print(f'Wygrano: {wyniki.count("W")}')
    print(f'Przegrano: {wyniki.count("L")}')
    print(f'Zremisowano: {wyniki.count("D")}')
    wr.write(str(wyniki.count('W') / roundsLimiter) + '\n')
    if wyniki.count('W') / roundsLimiter > lastWR:

        model_json = model.to_json()
        with open('./models/blackjackmodel.json', 'w') as json_file:
            json_file.write(model_json)
        model.save_weights("./weights/blackjackmodel.h5")
        print( "Model saved" )
    
    
    else:
        punktyGracza = open('./data/punktyGracza.txt').readlines()
        punktyKrupiera = open('./data/punktyKrupiera.txt').readlines()
        ruchyGracza = open('./data/ruchyGracza.txt').readlines()

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

        # czysczenie danych
        for i in range(len(punktyGracza)):
            rozdzielonePunktyGracza = punktyGracza[i].split(' ')
            rozdzielonePunktyKrupiera = punktyKrupiera[i].split(' ')
            #print(rozdzielonePunktyGracza, rozdzielonePunktyKrupiera)
            for j in range(len(rozdzielonePunktyGracza)-1):
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

    wr.close()