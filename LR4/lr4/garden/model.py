import os
import random
import shutil

import numpy
from lxml import etree

from lr4.garden.plants import what_the_plant, Plant, Weed
from lr4.garden.weather import Weather

dictonary = [
    "tomato",
    "carrot",
    "potato",
    "cucumber",
    "zucchini",
    "weed"
]


def create_xml(x, y):
    root = etree.Element('garden')
    square = etree.SubElement(root, "square")
    etree.SubElement(square, "x").text = str(x)
    etree.SubElement(square, "y").text = str(y)

    weather = etree.SubElement(root, "weather")

    etree.SubElement(weather, "type").text = "clear"
    etree.SubElement(weather, "time").text = str(10)
    etree.SubElement(root, 'time').text = str(0)

    seeds = etree.SubElement(root, 'seeds')

    for i in range(0, random.randint(0, x * y)):
        page = etree.SubElement(seeds, "entity")
        etree.SubElement(page, "name").text = random.choice(dictonary)
        etree.SubElement(page, "health").text = "100"
        etree.SubElement(page, "time").text = "0"
        position = etree.SubElement(page, "position")
        etree.SubElement(position, "x").text = str(random.randint(0, x - 1))
        etree.SubElement(position, "y").text = str(random.randint(0, y - 1))

    doc = etree.ElementTree(root)
    doc.write(os.getcwd() + '/.gardenrc/Entities/plants.xml', pretty_print=True,
              xml_declaration=True,
              encoding='utf-8')


def create_dir(x, y):
    try:
        shutil.rmtree(os.path.join(os.getcwd() + "/.gardenrc/"))
        os.makedirs(os.path.join(os.getcwd() + "/.gardenrc/", "Entities"))
        try:
            create_xml(x, y)
        except OSError as error:
            print(error)
    except OSError as error:
        print(error)


class Model:
    def __init__(self, garden):
        self.weather = Weather(typed="clear", time=10)
        self.x = garden.x
        self.y = garden.y
        self.garden = garden
        self.matrix = numpy.empty((self.x, self.y), dtype="object")

    def get_entity(self, x, y):
        return self.matrix[x][y]

    def add_entity(self, plant, x, y):
        self.matrix[x][y] = plant

    def remove_entity(self, x, y):
        self.matrix[x][y] = None

    def print(self):
        details = numpy.chararray((self.x, self.y), unicode=True)
        for i in range(len(self.matrix)):
            for j in range(len(self.matrix[0])):
                if self.matrix[i][j] is not None:
                    details[i][j] = self.matrix[i][j].icon
                else:
                    details[i][j] += "X"
        return details

    def find_nearest_weed(self, x, y):
        if x != len(self.matrix[0]) - 1 and y != len(self.matrix) - 1 and self.matrix[x][y] is not None:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if x + i != len(self.matrix) and y + j != len(self.matrix[0]):
                        if self.matrix[x + i][y + j] is not self.matrix[x][y]:
                            if self.matrix[x + i][y + j].__class__ == Weed:
                                self.matrix[x][y].health -= self.matrix[x + i][y + j].damage

    def garbage_collector(self) -> str:
        output = ""
        for i in range(len(self.matrix)):
            for j in range(len(self.matrix[0])):
                if self.matrix[i][j] is not None:
                    if not issubclass(self.matrix[i][j].__class__, Plant) and self.matrix[i][j].time >= 10:
                        time = self.matrix[i][j].time
                        self.matrix[i][j] = what_the_plant(self.matrix[i][j].name)
                        self.matrix[i][j].time = time
                    self.find_nearest_weed(i, j)
                    self.matrix[i][j].get_weather(self.weather)
                    if self.matrix[i][j].health <= 0:
                        print(f'{type(self.matrix[i][j]).__name__} (x: {i} y: {j}) has been died')
                        output += f'{type(self.matrix[i][j]).__name__} (x: {i} y: {j}) has been died \n'
                        self.remove_entity(i, j)
        return output

    def save(self):
        root = etree.Element('garden')
        square = etree.SubElement(root, "square")
        etree.SubElement(square, "x").text = str(self.x)
        etree.SubElement(square, "y").text = str(self.y)

        weather = etree.SubElement(root, "weather")
        if self.weather.time <= 0:
            self.weather.time = 10
            self.weather.weather = "clear"
        etree.SubElement(weather, "type").text = self.weather.weather
        etree.SubElement(weather, "time").text = str(self.weather.time - 1)
        etree.SubElement(root, 'time').text = str(self.garden.time)
        plant = etree.SubElement(root, 'plants')
        seeds = etree.SubElement(root, 'seeds')
        for i in range(len(self.matrix)):
            for j in range(len(self.matrix[0])):
                if self.matrix[i][j] is not None:
                    if issubclass(self.matrix[i][j].__class__, Plant):
                        page = etree.SubElement(plant, "entity")
                        etree.SubElement(page, "name").text = self.matrix[i][j].name
                        etree.SubElement(page, "length").text = str(self.matrix[i][j].length)
                        etree.SubElement(page, "time").text = str(self.matrix[i][j].time)
                        etree.SubElement(page, "health").text = str(self.matrix[i][j].health)
                        position = etree.SubElement(page, "position")
                        etree.SubElement(position, "x").text = str(i)
                        etree.SubElement(position, "y").text = str(j)
                    else:
                        page = etree.SubElement(seeds, "entity")
                        etree.SubElement(page, "name").text = self.matrix[i][j].name
                        etree.SubElement(page, "health").text = str(self.matrix[i][j].health)
                        etree.SubElement(page, "time").text = str(self.matrix[i][j].time)
                        position = etree.SubElement(page, "position")
                        etree.SubElement(position, "x").text = str(i)
                        etree.SubElement(position, "y").text = str(j)

        doc = etree.ElementTree(root)
        doc.write(os.getcwd() + '/.gardenrc/Entities/plants.xml', pretty_print=True,
                  xml_declaration=True,
                  encoding='utf-8')
