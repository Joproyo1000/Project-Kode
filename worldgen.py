"""Fichier Temporaire (ou pas) sur la génération procédurale de terrain et partie temporaire de visualisation des terrains générés"""

from random import randint
import matplotlib.pyplot as plt
from perlin_noise import PerlinNoise



def generateSeed():
    """Initie la génération d'une seed unique à chaque monde. La seed est compris entre 1 et 999999"""
    Seed = 000000
    Seed = randint(1,99999)
    return Seed

Seed = generateSeed()
nombreDeBiomes=12
noise = PerlinNoise(seed=Seed)

plt.plot([1,2,3,4],[])
plt.ylabel('Label 1')
plt.show()
