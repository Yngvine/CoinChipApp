import sys
import cadquery as cq
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from models import Geometries

class CadQueryViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CadQuery 3D Viewer")
        self.setGeometry(100, 100, 800, 600)
        
        # Set up the main window layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Initialize VTK render window
        self.vtk_widget = QVTKRenderWindowInteractor(self.central_widget)
        self.layout.addWidget(self.vtk_widget)

        # Create VTK renderer and assign it to the window
        self.vtk_renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.vtk_renderer)
        self.vtk_interactor = self.vtk_widget.GetRenderWindow().GetInteractor()

        # Load and display a simple CadQuery model
        self.render_model()

    def model(self):
        # Create a new instance of the Geometries class
        geom = Geometries()

        mid_chip = geom.external_piece()  # Create the central piece
        
        combined = mid_chip  # Combine the two extrusions
        
        return combined

    def render_model(self):
        # Example CadQuery model: a simple box
        model = self.model()

        # Convert CadQuery model to VTK-compatible PolyData
        poly_data = self.cadquery_to_vtk(model)

        # Create a VTK mapper and actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        # Add the actor to the VTK renderer
        self.vtk_renderer.AddActor(actor)

        # Set the background color and render the scene
        self.vtk_renderer.SetBackground(0.2, 0.3, 0.4)  # Background color (RGB)
        self.vtk_widget.GetRenderWindow().Render()
        self.vtk_interactor.Initialize()

    def cadquery_to_vtk(self, shape):
        """
        Converts a CadQuery shape into VTK PolyData for rendering.
        """
        # Get the solid from the Workplane
        solid = shape.val()

        # Tessellate the solid
        vertices, triangles = solid.tessellate(1.0)  # Tessellate the CadQuery solid

        # Create VTK Points object
        points = vtk.vtkPoints()
        for vertex in vertices:
            points.InsertNextPoint(vertex.x, vertex.y, vertex.z)

        # Create VTK PolyData
        poly_data = vtk.vtkPolyData()
        poly_data.SetPoints(points)

        # Create VTK Cells for the faces
        faces = vtk.vtkCellArray()
        for triangle in triangles:
            faces.InsertNextCell(3)
            for vertex_idx in triangle:
                faces.InsertCellPoint(vertex_idx)
        
        poly_data.SetPolys(faces)

        return poly_data


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = CadQueryViewer()
    viewer.show()
    sys.exit(app.exec())
