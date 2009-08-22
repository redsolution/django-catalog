from imagekit import processors
from imagekit.specs import ImageSpec 

class ResizeDisplay(processors.Resize):
    width = 200
    height = 300

class Display(ImageSpec):
    processors = [ResizeDisplay, ]

class ThumbDisplay(processors.Resize):
    width = 130
    height = 130

class Thumb(ImageSpec):
    pre_cache = True 
    processors = [ThumbDisplay, ]
