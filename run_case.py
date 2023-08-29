import flow360 as fl
import matplotlib.pyplot as plt
import time


def wait_for_simulations(created_cases):
    for case in created_cases:
        #case.submit()
        while not case.is_finished():
            print(f"Waiting for simulation {case.name} to finish...")
            time.sleep(60)  # Wait for 1 minute before checking again

############################################
# params = fl.SurfaceMeshingParams(
#     max_edge_length=0.16,
#     curvatureResolutionAngle= 15,
#     growthRate= 1.2,
#         edges={
#         "leadingEdge": fl.meshing.Aniso(method="angle", value=5),
#         "trailingEdge": fl.meshing.Aniso(method="height", value=0.001),
#         "root": fl.meshing.Aniso(method="aspectRatio", value=10),
#         "tip": fl.meshing.UseAdjacent(),
#         "fuselageSplit": fl.meshing.ProjectAniso(),
#     },
#     faces={
#         "rightWing": fl.meshing.Face(max_edge_length=0.08),
#         "leftWing": fl.meshing.Face(max_edge_length=0.08),
#         "fuselage": fl.meshing.Face(max_edge_length=0.1),
#     },
# )

params = fl.SurfaceMeshingParams("surface.json")
surface_mesh = fl.SurfaceMesh.create("airplane.csm", params=params, name="airplane-new-surf-mesh")
surface_mesh = surface_mesh.submit()

#####################################

# params = fl.VolumeMeshingParams(
#     refinementFactor=1,
#     volume=fl.meshing.Volume(
#         first_layer_thickness=1e-5,
#         growth_rate=1.2
#     ),
# )


params = fl.VolumeMeshingParams("volume.json")
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
#     time_stepping=fl.TimeStepping(CFL=fl.TimeSteppingCFL.adaptive()),
#     boundaries={
#         "1": fl.NoSlipWall(name="wing"),
#         "2": fl.SlipWall(name="symmetry"),
#         "3": fl.FreestreamBoundary(name="freestream"),
#     },
# )


created_cases = []
angle_of_attack_values = list(range(-5, 26, 5))

for alpha in angle_of_attack_values:
    params = fl.Flow360Params(
        geometry=fl.Geometry(
            ref_area=12.5,
            moment_center=(5, 0, 0),
            moment_length=(5, 2.5, 5),
            mesh_unit="m"
        ),
        freestream=fl.Freestream(
            mu_ref=4.2925193198151646e-8,
            Mach=0.1002074659499542,
            temperature=288.15,
            alpha=alpha,
            beta=0
        ),
        time_stepping=fl.TimeStepping(CFL=fl.TimeSteppingCFL.adaptive()),
        boundaries={
            "fluid/fuselage": fl.NoSlipWall(name="wing"),
            "fluid/leftWing": fl.NoSlipWall(name="symmetry"),
            "fluid/rightWing": fl.NoSlipWall(name="symmetry"),
            "fluid/farfield": fl.FreestreamBoundary(name="freestream")
        },
        navier_stokes_solver=fl.NavierStokesSolver(
            absolute_tolerance=1e-8,
            linear_iterations=35,
            # kappa_MUSCL=-1,
            order_of_accuracy=2
        ),
        turbulence_model_solver=fl.TurbulenceModelSolver(
            model_type="SpalartAllmaras",
            absolute_tolerance=1e-7,
            linear_iterations=25,
            # kappa_MUSCL=-1,
            order_of_accuracy=2
        ),
        # volume_output=fl.VolumeOutput(
        #     output_format="tecplot",
        #     primitive_vars=False,
        #     vorticity=False,
        #     cp=True,
        #     mach=True,
        #     qcriterion=True
        # ),
        # surface_output=fl.SurfaceOutput(
        #     cp=True,
        #     cf=False,
        #     cf_vec=True,
        #     output_format="tecplot"
        # )
    )

    # Create a simulation case for each alpha
    case = volume_mesh.create_case(f"airplane-case-alpha-{alpha}", params)
    created_cases.append(case)


wait_for_simulations(created_cases)
print("All simulations have been submitted.")
lift_coefficients = []
angles_of_attack = []

for case in created_cases:
    lift_coefficient = 0.75  # Replace with the actual calculated lift coefficient
    angle_of_attack = case.params.freestream.alpha
    lift_coefficients.append(lift_coefficient)
    angles_of_attack.append(angle_of_attack)

plt.figure()
plt.plot(angle_of_attack_values, lift_coefficients, marker='o')
plt.xlabel('Angle of Attack (degrees)')
plt.ylabel('Lift Coefficient (CL)')
plt.title('CL vs Angle of Attack')
plt.grid()
plt.show()
print("All simulations have been post-processed.")




####################################
