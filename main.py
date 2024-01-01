import logging
from random import randint
from mapGenerator.generation import MapGen
from mapGenerator.biome import biome as Biome





def main():
    """
    seed = randint(1000, 10000000)
    GenNormale = MapGen(seed, 200, 25, 20, 2, biomeList=Biome.simpleBiomes(1, 3, 15, -5, 40, 50))
    MapNormale = GenNormale.generate()
    Map3D, couleur = GenNormale.gen3DMap(MapNormale)
    GenNormale.save(Map3D)

    GenNormale.showMap(MapNormale)
    # GenNormale.show3DMap(Map3D, couleur)
    """


if __name__ == '__main__':
    logging.basicConfig(format="\x1b[31;1m %(asctime)s: %(message)s",
                        level=logging.INFO, datefmt="%H:%M:%S", encoding='utf-8')
    main()
