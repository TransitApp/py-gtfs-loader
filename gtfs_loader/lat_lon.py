
from math import *


class LatLon:
    # Sources:
    # http://www.movable-type.co.uk/scripts/gis-faq-5.1.html
    # http://www.movable-type.co.uk/scripts/latlong.html
    EARTH_RADIUS_M = 6_371_009.0
    __slots__ = ('lat', 'lon')

    def __init__(self, lat, lon, unit=degrees):
        self.lat = radians(lat) if unit == degrees else lat
        self.lon = radians(lon) if unit == degrees else lon

    def geojson(self):
        return f'[{degrees(self.lon)}, {degrees(self.lat)}]'

    def __repr__(self):
        return repr((degrees(self.lat), degrees(self.lon)))

    def angular_distance_to(self, other):
        d_lat = other.lat - self.lat
        d_lon = other.lon - self.lon
        a = sin(
            d_lat / 2)**2 + cos(self.lat) * cos(other.lat) * sin(d_lon / 2)**2
        return 2 * asin(sqrt(a))

    def distance_to(self, other):
        return LatLon.EARTH_RADIUS_M * self.angular_distance_to(other)

    def bearing_to(self, other):
        y = sin(other.lon - self.lon) * cos(other.lat)
        x = cos(self.lat) * sin(other.lat) - sin(self.lat) * cos(
            other.lat) * cos(other.lon - self.lon)
        return atan2(y, x)

    def add_bearing_and_angular_distance(self, bearing, dist):
        lat = asin(
            sin(self.lat) * cos(dist) +
            cos(self.lat) * sin(dist) * cos(bearing))
        lon = self.lon \
            + atan2(sin(bearing)*sin(dist)*cos(self.lat),
                    cos(dist) - sin(self.lat)*sin(lat))

        return LatLon(lat, lon, unit=radians)

    def distance_to_segment(x, l1, l2):
        """
                     x
                     |
                     |
        l1 ---------lx------------ l2
        """

        d_l1_x, t_l1_x = l1.angular_distance_to(x), l1.bearing_to(x)
        d_l1_l2, t_l1_l2 = l1.angular_distance_to(l2), l1.bearing_to(l2)
        d_l2_x = l2.angular_distance_to(x)

        d_cross = asin(sin(d_l1_x) * sin(t_l1_x - t_l1_l2))
        d_along = acos(cos(d_l1_x) / cos(d_cross))

        lx = l1.add_bearing_and_angular_distance(t_l1_l2, d_along)
        d_lx_x = lx.angular_distance_to(x)

        if d_along < d_l1_l2 and d_lx_x < d_l1_x and d_lx_x < d_l2_x:
            # closest point is somewhere along l1-l2 as in the above figure
            return LatLon.EARTH_RADIUS_M * d_lx_x
        else:
            # closest point is l1, l2 depending on which end is nearer to x
            return LatLon.EARTH_RADIUS_M * min(d_l1_x, d_l2_x)

    def __eq__(self, other):
        if other == None:
            return False
        return self.lat == other.lat and self.lon == other.lon

    def __hash__(self):
        return hash((self.lat, self.lon))
