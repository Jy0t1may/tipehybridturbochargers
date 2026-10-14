# Electrified Hybrid Turbocharger: Simulation, Dashboard & Test Rig (TIPE)

Research project (CPGE, 2025–2026) on an electric-assist turbocharger for small engines, aiming to reduce fuel consumption and emissions while increasing power.

## Contents
| File | What it is |
|---|---|
| `accel.py` | Python simulation of [what it computes] |
| `batteryconsump.py` | [status: used in results / experimental / not used] |
| `accel.html` | Interactive dashboard (HTML/CSS/JS) with live sliders and an accelerator wheel |
| `LowerS.stl`, `RotorS.stl`, `UpperS.stl` | 3D-printable parts for the DC-motor test rig |
| `PrintInstructions.rtf` | Print settings |
| `TIPE-JYOTI.pdf` | Full written report |


## Results
As the graphs illustrate, the introduction of this hybrid turbo minimizes fuel consumption while increasing engine power without increasing its displacement, which once again allows for fuel savings without the drawbacks of a traditional turbo, by completely eliminating turbo lag.
Once the hybrid’s acceleration phase is complete, this system can essentially serve as a substitute for the “wastegate” system where the motor then switches to generator mode and slows the turbo’s RPM when it exceeds the set limit, thereby converting the energy into electricity to recharge the batteries that power the system.

The main advantage of this system over a traditional hybrid car lies in the battery itself, as it does not require a high-capacity battery, which reduces the overall emissions associated with battery manufacturing.

## Limitations
Although this is a well-executed design, one issue remains: the recharge phase of the battery that powers the turbochargers. During long highway trips or prolonged use at high RPMs, the battery recharge phase is not reached—either because the turbos are not engaged or because they are spinning at nearly constant speeds, making it unnecessary for the engine to intervene to increase their RPMs.
Even though these situations are rare, they should still be taken into account.

## Run it
```bash
pip install [matplotlib numpy: check your imports]
python accel.py
```
Open `accel.html` in a browser for the dashboard.
