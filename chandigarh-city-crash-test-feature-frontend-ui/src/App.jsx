import { useState, useEffect } from 'react'
import {
  Activity,
  ArrowRight,
  ArrowUpRight,
  BarChart3,
  CheckCircle2,
  ClipboardList,
  Clock3,
  CloudRain,
  Construction,
  Droplets,
  FileText,
  GitBranch,
  LayoutDashboard,
  MapPin,
  Menu,
  ShieldCheck,
  Trash2,
  X,
  AlertTriangle,
  RotateCcw,
  Save,
} from 'lucide-react'
import {
  getSectors,
  getEvents,
  runStressTest as apiRunStressTest,
  saveScenario as apiSaveScenario,
} from './api/client.js'



const navigation = [
  { id: 'overview', label: 'City Overview', icon: LayoutDashboard },
  { id: 'stress-test', label: 'Stress-Test Lab', icon: Activity },
  { id: 'risk-analysis', label: 'Risk Analysis', icon: GitBranch },
  { id: 'interventions', label: 'Intervention Planner', icon: BarChart3 },
  { id: 'reports', label: 'Civic Reports', icon: ClipboardList },
  { id: 'methodology', label: 'Methodology', icon: FileText },
]



const descriptions = {
  overview: 'Explore modeled city-sector risks and recent civic events.',
  'stress-test': 'Configure hypothetical scenarios and examine possible outcomes.',
  'risk-analysis': 'Understand modeled risk factors and possible failure cascades.',
  interventions: 'Compare hypothetical interventions within available resources.',
  reports: 'Record and review sample reports about urban issues.',
  methodology: 'Understand the model, assumptions, and data provenance.',
}



// Static fallback — replaced by live API data when backend is available
const staticSectors = [
  { id: '01', x: 15, y: 20, risk: 32 },
  { id: '02', x: 30, y: 15, risk: 48 },
  { id: '03', x: 48, y: 22, risk: 65 },
  { id: '04', x: 70, y: 16, risk: 28 },
  { id: '05', x: 82, y: 32, risk: 74 },
  { id: '06', x: 20, y: 43, risk: 55 },
  { id: '07', x: 43, y: 43, risk: 71 },
  { id: '08', x: 63, y: 45, risk: 38 },
  { id: '09', x: 78, y: 57, risk: 83 },
  { id: '10', x: 33, y: 64, risk: 44 },
  { id: '11', x: 52, y: 70, risk: 59 },
  { id: '12', x: 68, y: 80, risk: 24 },
]



const initialEvents = [
  {
    time: '10:42 AM',
    category: 'Waterlogging',
    sector: 'Sector 07',
    severity: 'High',
    status: 'Unverified',
  },
  {
    time: '10:18 AM',
    category: 'Waste hotspot',
    sector: 'Sector 03',
    severity: 'Moderate',
    status: 'Under review',
  },
  {
    time: '09:56 AM',
    category: 'Drain blockage',
    sector: 'Sector 09',
    severity: 'High',
    status: 'Unverified',
  },
  {
    time: '09:30 AM',
    category: 'Road disruption',
    sector: 'Sector 05',
    severity: 'Low',
    status: 'Reviewed',
  },
]



const defaultScenario = {
  rainfall: 60,
  debris: 'High',
  drainCondition: 'Partial blockage',
  traffic: 'Peak',
  temperature: 38,
}



function RiskBadge({ risk }) {
  const color =
    risk >= 70
      ? 'bg-red-50 text-red-700'
      : risk >= 40
        ? 'bg-amber-50 text-amber-700'
        : 'bg-emerald-50 text-emerald-700'



  const label = risk >= 70 ? 'High' : risk >= 40 ? 'Moderate' : 'Low'



  return (
    <span className={`inline-flex whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-semibold ${color}`}>
      {label} Â· {risk}
    </span>
  )
}



function SectionHeading({ eyebrow, title, description }) {
  return (
    <div className="mb-6">
      <p className="mb-2 text-[10px] font-bold uppercase tracking-[0.18em] text-teal-700">
        {eyebrow}
      </p>
      <h2 className="text-xl font-bold tracking-tight text-[#14243c] sm:text-2xl">
        {title}
      </h2>
      {description && (
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
          {description}
        </p>
      )}
    </div>
  )
}



