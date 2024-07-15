"""Fichier Temporaire (ou pas) sur la génération procédurale de terrain et partie temporaire de visualisation des terrains générés"""

import perlinNoise
import matplotlib.pyplot as plt

noise=perlinNoise.Perlin()
x=[i*0.01 for i in range(100)]
y= [noise.valueAt(i) for i in x]
plt.plot(x,y)
plt.show()