# Machine Learning Report: Urban Disaster Risk & Infrastructure Failure Modeling
**Project:** Chandigarh City Crash Test (C3T)  
**Authors:** C3T Engineering & Data Science Team  
**Focus Area:** Digital Public Infrastructure (DPI), Multi-hazard Disaster Simulation, Machine Learning  

---

## 1. Executive Summary

The **Chandigarh City Crash Test (C3T)** system integrates classical machine learning (ML) algorithms alongside generative AI to simulate, predict, and optimize preventive interventions for urban emergencies such as monsoon waterlogging, storm-drain siltation, and cascading traffic gridlock.

To transition from purely heuristic rules to data-driven intelligence, C3T incorporates three core machine learning algorithms from **scikit-learn**:
1. **Unsupervised Learning — K-Means Clustering**: Partitions city sectors into vulnerability archetypes using multi-dimensional physical infrastructure attributes.
2. **Supervised Classification — Decision Tree Classifier**: Classifies flood and emergency severity levels with transparent, inspectable decision rules suitable for municipal auditing.
3. **Supervised Regression — Multiple Linear Regression (OLS)**: Empirically estimates continuous urban crash-test risk scores from meteorological and infrastructure stress inputs, providing statistical coefficients, $R^2$, and error metrics.

---

## 2. Dataset & Feature Engineering

The models operate on Chandigarh’s urban topology and environmental parameters:

| Feature Name | Description | Range / Unit | Used In |
|---|---|---|---|
| `elevation_factor` | Low-lying topographic depression index | `[0.0, 1.0]` (1.0 = deep basin) | K-Means, Decision Tree |
| `drain_vulnerability` | Stormwater drainage age, blockage susceptibility | `[0.0, 1.0]` (1.0 = high risk) | K-Means, Decision Tree |
| `road_exposure` | Arterial vehicle density & junction connectivity | `[0.0, 1.0]` (1.0 = critical choke point) | K-Means |
| `waste_pressure` | Commercial and market waste accumulation | `[0.0, 1.0]` (1.0 = heavy debris load) | K-Means |
| `green_cover_factor` | Forest, canopy, and permeable soil absorption | `[0.0, 1.0]` (1.0 = high green cover) | K-Means |
| `rainfall_mm` | Total storm precipitation volume | `[15.0, 100.0] mm` | Decision Tree, Regression |
| `drain_factor` | Grate & pipe conveyance status (good / partial / critical) | `[0.15, 0.95]` | Decision Tree, Regression |
| `debris_factor` | Solid waste & silt load (normal / high / extreme) | `[0.20, 1.00]` | Decision Tree, Regression |
| `traffic_factor` | City traffic level (normal / peak) | `[0.30, 0.85]` | Decision Tree, Regression |

---

## 3. Algorithm 1: K-Means Clustering (Sector Vulnerability Segmentation)

### 3.1 Objective & Mathematical Formulation
K-Means groups $N$ sectors into $K=3$ distinct clusters by minimizing the within-cluster sum of squared Euclidean distances (Inertia):

$$\arg\min_S \sum_{i=1}^K \sum_{\mathbf{x} \in S_i} \|\mathbf{x} - \boldsymbol{\mu}_i\|^2$$

Features are standardized using `StandardScaler` ($\mu=0, \sigma=1$) prior to clustering to ensure equal weighting across topographical and infrastructural metrics.

### 3.2 Results & Cluster Archetypes

| Cluster | Archetype Name | Sector Count | Key Characteristics | Representative Sectors |
|---|---|---|---|---|
| **0** | **Critical Flood & Traffic Bottlenecks** | High | High elevation depression ($>0.75$), high drain vulnerability ($>0.70$), high road exposure | Sector 17, Sector 22, Sector 43 |
| **1** | **Mixed Commercial & Surface Runoff** | Medium | Heavy waste pressure ($>0.80$), moderate green cover | Sector 26 (Mandi), Industrial Area Ph 1 |
| **2** | **Resilient Green-Cover Corridor** | Low | High green canopy ($>0.80$), gentle natural slope, low vulnerability ($<0.35$) | Sector 8, Sector 9 (Secretariat) |

### 3.3 Municipal Policy Takeaway
Municipal maintenance crews and suction pumps should prioritize **Cluster 0** prior to rain onset, while waste-clearing trucks should focus proactive sweeps on **Cluster 1**.

---

## 4. Algorithm 2: Decision Tree Classifier (Severity Classification)

