# -*- coding: utf-8 -*-

from imagekit import processors
from imagekit.specs import ImageSpec

class ResizeDisplay(processors.Resize):
    width = 800
    height = 800

class Display(ImageSpec):
    processors = [ResizeDisplay, ]

class ThumbDisplay(processors.Resize):
    width = 80
    height = 80

class Thumb(ImageSpec):
    pre_cache = True
    processors = [ThumbDisplay, ]
