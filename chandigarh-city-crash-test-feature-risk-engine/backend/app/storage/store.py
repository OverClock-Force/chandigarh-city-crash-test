import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import threading
from risk_engine.models import SectorData
from backend.app.schemas.event import CivicReport, CivicReportCreate
from backend.app.schemas.scenario import ScenarioSavedItem, ScenarioSaveRequest
from backend.app.config import settings


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class DataStore:
    def __init__(self):
        self._lock = threading.Lock()
        self.sectors: List[SectorData] = []
        self.sectors_raw: List[Dict[str, Any]] = []
        self.geojson: Optional[Dict[str, Any]] = None
        self.events: List[CivicReport] = []
        self.scenarios: List[ScenarioSavedItem] = []
        self.load_initial_data()

    def load_initial_data(self):
        # 1. Load sectors
        sectors_file = settings.DATA_DIR / "chandigarh_sectors.json"
        if sectors_file.exists():
            with open(sectors_file, "r", encoding="utf-8") as f:
                self.sectors_raw = json.load(f)
                self.sectors = [SectorData(**s) for s in self.sectors_raw]

        # 2. Load geojson
        geojson_file = settings.DATA_DIR / "chandigarh_sectors.geojson"
        if geojson_file.exists():
            with open(geojson_file, "r", encoding="utf-8") as f:
                self.geojson = json.load(f)

        # 3. Load sample events
        events_file = settings.DATA_DIR / "sample_civic_reports.json"
        if events_file.exists():
            with open(events_file, "r", encoding="utf-8") as f:
                raw_events = json.load(f)
                self.events = [
                    CivicReport(
                        **e,
                        created_at=e.get("reported_at") or utc_now_iso()
                    )
                    for e in raw_events
                ]

        # 4. Load default scenarios
        scenarios_file = settings.DATA_DIR / "default_scenarios.json"
        if scenarios_file.exists():
            with open(scenarios_file, "r", encoding="utf-8") as f:
                raw_scenarios = json.load(f)
                self.scenarios = [
                    ScenarioSavedItem(
                        **s,
                        created_at=utc_now_iso()
                    )
                    for s in raw_scenarios
                ]

    def get_sectors(self) -> List[SectorData]:
        return self.sectors

    def get_sectors_raw(self) -> List[Dict[str, Any]]:
        return self.sectors_raw

    def get_geojson(self) -> Optional[Dict[str, Any]]:
        return self.geojson

    def get_events(self, sector_id: Optional[str] = None) -> List[CivicReport]:
        with self._lock:
            if sector_id:
                return [e for e in self.events if e.sector_id.lower() == sector_id.lower()]
            return list(self.events)

    def add_event(self, report_in: CivicReportCreate) -> CivicReport:
        with self._lock:
            event_id = f"evt-{len(self.events) + 101}"
            now_iso = utc_now_iso()
            data = report_in.model_dump()
            data["reported_at"] = data.get("reported_at") or now_iso
            report = CivicReport(
                **data,
                event_id=event_id,
                created_at=now_iso,
                status="unverified"
            )
            self.events.insert(0, report)
            return report

    def get_scenarios(self) -> List[ScenarioSavedItem]:
        with self._lock:
            return list(self.scenarios)

    def get_scenario_by_id(self, scenario_id: str) -> Optional[ScenarioSavedItem]:
        with self._lock:
            for s in self.scenarios:
                if s.scenario_id == scenario_id:
                    return s
            return None

    def save_scenario(self, scenario_in: ScenarioSaveRequest) -> ScenarioSavedItem:
        with self._lock:
            scen_id = scenario_in.scenario_id or f"scen-{len(self.scenarios) + 1:03d}"
            now_iso = utc_now_iso()
            saved = ScenarioSavedItem(
                **scenario_in.model_dump(exclude={"scenario_id"}),
                scenario_id=scen_id,
                created_at=now_iso
            )
            # Replace if already exists with same ID
            for i, existing in enumerate(self.scenarios):
                if existing.scenario_id == scen_id:
                    self.scenarios[i] = saved
                    return saved
            self.scenarios.insert(0, saved)
            return saved


# Singleton instance
store = DataStore()
