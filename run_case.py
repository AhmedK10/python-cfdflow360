import flow360 as fl
import matplotlib.pyplot as plt
import time

# a function to make sure a simulation is finished before moving on to the next one
def wait_for_simulation(case, alpha):
    while not case.is_finished():
        print(f"Waiting for simulation with alpha={alpha} to finish...")
        time.sleep(200)

alpha_values = []
cl_values = []

# iterating through all aoa values and creating seprate simulations
angle_of_attack_values = list(range(-5, 26, 5))
for alpha in angle_of_attack_values:
    # creating and submitting the surface mesh from the json file
    params_surf = fl.SurfaceMeshingParams("surface.json")
    surface_mesh = fl.SurfaceMesh.create("airplane.csm", params=params_surf, name=f"airplane-surf-mesh-alpha({alpha})")
    surface_mesh = surface_mesh.submit()

    # creating and submitting the volume mesh from the json file
    params_vol = fl.VolumeMeshingParams("volume.json")
    volume_mesh = surface_mesh.create_volume_mesh(f"airplane-volume-mesh-alpha({alpha})", params=params_vol)
    volume_mesh = volume_mesh.submit()

    # creating simulations setup with adjusted aoa values per simulation
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
            "fluid/leftWing": fl.NoSlipWall(name="leftWing"),
            "fluid/rightWing": fl.NoSlipWall(name="rightWing"),
            "fluid/farfield": fl.FreestreamBoundary(name="freestream")
        },
        navier_stokes_solver=fl.NavierStokesSolver(
            absolute_tolerance=1e-8,
            linear_iterations=35,
            order_of_accuracy=2
        ),
        turbulence_model_solver=fl.TurbulenceModelSolver(
            model_type="SpalartAllmaras",
            absolute_tolerance=1e-7,
            linear_iterations=25,
            order_of_accuracy=2
        ),
    )

    # Create a simulation case for each alpha
    case = volume_mesh.create_case(f"airplane-case-alpha({alpha})", params)
    case = case.submit()
    wait_for_simulation(case, alpha)
    time.sleep(100)
    aoa = case.params.freestream.alpha
    # Getting the last CL value
    cl = case.results.total_forces.raw["CL"][-1]
    alpha_values.append(aoa)
    cl_values.append(cl)

# confirmation of finishing all simulations
print("All simulations have been performed")

# making a plot of CL values against corresponding aoa
plt.plot(alpha_values, cl_values, marker='o')
plt.xlabel("Angle of Attack (alpha)")
plt.ylabel("Lift Coefficient (CL)")
plt.title("CL vs. Alpha")
plt.grid()
plt.show()
# Saving the plot as an image
plt.savefig('plot.png')
