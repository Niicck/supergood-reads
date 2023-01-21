from django.db import models
from strategies.base.models import BaseStategy


class GarfunkelStrategy(BaseStategy):
    """
    The Garfunkel Strategy has no ranking schema whatsoever.
    
    Inspired by Art Garfunkel's reading list:
    https://www.artgarfunkel.com/library/list1.html
    """
    pass
