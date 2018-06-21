# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 12:17:50 2018

@author: jpelda
"""

class wcPERinhab:
    def __init__(self, df, country):
        self.df = df
        self.country = country
        self.water_consumption = self.country
        self.__source = None

    @property
    def water_consumption(self):
        return self.__water_consumption

    @water_consumption.setter
    def water_consumption(self, country):
        index = self.__index(country)
        self.__water_consumption = self.df['lPERpersonTIMESday'][index]

    def __index(self, x):
        names = self.df['country_name'].values.tolist()
        index = names.index(x)
        return index

    @property
    def source(self):
        pass
    @source.setter
    def source(self, x):
        pass