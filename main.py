import sys
import os
import zipfile
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
    QFileDialog,
)
from PySide6.QtCore import Qt
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from models import Geometries, def_dimensions


class CadQueryViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.geometries = Geometries()
        self.s_scale = 100.0 # Scale factor for sliders
        self.setWindowTitle("CadQuery 3D Viewer")
        self.setGeometry(100, 100, 800, 800)
        self.save_directory = os.getcwd()  # Default save directory

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
    
        # Set the interactor style to TrackballCamera
        interactor_style = vtk.vtkInteractorStyleTrackballCamera()
        vtk_interactor.SetInteractorStyle(interactor_style)
    
        return {"widget": viewport_widget, "vtk_widget": vtk_widget, "vtk_renderer": vtk_renderer}

    def create_picker_section(self):
        """
        Create the picker section for modifying values.
        """
        picker_widget = QWidget()
        picker_layout = QVBoxLayout(picker_widget)
        picker_layout.setAlignment(Qt.AlignTop)  # Align the layout to the top

        self.slider_values = {}
        self.sliders = {}
        self.min_slider_labels = {}
        self.max_slider_labels = {}
    
        # Slider for adjusting coin diameter
        slider_label_cd = QLabel("Adjust Coin Diameter:")
        picker_layout.addWidget(slider_label_cd)
    
        slider_layout_cd = self.create_slider("cd")
    
        picker_layout.addLayout(slider_layout_cd)
    
        # Slider for adjusting coin thickness
        slider_label_ct = QLabel("Adjust Coin Thickness:")
        picker_layout.addWidget(slider_label_ct)
    
        slider_layout_ct = self.create_slider("ct")

        picker_layout.addLayout(slider_layout_ct)
    
        # Slider for adjusting chip width
        slider_label_w = QLabel("Adjust Chip Width:")
        picker_layout.addWidget(slider_label_w)
    
        slider_layout_w = self.create_slider("w")
    
        picker_layout.addLayout(slider_layout_w)
    
        # Slider for adjusting chip height
        slider_label_h = QLabel("Adjust Chip Height:")
        picker_layout.addWidget(slider_label_h)
    
        slider_layout_h = self.create_slider("h")
    
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

        # ComboBox for selecting file format
        format_label = QLabel("Select File Format:")
        picker_layout.addWidget(format_label)
        self.format_combobox = QComboBox()
        self.format_combobox.addItems(["STEP", "STL"])
        picker_layout.addWidget(self.format_combobox)

        # Button to download the external chip STEP file
        download_external_button = QPushButton("Download External Chip")
        download_external_button.clicked.connect(self.download_external_chip)
        picker_layout.addWidget(download_external_button)

        # Button to download the middle chip STEP file
        download_middle_button = QPushButton("Download Middle Chip")
        download_middle_button.clicked.connect(self.download_middle_chip)
        picker_layout.addWidget(download_middle_button)

        # Button to download both STEP files as a ZIP
        download_both_button = QPushButton("Download Both as ZIP")
        download_both_button.clicked.connect(self.download_both_as_zip)
        picker_layout.addWidget(download_both_button)

        # Button to select the directory to save files
        select_directory_button = QPushButton("Select Directory")
        select_directory_button.clicked.connect(self.select_directory)
        picker_layout.addWidget(select_directory_button)
        
        return picker_widget

    def create_slider(self, label):
        """
        Create a slider with a label and return the slider and value label.
        """
        slider_layout = QHBoxLayout()
        
        # Minimum value label for the slider
        min_val = getattr(self.geometries, "min_" + label)
        max_val = getattr(self.geometries, "max_" + label)
        val = getattr(self.geometries, label)
    
        self.min_slider_labels[label] = QLabel(str(min_val))
        self.min_slider_labels[label].setFixedWidth(30)  # Set a fixed width for the label
        slider_layout.addWidget(self.min_slider_labels[label])
        
        self.sliders[label] = QSlider(Qt.Horizontal)
        self.sliders[label].setMinimum(min_val * self.s_scale)  # Scale by 10 to allow one decimal place
        self.sliders[label].setMaximum(max_val * self.s_scale)
        self.sliders[label].setValue(val * self.s_scale)
        self.sliders[label].valueChanged.connect(getattr(self, f"on_slider_value_changed_{label}"))
        self.sliders[label].sliderReleased.connect(self.update_slider_ranges)
        slider_layout.addWidget(self.sliders[label], 1)  # Add stretch factor to the slider
        
        # Maximum value label for the slider
        self.max_slider_labels[label] = QLabel(str(max_val))
        self.max_slider_labels[label].setFixedWidth(30)  # Set a fixed width for the label
        slider_layout.addWidget(self.max_slider_labels[label])
        
        self.slider_values[label] = QDoubleSpinBox()
        self.slider_values[label].setDecimals(2)
        self.slider_values[label].setSingleStep(0.1)
        self.slider_values[label].setRange(min_val, max_val)
        self.slider_values[label].setValue(self.sliders[label].value() / self.s_scale)
        self.slider_values[label].valueChanged.connect(lambda value: self.sliders[label].setValue(int(value * self.s_scale)))
        self.sliders[label].valueChanged.connect(lambda value: self.slider_values[label].setValue(value / self.s_scale))
        self.slider_values[label].editingFinished.connect(self.update_slider_ranges)
        self.slider_values[label].setFixedWidth(80)  # Set a fixed width for the spin box
        slider_layout.addWidget(self.slider_values[label])
    
        return slider_layout
    
    def download_external_chip(self):
        file_format = self.format_combobox.currentText().lower()
        file_path = os.path.join(self.save_directory, f"external_chip.{file_format}")
        self.geometries.external_piece().export(file_path)
        print(f"External chip {file_format.upper()} file saved to {file_path}")

    def download_middle_chip(self):
        file_format = self.format_combobox.currentText().lower()
        file_path = os.path.join(self.save_directory, f"middle_chip.{file_format}")
        self.geometries.central_piece().export(file_path)
        print(f"Middle chip {file_format.upper()} file saved to {file_path}")

    def download_both_as_zip(self):
        file_format = self.format_combobox.currentText().lower()
        external_file_path = os.path.join(self.save_directory, f"external_chip.{file_format}")
        middle_file_path = os.path.join(self.save_directory, f"middle_chip.{file_format}")
        zip_file_path = os.path.join(self.save_directory, "chips.zip")

        self.geometries.external_piece().export(external_file_path)
        self.geometries.central_piece().export(middle_file_path)

        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            zipf.write(external_file_path, os.path.basename(external_file_path))
            zipf.write(middle_file_path, os.path.basename(middle_file_path))

        print(f"Both {file_format.upper()} files saved to {zip_file_path}")

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.save_directory = directory
            print(f"Save directory set to {self.save_directory}")

    
    
    def render_models(self):
        """
        Render the central and external pieces in their respective viewports.
        """
        # Iitialize all the sliders to the default values
        self.slider_values['cd'].setValue(self.geometries.cd)
        self.slider_values['ct'].setValue(self.geometries.ct)
        self.slider_values['w'].setValue(self.geometries.w)
        self.slider_values['h'].setValue(self.geometries.h)

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
        self.slider_values['cd'].setValue(value / self.s_scale)
        self.geometries.cd = (value / self.s_scale)
    
    def on_slider_value_changed_ct(self, value):
        self.slider_values['ct'].setValue(value / self.s_scale)
        self.geometries.ct = (value / self.s_scale)
    
    def on_slider_value_changed_w(self, value):
        self.slider_values['w'].setValue(value / self.s_scale)
        self.geometries.w = (value / self.s_scale)
    
    def on_slider_value_changed_h(self, value):
        self.slider_values['h'].setValue(value / self.s_scale)
        self.geometries.h = (value / self.s_scale)

    def on_dropdown_changed(self, index):
        print(f"Dropdown selection changed: {index}")

    def update_slider_ranges(self):
        # Update the ranges of the sliders based on the current values
        min_cd = self.geometries.min_cd
        max_cd = self.geometries.max_cd
        cd = self.slider_values['cd']

        min_ct = self.geometries.min_ct
        max_ct = self.geometries.max_ct
        ct = self.slider_values['ct']

        min_w = self.geometries.min_w
        max_w = self.geometries.max_w
        w = self.slider_values['w']

        min_h = self.geometries.min_h
        max_h = self.geometries.max_h
        h = self.slider_values['h']

        self.sliders['cd'].setRange(min_cd * self.s_scale, max_cd * self.s_scale)
        self.sliders['ct'].setRange(min_ct * self.s_scale, max_ct * self.s_scale)
        self.sliders['w'].setRange(min_w * self.s_scale, max_w * self.s_scale)
        self.sliders['h'].setRange(min_h * self.s_scale, max_h * self.s_scale)

        self.slider_values['cd'].setRange(min_cd, max_cd)
        self.slider_values['ct'].setRange(min_ct, max_ct)
        self.slider_values['w'].setRange(min_w, max_w)
        self.slider_values['h'].setRange(min_h, max_h)

        self.min_slider_labels['cd'].setText(str(min_cd))
        self.max_slider_labels['cd'].setText(str(max_cd))
        self.min_slider_labels['ct'].setText(str(min_ct))
        self.max_slider_labels['ct'].setText(str(max_ct))
        self.min_slider_labels['w'].setText(str(min_w))
        self.max_slider_labels['w'].setText(str(max_w))
        self.min_slider_labels['h'].setText(str(min_h))
        self.max_slider_labels['h'].setText(str(max_h))


    def on_apply_changes(self):

        self.geometries.cd = self.slider_values['cd'].value()
        self.geometries.ct = self.slider_values['ct'].value()
        self.geometries.w = self.slider_values['w'].value()
        self.geometries.h = self.slider_values['h'].value()
 
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
