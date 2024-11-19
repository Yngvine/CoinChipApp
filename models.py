import cadquery as cq
import numpy as np

def_dimensions = {
        "w": 50,     # Width
        "iw": 38,    # Inner width
        "h": 6,      # Height
        "cd": 46,    # Coin diameter
        "ct": 1.5,   # Coin thickness
        "pdd": 4.6,  # Pin diagonal distance
        "phd": 1.5,  # Pin hole diameter
        "cf": 0.75,  # Coin fillet
        "pc": 0.5,   # Pin chamfer
        "pbd": 1.6,  # Pin base diameter
        "pd": 1.4,   # Pin diameter
        "phhd": 1.45 # Pin head hole diameter
    }

class Geometries:
    def __init__(self, dimensions=def_dimensions):
        self.w = dimensions["w"]       # Width
        self.hw = self.w / 2           # Half width
        self.iw = dimensions["iw"]     # Inner width
        self.h = dimensions["h"]       # Height
        self.cd = dimensions["cd"]     # Coin diameter
        self.ct = dimensions["ct"]     # Coin thickness
        self.pdd = dimensions["pdd"]   # Pin diagonal distance
        self.phd = dimensions["phd"]     # Pin hole diameter
        self.cf = min(dimensions["cf"], dimensions["ct"]/2) # Coin chamfer
        self.pc = min(dimensions["pc"], dimensions["pd"]/2) # Pin chamfer
        self.pbd = dimensions["pbd"]  # Pin base diameter
        self.pd = dimensions["pd"]   # Pin diameter
        self.phhd = dimensions["phhd"] # Pin head hole diameter

    @property
    def cr(self):
        return self.cd / 2  # Coin radius

    @property
    def pld(self):
        return np.sqrt((self.pdd**2) / 2)  # Pin linear distance

    @property
    def ppsw(self):
        return self.w - 2 * self.pld  # Pin position square width
    
    @property
    def first_diagonal(self):
        return [(self.hw - self.pld, self.hw - self.pld), (-self.hw + self.pld, -self.hw + self.pld)]
    
    @property
    def second_diagonal(self):
        return [(self.hw - self.pld, -self.hw + self.pld), (-self.hw + self.pld, self.hw - self.pld)]

    @property
    def mch(self):
        return self.ct # Mid chip height

    @property
    def ech(self):
        return (self.h - self.ct)/2 # External chip height
    
    @property
    def ph(self):
        return self.mch + self.ech + .718  # Pin height
    
    @property
    def pbh(self):
        return self.ech + .875 # Pin base height
    
    @property
    def phhh(self):
        return self.ech - .73 # Pin head hole height
    
    def central_piece(self):

        # Start with the base workplane, creating outer and inner rectangles
        result = cq.Workplane("XY")
        result = result.moveTo(0, 0).rect(self.w, self.w)  # Outer rectangle
        result = result.rect(self.ppsw, self.ppsw, forConstruction=True)  # Inner construction rectangle

        # Add circles at each vertex of the inner construction rectangle
        result = result.vertices().circle(self.phd).end(2)

        # Add a larger circle in the center
        result = result.circle(self.cr).tag("base")  # Tagging for later reference

        # Extrude the base face and apply chamfers and fillets
        result = result.faces().tag("base").extrude(self.mch)
        result = result.edges(cq.selectors.RadiusNthSelector(0)).chamfer(self.pc)
        result = result.edges(cq.selectors.RadiusNthSelector(2)).fillet(self.cf)

        # Final result
        return result

    def external_piece(self):
        # Define the base workplane with the initial rectangle and circles
        result = cq.Workplane("XY")
        result = result.moveTo(0, 0).rect(self.w, self.w)

        # Place circles in two specific positions and tag for later reference
        result = result.pushPoints(self.first_diagonal)
        result = result.circle(self.pbd).end(1)
        result = result.pushPoints(self.second_diagonal)
        result = result.circle(self.phhd).end(1)
        result = result.faces().extrude(self.ech)


        result = result.pushPoints(self.first_diagonal)
        result = result.circle(self.pbd)
        result = result.faces().extrude(self.pbh)

        result = result.pushPoints(self.first_diagonal)
        result = result.circle(self.pd)
        result = result.faces().extrude(self.ph)

        result = result.pushPoints(self.second_diagonal)
        result = result.circle(self.phhd)
        result = result.faces().extrude(self.phhh)


        # Create a triangle on a new workplane

        triangle = cq.Workplane("YZ")
        triangle = triangle.workplane(offset=(self.first_diagonal[0][0]))
        triangle = triangle.center(self.first_diagonal[0][1] + self.pd, self.ph)
        triangle = triangle.polyline([(0, 0), (0.4, -0.359), (0, -0.718), (0, 0)])  # Define a triangle
        triangle = triangle.close()
        triangle = triangle.sweep(result.moveTo(*self.first_diagonal[0]).circle(self.pd))	

        triangle1 = cq.Workplane("YZ")
        triangle1 = triangle1.workplane(offset=(self.first_diagonal[1][0]))
        triangle1 = triangle1.center(self.first_diagonal[1][1] - self.pd, self.ph)
        triangle1 = triangle1.polyline([(0, 0), (-0.4, -0.359), (0, -0.718), (0, 0)])  # Define a triangle
        triangle1 = triangle1.close()
        triangle1 = triangle1.sweep(result.moveTo(*self.first_diagonal[1]).circle(self.pd))	


        # Use the sweep operation
        result = result.union(triangle).union(triangle1)

        result = result.edges(cq.selectors.BoxSelector((-self.hw,-self.hw,self.ph-.72),(self.hw,self.hw,self.ph+.1))).fillet(0.26)

        for point in self.first_diagonal:
            hole =  cq.Workplane("XY").workplane(offset=(self.ph)).center(*point).circle(0.75).rect(0.4,5).extrude(-1).rotateAboutCenter((0, 0, 10), -45)

            result = result.cut(hole)

        triangle = cq.Workplane("YZ")
        triangle = triangle.workplane(offset=(self.second_diagonal[0][0]))
        triangle = triangle.center(self.second_diagonal[0][1] - self.phhd, self.ech)
        triangle = triangle.polyline([(0, 0), (-0.4, -0.365), (0, -0.73), (0, 0)])  # Define a triangle
        triangle = triangle.close()
        triangle = triangle.sweep(result.moveTo(*self.second_diagonal[0]).circle(self.phhd))	

        triangle1 = cq.Workplane("YZ")
        triangle1 = triangle1.workplane(offset=(self.second_diagonal[1][0]))
        triangle1 = triangle1.center(self.second_diagonal[1][1] + self.phhd, self.ech)
        triangle1 = triangle1.polyline([(0, 0), (0.4, -0.365), (0, -0.73), (0, 0)])  # Define a triangle
        triangle1 = triangle1.close()
        triangle1 = triangle1.sweep(result.moveTo(*self.second_diagonal[1]).circle(self.phhd))	

        result = result.cut(triangle).cut(triangle1)
        result = result.edges(cq.selectors.BoxSelector((-self.hw+.1,self.hw-.1,self.ech+.1),(0,0,0))).fillet(0.123)
        result = result.edges(cq.selectors.BoxSelector((self.hw-.1,-self.hw+.1,self.ech+.1),(0,0,0))).fillet(0.123)


        result = result.cut(cq.Workplane("XY").rect(self.iw, self.iw).extrude(self.ech))

        
        return result