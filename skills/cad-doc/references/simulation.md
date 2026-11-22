# Documenting simulations

The reference pattern is a bracket simulation: ask the manufacturer for the material property, derive the load case, vary parameters, decide against the limit. A complete example is in `examples/speaker/` in the repository.

## Which simulation fits the part?

Simulate only what answers a concrete question. If a hand calculation is sufficient, it is enough.

| Question | Type | Typical tool | Key result |
|---|---|---|---|
| Does the part hold? | static mechanical | Ansys Mechanical, Fusion 360 | stress, deformation, reaction force |
| How is the load distributed at joints? | contact | Ansys Mechanical | contact pressure, screw or adhesive force |
| Does it get too hot? | thermal | Ansys, Star-CCM+ | temperature against limit |
| Is the flow sufficient? | CFD | Star-CCM+ | flow rate, pressure drop |
| Does operation excite the part? | modal | Ansys Mechanical | natural frequencies against excitation |
| Do gears and bearings hold? | machine elements | KISSsoft | safety factors, service life |
| Is the change worth it at product level? | system simulation | MATLAB | score, cycle time |

## Simulation card

Create the card before you calculate. Enter the result right after the run. The heading starts with `Simulation:`.

```markdown
##### Simulation: sensor bracket under 40 g

| Item | Entry |
|------|-------|
| Question | Which plate thickness holds 40 g along the axis? |
| Tool | Ansys Mechanical 2026 R1, static mechanical |
| Model | reduced model, file and CAD state |
| Material | material, property, temperature, source |
| Load case | calculation with units and load direction |
| Supports | fixed and frictionless supports, justified |
| Contacts | type of contacts or "all bodies bonded" |
| Mesh | element type, element size, count |
| Mesh convergence | peak value at coarser and finer mesh |
| Limit | permissible value, safety factor, derivation |
| Result | maximum value with unit and location |
| Assessment | holds or does not hold, consequence for the design |

![Equivalent stress, peak at the outer edge](images/bracket-mises.png " =700x1029")
```

## Parameter study

Record every calculated variant in a table, including the failed ones. They show the next generation where the limit lies.

```markdown
| Variant | Thickness [mm] | Max stress [MPa] | Limit [MPa] | Utilisation [%] | Result |
|---------|----------------|------------------|-------------|-----------------|--------|
| V1 | 8 | 122 | 100 | 122 | does not hold |
| V2 | 9 | 98 | 100 | 98 | holds |
```

Link the CAD file and the result image for every variant.

## What matters when assessing

- **Limit:** use the material property at operating temperature and name the source. State the safety factor separately.
- **Stress peaks:** if a peak keeps growing with a finer mesh, it is probably a singularity. Assess it with a mesh study and a look at its surroundings, and give the value in numbers. "In the acceptable range" alone is not enough.
- **Result quantity:** von Mises suits ductile materials. For fibre composites, adhesive or brittle materials you need the matching failure criterion.
- **Plausibility:** compare the reaction force with the applied load.
- **Assumptions:** write down what the model leaves out and why, for example "axial direction only, because it is the most critical".
- **Comparison:** enter test data next to the simulation as soon as it exists.
- **Rules:** check load cases and temperatures against the current <Rulebook> <year> and cite the rule number.

## Working live

1. Enter question and limit before the calculation starts.
2. After every run save a screenshot, extend the table, write the assessment.
3. Record model changes in the `History` of the design decision.
4. If the geometry has changed, mark the old result as outdated and recalculate.
