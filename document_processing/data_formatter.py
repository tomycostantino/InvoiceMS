import pandas as pd
import numpy as np


class DataFormater:
    def __init__(self):
        pass

    def _str_to_tuple(self, s: str):
        '''
        Convert the str into tuple of floats
        :param s:
        :return:
        '''

        if isinstance(s, str):
            try:
                values = tuple(map(float, s.strip('()').split(', ')))
                return (values[0], values[1], values[2], values[3]) if len(values) == 4 else (0.0, 0.0, 0.0, 0.0)
            except ValueError:
                # Return a default value if the conversion fails
                return (0.0, 0.0, 0.0, 0.0)
        else:
            return (0.0, 0.0, 0.0, 0.0)
    
