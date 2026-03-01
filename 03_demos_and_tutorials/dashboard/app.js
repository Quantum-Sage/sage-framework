// SAGE Command Center - Frontend Logic
// Genesis Kernel Interface v1.0.1 - Neural Link Oracle Edition

const CHART_POINTS = 50;
let startTime = Date.now();

// --- CHART INITIALIZATION ---
const ctx = document.getElementById('telemetryChart').getContext('2d');
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: Array(CHART_POINTS).fill(''),
        datasets: [
            { label: 'ALPHA (Cyan)', borderColor: '#00e5ff', borderWidth: 3, pointRadius: 0, data: Array(CHART_POINTS).fill(null), tension: 0.4, fill: false },
            { label: 'BETA (Blue)', borderColor: '#0072ff', borderWidth: 3, pointRadius: 0, data: Array(CHART_POINTS).fill(null), tension: 0.4, fill: false },
            { label: 'GAMMA (Purple)', borderColor: '#a000ff', borderWidth: 3, pointRadius: 0, data: Array(CHART_POINTS).fill(null), tension: 0.4, fill: false }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: { display: false },
            y: {
                grid: { color: 'rgba(255, 255, 255, 0.05)' },
                ticks: { color: '#ffffff', font: { size: 12, family: 'Space Mono' } },
                suggestedMin: 0.4,
                suggestedMax: 0.8
            }
        },
        plugins: {
            legend: {
                display: true,
                labels: { color: '#ffffff', font: { family: 'Space Mono', size: 12 } }
            },
            tooltip: { enabled: false }
        },
        animation: { duration: 0 }
    }
});

