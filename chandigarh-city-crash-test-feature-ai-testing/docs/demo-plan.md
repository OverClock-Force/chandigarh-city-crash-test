# C3T Hackathon Demo Plan (5-Minute Rehearsal Script)

**Platform**: Chandigarh City Crash Test (C3T)  
**Deliverable**: Milestone M4 Polish & Demo Readiness  
**Lead Owner**: Aditya Raj (AI Intake, QA & Demo Lead)  
**Co-Presenters**: Aman Gairola (Frontend), Aman Gupta (Backend & Data), Ankit Yadav (Risk Engine)

---

## 🎯 Demo Objective
Demonstrate an end-to-end, preventive decision-intelligence platform for Chandigarh’s digital public infrastructure answering three questions:
1. **What could fail** under a given urban stress scenario?
2. **Why might it fail**, and what cascading risks follow?
3. **Which feasible intervention** gives the greatest modeled risk reduction within municipal resources?

---

## ⏱️ Step-by-Step 5-Minute Script

```
[00:00 - 01:00] Step 1: City Overview & Ethical Transparency
[01:00 - 02:00] Step 2: Stress-Test Lab (60mm Baseline)
[02:00 - 03:00] Step 3: Risk Analysis & Causal Cascade Graph
[03:00 - 04:00] Step 4: Intervention Planner & Resource Optimization
[04:00 - 05:00] Step 5: Methodology & Honest Limitations
```

---

### Step 1: City Overview & Ethical Baseline (0:00 – 1:00)
- **Presenter**: Aman Gairola & Aditya Raj
- **What to Show on Screen**:
  - Open `http://localhost:5173/` (Screen 01: City Overview).
  - Point out the prominent top banner: `SIMULATED DATA · Scores are illustrative demo estimates`.
  - Point to the live backend indicator: `Backend: Connected · Risk engine online`.
  - Click sector markers on the map (Sector 17, Sector 35, Sector 26).
- **What to Say**:
  > *"Conventional civic tech is reactive—waiting for citizen complaints after a street is already flooded. C3T flips this model: we stress-test urban infrastructure before reality does.*
  >
  > *First, our Golden Rule: Every simulated score is an unvalidated demonstration index from 0 to 100. We never present synthetic simulations as real-world forecasts for Chandigarh.*
  >
  > *Here on the City Overview, we see calibrated sector vulnerabilities across drainage capacity, debris loading, and road traffic exposure."*

---

### Step 2: Stress-Test Lab (1:00 – 2:00)
- **Presenter**: Ankit Yadav
- **What to Show on Screen**:
  - Navigate to Screen 02: **Stress-Test Lab**.
  - Show the controls: Rainfall (60 mm), Waste/Debris (High), Drain Condition (Partial blockage), Traffic (Peak), Temperature (38 °C).
  - Click **Run Stress Test**. Observe live recalculation and overall risk score (61 / 100).
  - Point out the subsystem breakdown: Drainage Stress, Waterlogging, Road Traffic, Emergency Access.
  - Highlight the separate **Independent Heat-Stress Pathway** card (38 °C).
- **What to Say**:
  > *"In the Stress-Test Lab, municipal planners can configure compound hazard scenarios. Under a standard 60 mm monsoon rain with high debris accumulation and partial drain blockage, the engine recalculates citywide stress.*
  >
  > *Notice that temperature is explicitly decoupled from stormwater mechanics—high ambient heat creates independent occupational stress but does not artificially inflate flood indices."*

---

### Step 3: Risk Analysis & Causal Cascade Graph (2:00 – 3:00)
- **Presenter**: Ankit Yadav & Aman Gupta
- **What to Show on Screen**:
  - Navigate to Screen 03: **Risk Analysis**.
  - Show the **C3T Causal Cascade Failure Chain**:
    1. Rainfall (60mm) $\rightarrow$ Drainage System Stress (60% intensity, Modeled)
    2. Debris & Drain Condition $\rightarrow$ Drainage Stress (65% intensity, Modeled)
    3. Drainage System Stress $\rightarrow$ Surface Waterlogging (72% intensity, Modeled)
    4. Surface Waterlogging $\rightarrow$ Road Traffic Disruption (68% intensity, Modeled)
    5. Road Traffic Disruption $\rightarrow$ Emergency Access Delay (75% intensity, Hypothetical)
- **What to Say**:
  > *"This is the core insight of C3T: urban failures do not happen in silos. They cascade.*
  >
  > *Solid waste clogs road-gully gratings, which slashes pipe conveyance. Trapped runoff floods arterial roundabouts, which bottlenecks vehicle speeds. That traffic gridlock then delays ambulance and fire response corridors.*
  >
  > *Every link in our cascade graph is transparently classified as either 'Modeled' by hydraulic heuristics or 'Hypothetical' cross-domain delay."*

---

### Step 4: Intervention Planner & Resource Optimization (3:00 – 4:00)
- **Presenter**: Aman Gupta
- **What to Show on Screen**:
  - Navigate to Screen 04: **Intervention Planner**.
  - Highlight the **Optimal Recommendation Banner**:
    - Recommended: *Full Emergency Response* or *Clear Priority Gullies + Reroute Traffic*.
    - Modeled Risk Reduction: -34.7 pts.
    - Resources used & remaining: Teams, Pumps, ₹ Budget.
  - Review the Candidate Evaluations Table comparing Do Nothing baseline against candidate interventions.
- **What to Say**:
  > *"Once risks are understood, what should the city do? Municipal teams have finite resources: 4 maintenance crews, 2 pumping units, and a ₹3.5 Lakh contingency budget.*
  >
  > *C3T's constrained optimizer clones the scenario state, applies each candidate intervention, and re-runs the identical risk engine. It penalizes cost and operational burden to find the highest-utility feasible action.*
  >
  > *Instead of guessing, the decision-maker gets an explainable recommendation showing exactly how many points of risk are eliminated per rupee spent."*

---

### Step 5: Methodology & Honest Limitations (4:00 – 5:00)
- **Presenter**: Aditya Raj
- **What to Show on Screen**:
  - Navigate to Screen 06: **Methodology** and Screen 05: **Civic Reports**.
  - Briefly demonstrate submitting a citizen report (e.g. *Choked grate near Sector 17 fountain*).
  - Conclude on the **Methodology & Responsible Use** card.
- **What to Say**:
  > *"To wrap up, our responsible AI and data commitments:*
  >
  > 1. *All current sector geometries and baseline reports are synthetic benchmarks calibrated to Chandigarh MC public accounts.*
  > 2. *No live municipal SCADA systems are connected yet; this is an exploratory prototype for decision intelligence.*
  > 3. *Our test suite has 100% pass rates across unit and API boundary conditions.*
  >
  > *With C3T, Chandigarh can stress-test preventive urban policy before reality tests the city. Thank you."*

---

## 📋 Presenter Checklist Before Demo
- [ ] Backend running: `python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000`
- [ ] Frontend running: `node .\node_modules\vite\bin\vite.js preview --port 5173`
- [ ] Browser open to `http://localhost:5173/` with `Backend: Connected` badge green.
- [ ] Default scenario reset: 60mm rain, High debris, Partial blockage, Peak traffic, 38°C.
