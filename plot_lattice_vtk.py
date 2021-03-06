from paraview.simple import *
import vtk
import numpy as np

import sys

if sys.argv[1]:
    filename = sys.argv[1]
else:
    filename = '/home/miguelito/myprojects/blog_posts/lattice/output/allcontrols000048.vtu'

reader = XMLUnstructuredGridReader(FileName=[filename])
radius_scale = 1.0

data = servermanager.Fetch(reader)
cells = data.GetCells()
cells.InitTraversal()

# Check there is cell data
assert data.GetCellData().GetArray(0)

list_cylinders = []

import vtk
# line source
line = vtk.vtkLineSource()

# tube source
tube = vtk.vtkTubeFilter()
tube.SetInputConnection(line.GetOutputPort())
tube.SetCapping(True)
tube.SetNumberOfSides(6)

model = vtk.vtkAppendPolyData()
i = 0

cell_data_arr = data.GetCellData().GetArray(0)

for i in range(cells.GetNumberOfCells()):
    cell = data.GetCell(i)
    radius_tup = cell_data_arr.GetTuple(i)
    [xm, xM, ym, yM, zm, zM] = cell.GetBounds()

    vert1 = np.array([xm, ym, zm])
    vert2 = np.array([xM, ym, zm])
    vert3 = np.array([xm, yM, zm])
    vert4 = np.array([xM, yM, zm])

    vert5 = np.array([xm, ym, zM])
    vert6 = np.array([xM, ym, zM])
    vert7 = np.array([xM, yM, zM])
    vert8 = np.array([xm, yM, zM])

    midpoint1 = (vert1 + vert2 + vert3 + vert4) / 4.0
    midpoint2 = (vert5 + vert6 + vert7 + vert8) / 4.0

    midpoint3 = (vert1 + vert3 + vert8 + vert5) / 4.0
    midpoint4 = (vert2 + vert6 + vert4 + vert7) / 4.0

    midpoint5 = (vert1 + vert2 + vert5 + vert6) / 4.0
    midpoint6 = (vert3 + vert4 + vert7 + vert8) / 4.0

    # Exterior trusses
    truss1 = np.array([vert1, vert4])
    truss2 = np.array([vert3, vert2])

    truss3 = np.array([vert8, vert6])
    truss4 = np.array([vert5, vert7])

    truss5 = np.array([vert6, vert4])
    truss6 = np.array([vert2, vert7])

    truss7 = np.array([vert1, vert8])
    truss8 = np.array([vert3, vert5])

    truss9 = np.array([vert1, vert6])
    truss10 = np.array([vert2, vert5])

    truss11 = np.array([vert8, vert4])
    truss12 = np.array([vert3, vert7])

    # Inner trusses
    itruss1 = np.array([midpoint2, midpoint5])
    itruss3 = np.array([midpoint2, midpoint6])
    itruss2 = np.array([midpoint1, midpoint5])
    itruss4 = np.array([midpoint1, midpoint6])

    itruss5 = np.array([midpoint1, midpoint3])
    itruss7 = np.array([midpoint1, midpoint4])
    itruss6 = np.array([midpoint2, midpoint3])
    itruss8 = np.array([midpoint2, midpoint4])

    itruss9 = np.array([midpoint4, midpoint6])
    itruss10 = np.array([midpoint4, midpoint5])
    itruss11 = np.array([midpoint3, midpoint5])
    itruss12 = np.array([midpoint3, midpoint6])

    xy_trusses = [truss1, truss2, itruss9, itruss10, itruss11, itruss12, truss3, truss4]
    yz_trusses = [truss5, truss6, itruss1, itruss2, itruss3, itruss4, truss7, truss8]
    zx_trusses = [truss9, truss10, itruss5, itruss6, itruss7, itruss8, truss11, truss12]


    #for diag in [truss1, truss2, truss3, truss4, truss5, truss6, truss7, truss8, truss9, truss10, truss11, truss12, itruss1, itruss3, itruss2, itruss4, itruss5, itruss7, itruss6, itruss8, itruss9, itruss10, itruss11, itruss12]:
    for truss_xy, truss_zy, truss_zx in zip(xy_trusses, yz_trusses, zx_trusses):
        i += 1
        for j, diag in enumerate([truss_xy, truss_zx, truss_zy]):
            input1 = vtk.vtkPolyData()
            #draw line
            line.SetPoint1(diag[0])
            line.SetPoint2(diag[1])
            line.Update()

            #set tube radius
            tube.SetRadius(radius_scale*radius_tup[j])
            tube.Update()

            input1.ShallowCopy(tube.GetOutput())

            model.AddInputData(input1)

model.Update()
print("Number of cylinders {}".format(i))
output = vtk.vtkXMLPolyDataWriter()
output.SetInputData(model.GetOutput())
output.SetFileName('octet_truss.vtp')
output.Write()

# Create the graphics structure. The renderer renders into the render
# window. The render window interactor captures mouse events and will
# perform appropriate camera or actor manipulation depending on the
# nature of the events.
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

colors = vtk.vtkNamedColors()
# Set the background color.
bkg = map(lambda x: x / 255.0, [26, 51, 102, 255])
colors.SetColor("BkgColor", *bkg)

# The mapper is responsible for pushing the geometry into the graphics
# library. It may also do color mapping, if scalars or other
# attributes are defined.
cylinderMapper = vtk.vtkPolyDataMapper()
cylinderMapper.SetInputConnection(model.GetOutputPort())

# The actor is a grouping mechanism: besides the geometry (mapper), it
# also has a property, transformation matrix, and/or texture map.
# Here we set its color and rotate it -22.5 degrees.
cylinderActor = vtk.vtkActor()
cylinderActor.SetMapper(cylinderMapper)
cylinderActor.GetProperty().SetColor(colors.GetColor3d("Beige"))
cylinderActor.RotateX(30.0)
cylinderActor.RotateY(-45.0)

# Add the actors to the renderer, set the background and size
ren.AddActor(cylinderActor)
renWin.SetSize(300, 300)
ren.SetBackground(colors.GetColor3d("SlateGray"))
renWin.SetWindowName('Cylinder')

# This allows the interactor to initalize itself. It has to be
# called before an event loop.
iren.Initialize()

# We'll zoom in a little by accessing the camera and invoking a "Zoom"
# method on it.
ren.ResetCamera()
ren.GetActiveCamera().Zoom(1.5)
renWin.Render()

# Start the event loop.
iren.Start()

exporter = vtk.vtkX3DExporter()
exporter.SetRenderWindow(renWin)
exporter.SetFileName("small_lattice.x3d")
exporter.Write()
exporter.Update()
