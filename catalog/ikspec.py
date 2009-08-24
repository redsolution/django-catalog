from imagekit import processors
from imagekit.specs import ImageSpec 

class ResizeDisplay(processors.Resize):
    width = 300
    height = 300

class Display(ImageSpec):
    processors = [ResizeDisplay, ]

class ThumbDisplay(processors.Resize):
    width = 180
    height = 180

class Thumb(ImageSpec):
    pre_cache = True 
    processors = [ThumbDisplay, ]
