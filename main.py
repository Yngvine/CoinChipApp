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
        self.geometries = Geometries()
        self.custom_dimensions = def_dimensions
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
    
        # Slider for adjusting coin diameter
        slider_label_cd = QLabel("Adjust Coin Diameter:")
        picker_layout.addWidget(slider_label_cd)
    
        slider_layout_cd = QHBoxLayout()
        
        # Minimum value label for coin diameter
        min_cd = self.geometries.min_cd
        max_cd = self.geometries.max_cd
        cd = self.geometries.cd

        min_label_cd = QLabel(str(min_cd))
        slider_layout_cd.addWidget(min_label_cd)
    
        slider_cd = QSlider(Qt.Horizontal)
        slider_cd.setMinimum(min_cd * 10)  # Scale by 10 to allow one decimal place
        slider_cd.setMaximum(max_cd * 10)
        slider_cd.setValue(cd * 10)
        slider_cd.valueChanged.connect(self.on_slider_value_changed_cd)
        slider_layout_cd.addWidget(slider_cd)
    
        # Maximum value label for coin diameter
        max_label_cd = QLabel(str(max_cd))
        slider_layout_cd.addWidget(max_label_cd)
    
        slider_value_cd = QDoubleSpinBox()
        slider_value_cd.setDecimals(1)
        slider_value_cd.setSingleStep(0.1)
        slider_value_cd.setRange(min_cd, max_cd)
        slider_value_cd.setValue(slider_cd.value() / 10.0)
        slider_value_cd.valueChanged.connect(lambda value: slider_cd.setValue(int(value * 10)))
        slider_cd.valueChanged.connect(lambda value: slider_value_cd.setValue(value / 10.0))
        slider_layout_cd.addWidget(slider_value_cd)
    
        picker_layout.addLayout(slider_layout_cd)
    
        # Slider for adjusting coin thickness
        slider_label_ct = QLabel("Adjust Coin Thickness:")
        picker_layout.addWidget(slider_label_ct)
    
        slider_layout_ct = QHBoxLayout()
        
        # Minimum value label for coin thickness
        min_ct = self.geometries.min_ct
        max_ct = self.geometries.max_ct
        ct = self.geometries.ct

        min_label_ct = QLabel(str(min_ct))
        slider_layout_ct.addWidget(min_label_ct)
    
        slider_ct = QSlider(Qt.Horizontal)
        slider_ct.setMinimum(min_ct * 10)
        slider_ct.setMaximum(max_ct * 10)
        slider_ct.setValue(ct * 10)
        slider_ct.valueChanged.connect(self.on_slider_value_changed_ct)
        slider_layout_ct.addWidget(slider_ct)
    
        # Maximum value label for coin thickness
        max_label_ct = QLabel(str(max_ct))
        slider_layout_ct.addWidget(max_label_ct)
    
        slider_value_ct = QDoubleSpinBox()
        slider_value_ct.setDecimals(1)
        slider_value_ct.setSingleStep(0.1)
        slider_value_ct.setRange(min_ct, max_ct)
        slider_value_ct.setValue(slider_ct.value() / 10.0)
        slider_value_ct.valueChanged.connect(lambda value: slider_ct.setValue(int(value * 10)))
        slider_ct.valueChanged.connect(lambda value: slider_value_ct.setValue(value / 10.0))
        slider_layout_ct.addWidget(slider_value_ct)
    
        picker_layout.addLayout(slider_layout_ct)
    
        # Slider for adjusting chip width
        slider_label_w = QLabel("Adjust Chip Width:")
        picker_layout.addWidget(slider_label_w)
    
        slider_layout_w = QHBoxLayout()
        
        # Minimum value label for chip width
        min_w = 1.0
        max_w = 70.0
        w = self.geometries.w

        min_label_w = QLabel(str(min_w))
        slider_layout_w.addWidget(min_label_w)
    
        slider_w = QSlider(Qt.Horizontal)
        slider_w.setMinimum(min_w * 10)
        slider_w.setMaximum(max_w * 10)
        slider_w.setValue(w * 10)
        slider_w.valueChanged.connect(self.on_slider_value_changed_w)
        slider_layout_w.addWidget(slider_w)
    
        # Maximum value label for chip width
        max_label_w = QLabel(str(max_w))
        slider_layout_w.addWidget(max_label_w)
    
        slider_value_w = QDoubleSpinBox()
        slider_value_w.setDecimals(1)
        slider_value_w.setSingleStep(0.1)
        slider_value_w.setRange(min_w, max_w)
        slider_value_w.setValue(slider_w.value() / 10.0)
        slider_value_w.valueChanged.connect(lambda value: slider_w.setValue(int(value * 10)))
        slider_w.valueChanged.connect(lambda value: slider_value_w.setValue(value / 10.0))
        slider_layout_w.addWidget(slider_value_w)
    
        picker_layout.addLayout(slider_layout_w)
    
        # Slider for adjusting chip height
        slider_label_h = QLabel("Adjust Chip Height:")
        picker_layout.addWidget(slider_label_h)
    
        slider_layout_h = QHBoxLayout()
        
        # Minimum value label for chip height
        min_h = 1.0
        max_h = 8.0
        h = self.geometries.h

        min_label_h = QLabel(str(min_h))
        slider_layout_h.addWidget(min_label_h)
    
        slider_h = QSlider(Qt.Horizontal)
        slider_h.setMinimum(min_h * 10)
        slider_h.setMaximum(max_h * 10)
        slider_h.setValue(h * 10)
        slider_h.valueChanged.connect(self.on_slider_value_changed_h)
        slider_layout_h.addWidget(slider_h)
    
        # Maximum value label for chip height
        max_label_h = QLabel(str(max_h))
        slider_layout_h.addWidget(max_label_h)
    
        slider_value_h = QDoubleSpinBox()
        slider_value_h.setDecimals(1)
        slider_value_h.setSingleStep(0.1)
        slider_value_h.setRange(min_h, max_h)
        slider_value_h.setValue(slider_h.value() / 10.0)
        slider_value_h.valueChanged.connect(lambda value: slider_h.setValue(int(value * 10)))
        slider_h.valueChanged.connect(lambda value: slider_value_h.setValue(value / 10.0))
        slider_layout_h.addWidget(slider_value_h)
    
        picker_layout.addLayout(slider_layout_h)
    
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
        # Iitialize all the sliders to the default values
        self.slider_value_cd = self.geometries.cd
        self.slider_value_ct = self.geometries.ct
        self.slider_value_w = self.geometries.w
        self.slider_value_h = self.geometries.h

        # Central piece in the first viewport
        central_piece = self.geometries.central_piece()
        self.add_model_to_renderer(self.viewport1["vtk_renderer"], central_piece)

        # External piece in the second viewport
        external_piece = self.geometries.external_piece()
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
    def on_slider_value_changed_cd(self, value):
        self.slider_value_cd = (value / 10.0)
    
    def on_slider_value_changed_ct(self, value):
        self.slider_value_ct = (value / 10.0)
    
    def on_slider_value_changed_w(self, value):
        self.slider_value_w = (value / 10.0)
    
    def on_slider_value_changed_h(self, value):
        self.slider_value_h = (value / 10.0)

    def on_dropdown_changed(self, index):
        print(f"Dropdown selection changed: {index}")

    def on_apply_changes(self):

        self.geometries.cd = self.slider_value_cd
        self.geometries.ct = self.slider_value_ct
        self.geometries.w = self.slider_value_w
        self.geometries.h = self.slider_value_h
 
        # Clear the existing actors from the renderer
        self.viewport1["vtk_renderer"].RemoveAllViewProps()
    
        # Render the updated central piece
        central_piece = self.geometries.central_piece()
        self.add_model_to_renderer(self.viewport1["vtk_renderer"], central_piece)

        # Clear the existing actors from the renderer
        self.viewport2["vtk_renderer"].RemoveAllViewProps()

        # Render the updated external piece
        external_piece = self.geometries.external_piece()
        self.add_model_to_renderer(self.viewport2["vtk_renderer"], external_piece)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = CadQueryViewer()
    viewer.show()
    sys.exit(app.exec())
