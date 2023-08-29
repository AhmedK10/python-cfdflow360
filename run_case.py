import flow360 as fl

############################################
params = fl.SurfaceMeshingParams(
    max_edge_length=0.16,
    curvatureResolutionAngle= 15,
    growthRate= 1.2,
        edges={
        "leadingEdge": fl.meshing.Aniso(method="angle", value=5),
        "trailingEdge": fl.meshing.Aniso(method="height", value=0.001),
        "root": fl.meshing.Aniso(method="aspectRatio", value=10),
        "tip": fl.meshing.UseAdjacent(),
        "fuselageSplit": fl.meshing.ProjectAniso(),
    },
    faces={
        "rightWing": fl.meshing.Face(max_edge_length=0.08),
        "leftWing": fl.meshing.Face(max_edge_length=0.08),
        "fuselage": fl.meshing.Face(max_edge_length=0.1),
    },
)

surface_mesh = fl.SurfaceMesh.create(
    "airplane.csm", params=params, name="airplane-new-surf-mesh"
)
surface_mesh = surface_mesh.submit()

#####################################

params = fl.VolumeMeshingParams(
    refinementFactor= 1,
    volume=fl.meshing.Volume(first_layer_thickness=1e-5),
)

volume_mesh = surface_mesh.create_volume_mesh("airplane-new-volume-mesh", params=params)
volume_mesh = volume_mesh.submit()

####################################

# params = fl.Flow360Params(
#     geometry=fl.Geometry(
#         ref_area=1.15315084119231,
#         moment_length=(1.47602, 0.801672958512342, 1.47602),
#         mesh_unit="m",
#     ),
#     freestream=fl.Freestream.from_speed((286, "m/s"), alpha=3.06),
#     time_stepping=fl.TimeStepping(max_pseudo_steps=500),
#     boundaries={
#         "1": fl.NoSlipWall(name="wing"),
#         "2": fl.SlipWall(name="symmetry"),
#         "3": fl.FreestreamBoundary(name="freestream"),
#     },
# )



####################################
