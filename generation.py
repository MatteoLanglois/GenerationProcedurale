import logging
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from matplotlib import pyplot as plt

from map2D import Map2D
from biome import biome as Biome


class MapGen:
    def __init__(self, seed, size, chunk_size, max_height, nb_Mountains, biomeList):
        self.FinalMap = np.empty((size, size), dtype=object)
        self.image = np.empty((size, size), dtype=object)
        self.Map = Map2D(size, seed, chunk_size, max_height)

        self.size = size
        self.chunk_size = chunk_size
        self.seed = seed
        self.MAX_HEIGHT = 100
        self.MAX_PLAIN_HEIGHT = max_height
        self.nb_Mountains = nb_Mountains

    def generate(self):
        logging.info(f"\x1b[33;32m Generating height map \x1b[0m")
        self.Map.heightMapGen()
        self.Map.addMountain(self.nb_Mountains)
        logging.info(f"\x1b[33;32m height map generated \x1b[0m")

        logging.info("\x1b[33;32m Variable initialization \x1b[0m")
        Chunks = self.Map.getChunks(self.Map.heightMap)
        chunkColumns = self.Map.getChunkCols()
        chunkRows = self.Map.getChunkRows()
        Thread_id = [T_id for T_id in range(1, int(self.size / self.chunk_size + 1) ** 2)]
        logging.info("\x1b[33;32m Variables initialized \x1b[0m")

        logging.info("\x1b[33;32m Generating map \x1b[0m")
        with ThreadPoolExecutor(max_workers=20) as executor:
            for result in executor.map(self.genChunk, Chunks, chunkRows, chunkColumns, Thread_id):
                th, th2, th3 = result[0], result[1], result[2]

                for i in range(0, self.chunk_size):
                    for j in range(0, self.chunk_size):
                        self.FinalMap[i + th2 * self.chunk_size, j + th3 * self.chunk_size] = th[i][j]

        logging.info("\x1b[33;32m Map generated \x1b[0m")
        logging.info("\x1b[33;32m Drawing map \x1b[0m")
        image = self.Map.drawMap(self.FinalMap)
        logging.info("\x1b[33;32m Map drawn \x1b[0m")
        return image

    def genChunk(self, chunk, row, col, t_id):
        logging.info(f"\x1b[33;32m Thread n°{t_id} starting \x1b[0m")
        tempMap = self.Map.tempMapGen(chunk, row, col)
        moistureMap = self.Map.moistureMapGen(tempMap, row, col)
        # = self.Map.addRiver(chunk, tempMap, row, col)
        biomeMap = self.Map.biomeMapGen(chunk, tempMap, moistureMap)
        logging.info(f"\x1b[33;20m Thread n°{t_id} finishing \x1b[0m")
        return biomeMap, row, col

    def gen3DMap(self, image):
        logging.info("\x1b[33;32m Generating 3D map \x1b[0m")
        logging.info("\x1b[33;32m Initialisation des variables \x1b[0m")
        Array = np.empty((self.size, self.size, self.MAX_HEIGHT), dtype=object)
        ArrayColor = np.empty((self.size, self.size, self.MAX_HEIGHT, 3), dtype=object)
        chunksHeight = self.Map.getChunks(self.Map.heightMap)
        chunks = self.Map.getChunks(np.asarray(image))
        chunkColumns = self.Map.getChunkCols()
        chunkRows = self.Map.getChunkRows()
        Thread_id = [T_id for T_id in range(0, int(self.size / self.chunk_size) ** 2)]
        logging.info("\x1b[33;32m Variables initialisées \x1b[0m")

        logging.info("\x1b[33;32m Génération de la map \x1b[0m")
        with ThreadPoolExecutor(max_workers=20) as executor:
            for result in executor.map(self.genVoxel, chunks, chunkRows, chunkColumns, Thread_id, chunksHeight):
                th, th2, th3, th4 = result[0], result[1], result[2], result[3]

                for i in range(0, self.chunk_size):
                    for j in range(0, self.chunk_size):
                        for k in range(0, self.MAX_HEIGHT):
                            ArrayColor[i + th2 * self.chunk_size, j + th3 * self.chunk_size, k] = th4[i][j][k]
                        Array[i + th2 * self.chunk_size, j + th3 * self.chunk_size] = th[i][j]
        Array = MapGen.deleteInvisibleVoxel(Array)
        return Array, ArrayColor

    @staticmethod
    def deleteInvisibleVoxel(Array):
        NewArray = np.empty((Array.shape[0], Array.shape[1], Array.shape[2]), dtype=object)
        for line in range(0, Array.shape[0]):
            for col in range(0, Array.shape[1]):
                height = 1
                while Array[line, col, height]:
                    if line == 1 or col == 1 or line == Array.shape[0] - 1 or col == Array.shape[1] - 1:
                        NewArray[line, col, height] = True
                    elif Array[line - 1, col, height] and Array[line + 1, col, height] \
                            and Array[line, col - 1, height] and Array[line, col + 1, height]\
                            and Array[line, col, height - 1] and Array[line, col, height + 1]:
                        NewArray[line, col, height] = False
                    else:
                        NewArray[line, col, height] = True
                    height += 1

        # Se renseigner sur Greedy Meshing
        return NewArray

    def genVoxel(self, chunk, row, column, Th_id, HeightMap):
        logging.info(f"\x1b[33;32m Thread n°{Th_id} starting : Voxel Gen \x1b[0m")
        ArrayColor = np.empty((np.asarray(chunk).shape[0], np.asarray(chunk).shape[1], self.MAX_HEIGHT, 3),
                              dtype=object)
        Array = np.empty((np.asarray(chunk).shape[0], np.asarray(chunk).shape[1], self.MAX_HEIGHT), dtype=object)
        for x in range(0, np.asarray(chunk).shape[0]):
            for y in range(0, np.asarray(chunk).shape[1]):
                for z in range(0, self.MAX_HEIGHT):
                    if z <= HeightMap[x][y]:
                        Array[x, y, z] = 1
                    else:
                        Array[x, y, z] = 0
                    ArrayColor[x, y, z] = [H / 255 for H in chunk[x][y]]
        logging.info(f"\x1b[33;20m Thread n°{Th_id} finishing : Voxel Gen \x1b[0m")
        return Array, row, column, ArrayColor

    def showMap(self, image):
        plt.figure(figsize=(10, 10))
        plt.subplot(121)
        plt.imshow(image)
        plt.subplot(122)
        plt.pie([1] * len(Biome.getBiomes()), labels=Biome.getBiomes(),
                colors=[Biome.rgbToHex(Biome.getBiomes()[biome][-1]) for biome in Biome.getBiomes()])
        plt.title(f"Seed : {self.seed}")
        plt.show()

    def show3DMap(self, image, couleurs):
        logging.info("\x1b[33;32m Drawing 3D map \x1b[0m")
        ax = plt.axes(projection='3d')
        ax.voxels(image, facecolors=couleurs, shade=False, edgecolor=(0, 0, 0, 0.05))
        ax.set_zscale('linear')
        ax.set_zticks([i for i in range(0, self.MAX_HEIGHT)])
        ax.set_aspect('equal', adjustable='box')
        ax.locator_params('z', nbins=1)
        ax.grid(False)
        ax.axis('off')
        plt.show()

    def showBothMap(self, image, image2, couleurs):
        plt.subplot(221)
        plt.imshow(image)
        plt.subplot(222)
        plt.pie([1] * len(Biome.getBiomes()), labels=Biome.getBiomes(),
                colors=[Biome.rgbToHex(Biome.getBiomes()[biome][-1]) for biome in Biome.getBiomes()])
        plt.title(f"Seed : {self.seed}")
        ax = plt.subplot(223, projection='3d')
        ax.voxels(image2, facecolors=couleurs, shade=False, edgecolor=(0, 0, 0, 0.1))
        ax.set_zscale('linear')
        ax.set_zticks([i for i in range(0, self.MAX_HEIGHT)])
        ax.set_aspect('equal', adjustable='box')
        ax.locator_params('z', nbins=1)
        ax.grid(False)

        ax.axis('off')

        plt.show()

    def save(self, map):
        logging.info("\x1b[33;32m Saving map \x1b[0m")
        np.save(f"map", map)
        logging.info("\x1b[33;32m Map saved \x1b[0m")
