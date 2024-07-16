"""Fichier Temporaire (ou pas) sur la génération procédurale de terrain et partie temporaire de visualisation des terrains générés"""

import perlinNoise
import matplotlib.pyplot as plt

noise=perlinNoise.Perlin()
x =[i*0.01 for i in range(1000)]
y = [0 for i in range(1000)]
for i in range(10):
    j = [(noise.valueAt(k))/2**(2*i) *(-1)**i for k in x]
    for h in range(len(y)):
        y[h]+=(j[h])

plt.plot(x,y)
plt.show()