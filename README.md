# Simulation of a lipid bilayer with forces applied

This repository contains a project for the *computational cell biology* course given at EPFL (BIOENG-455, 2019).

## Simulations

The simulations are performed using dissipative particle dynamics (DPD). The software used to run the simulations is provided in the repository.

## The idea

A lipid bilayer is simulated in a box. The goal is the calculation of the work needed to pull out a single lipid from the membrane.

The simulations take the following steps:

1. Create a bilayer with lipid randomly arranged.
2. Let the simulation reach an equilibrium.
3. Select a lipid monolayer and apply forces on the lipids to mitigate membrane drift.
4. Apply a force on a single lipid head from the other monolayer.
5. Increase the force applied to the single lipid to pull it out.
6. Calculate the work needed to pull the lipid out.

The following considerations must be (and are) taken into account:

* The membrane surface tension must be null. Consequently, the concentration of lipid in the box must be chosen to obtain a null tension. Be aware that a negative stress correspond to membrane compression.
* The membrane should not drift. Using small forces on the inferior lipid layer, this effect could be mitigated.

The following parameters are changed between simulations:

* The lipid tail length
