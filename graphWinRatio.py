import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

#Opening win ratios
wrFile = open("./data/wr.txt", "r")
data = wrFile.read()
dataListWR = data.split("\n")

print(dataListWR)
wrFile.close()

#Opening games played
gamesPlayed = open("./data/gamesPlayed.txt", "r")
playedData = gamesPlayed.read()
dataListPlayed = playedData.split("\n")

print(dataListPlayed)
gamesPlayed.close()

plt.title("Win ratio per 250 games.")
plt.xlabel("Games played")
plt.ylabel("Win ratio")

x = dataListPlayed
y = dataListWR
x = [float(line) for line in dataListPlayed]
y = [float(line) for line in dataListWR]

plt.scatter(x,y)
plt.show()
