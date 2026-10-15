
const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function adaptScenarioToBackend(scenario) {
    if (!scenario) return scenario;
    if (scenario.rainfall_mm !== undefined && scenario.debris_level !== undefined) {
        return scenario;
    }

    const debrisMap = {
        'low': 'normal',
        'medium': 'normal',
        'normal': 'normal',
        'high': 'high',
        'extreme': 'extreme',
    };
    const drainMap = {
        'good': 'good',
        'clear': 'good',
        'partial blockage': 'partial_blockage',
        'partial_blockage': 'partial_blockage',
        'blocked': 'critical',
        'critical': 'critical',
    };
    const trafficMap = {
        'normal': 'normal',
        'moderate': 'normal',
        'peak': 'peak',
    };

    const debrisKey = String(scenario.debris ?? scenario.debris_level ?? 'high').toLowerCase();
    const drainKey = String(scenario.drainCondition ?? scenario.drain_condition ?? 'partial_blockage').toLowerCase();
    const trafficKey = String(scenario.traffic ?? scenario.traffic_level ?? 'peak').toLowerCase();

    return {
        rainfall_mm: Number(scenario.rainfall_mm ?? scenario.rainfall ?? 60),
        rainfall_duration_hours: scenario.rainfall_duration_hours ?? null,
        debris_level: debrisMap[debrisKey] || 'high',
        drain_condition: drainMap[drainKey] || 'partial_blockage',
        traffic_level: trafficMap[trafficKey] || 'peak',
        temperature_c: Number(scenario.temperature_c ?? scenario.temperature ?? 38),
        resources: scenario.resources ?? {
            maintenance_teams: 4,
            pumping_units: 2,
            budget_inr: 350000.0,
        },
    };
}

async function request(path, options = {}) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...options.headers,
        },
    });

    if (!response.ok) {
        const detail = await response.text();
        throw new Error(`API error ${response.status}: ${detail}`);
    }

    return response.json();
}

export function getSectors() {
    return request("/api/sectors");
}

export function getEvents(sectorId) {
    const query = sectorId
        ? `?sector_id=${encodeURIComponent(sectorId)}`
        : "";

    return request(`/api/events${query}`);
}

export function runStressTest(scenario) {
    return request("/api/stress-test", {
        method: "POST",
        body: JSON.stringify(adaptScenarioToBackend(scenario)),
    });
}

export function optimizeInterventions(scenario) {
    return request("/api/optimize", {
        method: "POST",
        body: JSON.stringify(adaptScenarioToBackend(scenario)),
    });
}

export function getScenarios() {
    return request("/api/scenarios");
}

export function saveScenario(scenario) {
    return request("/api/scenarios", {
        method: "POST",
        body: JSON.stringify(adaptScenarioToBackend(scenario)),
    });
}
