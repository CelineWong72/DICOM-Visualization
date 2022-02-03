import sys
import vtk
from PyQt5.QtWidgets import QApplication, QMainWindow, QMdiArea, QAction, QMdiSubWindow,\
    QToolBar, QLabel, QPushButton, QDockWidget, QGridLayout, QVBoxLayout, QLineEdit, QTextEdit, QWidget, QToolBox
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import Qt
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class AppWindow(QMainWindow):
    count = 0

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon('icons/schwi_icon.png'))
        self.setWindowTitle("Schwi - Scientific Data Visualizer")

        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)
        self.resize(1200, 800)

        self.menu_bar()
        self.tool_bar()
        self.docker_widget()
        self.show()

    def menu_bar(self):
        bar = self.menuBar()
        file = bar.addMenu('File')
        file_new = self.create_action('New', 'icons/plus_icon.png', 'Ctrl+N', self.file_open_thr)
        file_exit = self.create_action('Exit', 'icons/exit_icon.png', 'Ctrl+Q', self.close)
        self.add_action(file, (file_new, file_exit))

        view = bar.addMenu('View')
        view_shortcut = self.create_action('Show navigation', 'icons/navi_icon.png', 'F4', self.tool_bar)
        view_variable = self.create_action('Show tool widget', 'icons/tool_icon.png', 'F2', self.docker_widget)
        # view_restore = self.create_action('Restore', 'icons/restore_icon.png', 'Ctrl+Y', self.file_open)
        view_tiled = self.create_action('Tiled Mode', 'icons/tile_icon.png', 'Ctrl+T', self.show_tiled)
        # self.add_action(view, (view_shortcut, view_variable, view_restore, view_tiled))
        self.add_action(view, (view_shortcut, view_variable, view_tiled))

    def tool_bar(self):
        navToolBar = self.addToolBar("Navigation")
        newAction = self.create_action('New', 'icons/plus_icon.png', 'Ctrl+N', self.file_open_thr)
        tileAction = self.create_action('Tiled Mode', 'icons/tile_icon.png', 'Ctrl+T', self.show_tiled)
        toolAction = self.create_action('Show tool widget', 'icons/tool_icon.png', 'F2', self.docker_widget)

        self.add_action(navToolBar, (newAction, tileAction, toolAction))
        navToolBar.setFloatable(False)

    def create_action(self, text, icon=None, shortcut=None, implement=None, signal='triggered'):
        action = QtWidgets.QAction(text, self)
        if icon is not None:
            action.setIcon(QtGui.QIcon(icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if implement is not None:
            getattr(action, signal).connect(implement)
        return action

    def add_action(self, dest, actions):
        for action in actions:
            if action is None:
                dest.addSeperator()
            else:
                dest.addAction(action)

    def show_tiled(self):
        self.mdi.tileSubWindows()

    def file_open_thr(self):
        AppWindow.count = AppWindow.count + 1
        self.filename = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')

        if self.filename:
            self.vtk(self.filename)

    def vtk(self, filename):
        self.sub = QMdiSubWindow()
        self.frame = Qt.QFrame()

        self.add_dataset(filename)
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.sub.setWidget(self.vtkWidget)
        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(0.2, 0.2, 0.2)
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        # Set Titlebar
        self.sub.setWindowTitle("Dataset " + str(AppWindow.count))

        self.imageData = vtk.vtkImageData()
        self.reader = vtk.vtkDICOMImageReader()

        self.volumeMapper = vtk.vtkSmartVolumeMapper()
        self.volumeProperty = vtk.vtkVolumeProperty()
        self.gradientOpacity = vtk.vtkPiecewiseFunction()
        self.scalarOpacity = vtk.vtkPiecewiseFunction()
        self.color = vtk.vtkColorTransferFunction()
        self.volume = vtk.vtkVolume()
        self.reader.SetDirectoryName(filename)
        self.reader.SetDataScalarTypeToUnsignedShort()
        self.reader.UpdateWholeExtent()
        self.reader.Update()
        self.imageData.ShallowCopy(self.reader.GetOutput())

        self.volumeMapper.SetBlendModeToComposite()
        self.volumeMapper.SetRequestedRenderModeToGPU()
        self.volumeMapper.SetInputData(self.imageData)
        self.volumeProperty.ShadeOn()
        self.volumeProperty.SetInterpolationTypeToLinear()
        self.volumeProperty.SetAmbient(0.1)
        self.volumeProperty.SetDiffuse(0.9)
        self.volumeProperty.SetSpecular(0.2)
        self.volumeProperty.SetSpecularPower(10.0)
        self.gradientOpacity.AddPoint(0.0, 0.0)
        self.gradientOpacity.AddPoint(2000.0, 1.0)
        self.volumeProperty.SetGradientOpacity(self.gradientOpacity)
        self.scalarOpacity.AddPoint(-800.0, 0.0)
        self.scalarOpacity.AddPoint(-750.0, 1.0)
        self.scalarOpacity.AddPoint(-350.0, 1.0)
        self.scalarOpacity.AddPoint(-300.0, 0.0)
        self.scalarOpacity.AddPoint(-200.0, 0.0)
        self.scalarOpacity.AddPoint(-100.0, 1.0)
        self.scalarOpacity.AddPoint(1000.0, 0.0)
        self.scalarOpacity.AddPoint(2750.0, 0.0)
        self.scalarOpacity.AddPoint(2976.0, 1.0)
        self.scalarOpacity.AddPoint(3000.0, 0.0)
        self.volumeProperty.SetScalarOpacity(self.scalarOpacity)
        self.color.AddRGBPoint(-750.0, 0.08, 0.05, 0.03)
        self.color.AddRGBPoint(-350.0, 0.39, 0.25, 0.16)
        self.color.AddRGBPoint(-200.0, 0.80, 0.80, 0.80)
        self.color.AddRGBPoint(2750.0, 0.70, 0.70, 0.70)
        self.color.AddRGBPoint(3000.0, 0.35, 0.35, 0.35)
        self.volumeProperty.SetColor(self.color)
        self.volume.SetMapper(self.volumeMapper)
        self.volume.SetProperty(self.volumeProperty)
        self.ren.AddVolume(self.volume)
        self.ren.ResetCamera()

        self.mdi.addSubWindow(self.sub)
        self.sub.show()
        self.iren.Initialize()
        self.iren.Start()

    def docker_widget(self):
        dockWid = QDockWidget('Tool', self)
        layout = QGridLayout()
        styleSheet = """
                        QToolBox::tab {
                            border: 1px solid #C4C4C4;
                            border-bottom-color: RGB(0, 0, 225);
                        }
                        QToolBox::tab:selected {
                            background-color: #4E14C2;
                            color: white;
                            border-bottom-color: none;
                        }
        """

        toolbox = QToolBox()
        layout.addWidget(toolbox, 0, 0)

        # TAB TRANSFORMATION
        w1 = QWidget()
        scale = QLabel('Scale')
        sx_coord = QLabel('X')
        sy_coord = QLabel('Y')
        sz_coord = QLabel('Z')
        rotate = QLabel('Rotate')
        rx_coord = QLabel('X')
        ry_coord = QLabel('Y')
        rz_coord = QLabel('Z')
        translate = QLabel('Translate')
        tx_coord = QLabel('X')
        ty_coord = QLabel('Y')
        tz_coord = QLabel('Z')

        self.scaleX = QLineEdit(self)
        self.scaleY = QLineEdit(self)
        self.scaleZ = QLineEdit(self)
        scalee = QPushButton('Apply', self)
        scalee.clicked.connect(self.scaleXYZ)
        self.scaleX.setFixedWidth(30)
        self.scaleY.setFixedWidth(30)
        self.scaleZ.setFixedWidth(30)
        self.rotateX = QLineEdit(self)
        self.rotateY = QLineEdit(self)
        self.rotateZ = QLineEdit(self)
        rotatee = QPushButton('Apply', self)
        rotatee.clicked.connect(self.rotateXYZ)
        self.rotateX.setFixedWidth(30)
        self.rotateY.setFixedWidth(30)
        self.rotateZ.setFixedWidth(30)
        self.translateX = QLineEdit()
        self.translateY = QLineEdit()
        self.translateZ = QLineEdit()
        self.translateX.setFixedWidth(30)
        self.translateY.setFixedWidth(30)
        self.translateZ.setFixedWidth(30)
        translatee = QPushButton('Apply', self)
        translatee.clicked.connect(self.translateXYZ)

        grid = QGridLayout()
        grid.setSpacing(5)

        grid.addWidget(scale, 1, 0)
        grid.addWidget(sx_coord, 1, 1)
        grid.addWidget(self.scaleX, 1, 2)
        grid.addWidget(sy_coord, 1, 3)
        grid.addWidget(self.scaleY, 1, 4)
        grid.addWidget(sz_coord, 1, 5)
        grid.addWidget(self.scaleZ, 1, 6)
        grid.addWidget(scalee, 1, 7)

        grid.addWidget(rotate, 2, 0)
        grid.addWidget(rx_coord, 2, 1)
        grid.addWidget(self.rotateX, 2, 2)
        grid.addWidget(ry_coord, 2, 3)
        grid.addWidget(self.rotateY, 2, 4)
        grid.addWidget(rz_coord, 2, 5)
        grid.addWidget(self.rotateZ, 2, 6)
        grid.addWidget(rotatee, 2, 7)

        grid.addWidget(translate, 3, 0)
        grid.addWidget(tx_coord, 3, 1)
        grid.addWidget(self.translateX, 3, 2)
        grid.addWidget(ty_coord, 3, 3)
        grid.addWidget(self.translateY, 3, 4)
        grid.addWidget(tz_coord, 3, 5)
        grid.addWidget(self.translateZ, 3, 6)
        grid.addWidget(translatee, 3, 7)
        w1.setLayout(grid)

        toolbox.addItem(w1, 'Transformation')

        # TAB MAGNIFIER
        w2 = QWidget()
        grid = QGridLayout()
        grid.setSpacing(10)

        z_in = QPushButton('Zoom In', self)
        z_in.setIcon(QtGui.QIcon('icons/zoom-in_icon.png'))
        z_in.clicked.connect(self.zoom_in)
        z_out = QPushButton('Zoom Out', self)
        z_out.setIcon(QtGui.QIcon('icons/zoom-out_icon.png'))
        z_in.clicked.connect(self.zoom_out)

        grid.addWidget(z_in, 0, 0)
        grid.addWidget(z_out, 0, 1)

        w2.setLayout(grid)
        toolbox.addItem(w2, 'Magnifier')

        # TAB WIDGET
        w3 = QWidget()
        grid_w = QGridLayout()
        grid_w.setSpacing(10)

        axis = QPushButton('3D Axis', self)
        axis.setIcon(QtGui.QIcon('icons/axis_icon.png'))
        axis.clicked.connect(self.thrDaxis)
        box = QPushButton('3D Box', self)
        box.setIcon(QtGui.QIcon('icons/cube_icon.png'))
        box.clicked.connect(self.thrBox)

        grid_w.addWidget(axis, 0, 0)
        grid_w.addWidget(box, 0, 1)

        w3.setLayout(grid_w)
        toolbox.addItem(w3, 'Widget')

        # TAB DATASET
        w4 = QWidget()
        self.grid_d = QGridLayout()
        self.grid_d.setSpacing(5)

        filename = 'Unknown'
        self.add_dataset(filename)

        w4.setLayout(self.grid_d)
        toolbox.addItem(w4, 'Dataset')

        #############################
        toolbox.setCurrentIndex(0)
        self.setStyleSheet(styleSheet)
        self.setLayout(layout)

        #
        dockWid.setWidget(toolbox)
        dockWid.setFloating(False)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dockWid)

    def add_dataset(self, filename):
        file_loc = QLabel('File Location ' + str(AppWindow.count) + ': ')
        location = QLabel(filename)

        self.grid_d.addWidget(file_loc, AppWindow.count, 0)
        self.grid_d.addWidget(location, AppWindow.count, 1)

        return self.grid_d

    def zoom_in(self):
        self.ren.GetActiveCamera().Zoom(2.2)

    def zoom_out(self):
        self.ren.GetActiveCamera().Zoom(0.8)

    def thrDaxis(self):
        axesActor = vtk.vtkAxesActor()
        self.axes = vtk.vtkOrientationMarkerWidget()
        self.axes.SetOrientationMarker(axesActor)
        self.axes.SetInteractor(self.iren)
        self.axes.EnabledOn()
        self.axes.InteractiveOn()
        self.ren.ResetCamera()
        # self.frame.setLayout(self.vl)
        # self.setCentralWidget(self.frame)
        # self.show()
        # self.iren.Initialize()

    def thrBox(self):
        outline = vtk.vtkOutlineFilter()
        outline.SetInputConnection(self.reader.GetOutputPort())

        outlineMapper = vtk.vtkPolyDataMapper()
        outlineMapper.SetInputConnection(outline.GetOutputPort())

        self.outlineActor = vtk.vtkActor()
        self.outlineActor.SetMapper(outlineMapper)
        self.outlineActor.GetProperty().SetColor(1, 1, 1)
        self.ren.AddActor(self.outlineActor)
        self.ren.ResetCamera()

    def scaleXYZ(self):
        x = int(self.scaleX.text())
        y = int(self.scaleY.text())
        z = int(self.scaleZ.text())
        # print(x, y, z)
        # self.volume.SetOrientation(x, y, z)
        self.ren.Render()
        self.ren.EraseOff()
        self.outlineActor.SetScale(x, y, z)
        self.volume.SetScale(x, y, z)
        self.ren.Render()
        self.ren.EraseOn()

    def rotateXYZ(self):
        x = int(self.rotateX.text())
        y = int(self.rotateY.text())
        z = int(self.rotateZ.text())
        self.outlineActor.SetOrientation(x, y, z)
        self.volume.SetOrientation(x, y, z)
        self.ren.Render()
        self.ren.EraseOff()

        self.volume.RotateX(x)
        self.volume.RotateY(y)
        self.volume.RotateZ(z)
        self.outlineActor.RotateX(x)
        self.outlineActor.RotateY(y)
        self.outlineActor.RotateZ(z)

        self.ren.Render()
        self.ren.EraseOn()

    def translateXYZ(self):
        x = int(self.translateX.text())
        y = int(self.translateY.text())
        z = int(self.translateZ.text())
        # self.volume.SetOrientation(0, 0, 0)
        self.ren.Render()
        self.ren.EraseOff()
        self.outlineActor.SetPosition(x, y, z)
        self.volume.SetPosition(x, y, z)
        self.ren.Render()
        self.ren.EraseOn()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app_win = AppWindow()
    sys.exit(app.exec())