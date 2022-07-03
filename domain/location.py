from typing_extensions import Self


class Location:
    def __init__(self, lng, lat):
        self.lat = lat
        self.lng = lng

    def __eq__(self, other):
        if not isinstance(other, Location):
            return False

        return self.lng == other.lng and self.lat == other.lat

    def __hash__(self):
        return hash((self.lng, self.lat))