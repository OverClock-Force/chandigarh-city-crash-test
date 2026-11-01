import { useState, useEffect } from 'react'
import {
  Brain,
  Cpu,
  BarChart2,
  GitBranch,
  Layers,
  Sparkles,
  CheckCircle2,
  Copy,
  Check,
  RefreshCw,
  Sliders,
  TrendingUp,
  ShieldAlert,
  TreeDeciduous,
} from 'lucide-react'
import { getMLSuite } from '../api/client.js'

export default function MLSuiteView() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [copied, setCopied] = useState(false)
  const [activeSubTab, setActiveSubTab] = useState('all')

  // Interactive Regression Playground state
  const [rainInput, setRainInput] = useState(60)
  const [drainInput, setDrainInput] = useState(0.60)
  const [debrisInput, setDebrisInput] = useState(0.65)
  const [trafficInput, setTrafficInput] = useState(0.85)

  const loadMLData = () => {
    setLoading(true)
    setError(null)
    getMLSuite()
      .then((res) => {
        setData(res)
        setLoading(false)
      })
      .catch((err) => {
        console.error('Failed to load ML suite:', err)
        setError(err.message || 'Failed to connect to backend ML API')
        setLoading(false)
      })
  }

  useEffect(() => {
    loadMLData()
  }, [])

  // Calculate live playground prediction if regression model is loaded
  const regModel = data?.models?.linear_regression
  const predictedScore = regModel
    ? Math.min(
        100,
        Math.max(
          0,
          regModel.intercept +
            (regModel.coefficients.rainfall_mm || 0) * rainInput +
            (regModel.coefficients.drain_factor || 0) * drainInput +
            (regModel.coefficients.debris_factor || 0) * debrisInput +
            (regModel.coefficients.traffic_factor || 0) * trafficInput
        )
      ).toFixed(1)
    : null

  const handleCopyReport = () => {
    const reportText = `=== C3T Machine Learning Algorithms Report ===
1. K-Means Clustering:
   - Partitions Chandigarh sectors into 3 vulnerability clusters based on elevation, drainage age, road exposure, waste pressure, and green cover.
   - Inertia: ${data?.models?.k_means?.inertia || 'N/A'}
   - Cleanly isolates high-vulnerability commercial bottlenecks (Sec 17, 22, 26, 43) from resilient high green-cover zones (Sec 8, 9).

2. Decision Tree Classifier:
   - Predicts risk severity (Low, Moderate, High, Severe) using Gini impurity splits.
   - Test Accuracy: ${((data?.models?.decision_tree?.accuracy || 0) * 100).toFixed(1)}%
   - Top Predictor: Rainfall volume (${((data?.models?.decision_tree?.feature_importances?.rainfall_mm || 0) * 100).toFixed(1)}% importance), followed by drain condition and low elevation.

3. Multiple Linear Regression:
   - Equation: ${data?.models?.linear_regression?.regression_equation || 'N/A'}
   - Goodness of Fit (R²): ${data?.models?.linear_regression?.r2_score || 'N/A'}
   - Root Mean Squared Error (RMSE): ${data?.models?.linear_regression?.rmse || 'N/A'}
   - Demonstrates that each 10mm increment in rainfall raises citywide risk by ~${((data?.models?.linear_regression?.coefficients?.rainfall_mm || 0.44) * 10).toFixed(1)} points.
==============================================`

    navigator.clipboard.writeText(reportText)
    setCopied(true)
    setTimeout(() => setCopied(false), 3000)
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-slate-500">
        <RefreshCw className="h-8 w-8 animate-spin text-teal-600 mb-3" />
        <p className="font-semibold text-slate-700">Running Machine Learning Pipeline...</p>
        <p className="text-xs text-slate-400 mt-1">Fitting K-Means, Decision Tree & Linear Regression via scikit-learn</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-xl border border-rose-200 bg-rose-50 p-6 text-rose-800">
        <div className="flex items-center gap-2 font-bold">
          <ShieldAlert className="h-5 w-5 text-rose-600" />
          <span>ML Suite Offline</span>
        </div>
        <p className="text-sm mt-1">{error}</p>
        <button
          onClick={loadMLData}
          className="mt-4 inline-flex items-center gap-1.5 rounded-lg bg-rose-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-rose-700"
        >
          <RefreshCw className="h-3.5 w-3.5" /> Retry
        </button>
      </div>
    )
  }

  const kmeans = data.models.k_means
  const dtree = data.models.decision_tree
  const reg = data.models.linear_regression

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="rounded-2xl border border-teal-200/80 bg-gradient-to-r from-teal-900 via-[#102a3a] to-[#0c1e2b] p-6 text-white shadow-lg">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1 rounded-full bg-teal-500/20 px-2.5 py-0.5 text-xs font-semibold text-teal-300 ring-1 ring-teal-400/30">
                <Brain className="h-3.5 w-3.5" /> Scikit-Learn 1.9 Engine
              </span>
              <span className="text-xs text-slate-300">Live Mathematical Models</span>
            </div>
            <h1 className="mt-2 text-2xl font-extrabold tracking-tight sm:text-3xl">
              Machine Learning Analytics Suite
            </h1>
            <p className="mt-1 text-sm text-slate-300 max-w-2xl">
              Classical ML algorithms powering Chandigarh city disaster intelligence: K-Means sector clustering, Decision Tree severity classification, and Multiple Linear Regression.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleCopyReport}
              className="inline-flex items-center gap-1.5 rounded-xl bg-teal-600 px-4 py-2.5 text-xs font-bold text-white shadow-sm hover:bg-teal-500 transition-all"
            >
              {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              {copied ? 'Copied to Clipboard!' : 'Copy for Project Report'}
            </button>
            <button
              onClick={loadMLData}
              title="Re-run models"
              className="rounded-xl border border-slate-700 bg-slate-800/80 p-2.5 text-slate-300 hover:text-white hover:bg-slate-700 transition-all"
            >
              <RefreshCw className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Executive Highlights */}
        <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-3">
          <div className="rounded-xl bg-white/5 p-3.5 backdrop-blur-sm border border-white/10">
            <div className="flex items-center justify-between text-xs text-teal-300 font-semibold">
              <span>K-Means Clustering</span>
              <Layers className="h-4 w-4" />
            </div>
            <p className="mt-1 text-lg font-bold text-white">k = {kmeans.n_clusters} Clusters</p>
            <p className="text-[11px] text-slate-400">Inertia: {kmeans.inertia} · 5 physical dimensions</p>
          </div>

          <div className="rounded-xl bg-white/5 p-3.5 backdrop-blur-sm border border-white/10">
            <div className="flex items-center justify-between text-xs text-teal-300 font-semibold">
              <span>Decision Tree</span>
              <GitBranch className="h-4 w-4" />
            </div>
            <p className="mt-1 text-lg font-bold text-white">{(dtree.accuracy * 100).toFixed(1)}% Accuracy</p>
            <p className="text-[11px] text-slate-400">Max Depth: {dtree.max_depth} · Gini impurity splits</p>
          </div>

          <div className="rounded-xl bg-white/5 p-3.5 backdrop-blur-sm border border-white/10">
            <div className="flex items-center justify-between text-xs text-teal-300 font-semibold">
              <span>Multiple Regression</span>
              <TrendingUp className="h-4 w-4" />
            </div>
            <p className="mt-1 text-lg font-bold text-white">R² = {reg.r2_score}</p>
            <p className="text-[11px] text-slate-400">RMSE: {reg.rmse} · Ordinary Least Squares</p>
          </div>
        </div>
      </div>

      {/* Navigation Filter Buttons */}
      <div className="flex flex-wrap gap-2 border-b border-slate-200 pb-2">
        {[
          { id: 'all', label: 'All 3 Algorithms' },
          { id: 'kmeans', label: '1. K-Means Clustering' },
          { id: 'tree', label: '2. Decision Tree Classifier' },
          { id: 'regression', label: '3. Multiple Linear Regression' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveSubTab(tab.id)}
            className={`rounded-lg px-3.5 py-1.5 text-xs font-semibold transition-all ${
              activeSubTab === tab.id
                ? 'bg-slate-900 text-white shadow-sm'
                : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* ────────────────────────────────────────────────────────────────────────── */}
      {/* 1. K-MEANS CLUSTERING SECTION */}
      {/* ────────────────────────────────────────────────────────────────────────── */}
      {(activeSubTab === 'all' || activeSubTab === 'kmeans') && (
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="rounded-lg bg-teal-50 p-2 text-teal-700">
                <Layers className="h-5 w-5" />
              </div>
              <div>
                <h2 className="text-base font-bold text-slate-900">1. K-Means Clustering (Sector Vulnerability Segmentation)</h2>
                <p className="text-xs text-slate-500">Unsupervised learning partitioning Chandigarh sectors into multi-dimensional vulnerability archetypes</p>
              </div>
            </div>
            <span className="rounded-full bg-teal-50 px-2.5 py-1 text-xs font-bold text-teal-700">
              Inertia: {kmeans.inertia}
            </span>
          </div>

          {/* Cluster Cards */}
          <div className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-3">
            {kmeans.clusters.map((c) => {
              const border =
                c.tag === 'critical'
                  ? 'border-red-200 bg-red-50/50'
                  : c.tag === 'moderate'
                    ? 'border-amber-200 bg-amber-50/50'
                    : 'border-emerald-200 bg-emerald-50/50'
              const text =
                c.tag === 'critical'
                  ? 'text-red-800'
                  : c.tag === 'moderate'
                    ? 'text-amber-800'
                    : 'text-emerald-800'

              return (
                <div key={c.cluster_id} className={`rounded-xl border p-4 ${border}`}>
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                      Cluster {c.cluster_id}
                    </span>
                    <span className={`text-xs font-extrabold ${text}`}>
                      {c.sector_count} Sectors
                    </span>
                  </div>
                  <h3 className={`mt-1 font-bold text-sm ${text}`}>{c.label}</h3>

                  <div className="mt-3 space-y-1 text-xs text-slate-600">
                    <div className="flex justify-between">
                      <span>Avg Elevation Basin:</span>
                      <span className="font-semibold">{c.centroid.elevation_factor}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Drain Vulnerability:</span>
                      <span className="font-semibold">{c.centroid.drain_vulnerability}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Road Traffic Exposure:</span>
                      <span className="font-semibold">{c.centroid.road_exposure}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Solid Waste Pressure:</span>
                      <span className="font-semibold">{c.centroid.waste_pressure}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Green Cover Canopy:</span>
                      <span className="font-semibold">{c.centroid.green_cover_factor}</span>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>

          {/* Sector Mapping Table */}
          <div className="mt-5 overflow-x-auto">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
              Sectors Cluster Assignments
            </h4>
            <table className="w-full text-left text-xs text-slate-700">
              <thead className="bg-slate-50 text-slate-500 font-semibold border-y border-slate-200">
                <tr>
                  <th className="py-2 px-3">Sector</th>
                  <th className="py-2 px-3">Assigned Cluster</th>
                  <th className="py-2 px-3">Elevation</th>
                  <th className="py-2 px-3">Drain Vulnerability</th>
                  <th className="py-2 px-3">Road Exposure</th>
                  <th className="py-2 px-3">Green Cover</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {kmeans.sectors.map((s) => {
                  const badge =
                    s.cluster_tag === 'critical'
                      ? 'bg-red-100 text-red-800'
                      : s.cluster_tag === 'moderate'
                        ? 'bg-amber-100 text-amber-800'
                        : 'bg-emerald-100 text-emerald-800'

                  return (
                    <tr key={s.sector_id} className="hover:bg-slate-50/80">
                      <td className="py-2 px-3 font-semibold text-slate-900">{s.name}</td>
                      <td className="py-2 px-3">
                        <span className={`inline-block px-2 py-0.5 rounded-full text-[11px] font-bold ${badge}`}>
                          Cluster {s.cluster_id}: {s.cluster_tag}
                        </span>
                      </td>
                      <td className="py-2 px-3 font-mono">{s.features.elevation_factor}</td>
                      <td className="py-2 px-3 font-mono">{s.features.drain_vulnerability}</td>
                      <td className="py-2 px-3 font-mono">{s.features.road_exposure}</td>
                      <td className="py-2 px-3 font-mono">{s.features.green_cover_factor}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* ────────────────────────────────────────────────────────────────────────── */}
      {/* 2. DECISION TREE CLASSIFIER SECTION */}
      {/* ────────────────────────────────────────────────────────────────────────── */}
      {(activeSubTab === 'all' || activeSubTab === 'tree') && (
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="rounded-lg bg-indigo-50 p-2 text-indigo-700">
                <GitBranch className="h-5 w-5" />
              </div>
              <div>
                <h2 className="text-base font-bold text-slate-900">2. Decision Tree Classifier (Severity Classification)</h2>
                <p className="text-xs text-slate-500">Supervised classification predicting risk categories with transparent, inspectable Gini impurity splits</p>
              </div>
            </div>
            <span className="rounded-full bg-indigo-50 px-3 py-1 text-xs font-bold text-indigo-700">
              Accuracy: {(dtree.accuracy * 100).toFixed(1)}%
            </span>
          </div>

          <div className="mt-5 grid grid-cols-1 gap-6 lg:grid-cols-2">
            {/* Feature Importances */}
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
                Feature Importances (Normalized Gini Reduction)
              </h3>
              <div className="space-y-3">
                {Object.entries(dtree.feature_importances).map(([feat, imp]) => {
                  const pct = Math.round(imp * 100)
                  return (
                    <div key={feat} className="text-xs">
                      <div className="flex justify-between font-semibold text-slate-700 mb-1">
                        <span className="font-mono">{feat}</span>
                        <span>{(imp * 100).toFixed(1)}%</span>
                      </div>
                      <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                        <div
                          className="h-full rounded-full bg-indigo-600 transition-all duration-500"
                          style={{ width: `${Math.max(4, pct)}%` }}
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
              <p className="mt-3 text-xs text-slate-500">
                {dtree.interpretation}
              </p>
            </div>

            {/* Decision Path Rules */}
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
                Extracted If-Then Tree Decision Rules
              </h3>
              <div className="rounded-xl border border-slate-200 bg-slate-900 p-4 font-mono text-[11px] leading-5 text-slate-200 overflow-x-auto max-h-64">
                {dtree.text_rules.map((rule, idx) => (
                  <div
                    key={idx}
                    className={
                      rule.includes('class:')
                        ? 'text-emerald-400 font-bold'
                        : rule.includes('rainfall_mm')
                          ? 'text-sky-300'
                          : 'text-slate-300'
                    }
                  >
                    {rule}
                  </div>
                ))}
              </div>
              <p className="mt-2 text-[11px] text-slate-400">
                Decision tree depth restricted to {dtree.max_depth} to prevent overfitting and ensure municipal auditability.
              </p>
            </div>
          </div>
        </section>
      )}

      {/* ────────────────────────────────────────────────────────────────────────── */}
      {/* 3. MULTIPLE LINEAR REGRESSION SECTION */}
      {/* ────────────────────────────────────────────────────────────────────────── */}
      {(activeSubTab === 'all' || activeSubTab === 'regression') && (
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="rounded-lg bg-emerald-50 p-2 text-emerald-700">
                <TrendingUp className="h-5 w-5" />
              </div>
              <div>
                <h2 className="text-base font-bold text-slate-900">3. Multiple Linear Regression (Risk Index Modeling)</h2>
                <p className="text-xs text-slate-500">Ordinary Least Squares (OLS) regression mapping continuous environmental and drainage parameters</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-bold text-emerald-700">
                R² = {reg.r2_score}
              </span>
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
                RMSE: {reg.rmse}
              </span>
            </div>
          </div>

          {/* Regression Equation Box */}
          <div className="mt-5 rounded-xl border border-emerald-200 bg-emerald-50/60 p-4">
            <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-800">
              Fitted Empirical Regression Equation
            </span>
            <p className="mt-1 font-mono text-sm font-bold text-emerald-950 break-all">
              {reg.regression_equation}
            </p>
            <p className="mt-2 text-xs text-emerald-800/90">
              Intercept: <strong>{reg.intercept}</strong> · Explains <strong>{(reg.r2_score * 100).toFixed(1)}%</strong> of variance across stress scenarios.
            </p>
          </div>

          <div className="mt-5 grid grid-cols-1 gap-6 lg:grid-cols-2">
            {/* Learned Beta Weights */}
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
                Learned Coefficients (Marginal Impact / Beta Slopes)
              </h3>
              <div className="divide-y divide-slate-100 border border-slate-200 rounded-xl overflow-hidden text-xs">
                {Object.entries(reg.coefficients).map(([feat, coef]) => (
                  <div key={feat} className="flex items-center justify-between p-3 bg-white hover:bg-slate-50">
                    <div>
                      <p className="font-semibold text-slate-900 font-mono">{feat}</p>
                      <p className="text-[11px] text-slate-500">
                        {feat === 'rainfall_mm'
                          ? '+1 mm rain increases risk by this amount'
                          : '+100% factor degradation contribution'}
                      </p>
                    </div>
                    <span className="font-mono text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-1 rounded">
                      {coef > 0 ? `+${coef}` : coef}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Interactive Model Playground */}
            <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                  Interactive Live Regressor
                </h3>
                <span className="rounded bg-teal-600 px-2.5 py-1 text-xs font-extrabold text-white">
                  Predicted: {predictedScore} / 100
                </span>
              </div>

              <div className="space-y-3 text-xs">
                <div>
                  <div className="flex justify-between font-semibold text-slate-700">
                    <span>Rainfall ({rainInput} mm)</span>
                    <span className="text-slate-500 font-mono">15 to 100 mm</span>
                  </div>
                  <input
                    type="range"
                    min="15"
                    max="100"
                    value={rainInput}
                    onChange={(e) => setRainInput(Number(e.target.value))}
                    className="w-full accent-teal-600"
                  />
                </div>

                <div>
                  <div className="flex justify-between font-semibold text-slate-700">
                    <span>Drain Condition Factor ({drainInput.toFixed(2)})</span>
                    <span className="text-slate-500 font-mono">0.15 (good) - 0.95 (critical)</span>
                  </div>
                  <input
                    type="range"
                    min="0.15"
                    max="0.95"
                    step="0.05"
                    value={drainInput}
                    onChange={(e) => setDrainInput(Number(e.target.value))}
                    className="w-full accent-teal-600"
                  />
                </div>

                <div>
                  <div className="flex justify-between font-semibold text-slate-700">
                    <span>Debris Blockage Factor ({debrisInput.toFixed(2)})</span>
                    <span className="text-slate-500 font-mono">0.20 (normal) - 1.00 (extreme)</span>
                  </div>
                  <input
                    type="range"
                    min="0.20"
                    max="1.00"
                    step="0.05"
                    value={debrisInput}
                    onChange={(e) => setDebrisInput(Number(e.target.value))}
                    className="w-full accent-teal-600"
                  />
                </div>

                <div>
                  <div className="flex justify-between font-semibold text-slate-700">
                    <span>Traffic Load Factor ({trafficInput.toFixed(2)})</span>
                    <span className="text-slate-500 font-mono">0.30 (normal) - 0.85 (peak)</span>
                  </div>
                  <input
                    type="range"
                    min="0.30"
                    max="0.85"
                    step="0.05"
                    value={trafficInput}
                    onChange={(e) => setTrafficInput(Number(e.target.value))}
                    className="w-full accent-teal-600"
                  />
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* ────────────────────────────────────────────────────────────────────────── */}
      {/* REPORT SNIPPET BOX */}
      {/* ────────────────────────────────────────────────────────────────────────── */}
      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="rounded-lg bg-slate-100 p-2 text-slate-700">
              <Copy className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900">Project Report Summary Snippet</h3>
              <p className="text-xs text-slate-500">Ready-to-paste markdown summary for your academic or technical project report</p>
            </div>
          </div>
          <button
            onClick={handleCopyReport}
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
          >
            {copied ? <Check className="h-3.5 w-3.5 text-emerald-600" /> : <Copy className="h-3.5 w-3.5" />}
            {copied ? 'Copied!' : 'Copy Snippet'}
          </button>
        </div>

        <div className="mt-4 rounded-xl bg-slate-900 p-4 font-mono text-xs text-slate-300 overflow-x-auto leading-6">
          <p className="text-teal-400 font-bold"># Machine Learning Implementation in C3T</p>
          <p className="mt-1">• <strong>K-Means Clustering:</strong> Sectors grouped into {kmeans.n_clusters} clusters (Inertia: {kmeans.inertia}). Categorizes low-lying flood-prone commercial hubs vs high-permeability green corridors.</p>
          <p>• <strong>Decision Tree Classifier:</strong> Achieved {(dtree.accuracy * 100).toFixed(1)}% accuracy with depth {dtree.max_depth}. Rainfall ({((dtree.feature_importances.rainfall_mm || 0) * 100).toFixed(0)}%) and drain blockage ({((dtree.feature_importances.drain_factor || 0) * 100).toFixed(0)}%) dominate split decisions.</p>
          <p>• <strong>Multiple Linear Regression:</strong> Fitted continuous risk model with R² = {reg.r2_score} and RMSE = {reg.rmse}. Equation: {reg.regression_equation}.</p>
        </div>
      </section>
    </div>
  )
}
