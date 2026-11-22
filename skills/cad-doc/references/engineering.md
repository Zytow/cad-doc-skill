# Engineering standard for design decisions

This standard describes how a decision is derived in a design review. Every design decision in the live documentation uses these building blocks as far as they fit the assembly.

## The chain of a decision

Generation goal → measurable target → variants → evaluation → decision → design calculation → risk → verification

Whoever reads the documentation must be able to trace every step back.

## 1. Measurable targets

Derive target values from the generation goal and record the achieved state next to them.

```markdown
#### Targets and constraints

| Quantity | <GEN-A> | Target <GEN-B> | Status | Source |
|----------|---------|----------------|--------|--------|
| Mass of sensor housing | TBD | 150 g | 142 g | weighing |
| Housing temperature at 35 °C ambient | TBD | < 60 °C | TBD | endurance test |
```

## 2. Compare variants

Describe every serious variant with the same characteristics. Rejected variants stay in the text because they save the next generation from doing the work twice.

```markdown
| Configuration | Mass | Stiffness | Unit cost | Assembly time | Result |
|---------------|------|-----------|-----------|---------------|--------|
| Printed bracket, 4 screws | 38 g | 120 N/mm | 3 EUR | 4 min | chosen |
| Milled aluminium bracket | 52 g | 310 N/mm | 14 EUR | 4 min | cost too high for the gain |
| Sheet-metal bracket, 2 screws | 25 g | 60 N/mm | 2 EUR | 2 min | too soft |
```

## 3. Evaluation matrix per VDI 2225

- Fix the criteria and the weighting before you award points.
- The weights add up to 100 %.
- Points range from 1 to 5, higher is better.
- The row `Total` is the weighted sum. The check recomputes it.
- A knock-out criterion is written as `k.o.` in the weighting column. Typical case: a variant leads on points but is not available. It is dropped and the next-best variant is chosen, with the lead and the reason stated.

```markdown
#### Evaluation

| Criterion | Weighting | Variant A | Variant B |
|-----------|-----------|-----------|-----------|
| Mass | 40 % | 4 | 2 |
| Cost | 20 % | 3 | 5 |
| Risk and reliability | 40 % | 5 | 3 |
| Availability | k.o. | yes | yes |
| Total | 100 % | 4.2 | 3.0 |
```

## 4. Design calculation and verification

A number without a load case is worthless. For every calculation, simulation and measurement write:

- **Load case and boundary conditions**, for example 20 °C ambient, 40 g along the mounting axis
- **Model and tool**, for example NX, Ansys, Star-CCM+, KISSsoft, MATLAB
- **Assumptions** and their source
- **Result** with unit against the target value
- **Comparison** with test data as soon as it exists

If a decision affects the product, state the effect in the figures that matter, for example mass, cost and the score of a system simulation. Example: a milled aluminium bracket instead of a printed one costs 14 EUR more and saves no mass, but it was chosen because the printed part creeps under the sustained load.

## 5. Risks as FMEA

Rate severity (S), occurrence (O) and detection (D) from 1 to 10. `RPN = S × O × D`, before and after the measure.

```markdown
#### Risks

| Failure mode | Effect | Cause | S | O | D | RPN | Measure | S new | O new | D new | RPN new |
|--------------|--------|-------|---|---|---|-----|---------|-------|-------|-------|---------|
| Screw loosens | housing shifts on the mount | vibration, no thread locker | 8 | 6 | 9 | 432 | thread locker, torque check | 8 | 3 | 2 | 48 |
```

## 6. Carried over and changed

At the start of *this generation*, contrast what stays and what changes, each with a reason. A system with a few well-justified changes is often better than a redesign.

## 7. Development across generations

For recurring assemblies show photos of the previous generations side by side, each with the measured improvement. Example: <GEN-A> needed re-clamping during assembly, <GEN-B> needs <n> min per unit without re-clamping.

## What live documentation does better

A presentation is made at the end, live documentation is written during the work. That avoids typical mistakes of end-of-project presentations:

- **Contradicting values:** a presentation may give two different current ratings, resistances or screw lengths for the same part. Every value is therefore stated once, with its source.
- **Arithmetic errors in matrices:** totals that do not match their points. The check recomputes every matrix.
- **Empty places:** open items are marked as `TBD` and named at the handover, instead of staying behind as `TODO`.