### 4.1 Objective & Splitting Mechanism
The Decision Tree partitions the feature space into orthogonal hyperplanes to classify disaster severity into four classes:
$$\mathcal{Y} = \{\text{Low}, \text{Moderate}, \text{High}, \text{Severe}\}$$

Splits are chosen greedily by minimizing **Gini Impurity**:
$$I_G(p) = 1 - \sum_{i=1}^{C} p_i^2$$

### 4.2 Model Performance & Feature Importances
With a tree depth of `max_depth = 4`, the model achieves **~91–95% test accuracy**.

| Feature | Importance Score | Municipal Interpretation |
|---|---|---|
| `rainfall_mm` | **0.42** | Primary environmental trigger; storm intensity dictates runoff volume |
| `drain_factor` | **0.26** | Infrastructure condition dictates whether stormwater pools or drains |
| `elevation_factor` | **0.15** | Determines local water accumulation in low-lying depressions |
| `debris_factor` | **0.10** | Clogging factor on intake grates and culverts |
| `traffic_factor` | **0.07** | Exacerbates cascading emergency access disruption |

### 4.3 Extracted Decision Path Sample
```text
|--- rainfall_mm <= 48.50
|   |--- drain_factor <= 0.38
|   |   |--- class: low
|   |--- drain_factor > 0.38
|   |   |--- elevation_factor <= 0.65 -> class: moderate
|   |   |--- elevation_factor >  0.65 -> class: high
|--- rainfall_mm > 48.50
|   |--- drain_factor <= 0.38 -> class: moderate
|   |--- drain_factor >  0.38
|   |   |--- debris_factor > 0.60 -> class: severe
|   |   |--- debris_factor <= 0.60 -> class: high
```

---

## 5. Algorithm 3: Multiple Linear Regression (Risk Index Modeling)

### 5.1 Objective & OLS Formulation
Multiple Linear Regression estimates continuous urban risk index ($0.0 \le \hat{y} \le 100.0$) using Ordinary Least Squares:
$$\hat{y} = \beta_0 + \beta_1 (\text{Rainfall}) + \beta_2 (\text{DrainFactor}) + \beta_3 (\text{DebrisFactor}) + \beta_4 (\text{TrafficFactor}) + \epsilon$$

### 5.2 Fitted Regression Equation
$$\text{RiskScore} \approx 6.42 + 0.44 \cdot (\text{Rainfall}_{\text{mm}}) + 23.85 \cdot (\text{DrainFactor}) + 18.20 \cdot (\text{DebrisFactor}) + 14.50 \cdot (\text{TrafficFactor})$$

### 5.3 Goodness-of-Fit & Error Metrics

| Metric | Value | Interpretation |
|---|---|---|
| **$R^2$ (Coefficient of Determination)** | **0.942** | Explains **94.2%** of the variance in city risk scoring |
| **MSE (Mean Squared Error)** | **5.18** | Extremely low variance around the regression plane |
| **RMSE (Root Mean Squared Error)** | **2.28** | Average prediction error is only ~2.3 points on a 100-point index |

---

## 6. Synthesis: Comparing ML & AI Approaches in C3T

| Capability | Classical ML (K-Means / Trees / Regression) | Generative AI (Google Gemini Flash) |
|---|---|---|
| **Primary Function** | Deterministic clustering, numeric risk prediction, and classification | Natural language narratives, citizen complaint extraction, and photo vision analysis |
| **Interpretability** | High (coefficients, $R^2$, tree rules, cluster centroids) | Qualitative (natural language explanations) |
| **Execution Speed** | Sub-millisecond ($<5\text{ ms}$) | Network-dependent ($1–2\text{ s}$) |
| **Offline Capability** | 100% offline (scikit-learn + numpy) | Requires API key / internet connection |

---

## 7. How to Query the ML Models via API

The models are exposed through FastAPI endpoints:
- `GET /api/ml/suite`: Returns full analytical payload with clustering, decision tree, and regression statistics.
- `GET /api/ml/clustering?n_clusters=3`: Returns cluster assignments and centroids.
- `GET /api/ml/decision-tree?max_depth=4`: Returns tree accuracy, feature importances, and text rules.
- `GET /api/ml/regression`: Returns $R^2$, MSE, and linear equation.
- `POST /api/ml/predict-regression`: Predicts continuous risk for custom rainfall/drain/traffic inputs.
- `POST /api/ml/predict-tree`: Predicts risk category (`low`/`moderate`/`high`/`severe`) for a given sector.
