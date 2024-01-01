from random import randint

import numpy as np
import skimage
from perlin_noise import PerlinNoise
from biome import biome as Biome
from scipy.ndimage import gaussian_filter


class Map2D:
    def __init__(self, size, seed, chunk_size, max_height):
        self.size = size
        self.chunk_size = chunk_size
        self.MAX_HEIGHT = max_height

        self.map = np.empty((size, size), dtype=object)
        self.heightMap = np.empty((size, size))
        self.tempMap = np.empty((size, size))
        self.moistureMap = np.empty((size, size))

        self.perlin1 = PerlinNoise(octaves=2, seed=seed)
        self.perlin2 = PerlinNoise(octaves=4, seed=seed)
        self.perlin3 = PerlinNoise(octaves=8, seed=seed)
        self.perlin4 = PerlinNoise(octaves=16, seed=seed)

    def heightMapGen(self):
        scale = self.size

        for i in range(0, self.size):
            for j in range(0, self.size):
                noise_val = self.perlin1([i / scale, j / scale]) + 0.5 * \
                            self.perlin2([i / scale, j / scale]) + 0.25 * \
                            self.perlin3([i / scale, j / scale]) + 0.125 * \
                            self.perlin4([i / scale, j / scale]) - 0.625 * \
                            self.perlin1([i / scale, j / scale])
                height = int(noise_val * self.MAX_HEIGHT) + 5
                if height < 1:
                    height = 1
                self.heightMap[i, j] = height
                # self.heightMap[i, j] = 1 if height <= 1 else height
        return gaussian_filter(self.heightMap, sigma=40)

    def getHeightMap(self):
        return self.heightMap

    def tempMapGen(self, chunk, row, col):
        size = np.asarray(chunk).shape[0]
        TEMPERATURE_SCALE = 0.001
        DEFAULT_TEMPERATURE = 25
        TEMPERATURE_INCREMENT = 0.3
        tempChunk = np.empty((size, size))
        for i in range(0, size):
            for j in range(0, size):
                tempNoise = int(
                    (self.perlin1([(i + (row * size)) * TEMPERATURE_SCALE, (j + (col * size)) * TEMPERATURE_SCALE]) +
                     self.perlin2(
                         [(i + (row * size)) * TEMPERATURE_SCALE, (j + (col * size)) * TEMPERATURE_SCALE]) * 0.5 +
                     self.perlin3(
                         [(i + (row * size)) * TEMPERATURE_SCALE, (j + (col * size)) * TEMPERATURE_SCALE]) * 0.25 +
                     self.perlin4([(i + (row * size)) * TEMPERATURE_SCALE,
                                   (j + (col * size)) * TEMPERATURE_SCALE]) * 0.125) * 100)
                tempAltitude = DEFAULT_TEMPERATURE - abs(chunk[i, j] - 2) * TEMPERATURE_INCREMENT
                temp = tempNoise + tempAltitude
                temp = temp if temp > -20 else -20
                temp = temp if temp < 60 else 60
                tempChunk[i, j] = temp
        return tempChunk

    def moistureMapGen(self, chunk, row, col):
        size = np.asarray(chunk).shape[0]
        HUMIDITY_SCALE = 0.003
        HUMIDITY_TEMPERATURE = 1.3
        HUMIDITY_HIGH_TEMP = 23
        HUMIDITY_LOW_TEMP = 2
        moistureChunk = np.empty((size, size))
        for i in range(0, size):
            for j in range(0, size):
                humidityNoise = int(
                    (self.perlin1([(i + (row * size)) * HUMIDITY_SCALE, (j + (col * size)) * HUMIDITY_SCALE]) +
                     self.perlin2([(i + (row * size)) * HUMIDITY_SCALE, (j + (col * size)) * HUMIDITY_SCALE]) * 0.5 +
                     self.perlin3([(i + (row * size)) * HUMIDITY_SCALE, (j + (col * size)) * HUMIDITY_SCALE]) * 0.25 +
                     self.perlin4([(i + (row * size)) * HUMIDITY_SCALE,
                                   (j + (col * size)) * HUMIDITY_SCALE]) * 0.125) * 100 - 10)
                if self.tempMap[i, j] > HUMIDITY_HIGH_TEMP:
                    humidityFromTemperature = self.tempMap[i, j] * 2 - HUMIDITY_HIGH_TEMP
                elif self.tempMap[i, j] < HUMIDITY_LOW_TEMP:
                    humidityFromTemperature = HUMIDITY_LOW_TEMP
                else:
                    humidityFromTemperature = self.tempMap[i, j]
                humidityVal = int(humidityNoise + humidityFromTemperature * HUMIDITY_TEMPERATURE)
                moistureChunk[i, j] = humidityVal
        return moistureChunk

    def addRiver(self, heightMap, row, col):
        lakesMap = np.zeros((self.chunk_size, self.chunk_size))
        # TODO: Find nearer lakes to create river
        for line in heightMap:
            for pixel in heightMap:
                if pixel <= 2:
                    lakesMap[line, pixel] = 1

    def addMountain(self, nbMountains):
        x, y = self.getMountainsCoord(nbMountains)
        if x.size == 1:
            self.genMountain(x, y)
        else:
            for i in range(0, x.size):
                self.genMountain(x[i], y[i])

    def genMountain(self, x, y):
        size = randint(20, 25)
        scale = size * 2
        for i in range(x-size, x+size):
            for j in range(y-size, y+size):
                noise_val = self.perlin1([i / scale, j / scale]) + 0.5 * \
                            self.perlin2([i / scale, j / scale]) + 0.5 * \
                            self.perlin3([i / scale, j / scale]) + 0.125 * \
                            self.perlin4([i / scale, j / scale])
                height = int(noise_val * (self.MAX_HEIGHT + 30)) + 5
                if height < 1:
                    height = 1
                if 0 < i < self.size and 0 < j < self.size:
                    self.heightMap[i, j] = height

    def getMountainsCoord(self, nbMountains):
        maxValue = np.amax(self.heightMap)
        maxPos = np.where(self.heightMap == maxValue)
        if len(maxPos[0]) > nbMountains:
            for i in range(0, nbMountains):
                index = randint(0, len(maxPos[0]) - 1)
                x, y = maxPos[0][index], maxPos[1][index]
        else:
            for i in range(0, len(maxPos[0])):
                index = randint(0, len(maxPos[0]) - 1)
                x, y = maxPos[0][index], maxPos[1][index]
        return x, y

    @staticmethod
    def biomeMapGen(heightMap, tempMap, moistureMap):
        biomeMap = []
        for i in range(0, np.asarray(heightMap).shape[0]):
            biomeMap.append([])
            for j in range(0, np.asarray(heightMap).shape[0]):
                biome = Biome.getBiome(heightMap[i][j], tempMap[i][j], moistureMap[i][j])
                if len(biome) == 0:
                    biomeMap[i].append("None")
                else:
                    biomeMap[i].append(biome[0])
        return biomeMap

    def drawMap(self, biomeMap):
        image = []
        for i in range(0, self.size):
            image.append([])
            for j in range(0, self.size):
                image[i].append(Biome.getBiomeColor(biomeMap[i][j]))
        return image

    def getChunks(self, mapToDivide):
        chunks = []
        for i in range(0, self.size, self.chunk_size):
            for j in range(0, self.size, self.chunk_size):
                chunks.append(mapToDivide[i:i + self.chunk_size, j:j + self.chunk_size])
        return chunks

    def getChunkRows(self):
        rows = []
        row = 0
        for i in range(0, self.size, self.chunk_size):
            for j in range(0, self.size, self.chunk_size):
                rows.append(row)
            row += 1
        return rows

    def getChunkCols(self):
        cols = []
        for i in range(0, self.size, self.chunk_size):
            col = 0
            for j in range(0, self.size, self.chunk_size):
                cols.append(col)
                col += 1
        return cols
