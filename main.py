import sys
import cadquery as cq
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QSplitter,
    QLabel,
    QHBoxLayout,
    QSlider,
    QComboBox,
    QPushButton,
    QDoubleSpinBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator  # Add this import
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from models import Geometries, def_dimensions


class CadQueryViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CadQuery 3D Viewer")
        self.setGeometry(100, 100, 800, 800)

        # Main layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)

        # Picker section
        self.picker_section = self.create_picker_section()
        self.layout.addWidget(self.picker_section)

        # Create a splitter to divide render viewports and picker section
        self.main_splitter = QSplitter(self.central_widget)
        self.main_splitter.setOrientation(Qt.Vertical)
        self.layout.addWidget(self.main_splitter)

        # Create a splitter for render viewports
        self.render_splitter = QSplitter(self.central_widget)
        self.render_splitter.setOrientation(Qt.Vertical)
        self.main_splitter.addWidget(self.render_splitter)

        # First viewport for the central piece
        self.viewport1 = self.create_viewport("Central Piece")
        self.render_splitter.addWidget(self.viewport1["widget"])

        # Second viewport for the external piece
        self.viewport2 = self.create_viewport("External Piece")
        self.render_splitter.addWidget(self.viewport2["widget"])

        # Render the models in the viewports
        self.render_models()

    def create_viewport(self, label_text):
        """
        Create a viewport with a label and a VTK render window.
        """
        viewport_widget = QWidget()
        viewport_layout = QVBoxLayout(viewport_widget)

        # Add a label to identify the viewport
        label = QLabel(label_text)
        viewport_layout.addWidget(label)

        # Add the VTK render window interactor
        vtk_widget = QVTKRenderWindowInteractor(viewport_widget)
        viewport_layout.addWidget(vtk_widget)

        # Create the renderer and attach it to the VTK widget
        vtk_renderer = vtk.vtkRenderer()
        vtk_widget.GetRenderWindow().AddRenderer(vtk_renderer)
        vtk_interactor = vtk_widget.GetRenderWindow().GetInteractor()

        return {"widget": viewport_widget, "vtk_widget": vtk_widget, "vtk_renderer": vtk_renderer}

    def create_picker_section(self):
        """
        Create the picker section for modifying values.
        """
        picker_widget = QWidget()
        picker_layout = QVBoxLayout(picker_widget)
        picker_layout.setAlignment(Qt.AlignTop)  # Align the layout to the top
    
        # Example slider for adjusting a parameter
        slider_label = QLabel("Adjust Parameter:")
        picker_layout.addWidget(slider_label)
    
        slider_layout = QHBoxLayout()
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(10)
        slider.setMaximum(1000)
        slider.setValue(500)
        slider.valueChanged.connect(self.on_slider_value_changed)
        slider_layout.addWidget(slider)
    
        slider_value = QDoubleSpinBox()
        slider_value.setDecimals(1)
        slider_value.setSingleStep(0.1)
        slider_value.setRange(1.0, 100.0)
        slider_value.setValue(slider.value() / 10.0)
        slider_value.valueChanged.connect(lambda value: slider.setValue(int(value * 10)))
        slider.valueChanged.connect(lambda value: slider_value.setValue(value / 10.0))
        slider_layout.addWidget(slider_value)
    
        picker_layout.addLayout(slider_layout)
    
        # Example dropdown for selecting a parameter
        dropdown_label = QLabel("Select Option:")
        picker_layout.addWidget(dropdown_label)
    
        dropdown = QComboBox()
        dropdown.addItems(["Option 1", "Option 2", "Option 3"])
        dropdown.currentIndexChanged.connect(self.on_dropdown_changed)
        picker_layout.addWidget(dropdown)
    
        # Example button to apply changes
        apply_button = QPushButton("Apply Changes")
        apply_button.clicked.connect(self.on_apply_changes)
        picker_layout.addWidget(apply_button)
    
        return picker_widget
        """
        Create the picker section for modifying values.
        """
        picker_widget = QWidget()
        picker_layout = QVBoxLayout(picker_widget)
        picker_layout.setAlignment(Qt.AlignTop)  # Align the layout to the top

        # Example slider for adjusting a parameter
        slider_label = QLabel("Adjust Parameter:")
        picker_layout.addWidget(slider_label)

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(1)
        slider.setMaximum(100)
        slider.setValue(50)
        slider.valueChanged.connect(self.on_slider_value_changed)
        picker_layout.addWidget(slider)

        # Example dropdown for selecting a parameter
        dropdown_label = QLabel("Select Option:")
        picker_layout.addWidget(dropdown_label)

        dropdown = QComboBox()
        dropdown.addItems(["Option 1", "Option 2", "Option 3"])
        dropdown.currentIndexChanged.connect(self.on_dropdown_changed)
        picker_layout.addWidget(dropdown)

        # Example button to apply changes
        apply_button = QPushButton("Apply Changes")
        apply_button.clicked.connect(self.on_apply_changes)
        picker_layout.addWidget(apply_button)

        return picker_widget

    def render_models(self):
        """
        Render the central and external pieces in their respective viewports.
        """
        custom_dimensions = def_dimensions
        custom_dimensions["cd"] = 26
        #custom_dimensions["ct"] = 3
        # Create an instance of the Geometries class
        geom = Geometries(dimensions=custom_dimensions)

        # Central piece in the first viewport
        central_piece = geom.central_piece()
        self.add_model_to_renderer(self.viewport1["vtk_renderer"], central_piece)

        # External piece in the second viewport
        external_piece = geom.external_piece()
        self.add_model_to_renderer(self.viewport2["vtk_renderer"], external_piece)

    def add_model_to_renderer(self, renderer, model):
        """
        Add a CadQuery model to a VTK renderer.
        """
        poly_data = self.cadquery_to_vtk(model)

        # Create a mapper and actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        # Add the actor to the renderer
        renderer.AddActor(actor)
        renderer.SetBackground(0.2, 0.3, 0.4)  # Background color (RGB)

        # Render the scene
        renderer.GetRenderWindow().Render()

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

    def closeEvent(self, event):
        """
        Handle the close event to clean up VTK render window interactors.
        """
        self.viewport1["vtk_widget"].GetRenderWindow().Finalize()
        self.viewport1["vtk_widget"].GetRenderWindow().GetInteractor().TerminateApp()
        self.viewport2["vtk_widget"].GetRenderWindow().Finalize()
        self.viewport2["vtk_widget"].GetRenderWindow().GetInteractor().TerminateApp()
        event.accept()

    # Picker section event handlers
    def on_slider_value_changed(self, value):
        print(f"Slider value changed: {value}")

    def on_dropdown_changed(self, index):
        print(f"Dropdown selection changed: {index}")

    def on_apply_changes(self):
        print("Apply changes button clicked!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = CadQueryViewer()
    viewer.show()
    sys.exit(app.exec())
