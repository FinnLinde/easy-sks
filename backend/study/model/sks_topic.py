from enum import Enum


class SksTopic(str, Enum):
    """The five theoretical exam areas of the Sportkuestenschifferschein (SKS).

    Based on the official ELWIS Fragenkatalog:
    https://www.elwis.de/DE/Sportschifffahrt/Sportbootfuehrerscheine/Fragenkatalog-SKS/
    """

    NAVIGATION = "navigation"
    SCHIFFFAHRTSRECHT = "schifffahrtsrecht"
    WETTERKUNDE = "wetterkunde"
    SEEMANNSCHAFT_I = "seemannschaft_i"    # Antriebsmaschine und unter Segel
    SEEMANNSCHAFT_II = "seemannschaft_ii"  # nur Antriebsmaschine
