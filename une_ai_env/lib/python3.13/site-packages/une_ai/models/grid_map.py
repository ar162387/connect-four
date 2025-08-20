import numpy as np

class GridMap:
    def __init__(self, w, h, default_value=False):
        self._w = w
        self._h = h
        self._default_value = default_value
        self._map = np.array([[default_value]*w]*h) #np.zeros((h, w), dtype=dtype)

    def get_width(self):
        return self._w
    
    def get_height(self):
        return self._h
    
    def set_item_value(self, x, y, value):
        assert x >= 0 and x < self._w, "Coordinate x={0} out of bounds (w={1})".format(x, self._w)
        assert y >= 0 and y < self._h, "Coordinate y={0} out of bounds (h={1})".format(y, self._h)

        self._map[y, x] = value
    
    def get_item_value(self, x, y):
        assert x >= 0 and x < self._w, "Coordinate x={0} out of bounds (w={1})".format(x, self._w)
        assert y >= 0 and y < self._h, "Coordinate y={0} out of bounds (h={1})".format(y, self._h)

        return self._map[y, x]
    
    def get_row(self, row_idx):
        assert row_idx >= 0 and row_idx < self._h, "Row index = {0} out of bounds (h={1})".format(row_idx, self._h)

        return self._map[row_idx, :]
    
    def get_column(self, col_idx):
        assert col_idx >= 0 and col_idx < self._w, "Column index = {0} out of bounds (w={1})".format(col_idx, self._w)

        return self._map[:, col_idx]
    
    def get_map(self):
        return self._map.copy()
    
    def find_value_by_condition(self, condition_function):
        rc_coords = np.argwhere(condition_function(self._map)).tolist()
        xy_coords = []
        for coord in rc_coords:
            xy_coords.append((coord[1], coord[0]))
        
        return xy_coords

    def find_value(self, value):
        return self.find_value_by_condition(lambda gridmap: gridmap == value)
    
    def set_map(self, new_map):
        assert new_map.shape[0] == self._h and new_map.shape[1] == self._w, "The new map does not have the same dimensions of the original map. Original map dimensions {0}, new map dimensions {1}.".format(self._map.shape, new_map.shape)
        self._map = new_map.copy()

    def copy(self):
        new_grid = GridMap(self._w, self._h, self._default_value)
        new_grid.set_map(self._map)

        return new_grid