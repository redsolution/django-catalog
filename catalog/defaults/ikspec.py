from imagekit import processors
from imagekit.specs import ImageSpec

class ResizeDisplay(processors.Resize):
    width = 300
    height = 300

class Display(ImageSpec):
    processors = [ResizeDisplay, ]

class ResizeThumb(processors.Resize):
    width = 100
    height = 100

class Thumb(ImageSpec):
    pre_cache = True
    processors = [ResizeThumb, ]