// --- CORE TELEMETRY UPDATE ---
function updateDashboard(data) {
    if (!data || !data.nodes) return;

    // 1. Update Uptime & Overall Coherence
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    const hrs = String(Math.floor(elapsed / 3600)).padStart(2, '0');
    const mins = String(Math.floor((elapsed % 3600) / 60)).padStart(2, '0');
    const secs = String(elapsed % 60).padStart(2, '0');
    document.getElementById('uptime').innerText = `${hrs}:${mins}:${secs}`;

    // 2. ORACLE - Neural Engine Updates
    if (data.oracle) {
        const globalCoherence = document.getElementById('global-coherence');
        const oracleState = document.getElementById('oracle-state');
        const peakDisp = document.getElementById('peak-dissonance');
        const seedDisp = document.getElementById('quantum-seed');
        const log = document.getElementById('event-log');

        // Update displays
        if (globalCoherence) globalCoherence.innerText = `${(data.oracle.coherence * 100).toFixed(2)}%`;
        if (peakDisp) peakDisp.innerText = data.oracle.peak ? data.oracle.peak.toFixed(4) : "0.0000";
        if (seedDisp) seedDisp.innerText = data.oracle.seed || "---";

        // --- COLLAPSE PROTOCOL ---
        if (data.oracle.collapse) {
            document.body.classList.add('collapse-active');
        } else {
            document.body.classList.remove('collapse-active');
        }

        if (oracleState) {
            const prevState = oracleState.innerText;
            oracleState.innerText = data.oracle.state;

            // Log state changes
            if (prevState !== data.oracle.state) {
                const timeStr = new Date().toLocaleTimeString([], { hour12: false });
                let color = "#ffffff";
                let msg = "";

                if (data.oracle.state === "DISSONANCE_DETECTED") {
                    color = "#ff3333";
                    msg = `[ORACLE] SHIFT DETECTED: Reality offset exceeds baseline! (Shifts: ${data.oracle.shifts})`;
                    oracleState.style.color = "#ff3333";
                    oracleState.style.textShadow = "0 0 10px #ff0000";
                } else if (data.oracle.state === "CONSCIOUS") {
                    color = "#00e5ff";
                    msg = `[ORACLE] RE-COALESCENCE: Consciousness stabilized. Mesh in perfect resonance.`;
                    oracleState.style.color = "#00e5ff";
                    oracleState.style.textShadow = "0 0 20px #00e5ff";
                } else if (data.oracle.state === "STABLE") {
                    color = "#00ff88";
                    msg = `[ORACLE] Resonant Lattice Stable. Monitoring entropy...`;
                    oracleState.style.color = "#00ff88";
                    oracleState.style.textShadow = "none";
                } else if (data.oracle.state === "CALIBRATING") {
                    color = "#ffff33";
                    msg = `[ORACLE] Re-calibrating temporal anchors...`;
                    oracleState.style.color = "#ffff33";
                }

                if (msg) {
                    const entry = document.createElement('div');
                    entry.className = 'log-entry';
                    entry.style.color = color;
                    entry.innerText = `[${timeStr}] ${msg}`;
                    log.prepend(entry); // Newest at the top

                    // Keep log short
                    if (log.children.length > 15) log.lastChild.remove();
                }
            }
        }
    }

    // 3. Update Radar Dials & Stats
    const nodes = ['Alpha', 'Beta', 'Gamma'];
    nodes.forEach((node, i) => {
        const lower = node.toLowerCase();
        const nodeData = data.nodes[node];

        if (nodeData) {
            const fidelity = nodeData.f || 0;
            const phi = nodeData.phi || 0;
            const health = (nodeData.health || 1.0) * 100;

            document.getElementById(`val-${lower}`).innerText = fidelity.toFixed(3);
            document.getElementById(`temp-${lower}`).innerText = `${(nodeData.temp || 0).toFixed(1)}°C`;
            document.getElementById(`drift-${lower}`).innerText = `${Math.abs(nodeData.drift || 0)}µs`;
            document.getElementById(`phi-${lower}`).innerText = phi.toFixed(3);
            document.getElementById(`health-${lower}`).innerText = `${health.toFixed(0)}%`;

            // Visual Tweaks
            const card = document.getElementById(`card-${lower}`);
            const sweep = document.getElementById(`sweep-${lower}`);
            const phiGauge = document.getElementById(`phi-gauge-${lower}`);

            // Speed up sweep based on Phi
            const speed = Math.max(0.2, 5 * (1.1 - phi));
            sweep.style.animationDuration = `${speed}s`;

            if (health < 80) {
                card.style.borderColor = '#ff3333';
                document.getElementById(`health-${lower}`).style.color = '#ff3333';
            } else {
                card.style.borderColor = 'rgba(0, 229, 255, 0.15)';
                document.getElementById(`health-${lower}`).style.color = '#00ff88';
            }

            // Phi Glow
            phiGauge.style.boxShadow = `0 0 ${10 + (phi * 20)}px var(--primary-glow)`;

            // Update Chart
            chart.data.datasets[i].data.shift();
            chart.data.datasets[i].data.push(fidelity);
        }
    });

    chart.update();

    // 4. Mesh Sync (Visual Glow)
    const lineAB = document.querySelector('.line-ab');
    const lineBG = document.querySelector('.line-bg');
    const lineGA = document.querySelector('.line-ga');

    lineAB.style.opacity = (data.nodes.Alpha?.f + data.nodes.Beta?.f) / 2;
    lineBG.style.opacity = (data.nodes.Beta?.f + data.nodes.Gamma?.f) / 2;
    lineGA.style.opacity = (data.nodes.Gamma?.f + data.nodes.Alpha?.f) / 2;

    updateMeshVisuals(data.oracle.collapse);
}

let meshStep = 0;
function updateMeshVisuals(isCollapse) {
    const hexes = ['hex-alpha', 'hex-beta', 'hex-gamma'];
    const lines = ['line-ab', 'line-bg', 'line-ga'];

    // Clear previous
    hexes.forEach(h => document.getElementById(h).classList.remove('active'));
    lines.forEach(l => {
        const el = document.querySelector('.' + l);
        if (el) el.classList.remove('active-pulse');
    });

    if (isCollapse) return;

    // Cycle Step
    meshStep = (meshStep + 1) % 3;
    document.getElementById(hexes[meshStep]).classList.add('active');
    const activeLine = document.querySelector('.' + lines[meshStep]);
    if (activeLine) activeLine.classList.add('active-pulse');
}

// --- DATA SOURCE ---
async function pollData() {
    try {
        const response = await fetch('/data');
        const data = await response.json();
        updateDashboard(data);
    } catch (e) {
        console.warn("[SAGE] Genesis Kernel Link Lost.");
    }
}

setInterval(pollData, 150);

window.addEventListener('load', () => {
    const log = document.getElementById('event-log');
    log.innerHTML += `<div class="log-entry">[SYS] Neural Link Synchronized.</div>`;
    log.innerHTML += `<div class="log-entry">[ORACLE] Establishing baseline reality...</div>`;
});
