class biome:
    biomes = {}

    def __init__(self, name, minHeight, maxHeight, minTemp, maxTemp, minMoisture, maxMoisture, color):
        self.name = name
        self.minHeight = minHeight
        self.maxHeight = maxHeight
        self.minTemp = minTemp
        self.maxTemp = maxTemp
        self.minMoisture = minMoisture
        self.maxMoisture = maxMoisture
        self.color = color
        if name not in biome.biomes:
            biome.biomes[name] = self

    @classmethod
    def simpleBiomes(cls, sea_level, beach_level, mountain_level, cold_level, hot_level, humidity_level):
        minVal = -1000
        maxVal = 1000
        biome.biomes = {
            "ocean":
                [minVal, sea_level, minVal, maxVal, minVal, humidity_level, (38, 61, 255)],
            "Dry Ocean":
                [minVal, sea_level, minVal, maxVal, humidity_level, maxVal, (153, 118, 58)],
            "Beach":
                [sea_level, beach_level, cold_level, maxVal, minVal, humidity_level, (255, 255, 0)],
            "Cold_beach":
                [sea_level, beach_level, minVal, cold_level, minVal, maxVal, (200, 200, 200)],
            "Swamp":
                [sea_level, beach_level, cold_level, maxVal, humidity_level, maxVal, (24, 87, 8)],
            "Plain":
                [beach_level, mountain_level, cold_level, hot_level, minVal, maxVal, (133, 235, 118)],
            "Tundra":
                [beach_level, mountain_level, minVal, cold_level, minVal, maxVal, (255, 255, 255)],
            "Desert":
                [beach_level, mountain_level, hot_level, maxVal, minVal, humidity_level, (255, 234, 128)],
            "Jungle":
                [beach_level, mountain_level, hot_level, maxVal, humidity_level, maxVal, (0, 143, 0)],
            "Snowy_mountains":
                [mountain_level, maxVal, minVal, cold_level, minVal, maxVal, (196, 207, 215)],
            "Mountains":
                [mountain_level, maxVal, cold_level, maxVal, minVal, maxVal, (173, 168, 169)],
            "None":
                [minVal, maxVal, minVal, maxVal, minVal, maxVal, (204, 0, 204)]
        }

    @classmethod
    def getBiome(cls, height, temp, moisture):
        retour = []
        for biomeName in cls.biomes:
            if cls.biomes[biomeName][0] <= height <= cls.biomes[biomeName][1] and \
                    cls.biomes[biomeName][2] <= temp <= cls.biomes[biomeName][3] and \
                    cls.biomes[biomeName][4] <= moisture <= cls.biomes[biomeName][5]:
                retour.append(biomeName)
        return retour

    @classmethod
    def getBiomes(cls):
        return cls.biomes

    @classmethod
    def getBiomeColor(cls, biomeName):
        return cls.biomes[biomeName][6]

    @staticmethod
    def rgbToHex(rgb):
        return f"#{hex(rgb[0])[2:].upper() if len(hex(rgb[0])[2:]) == 2 else '0' + hex(rgb[0])[2:].upper()}{hex(rgb[1])[2:].upper() if len(hex(rgb[1])[2:]) == 2 else '0' + hex(rgb[1])[2:].upper()}{hex(rgb[2])[2:].upper() if len(hex(rgb[2])[2:]) == 2 else '0' + hex(rgb[2])[2:].upper()}"
