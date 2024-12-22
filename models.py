import cadquery as cq
import numpy as np
import math

def_dimensions = {
        "chip width": 50,               # Width
        "chip window width": 38,        # Inner width
        "chip height": 6,               # Height
        "coin diameter": 46,            # Coin diameter
        "coin thickness": 1.5,          # Coin thickness
        "pin diagonal distance": 4.6,   # Pin diagonal distance
        "pin hole diameter": 1.5,       # Pin hole diameter
        "coin fillet": 0.75,            # Coin fillet
        "pin chamfer": 0.5,             # Pin chamfer
        "pin base diameter": 1.6,       # Pin base diameter
        "pin diameter": 1.4,            # Pin diameter
        "pin head hole diameter": 1.45, # Pin head hole diameter
        "screen thickness": 0.15,       # Screen thickness
    }

class Geometries:
    """
    Class to define the geometries of the pieces of the chip that is to hold the coin.
    """


    def __init__(self, dimensions=def_dimensions):
        self.w = dimensions["chip width"]                   # Width
        """The width of the chip"""

        self.iw = dimensions["chip window width"]           # Inner width
        """The inner width reserverd for the window of the chip"""

        self.h = dimensions["chip height"]                  # Height
        """The height (total thickness) of the chip"""

        self.cd = dimensions["coin diameter"]               # Coin diameter
        """The diameter of the coin"""

        self.ct = dimensions["coin thickness"]              # Coin thickness
        """The thickness of the coin"""
        
        self._pdd = dimensions["pin diagonal distance"]      # Pin diagonal distance
        """The distance between the corner of the chip and the center of the pin"""

        self._phd = dimensions["pin hole diameter"]          # Pin hole diameter
        """The diameter of the hole for the pin"""

        self._cf = dimensions["coin fillet"]                # Coin fillet
        """The radius of the fillet of the coin"""

        self._pc = dimensions["pin chamfer"]                # Pin chamfer
        """The distance of the chamfer of the pin"""

        self._pbd = dimensions["pin base diameter"]          # Pin base diameter
        """The diameter of the base of the pin"""

        self._pd = dimensions["pin diameter"]                # Pin diameter
        """The diameter of the pin"""

        self._phhd = dimensions["pin head hole diameter"]    # Pin head hole diameter
        """The diameter of the hole for the pin head"""

        self._st = dimensions["screen thickness"]            # Screen thickness
        """The thickness of the plastic screen that should cover the coin from both sides"""

    @property
    def _cr(self):
        """Coin radius"""
        return self.cd / 2

    @property
    def _pld(self):
        """Pin linear distance"""
        return np.sqrt((self._pdd**2) / 2)
    
    @property
    def _hw(self):
        """Half width of the chip"""
        return self.w / 2

    @property
    def _ppsw(self):
        """Pin position square width"""
        return self.w - 2 * self._pld

    @property
    def _first_diagonal(self):
        """First diagonal coordinates"""
        return [(self._hw - self._pld, self._hw - self._pld), (-self._hw + self._pld, -self._hw + self._pld)]

    @property
    def _second_diagonal(self):
        """Second diagonal coordinates"""
        return [(self._hw - self._pld, -self._hw + self._pld), (-self._hw + self._pld, self._hw - self._pld)]

    @property
    def _mch(self):
        """Mid chip height"""
        return self.ct

    @property
    def _ccf(self):
        """Coin fillet with correction to avoid errors"""
        return min(self._cf, self._mch / 2 - .001)

    @property
    def _cpc(self):
        """Pin chamfer with correction to avoid errors"""
        return min(self._pc, self._mch / 2 - .001)

    @property
    def _ech(self):
        """External chip height"""
        return (self.h - self.ct) / 2 - self._st
    
    @property
    def _min_ech(self):
        """Minimum external chip height"""
        return .73 + self._phhhwt

    @property
    def _ph(self):
        """Pin height"""
        return self._mch + self._ech + .718

    @property
    def _pbh(self):
        """Pin base height"""
        return self._ech + .875

    @property
    def _phhh(self):
        """Pin head hole height"""
        return self._ech - .73
    
    @property
    def _phhhwt(self):
        """Pin head hole height wall thickness"""
        return .2 # Accounr for the printer minimum height resolution and number of walls
        
    @property
    def max_cd(self):
        """Maximum diameter of the coin"""
        return math.floor((self.w - 2 * self._ccf) * 100) / 100
    
    @property
    def max_ct(self):
        """Maximum thickness of the coin"""
        return min(math.floor((self.h - 2 * (self._min_ech + self._st)) * 100) / 100, 3.5) # Didn't find any coin thicker than 3.5mm thus this is the maximum thickness
    
    @property
    def min_cd(self):
        """Minimum diameter of the coin"""
        return 10 # Honestly, I don't know which should be the minimum diameter of a coin
    
    @property
    def min_ct(self):
        """Minimum thickness of the coin"""
        return 1.0 # The 3D model will breack if the thickness is less than 1.0 (I didn't find any coins with thickness less than 1.0 regardless)

    @property
    def max_w(self):
        """Maximum width of the chip"""
        return 70 # Just a value that I think is reasonable as placeholder
    
    @property
    def min_w(self):
        """Minimum width of the chip"""
        return max(math.ceil((self.cd + 2 * self._ccf) * 100) / 100, 30) # Just a value that I think is reasonable as placeholder
    
    @property
    def max_h(self):
        """Maximum height of the chip"""
        return 10 # Just a value that I think is reasonable as placeholder
    
    @property
    def min_h(self):
        """Minimum height of the chip"""
        return max(math.ceil((self.ct + 2 * (self._min_ech + self._st)) * 100) / 100, 2) # Just a value that I think is reasonable as placeholder

    def central_piece(self):

        # Start with the base workplane, creating outer and inner rectangles
        result = cq.Workplane("XY")
        result = result.moveTo(0, 0).rect(self.w, self.w)  # Outer rectangle
        result = result.rect(self._ppsw, self._ppsw, forConstruction=True)  # Inner construction rectangle

        # Add circles at each vertex of the inner construction rectangle
        result = result.vertices().circle(self._phd).end(2)

        # Add a larger circle in the center
        result = result.circle(self._cr).tag("base")  # Tagging for later reference

        # Extrude the base face and apply chamfers and fillets
        result = result.faces().tag("base").extrude(self._mch)
        result = result.edges(cq.selectors.RadiusNthSelector(0)).chamfer(self._cpc)
        result = result.edges(cq.selectors.RadiusNthSelector(2)).fillet(self._ccf)

        # Final result
        return result

    def external_piece(self):
        # Define the base workplane with the initial rectangle and circles
        result = cq.Workplane("XY")
        result = result.moveTo(0, 0).rect(self.w, self.w)

        # Place circles in two specific positions and tag for later reference
        result = result.pushPoints(self._first_diagonal)
        result = result.circle(self._pbd).end(1)
        result = result.pushPoints(self._second_diagonal)
        result = result.circle(self._phhd).end(1)
        result = result.faces().extrude(self._ech)


        result = result.pushPoints(self._first_diagonal)
        result = result.circle(self._pbd)
        result = result.faces().extrude(self._pbh)

        result = result.pushPoints(self._first_diagonal)
        result = result.circle(self._pd)
        result = result.faces().extrude(self._ph)

        result = result.pushPoints(self._second_diagonal)
        result = result.circle(self._phhd)
        result = result.faces().extrude(self._phhh)


        # Create a triangle on a new workplane

        triangle = cq.Workplane("YZ")
        triangle = triangle.workplane(offset=(self._first_diagonal[0][0]))
        triangle = triangle.center(self._first_diagonal[0][1] + self._pd, self._ph)
        triangle = triangle.polyline([(0, 0), (0.4, -0.359), (0, -0.718), (0, 0)])  # Define a triangle
        triangle = triangle.close()
        triangle = triangle.sweep(result.moveTo(*self._first_diagonal[0]).circle(self._pd))	

        triangle1 = cq.Workplane("YZ")
        triangle1 = triangle1.workplane(offset=(self._first_diagonal[1][0]))
        triangle1 = triangle1.center(self._first_diagonal[1][1] - self._pd, self._ph)
        triangle1 = triangle1.polyline([(0, 0), (-0.4, -0.359), (0, -0.718), (0, 0)])  # Define a triangle
        triangle1 = triangle1.close()
        triangle1 = triangle1.sweep(result.moveTo(*self._first_diagonal[1]).circle(self._pd))	


        # Use the sweep operation
        result = result.union(triangle).union(triangle1)

        result = result.edges(cq.selectors.BoxSelector((-self._hw,-self._hw,self._ph-.72),(self._hw,self._hw,self._ph+.1))).fillet(0.26)

        for point in self._first_diagonal:
            hole =  cq.Workplane("XY").workplane(offset=(self._ph)).center(*point).circle(0.75).rect(0.4,5).extrude(-1).rotateAboutCenter((0, 0, 10), -45)

            result = result.cut(hole)

        triangle = cq.Workplane("YZ")
        triangle = triangle.workplane(offset=(self._second_diagonal[0][0]))
        triangle = triangle.center(self._second_diagonal[0][1] - self._phhd, self._ech)
        triangle = triangle.polyline([(0, 0), (-0.4, -0.365), (0, -0.73), (0, 0)])  # Define a triangle
        triangle = triangle.close()
        triangle = triangle.sweep(result.moveTo(*self._second_diagonal[0]).circle(self._phhd))	

        triangle1 = cq.Workplane("YZ")
        triangle1 = triangle1.workplane(offset=(self._second_diagonal[1][0]))
        triangle1 = triangle1.center(self._second_diagonal[1][1] + self._phhd, self._ech)
        triangle1 = triangle1.polyline([(0, 0), (0.4, -0.365), (0, -0.73), (0, 0)])  # Define a triangle
        triangle1 = triangle1.close()
        triangle1 = triangle1.sweep(result.moveTo(*self._second_diagonal[1]).circle(self._phhd))	

        result = result.cut(triangle).cut(triangle1)
        result = result.edges(cq.selectors.BoxSelector((-self._hw+.1,self._hw-.1,self._ech+.1),(0,0,0))).fillet(0.123)
        result = result.edges(cq.selectors.BoxSelector((self._hw-.1,-self._hw+.1,self._ech+.1),(0,0,0))).fillet(0.123)


        result = result.cut(cq.Workplane("XY").rect(self.iw, self.iw).extrude(self._ech))

        
        return result