function App() {
  const [activePage, setActivePage] = useState('overview')
  const [selectedSector, setSelectedSector] = useState('07')
  const [sidebarOpen, setSidebarOpen] = useState(false)



  const [scenario, setScenario] = useState({ ...defaultScenario })
  const [lastRun, setLastRun] = useState({ ...defaultScenario })
  const [scenarioRun, setScenarioRun] = useState(true)
  const [savedScenario, setSavedScenario] = useState(null)



  const [events, setEvents] = useState(initialEvents)
  const [reportMessage, setReportMessage] = useState('')
  // ── API / backend integration state ──────────────────────────────────────
  const [sectors, setSectors] = useState(staticSectors)
  const [backendStatus, setBackendStatus] = useState('unknown') // 'unknown' | 'online' | 'offline'
  const [stressTestLoading, setStressTestLoading] = useState(false)
  const [apiRisk, setApiRisk] = useState(null)       // score from backend engine
  const [apiRiskLabel, setApiRiskLabel] = useState(null) // score_label / data_status from backend
  const [saveStatus, setSaveStatus] = useState(null) // 'saving' | 'saved' | 'error'

  // On mount: probe backend by fetching sectors
  useEffect(() => {
    getSectors()
      .then((data) => {
        setBackendStatus('online')
        const list = Array.isArray(data) ? data : (data?.sectors || [])
        if (list.length > 0) {
          setSectors((prev) =>
            prev.map((s) => {
              const live = list.find((d) => String(d.sector_id || d.id) === `sector-${s.id}` || String(d.id || d.sector_id) === String(s.id))
              return live ? { ...s, risk: Math.round(live.score ?? live.risk ?? s.risk) } : s
            })
          )
        }
      })
      .catch(() => setBackendStatus('offline'))
  }, [])

  // When selectedSector changes and backend is online, refresh events list
  useEffect(() => {
    if (backendStatus !== 'online') return
    getEvents(selectedSector)
      .then((data) => {
        const list = Array.isArray(data) ? data : (data?.events || [])
        if (list.length > 0) {
          const mapped = list.map((ev) => ({
            time: ev.time ?? (ev.reported_at ? new Date(ev.reported_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })),
            category: ev.category ?? ev.type ?? 'Unknown',
            sector: ev.sector ?? ev.sector_id ?? selectedSector,
            severity: ev.severity ?? 'Moderate',
            status: ev.status ?? 'Unverified',
          }))
          setEvents(mapped)
        }
      })
      .catch(() => { /* keep existing events list */ })
  }, [selectedSector, backendStatus])



  const currentPage = navigation.find((item) => item.id === activePage)
  const CurrentPageIcon = currentPage.icon
  const selected = sectors.find((sector) => sector.id === selectedSector)



  // Illustrative frontend-only score. Not a validated risk model.
  const calculateRisk = (values) =>
    Math.min(
      100,
      Math.max(
        0,
        Math.round(
          20 +
          values.rainfall * 0.45 +
          (values.debris === 'High'
            ? 12
            : values.debris === 'Medium'
              ? 6
              : 0) +
          (values.drainCondition === 'Blocked'
            ? 18
            : values.drainCondition === 'Partial blockage'
              ? 10
              : 0) +
          (values.traffic === 'Peak'
            ? 8
            : values.traffic === 'Moderate'
              ? 4
              : 0),
        ),
      ),
    )



  const modeledRisk = calculateRisk(lastRun)
  const currentRisk = calculateRisk(scenario)



  function updateScenario(field, value) {
    setScenario((previous) => ({ ...previous, [field]: value }))
    setScenarioRun(false)
  }



  function runStressTest() {
    setLastRun({ ...scenario })
    setScenarioRun(true)
    setApiRisk(null)
    setApiRiskLabel(null)

    if (backendStatus === 'online') {
      setStressTestLoading(true)
      apiRunStressTest(scenario)
        .then((result) => {
          const score =
            result.overall_score ?? result.risk ?? result.risk_score ?? result.score ?? result.waterlogging_risk ?? null
          if (score !== null && !Number.isNaN(Number(score))) {
            setApiRisk(Math.round(Number(score)))
          }
          setApiRiskLabel(result.score_label ?? result.data_status ?? null)
        })
        .catch(() => { /* frontend calc remains */ })
        .finally(() => setStressTestLoading(false))
    }
  }



  function resetScenario() {
    setScenario({ ...defaultScenario })
    setLastRun({ ...defaultScenario })
    setScenarioRun(true)
    setApiRisk(null)
    setApiRiskLabel(null)
  }



  function saveScenario() {
    setSavedScenario({ ...scenario })
    setSaveStatus('saving')
    apiSaveScenario(scenario)
      .then(() => setSaveStatus('saved'))
      .catch(() => setSaveStatus('error'))
      .finally(() => setTimeout(() => setSaveStatus(null), 3000))
  }



  function openPage(page) {
    setActivePage(page)
    setSidebarOpen(false)
    setReportMessage('')
  }



  function submitDemoReport(event) {
    event.preventDefault()



    const form = new FormData(event.currentTarget)
    const category = form.get('category')
    const sector = form.get('sector')
    const severity = form.get('severity')
    const description = form.get('description')



    if (!description.trim()) {
      setReportMessage('Please enter a description.')
      return
    }



    const newEvent = {
      time: new Date().toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
      }),
      category,
      sector: `Sector ${sector}`,
      severity,
      status: 'Unverified',
    }



    setEvents((previous) => [newEvent, ...previous])
    setReportMessage('Demo report added successfully.')
    event.currentTarget.reset()
  }



  return (
    <div className="min-h-screen bg-[#f3f5f9] text-[#17243b]">
      {sidebarOpen && (
        <button
          aria-label="Close navigation overlay"
          className="fixed inset-0 z-30 bg-slate-950/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}



      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-[250px] flex-col bg-[#0d203b] text-white transition-transform duration-200 lg:translate-x-0 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'
          }`}
      >
        <div className="flex h-[76px] items-center gap-3 border-b border-white/10 px-6">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#13aa9c] font-black text-[#09233c]">
            C3
          </div>
          <div>
            <p className="text-sm font-bold">C3T</p>
            <p className="text-xs text-slate-300">City Crash Test</p>
          </div>
          <button
            className="ml-auto rounded-lg p-1 text-slate-300 lg:hidden"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close sidebar"
          >
            <X size={19} />
          </button>
        </div>



        <div className="px-6 pb-3 pt-8 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">
          Workspace
        </div>



        <nav className="space-y-1 px-3">
          {navigation.map((item) => {
            const Icon = item.icon
            const selectedNav = activePage === item.id



            return (
              <button
                key={item.id}
                onClick={() => openPage(item.id)}
                className={`flex w-full items-center gap-3 rounded-lg px-3 py-3 text-left text-sm transition ${selectedNav
                  ? 'bg-[#203957] font-semibold text-white'
                  : 'text-slate-300 hover:bg-white/5 hover:text-white'
                  }`}
              >
                <Icon size={18} strokeWidth={1.8} />
                <span>{item.label}</span>
                {selectedNav && (
                  <span className="ml-auto h-1.5 w-1.5 rounded-full bg-[#20c7b2]" />
                )}
              </button>
            )
          })}
        </nav>



        <div className="mt-auto p-4">
          <div className="rounded-xl border border-white/10 bg-[#152c4b] p-3">
            {backendStatus === 'online' ? (
              <>
                <div className="mb-2 flex items-center gap-2 text-[10px] font-bold uppercase tracking-wider text-[#20c7b2]">
                  <span className="h-2 w-2 rounded-full bg-[#20c7b2]" />
                  Backend: connected
                </div>
                <p className="text-xs leading-5 text-slate-300">
                  Risk engine online. Scores are illustrative demo estimates.
                </p>
              </>
            ) : backendStatus === 'offline' ? (
              <>
                <div className="mb-2 flex items-center gap-2 text-[10px] font-bold uppercase tracking-wider text-[#f6c768]">
                  <span className="h-2 w-2 rounded-full bg-[#f6c768]" />
                  Data mode: simulated
                </div>
                <p className="text-xs leading-5 text-slate-300">
                  Synthetic sample data. Backend not reachable.
                </p>
              </>
            ) : (
              <>
                <div className="mb-2 flex items-center gap-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  <span className="h-2 w-2 rounded-full bg-slate-400" />
                  Data mode: simulated
                </div>
                <p className="text-xs leading-5 text-slate-300">
                  Probing backend…
                </p>
              </>
            )}
          </div>
          <p className="px-1 pb-1 pt-5 text-[10px] text-slate-500">
            AI for DPI Â· Chandigarh
          </p>
        </div>
      </aside>



      {/* Main workspace */}
      <div className="min-h-screen lg:pl-[250px]">
        <div className="flex items-center gap-2 bg-[#fff3d7] px-4 py-2 text-[10px] leading-4 text-[#78541b] sm:px-7">
          <ShieldCheck size={13} className="shrink-0" />
          <strong className="uppercase tracking-wider">Simulated data</strong>
          <span className="hidden sm:inline">
            Scores are illustrative demo estimates, not operational forecasts.
          </span>
        </div>



        <header className="flex min-h-[68px] items-center justify-between border-b border-slate-200 bg-white px-4 sm:px-7">
          <div className="flex items-center gap-3">
            <button
              className="rounded-lg border border-slate-200 p-2 lg:hidden"
              onClick={() => setSidebarOpen(true)}
              aria-label="Open navigation"
            >
              <Menu size={19} />
            </button>
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-400">
                C3T / Workspace
              </p>
              <p className="mt-1 text-xs font-semibold text-slate-600">
                Chandigarh Â· Urban resilience prototype
              </p>
            </div>
          </div>
          <div className="hidden items-center gap-2 rounded-full border border-slate-200 px-3 py-1.5 text-xs text-slate-600 sm:flex">
            <span className="h-2 w-2 rounded-full bg-[#13aa9c]" />
            Prototype environment
          </div>
        </header>



        <main className="mx-auto max-w-[1500px] px-4 py-7 sm:px-7 sm:py-9">
          <div className="mb-7 flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="mb-2 text-[10px] font-bold uppercase tracking-[0.18em] text-[#0b948b]">
                {String(
                  navigation.findIndex((item) => item.id === activePage) + 1,
                ).padStart(2, '0')}{' '}
                / C3T WORKSPACE
              </p>
              <h1 className="text-2xl font-bold tracking-tight text-[#14243c] sm:text-3xl flex items-center gap-2.5">
                <CurrentPageIcon size={26} className="text-[#0b948b] shrink-0" />
                {currentPage.label}
              </h1>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                {descriptions[activePage]}
              </p>
            </div>



            {activePage !== 'stress-test' && (
              <button
                onClick={() => openPage('stress-test')}
                className="flex items-center gap-2 rounded-lg bg-[#126bdf] px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-700"
              >
                Open Stress-Test Lab <ArrowRight size={16} />
              </button>
            )}
          </div>



          {/* CITY OVERVIEW */}
          {activePage === 'overview' && (
            <>
              <section className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
                {[
                  {
                    label: 'Study sectors',
                    value: '20',
                    note: 'Illustrative study area',
                    icon: MapPin,
                    color: 'text-blue-700 bg-blue-50',
                  },
                  {
                    label: 'High-risk sectors',
                    value: '04',
                    note: 'Demo risk index â‰¥ 70',
                    icon: AlertTriangle,
                    color: 'text-red-700 bg-red-50',
                  },
                  {
                    label: 'Civic events',
                    value: String(events.length).padStart(2, '0'),
                    note: 'Sample records',
                    icon: ClipboardList,
                    color: 'text-amber-700 bg-amber-50',
                  },
                  {
                    label: 'Scenario rainfall',
                    value: `${scenario.rainfall} mm`,
                    note: 'Current scenario input',
                    icon: CloudRain,
                    color: 'text-cyan-700 bg-cyan-50',
                  },
                ].map((card) => {
                  const Icon = card.icon



                  return (
                    <article
                      key={card.label}
                      className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="text-xs font-medium text-slate-500">
                            {card.label}
                          </p>
                          <p className="mt-3 text-3xl font-bold tracking-tight">
                            {card.value}
                          </p>
                        </div>
                        <div className={`rounded-lg p-2.5 ${card.color}`}>
                          <Icon size={19} />
                        </div>
                      </div>
                      <p className="mt-3 text-xs text-slate-400">
                        {card.note}
                      </p>
                    </article>
                  )
                })}
              </section>



              <section className="grid grid-cols-1 gap-5 xl:grid-cols-[1.55fr_1fr]">
                <article className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
                  <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 p-5">
                    <div>
                      <h2 className="font-semibold">Sector risk map</h2>
                      <p className="mt-1 text-xs text-slate-500">
                        Select a marker to inspect a sample sector
                      </p>
                    </div>
                    <span className="rounded-md bg-slate-100 px-2.5 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-slate-500">
                      Illustrative Â· Not to scale
                    </span>
                  </div>



                  <div className="relative min-h-[340px] overflow-hidden bg-[#f7fafc] p-4 sm:p-6">
                    <svg
                      viewBox="0 0 500 320"
                      preserveAspectRatio="none"
                      className="absolute inset-0 h-full w-full"
                      aria-label="Illustrative map geometry"
                    >
                      <path
                        d="M20 40 L110 20 L180 60 L260 25 L350 60 L480 30 M10 110 L95 90 L170 125 L260 95 L340 130 L490 100 M5 195 L90 165 L170 205 L260 175 L365 215 L490 180 M20 280 L120 245 L200 285 L310 250 L410 290 L490 260"
                        fill="none"
                        stroke="#dbe5ee"
                        strokeWidth="2"
                      />
                      <path
                        d="M50 0 L75 320 M150 0 L180 320 M270 0 L290 320 M390 0 L410 320 M0 70 L500 250"
                        fill="none"
                        stroke="#e6edf3"
                        strokeWidth="1.5"
                      />
                      <path
                        d="M0 155 Q110 120 190 175 T350 160 T500 185"
                        fill="none"
                        stroke="#9bc9e6"
                        strokeWidth="5"
                        strokeDasharray="8 7"
                      />
                    </svg>



                    {sectors.map((sector) => (
                      <button
                        key={sector.id}
                        onClick={() => setSelectedSector(sector.id)}
                        style={{
                          left: `${sector.x}%`,
                          top: `${sector.y}%`,
                        }}
                        className={`absolute flex h-10 w-10 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border-[3px] text-xs font-bold shadow-sm transition hover:scale-110 ${sector.id === selectedSector
                          ? 'z-10 border-[#123b62] ring-4 ring-blue-100'
                          : 'border-white'
                          } ${sector.risk >= 70
                            ? 'bg-red-200 text-red-900'
                            : sector.risk >= 50
                              ? 'bg-amber-200 text-amber-900'
                              : 'bg-emerald-200 text-emerald-900'
                          }`}
                        aria-label={`Select sector ${sector.id}, risk ${sector.risk}`}
                      >
                        {sector.id}
                      </button>
                    ))}



                    <div className="absolute bottom-4 left-4 flex flex-wrap gap-3 rounded-lg border border-slate-200 bg-white/95 px-3 py-2 text-[10px] shadow-sm">
                      <span className="flex items-center gap-1.5">
                        <i className="h-2 w-2 rounded-full bg-emerald-400" />
                        Low
                      </span>
                      <span className="flex items-center gap-1.5">
                        <i className="h-2 w-2 rounded-full bg-amber-400" />
                        Moderate
                      </span>
                      <span className="flex items-center gap-1.5">
                        <i className="h-2 w-2 rounded-full bg-red-400" />
                        High
                      </span>
                    </div>
                  </div>
                </article>



                <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p className="text-[10px] font-bold uppercase tracking-[0.15em] text-slate-400">
                        Selected sector
                      </p>
                      <h2 className="mt-2 text-xl font-bold">
                        Sample sector {selected.id}
                      </h2>
                    </div>
                    <RiskBadge risk={selected.risk} />
                  </div>



                  <p className="mt-5 text-sm font-semibold">
                    Modeled contributing factors
                  </p>



                  <div className="mt-4 space-y-4">
                    <div className="flex gap-3">
                      <div className="h-9 w-9 shrink-0 rounded-lg bg-blue-50 p-2 text-blue-700">
                        <Droplets size={18} />
                      </div>
                      <div>
                        <p className="text-sm font-medium">Drainage capacity</p>
                        <p className="mt-1 text-xs leading-5 text-slate-500">
                          Partial drain blockage can reduce effective drainage
                          capacity.
                        </p>
                      </div>
                    </div>



                    <div className="flex gap-3">
                      <div className="h-9 w-9 shrink-0 rounded-lg bg-amber-50 p-2 text-amber-700">
                        <Trash2 size={18} />
                      </div>
                      <div>
                        <p className="text-sm font-medium">Debris load</p>
                        <p className="mt-1 text-xs leading-5 text-slate-500">
                          High debris near an inlet adds modeled drainage
                          stress.
                        </p>
                      </div>
                    </div>



                    <div className="flex gap-3">
                      <div className="h-9 w-9 shrink-0 rounded-lg bg-red-50 p-2 text-red-700">
                        <Construction size={18} />
                      </div>
                      <div>
                        <p className="text-sm font-medium">Road exposure</p>
                        <p className="mt-1 text-xs leading-5 text-slate-500">
                          Peak traffic can increase exposure on nearby roads.
                        </p>
                      </div>
                    </div>
                  </div>



                  <div className="mt-6 rounded-lg bg-slate-50 p-3">
                    <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                      Provenance
                    </p>
                    <p className="mt-1 text-xs leading-5 text-slate-500">
                      Synthetic assets and illustrative geometry. Not verified
                      infrastructure.
                    </p>
                  </div>



                  <button
                    onClick={() => openPage('risk-analysis')}
                    className="mt-5 flex w-full items-center justify-center gap-2 rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-semibold hover:bg-slate-50"
                  >
                    Analyse this sector <ArrowUpRight size={16} />
                  </button>
                </article>
              </section>



              <section className="mt-6 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
                <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 p-5">
                  <div>
                    <h2 className="font-semibold">Recent civic events</h2>
                    <p className="mt-1 text-xs text-slate-500">
                      Sample records Â· Not connected to municipal systems
                    </p>
                  </div>
                  <button
                    onClick={() => openPage('reports')}
                    className="text-xs font-semibold text-blue-700 hover:underline"
                  >
                    View all reports <ArrowRight size={14} className="ml-1 inline" />
                  </button>
                </div>



                <div className="overflow-x-auto">
                  <table className="w-full min-w-[650px] text-left text-xs">
                    <thead className="bg-slate-50 text-[10px] uppercase tracking-wider text-slate-500">
                      <tr>
                        {[
                          'Time',
                          'Category',
                          'Sector',
                          'Severity',
                          'Verification',
                          'Status',
                        ].map((heading) => (
                          <th key={heading} className="px-5 py-3 font-semibold">
                            {heading}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {events.map((event, index) => (
                        <tr key={`${event.time}-${index}`} className="hover:bg-slate-50/70">
                          <td className="whitespace-nowrap px-5 py-4 text-slate-500">
                            <Clock3 size={13} className="mr-2 inline" />
                            {event.time}
                          </td>
                          <td className="px-5 py-4 font-medium">{event.category}</td>
                          <td className="px-5 py-4">{event.sector}</td>
                          <td className="px-5 py-4">
                            <RiskBadge
                              risk={
                                event.severity === 'High'
                                  ? 75
                                  : event.severity === 'Moderate'
                                    ? 55
                                    : 30
                              }
                            />
                          </td>
                          <td className="px-5 py-4 text-slate-500">
                            {event.status === 'Unverified'
                              ? 'Pending review'
                              : 'Sample review'}
                          </td>
                          <td className="px-5 py-4">
                            <span className="rounded-full bg-slate-100 px-2.5 py-1 text-[10px] font-medium text-slate-600">
                              {event.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            </>
          )}



          {/* STRESS-TEST LAB */}
          {activePage === 'stress-test' && (
            <section className="grid grid-cols-1 gap-6 xl:grid-cols-[0.9fr_1.1fr]">
              <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
                <div className="mb-6">
                  <p className="text-[10px] font-bold uppercase tracking-wider text-teal-700">
                    Scenario editor
                  </p>
                  <h2 className="mt-2 text-lg font-bold">
                    Configure conditions
                  </h2>
                  <p className="mt-1 text-xs leading-5 text-slate-500">
                    Adjust hypothetical inputs and run the demo calculation.
                  </p>
                </div>



                <div className="mb-6">
                  <div className="mb-2 flex items-center justify-between">
                    <label htmlFor="rainfall" className="text-sm font-medium">
                      Rainfall
                    </label>
                    <span className="text-sm font-bold">{scenario.rainfall} mm</span>
                  </div>
                  <input
                    id="rainfall"
                    type="range"
                    min="15"
                    max="100"
                    step="5"
                    value={scenario.rainfall}
                    onChange={(event) =>
                      updateScenario('rainfall', Number(event.target.value))
                    }
                    className="w-full accent-blue-600"
                  />
                  <div className="mt-1 flex justify-between text-xs text-slate-400">
                    <span>15 mm</span>
                    <span>100 mm</span>
                  </div>
                </div>



                <div className="mb-5">
                  <label htmlFor="debris" className="mb-2 block text-sm font-medium">
                    Waste / debris load
                  </label>
                  <select
                    id="debris"
                    value={scenario.debris}
                    onChange={(event) => updateScenario('debris', event.target.value)}
                    className="w-full rounded-lg border border-slate-200 bg-white p-3 text-sm outline-none focus:border-blue-500"
                  >
                    <option>Low</option>
                    <option>Medium</option>
                    <option>High</option>
                  </select>
                </div>



                <div className="mb-5">
                  <label htmlFor="drain" className="mb-2 block text-sm font-medium">
                    Drain condition
                  </label>
                  <select
                    id="drain"
                    value={scenario.drainCondition}
                    onChange={(event) =>
                      updateScenario('drainCondition', event.target.value)
                    }
                    className="w-full rounded-lg border border-slate-200 bg-white p-3 text-sm outline-none focus:border-blue-500"
                  >
                    <option>Clear</option>
                    <option>Partial blockage</option>
                    <option>Blocked</option>
                  </select>
                </div>



                <div className="mb-5">
                  <label htmlFor="traffic" className="mb-2 block text-sm font-medium">
                    Traffic load
                  </label>
                  <select
                    id="traffic"
                    value={scenario.traffic}
                    onChange={(event) => updateScenario('traffic', event.target.value)}
                    className="w-full rounded-lg border border-slate-200 bg-white p-3 text-sm outline-none focus:border-blue-500"
                  >
                    <option>Low</option>
                    <option>Moderate</option>
                    <option>Peak</option>
                  </select>
                </div>



                <div className="mb-6">
                  <div className="mb-2 flex items-center justify-between">
                    <label htmlFor="temperature" className="text-sm font-medium">
                      Temperature
                    </label>
                    <span className="text-sm font-bold">
                      {scenario.temperature} Â°C
                    </span>
                  </div>
                  <input
                    id="temperature"
                    type="range"
                    min="32"
                    max="43"
                    step="1"
                    value={scenario.temperature}
                    onChange={(event) =>
                      updateScenario('temperature', Number(event.target.value))
                    }
                    className="w-full accent-orange-500"
                  />
                  <div className="mt-1 flex justify-between text-xs text-slate-400">
                    <span>32 Â°C</span>
                    <span>43 Â°C</span>
                  </div>
                  <p className="mt-2 text-xs leading-5 text-slate-500">
                    Heat is modeled separately and is excluded from waterlogging risk.
                  </p>
                </div>



                <div className="flex flex-wrap gap-3">
                  <button
                    onClick={runStressTest}
                    disabled={stressTestLoading}
                    className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-[#126bdf] px-4 py-3 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
                  >
                    <Activity size={16} className={stressTestLoading ? "animate-spin" : ""} /> {stressTestLoading ? "Running Stress Test..." : "Run Stress Test"}
                  </button>
                  <button
                    onClick={resetScenario}
                    className="flex items-center justify-center gap-2 rounded-lg border border-slate-200 px-3 py-3 text-sm font-medium hover:bg-slate-50"
                    title="Reset scenario"
                  >
                    <RotateCcw size={16} /> Reset
                  </button>
                </div>



                <div className="mt-3 flex gap-3">
                  <button
                    onClick={saveScenario}
                    className="flex flex-1 items-center justify-center gap-2 rounded-lg border border-slate-200 px-3 py-2.5 text-sm font-medium hover:bg-slate-50"
                  >
                    <Save size={15} /> Save scenario
                  </button>
                  <button
                    onClick={() => {
                      if (savedScenario) {
                        setScenario({ ...savedScenario })
                        setLastRun({ ...savedScenario })
                        setScenarioRun(true)
                      }
                    }}
                    disabled={!savedScenario}
                    className="flex flex-1 items-center justify-center gap-2 rounded-lg border border-slate-200 px-3 py-2.5 text-sm font-medium hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    Load saved
                  </button>
                </div>



                {savedScenario && (
                  <p className="mt-3 text-xs text-emerald-700">
                    <CheckCircle2 size={14} className="mr-1 inline" />
                    {saveStatus === 'saving'
                      ? 'Saving to backend…'
                      : saveStatus === 'saved'
                      ? 'Saved to backend and this session.'
                      : saveStatus === 'error'
                      ? 'Session saved (backend save failed).'
                      : 'Scenario saved for this session.'}
                  </p>
                )}



                <p className="mt-4 text-center text-[10px] text-slate-400">
                  Frontend-only demo calculation Â· Not a validated forecast
                </p>
              </article>



              <div className="space-y-5">
                <article className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                        Stress-test result
                      </p>
                      <h2 className="mt-2 text-lg font-bold">
                        Overall modeled waterlogging risk
                      </h2>
                    </div>
                    {scenarioRun && <RiskBadge risk={apiRisk ?? modeledRisk} />}
                  </div>



                  <div className="mt-6 flex items-end gap-3">
                    <span className="text-6xl font-bold tracking-tight text-[#17243b]">
                      {scenarioRun ? modeledRisk : 'â€”'}
                    </span>
                    <span className="mb-2 text-sm text-slate-400">
                      / 100 {apiRisk !== null ? (apiRiskLabel ?? 'engine index') : 'demo index'}
                    </span>
                  </div>



                  <div className="mt-5 h-3 overflow-hidden rounded-full bg-slate-100">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${modeledRisk >= 70
                        ? 'bg-red-500'
                        : modeledRisk >= 40
                          ? 'bg-amber-400'
                          : 'bg-emerald-500'
                        }`}
                      style={{ width: `${scenarioRun ? modeledRisk : 0}%` }}
                    />
                  </div>



                  <div className="mt-3 flex justify-between text-[10px] text-slate-400">
                    <span>0 Â· Low</span>
                    <span>40 Â· Moderate</span>
                    <span>70 Â· High</span>
                    <span>100</span>
                  </div>



                  <p className="mt-5 text-sm font-semibold">
                    {scenarioRun
                      ? modeledRisk >= 70
                        ? 'High modeled risk'
                        : modeledRisk >= 40
                          ? 'Moderate modeled risk'
                          : 'Low modeled risk'
                      : 'Inputs changed â€” run the test again'}
                  </p>



                  <p className="mt-3 text-sm leading-6 text-slate-500">
                    {scenarioRun
                      ? `Under the selected scenario of ${lastRun.rainfall} mm rainfall, ${lastRun.debris.toLowerCase()} debris, ${lastRun.drainCondition.toLowerCase()} drains and ${lastRun.traffic.toLowerCase()} traffic, the ${apiRisk !== null ? 'backend engine' : 'illustrative model'} produces a score of ${apiRisk ?? modeledRisk}.`
                      : `Your new inputs would produce a demo score of ${currentRisk}. Run the test to apply the scenario.`}
                  </p>
                </article>



                <article className="rounded-xl border border-orange-200 bg-orange-50 p-5">
                  <div className="flex items-center gap-2 text-sm font-bold text-orange-900">
                    <Activity size={18} /> Separate heat-stress pathway
                  </div>
                  <p className="mt-3 text-3xl font-bold text-orange-900">
                    {scenarioRun ? lastRun.temperature : scenario.temperature} Â°C
                  </p>
                  <p className="mt-2 text-sm leading-6 text-orange-800">
                    Heat stress is tracked independently. Temperature does not
                    increase the waterlogging score in this demo.
                  </p>
                </article>



                <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                  <h3 className="font-semibold">Scenario summary</h3>
                  <div className="mt-4 grid grid-cols-2 gap-5 text-sm">
                    {[
                      {
                        label: 'Rainfall',
                        value: `${scenarioRun ? lastRun.rainfall : scenario.rainfall} mm`,
                      },
                      {
                        label: 'Debris load',
                        value: scenarioRun ? lastRun.debris : scenario.debris,
                      },
                      {
                        label: 'Drain condition',
                        value: scenarioRun
                          ? lastRun.drainCondition
                          : scenario.drainCondition,
                      },
                      {
                        label: 'Traffic',
                        value: scenarioRun ? lastRun.traffic : scenario.traffic,
                      },
                    ].map((item) => (
                      <div key={item.label}>
                        <p className="text-xs text-slate-400">{item.label}</p>
                        <p className="mt-1 font-semibold">{item.value}</p>
                      </div>
                    ))}
                  </div>
                </article>
              </div>
            </section>
          )}



          {/* RISK ANALYSIS */}
          {activePage === 'risk-analysis' && (
            <>
              <SectionHeading
                eyebrow="03 / Risk analysis"
                title={`Why might sector ${selected.id} fail?`}
                description="Explore the illustrative relationships between scenario inputs, intermediate states and possible consequences."
              />



              <div className="grid gap-5 lg:grid-cols-3">
                {[
                  {
                    number: '01',
                    title: 'Scenario signals',
                    text: 'Rainfall, debris load, drain condition and traffic.',
                    color: 'border-blue-200 bg-blue-50',
                  },
                  {
                    number: '02',
                    title: 'Intermediate states',
                    text: 'Reduced drainage capacity and increased road exposure.',
                    color: 'border-amber-200 bg-amber-50',
                  },
                  {
                    number: '03',
                    title: 'Possible consequences',
                    text: 'Water pooling, slower road movement and service disruption.',
                    color: 'border-red-200 bg-red-50',
                  },
                ].map((step) => (
                  <article key={step.number} className={`rounded-xl border p-5 ${step.color}`}>
                    <p className="text-xs font-bold">{step.number}</p>
                    <h3 className="mt-3 font-bold">{step.title}</h3>
                    <p className="mt-2 text-sm leading-6 text-slate-600">{step.text}</p>
                  </article>
                ))}
              </div>



              <article className="mt-5 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
                <h3 className="font-semibold">Main contributing factors</h3>
                <p className="mt-2 text-sm leading-6 text-slate-500">
                  These are qualitative demo explanations, not calibrated causal estimates.
                </p>
                <div className="mt-5 space-y-5">
                  {[
                    ['Rainfall', `${lastRun.rainfall} mm`, lastRun.rainfall],
                    ['Debris load', lastRun.debris, lastRun.debris === 'High' ? 85 : lastRun.debris === 'Medium' ? 55 : 25],
                    ['Drain blockage', lastRun.drainCondition, lastRun.drainCondition === 'Blocked' ? 90 : lastRun.drainCondition === 'Partial blockage' ? 60 : 20],
                    ['Traffic exposure', lastRun.traffic, lastRun.traffic === 'Peak' ? 80 : lastRun.traffic === 'Moderate' ? 50 : 25],
                  ].map(([label, value, score]) => (
                    <div key={label}>
                      <div className="mb-2 flex justify-between gap-3 text-sm">
                        <span className="font-medium">{label}</span>
                        <span className="text-slate-500">{value}</span>
                      </div>
                      <div className="h-2 rounded-full bg-slate-100">
                        <div className="h-2 rounded-full bg-blue-600" style={{ width: `${Math.min(100, Number(score))}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
                <button onClick={() => openPage('interventions')} className="mt-6 flex items-center gap-2 rounded-lg bg-[#126bdf] px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700">
                  Compare interventions <ArrowRight size={16} />
                </button>
              </article>
            </>
          )}



          {/* INTERVENTION PLANNER */}
          {activePage === 'interventions' && (
            <>
              <SectionHeading
                eyebrow="04 / Intervention planner"
                title="Compare hypothetical actions"
                description="Illustrative intervention comparisons based on the current demo scenario. The backend risk engine can replace these estimates later."
              />



              <div className="grid gap-5 sm:grid-cols-2">
                <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                  <p className="text-xs text-slate-500">Baseline modeled risk</p>
                  <p className="mt-3 text-4xl font-bold">{calculateRisk(scenario)}</p>
                  <p className="mt-2 text-xs text-slate-400">Before hypothetical actions</p>
                </article>
                <article className="rounded-xl border border-emerald-200 bg-emerald-50 p-5">
                  <p className="text-xs text-emerald-800">Illustrative reduction target</p>
                  <p className="mt-3 text-4xl font-bold text-emerald-900">
                    {Math.max(0, calculateRisk(scenario) - 17)}
                  </p>
                  <p className="mt-2 text-xs text-emerald-800">
                    Example only Â· Not an engine result
                  </p>
                </article>
              </div>



              <div className="mt-5 overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
                <table className="w-full min-w-[550px] text-left text-sm">
                  <thead className="bg-slate-50 text-xs text-slate-500">
                    <tr>
                      <th className="px-5 py-4">Candidate action</th>
                      <th className="px-5 py-4">Target</th>
                      <th className="px-5 py-4">Demo cost</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    <tr>
                      <td className="px-5 py-4 font-medium">Clear priority drain</td>
                      <td className="px-5 py-4">Drainage capacity</td>
                      <td className="px-5 py-4">â‚¹20,000</td>
                    </tr>
                    <tr>
                      <td className="px-5 py-4 font-medium">Remove debris hotspot</td>
                      <td className="px-5 py-4">Waste accumulation</td>
                      <td className="px-5 py-4">â‚¹12,000</td>
                    </tr>
                    <tr>
                      <td className="px-5 py-4 font-medium">Prepare traffic diversion</td>
                      <td className="px-5 py-4">Road exposure</td>
                      <td className="px-5 py-4">â‚¹8,000</td>
                    </tr>
                  </tbody>
                </table>
              </div>



              <p className="mt-4 text-xs leading-5 text-slate-500">
                All costs are fictional demo values. Actual intervention ranking and
                risk reductions require the validated backend engine.
              </p>
            </>
          )}



          {/* CIVIC REPORTS */}
          {activePage === 'reports' && (
            <>
              <SectionHeading
                eyebrow="05 / Civic reports"
                title="Report an urban issue"
                description="Create a local demo record. Nothing is sent to a municipal system or backend."
              />



              <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
                <form onSubmit={submitDemoReport} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                  <h3 className="font-semibold">New report</h3>



                  <label htmlFor="description" className="mb-2 mt-5 block text-sm font-medium">Description</label>
                  <textarea id="description" name="description" required rows="4" placeholder="Describe the observed urban issue..." className="w-full rounded-lg border border-slate-200 p-3 text-sm outline-none focus:border-blue-500" />



                  <label htmlFor="category" className="mb-2 mt-4 block text-sm font-medium">Event category</label>
                  <select id="category" name="category" className="w-full rounded-lg border border-slate-200 bg-white p-3 text-sm">
                    <option>Waterlogging</option>
                    <option>Waste hotspot</option>
                    <option>Drain blockage</option>
                    <option>Road disruption</option>
                    <option>Other</option>
                  </select>



                  <label htmlFor="sector" className="mb-2 mt-4 block text-sm font-medium">Sample sector</label>
                  <select id="sector" name="sector" className="w-full rounded-lg border border-slate-200 bg-white p-3 text-sm">
                    {sectors.map((sector) => (
                      <option key={sector.id} value={sector.id}>{sector.id}</option>
                    ))}
                  </select>



                  <label htmlFor="severity" className="mb-2 mt-4 block text-sm font-medium">Severity</label>
                  <select id="severity" name="severity" className="w-full rounded-lg border border-slate-200 bg-white p-3 text-sm">
                    <option>Low</option>
                    <option>Moderate</option>
                    <option>High</option>
                  </select>



                  <button type="submit" className="mt-5 w-full rounded-lg bg-[#126bdf] px-4 py-3 text-sm font-semibold text-white hover:bg-blue-700">
                    Submit demo report
                  </button>



                  {reportMessage && (
                    <p className="mt-3 text-sm text-teal-700">{reportMessage}</p>
                  )}
                </form>



                <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                  <h3 className="font-semibold">Recent reports</h3>
                  <p className="mt-1 text-xs text-slate-500">Session-only sample records</p>
                  <div className="mt-4 divide-y divide-slate-100">
                    {events.map((event, index) => (
                      <div key={`${event.time}-${index}`} className="flex items-start justify-between gap-3 py-4">
                        <div>
                          <p className="text-sm font-semibold">{event.category}</p>
                          <p className="mt-1 text-xs text-slate-500">{event.sector} Â· {event.time}</p>
                          <p className="mt-2 text-xs text-slate-400">{event.status}</p>
                        </div>
                        <RiskBadge risk={event.severity === 'High' ? 75 : event.severity === 'Moderate' ? 55 : 30} />
                      </div>
                    ))}
                  </div>
                </article>
              </div>
            </>
          )}



          {/* METHODOLOGY */}
          {activePage === 'methodology' && (
            <>
              <SectionHeading
                eyebrow="06 / About & methodology"
                title="How C3T works"
                description="C3T explores how hypothetical failures across drainage, waste and roads could interact, and how preventive actions might help."
              />



              <div className="grid gap-5 md:grid-cols-3">
                {[
                  {
                    number: '01',
                    title: 'Scenario inputs',
                    text: 'Define rainfall, debris, drain conditions, traffic and temperature.',
                  },
                  {
                    number: '02',
                    title: 'Risk analysis',
                    text: 'Explore illustrative relationships between inputs and possible outcomes.',
                  },
                  {
                    number: '03',
                    title: 'Interventions',
                    text: 'Compare possible actions and resource trade-offs.',
                  },
                ].map((step) => (
                  <article key={step.number} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                    <p className="text-xs font-bold text-teal-700">{step.number}</p>
                    <h3 className="mt-3 font-bold">{step.title}</h3>
                    <p className="mt-2 text-sm leading-6 text-slate-500">{step.text}</p>
                  </article>
                ))}
              </div>



              <article className="mt-5 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
                <h3 className="font-semibold">Limitations and responsible use</h3>
                <ul className="mt-4 space-y-3 text-sm leading-6 text-slate-600">
                  <li>â€¢ All current frontend records and sector geometry are synthetic.</li>
                  <li>â€¢ Scores are illustrative demo indices, not calibrated probabilities.</li>
                  <li>â€¢ Intervention costs and effects are fictional examples.</li>
                  <li>â€¢ Heat stress is a separate pathway and is excluded from waterlogging risk.</li>
                  <li>â€¢ No live municipal system is connected.</li>
                  <li>â€¢ The frontend calculations will need to be replaced by the team's backend risk engine.</li>
                </ul>
              </article>
            </>
          )}



          <footer className="mt-8 border-t border-slate-200 py-5 text-center text-[10px] leading-5 text-slate-400">
            C3T Â· AI for DPI Â· Chandigarh
            <br />
            Simulated prototype Â· Not for operational decision-making
          </footer>
        </main>
      </div>
    </div>
  )
}



export default App
