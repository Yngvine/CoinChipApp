import sys
import cadquery as cq
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QSplitter,
    QListWidget,
)
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from models import Geometries


class CadQueryViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CadQuery 3D Viewer")
        self.setGeometry(100, 100, 1000, 600)

        # Set up the main layout with a splitter
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Create a splitter for the left and right panels
        self.splitter = QSplitter(self.central_widget)
        self.main_layout.addWidget(self.splitter)

        # Left panel (toolbox, list, or settings)
        self.left_panel = QWidget(self.splitter)
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_panel.setLayout(self.left_layout)

        # Example: Adding a list widget and a label to the left panel
        self.list_widget = QListWidget()
        self.list_widget.addItems(["Object 1", "Object 2", "Object 3"])
        self.left_layout.addWidget(QLabel("Objects:"))
        self.left_layout.addWidget(self.list_widget)

        # Right panel (3D Viewer)
        self.right_panel = QWidget(self.splitter)
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_panel.setLayout(self.right_layout)

        # VTK Render Window for the 3D Viewer
        self.vtk_widget = QVTKRenderWindowInteractor(self.right_panel)
        self.right_layout.addWidget(self.vtk_widget)

        # Initialize the VTK renderer
        self.vtk_renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.vtk_renderer)
        self.vtk_interactor = self.vtk_widget.GetRenderWindow().GetInteractor()

        # Load and display the CadQuery model
        self.render_model()

    def render_model(self):
        # Create a new instance of the Geometries class
        geom = Geometries()

        # Get the middle chip
        middle_chip = geom.central_piece()

        # Example CadQuery model: a simple box
        model = middle_chip

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
        solid = shape.val()
        vertices, triangles = solid.tessellate(1.0)

        points = vtk.vtkPoints()
        for vertex in vertices:
            points.InsertNextPoint(vertex.x, vertex.y, vertex.z)

        poly_data = vtk.vtkPolyData()
        poly_data.SetPoints(points)

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
