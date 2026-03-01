import { useState, useCallback, useMemo } from "react";

// ═══════════════════════════════════════════════════════════════
// THE SAGE BOUND CALCULATOR
// Closed-form quantum network feasibility from hardware datasheets
// No simulation required — O(1) from specs to answer
// ═══════════════════════════════════════════════════════════════

const PRESETS = {
  willow: { name: "Google Willow", fGate: 0.997, t2: 1.0, pGen: 0.10 },
  quera: { name: "QuEra", fGate: 0.995, t2: 10.0, pGen: 0.05 },
  custom: { name: "Custom", fGate: 0.998, t2: 2.0, pGen: 0.15 },
};

const C = 200000; // speed of light in fiber, km/s
const S_THRESH = 0.851; // BB84 security threshold

// ─── Core Math ───────────────────────────────────────────────
// All t2 values are in SECONDS throughout

function sageBound(fGate, t2, pGen, L, N) {
  const s = L / N;
  const tLink = s / C;
  const alphaDet = 2 * Math.log(fGate) - tLink / t2;
  const alphaStoch = 2 * Math.log(fGate) - (tLink / t2) * (1 + 2 / pGen);
  return {
    fDet: Math.exp(N * alphaDet),
    fStoch: Math.exp(N * alphaStoch),
    hopDet: Math.exp(alphaDet),
    hopStoch: Math.exp(alphaStoch),
    gateBudget: 2 * N * Math.log(fGate),
    decoBudget: -N * (tLink / t2) * (1 + 2 / pGen),
    spacing: s,
  };
}

function findOptimal(fGate, t2, pGen, L) {
  let bestF = 0, bestN = 1, minN = null;
  for (let n = 1; n <= 500; n++) {
    const f = sageBound(fGate, t2, pGen, L, n).fStoch;
    if (f > bestF) { bestF = f; bestN = n; }
    if (f >= S_THRESH && minN === null) minN = n;
    if (n > 10 && f < bestF * 0.2) break;
  }
  return { minN, bestF, bestN };
}

function sweepNodes(fGate, t2, pGen, L) {
  const out = [];
  const cap = Math.min(200, Math.max(50, Math.ceil(L / 8)));
  for (let n = 1; n <= cap; n++) {
    const r = sageBound(fGate, t2, pGen, L, n);
    out.push({ n, fDet: Math.max(0, r.fDet), fStoch: Math.max(0, r.fStoch) });
  }
  return out;
}

function sageWall(fGate, t2, pGen) {
  for (let L = 100; L <= 50000; L += 100) {
    if (findOptimal(fGate, t2, pGen, L).minN === null) return L - 100;
  }
  return 50000;
}

// ─── SVG Charts ──────────────────────────────────────────────

function NodeChart({ data, width = 540, height = 210 }) {
  if (!data || data.length < 2) return null;
  const m = { t: 22, r: 20, b: 36, l: 52 };
  const w = width - m.l - m.r;
  const h = height - m.t - m.b;
  const maxN = data[data.length - 1].n;
  const vals = data.flatMap(d => [d.fDet, d.fStoch]).filter(v => v > 0.001);
  if (vals.length === 0) return <svg width={width} height={height}><text x={width/2} y={height/2} fill="#4a6a8a" fontSize="12" textAnchor="middle" fontFamily="monospace">All fidelities near zero — hardware insufficient</text></svg>;
  const yMax = Math.min(1.0, Math.max(...vals) * 1.06);
  const yMin = Math.max(0, Math.min(...vals) - 0.05);
  const sx = n => m.l + (n / maxN) * w;
  const sy = f => m.t + (1 - (Math.max(yMin, Math.min(yMax, f)) - yMin) / (yMax - yMin)) * h;
  const mkPath = key => data.filter(d => d[key] > 0.001).map((d, i) => `${i === 0 ? "M" : "L"}${sx(d.n).toFixed(1)},${sy(d[key]).toFixed(1)}`).join(" ");
  const tY = sy(S_THRESH);
  const fTicks = [];
  for (let f = Math.ceil(yMin * 10) / 10; f <= yMax + 0.001; f += 0.1) fTicks.push(+f.toFixed(1));
  const nTicks = [1, Math.round(maxN * 0.25), Math.round(maxN * 0.5), Math.round(maxN * 0.75), maxN].filter((v, i, a) => a.indexOf(v) === i);

  return (
    <svg width={width} height={height} style={{ display: "block" }}>
      {fTicks.map(f => <line key={f} x1={m.l} x2={width - m.r} y1={sy(f)} y2={sy(f)} stroke="#111c28" strokeWidth="1" />)}
      {S_THRESH >= yMin && S_THRESH <= yMax && <>
        <line x1={m.l} x2={width - m.r} y1={tY} y2={tY} stroke="#ff4757" strokeWidth="1.5" strokeDasharray="6,4" />
        <text x={width - m.r - 2} y={tY - 5} fill="#ff4757" fontSize="9" textAnchor="end" fontFamily="monospace">S={S_THRESH}</text>
      </>}
      <path d={mkPath("fDet")} fill="none" stroke="#2a4a7a" strokeWidth="1.5" opacity="0.45" />
      <path d={mkPath("fStoch")} fill="none" stroke="#00d4ee" strokeWidth="2.2" />
      <line x1={m.l} x2={m.l} y1={m.t} y2={height - m.b} stroke="#1a2a38" />
      <line x1={m.l} x2={width - m.r} y1={height - m.b} y2={height - m.b} stroke="#1a2a38" />
      {nTicks.map(n => <text key={n} x={sx(n)} y={height - m.b + 14} fill="#3a5a7a" fontSize="9" textAnchor="middle" fontFamily="monospace">{n}</text>)}
      <text x={m.l + w / 2} y={height - 2} fill="#2a4a5a" fontSize="9" textAnchor="middle" fontFamily="monospace">Nodes (N)</text>
      {fTicks.map(f => <text key={f} x={m.l - 5} y={sy(f) + 3} fill="#3a5a7a" fontSize="9" textAnchor="end" fontFamily="monospace">{f.toFixed(1)}</text>)}
      <line x1={m.l + 8} x2={m.l + 26} y1={m.t + 6} y2={m.t + 6} stroke="#00d4ee" strokeWidth="2" />
      <text x={m.l + 30} y={m.t + 9} fill="#6aa4c8" fontSize="9" fontFamily="monospace">Stochastic</text>
      <line x1={m.l + 104} x2={m.l + 122} y1={m.t + 6} y2={m.t + 6} stroke="#2a4a7a" strokeWidth="1.5" opacity="0.5" />
      <text x={m.l + 126} y={m.t + 9} fill="#3a5a7a" fontSize="9" fontFamily="monospace">Deterministic</text>
    </svg>
  );
}

function DistChart({ fGate, t2, pGen, width = 540, height = 210 }) {
  const dists = [100, 250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8200, 10000];
  const pts = dists.map(L => ({ L, ...findOptimal(fGate, t2, pGen, L) }));
  const m = { t: 22, r: 20, b: 36, l: 52 };
  const w = width - m.l - m.r;
  const h = height - m.t - m.b;
  const sx = l => m.l + (l / 10000) * w;
  const sy = f => m.t + (1 - f) * h;
  const path = pts.map((d, i) => `${i === 0 ? "M" : "L"}${sx(d.L).toFixed(1)},${sy(d.bestF).toFixed(1)}`).join(" ");

  return (
    <svg width={width} height={height} style={{ display: "block" }}>
      <line x1={m.l} x2={width - m.r} y1={sy(S_THRESH)} y2={sy(S_THRESH)} stroke="#ff4757" strokeWidth="1.5" strokeDasharray="6,4" />
      <text x={width - m.r - 2} y={sy(S_THRESH) - 5} fill="#ff4757" fontSize="9" textAnchor="end" fontFamily="monospace">BB84</text>
      <path d={path} fill="none" stroke="#00d4ee" strokeWidth="2" />
      {pts.map((d, i) => <circle key={i} cx={sx(d.L)} cy={sy(d.bestF)} r={3} fill={d.minN !== null ? "#00d4ee" : "#ff4757"} />)}
      <line x1={m.l} x2={m.l} y1={m.t} y2={height - m.b} stroke="#1a2a38" />
      <line x1={m.l} x2={width - m.r} y1={height - m.b} y2={height - m.b} stroke="#1a2a38" />
      {[0, 2000, 4000, 6000, 8000, 10000].map(l => <text key={l} x={sx(l)} y={height - m.b + 14} fill="#3a5a7a" fontSize="9" textAnchor="middle" fontFamily="monospace">{l >= 1000 ? `${l / 1000}k` : l}</text>)}
      <text x={m.l + w / 2} y={height - 2} fill="#2a4a5a" fontSize="9" textAnchor="middle" fontFamily="monospace">Distance (km)</text>
      {[0, 0.2, 0.4, 0.6, 0.8, 1.0].map(f => <text key={f} x={m.l - 5} y={sy(f) + 3} fill="#3a5a7a" fontSize="9" textAnchor="end" fontFamily="monospace">{f.toFixed(1)}</text>)}
    </svg>
  );
}

// ─── UI Components ───────────────────────────────────────────

function Slider({ label, value, onChange, min, max, step, unit }) {
  const fmt = step < 0.01 ? value.toFixed(4) : step < 1 ? value.toFixed(2) : value.toFixed(1);
  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
        <span style={{ color: "#6a94b8", fontSize: 12, fontFamily: "monospace" }}>{label}</span>
        <span style={{ color: "#d0e0f0", fontSize: 13, fontFamily: "monospace", fontWeight: 700 }}>
          {fmt}{unit && <span style={{ color: "#3a5a7a", marginLeft: 3, fontSize: 10, fontWeight: 400 }}>{unit}</span>}
        </span>
      </div>
      <input type="range" min={min} max={max} step={step} value={value}
        onChange={e => onChange(parseFloat(e.target.value))}
        style={{ width: "100%", accentColor: "#00d4ee", height: 3, cursor: "pointer" }} />
    </div>
  );
}

function Stat({ label, value, sub, warn }) {
  return (
    <div style={{
      background: warn ? "rgba(255,71,87,0.06)" : "rgba(0,212,238,0.025)",
      border: `1px solid ${warn ? "rgba(255,71,87,0.15)" : "rgba(0,212,238,0.07)"}`,
      borderRadius: 6, padding: "10px 13px", flex: 1, minWidth: 115,
    }}>
      <div style={{ color: "#3a5a7a", fontSize: 10, fontFamily: "monospace", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 4 }}>{label}</div>
      <div style={{ color: warn ? "#ff6050" : "#d0e8f8", fontSize: 20, fontFamily: "monospace", fontWeight: 700 }}>{value}</div>
      {sub && <div style={{ color: "#2a4a5a", fontSize: 10, fontFamily: "monospace", marginTop: 2 }}>{sub}</div>}
    </div>
  );
}

function Bar({ label, pct, val, color }) {
  return (
    <div style={{ marginBottom: 13 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
        <span style={{ color: color === "cyan" ? "#6ab4d8" : "#d8a07a", fontSize: 11, fontFamily: "monospace" }}>{label}</span>
        <span style={{ color: "#c8d8e8", fontSize: 11, fontFamily: "monospace", fontWeight: 600 }}>{pct}%</span>
      </div>
      <div style={{ background: "#060e18", borderRadius: 3, height: 11, overflow: "hidden" }}>
        <div style={{
          background: color === "cyan" ? "linear-gradient(90deg, #00b8d4, #005566)" : "linear-gradient(90deg, #d06030, #7a2200)",
          height: "100%", width: `${pct}%`, borderRadius: 3, transition: "width 0.2s"
        }} />
      </div>
      <div style={{ color: "#1a2a3a", fontSize: 9, fontFamily: "monospace", marginTop: 1 }}>= {val}</div>
    </div>
  );
}

// ─── Main App ────────────────────────────────────────────────

export default function SageBoundCalculator() {
  const [preset, setPreset] = useState("willow");
  const [fGate, setFGate] = useState(0.997);
  const [t2, setT2] = useState(1.0);
  const [pGen, setPGen] = useState(0.10);
  const [dist, setDist] = useState(1000);
  const [tab, setTab] = useState("fidelity");

  const pick = useCallback((k) => {
    setPreset(k);
    const p = PRESETS[k];
    setFGate(p.fGate); setT2(p.t2); setPGen(p.pGen);
  }, []);
  const adj = useCallback((fn) => (v) => { setPreset("custom"); fn(v); }, []);

  const opt = useMemo(() => findOptimal(fGate, t2, pGen, dist), [fGate, t2, pGen, dist]);
  const data = useMemo(() => sweepNodes(fGate, t2, pGen, dist), [fGate, t2, pGen, dist]);
  const wall = useMemo(() => sageWall(fGate, t2, pGen), [fGate, t2, pGen]);
  const det = useMemo(() => sageBound(fGate, t2, pGen, dist, opt.minN || opt.bestN), [fGate, t2, pGen, dist, opt]);

  const ok = opt.minN !== null;
  const pen = (1 + 2 / pGen).toFixed(1);

  // Sensitivity: find improvements needed when infeasible
  const sens = useMemo(() => {
    if (ok) return null;
    let nfg = null, npg = null, nt2 = null;
    for (let f = fGate; f <= 0.9999; f += 0.0001) { if (findOptimal(f, t2, pGen, dist).minN !== null) { nfg = f; break; } }
    for (let p = pGen; p <= 0.50; p += 0.01) { if (findOptimal(fGate, t2, p, dist).minN !== null) { npg = p; break; } }
    for (let t = t2; t <= 120; t += 0.5) { if (findOptimal(fGate, t, pGen, dist).minN !== null) { nt2 = t; break; } }
    return { nfg, npg, nt2 };
  }, [ok, fGate, t2, pGen, dist]);

  // Error budget
  const gAbs = Math.abs(det.gateBudget);
  const dAbs = Math.abs(det.decoBudget);
  const total = gAbs + dAbs || 1;
  const gPct = (gAbs / total * 100).toFixed(1);
  const dPct = (dAbs / total * 100).toFixed(1);
  const useN = opt.minN || opt.bestN;

  return (
    <div style={{ minHeight: "100vh", background: "#070c16", color: "#a8b8c8", fontFamily: "'SF Mono', 'Fira Code', 'Cascadia Code', Consolas, monospace" }}>
      <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&display=swap" rel="stylesheet" />

      {/* Header */}
      <div style={{ borderBottom: "1px solid rgba(0,212,238,0.07)", padding: "16px 22px 12px", background: "linear-gradient(180deg, rgba(0,212,238,0.015) 0%, transparent 100%)" }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: 10, flexWrap: "wrap" }}>
          <h1 style={{ fontSize: 21, fontFamily: "'Playfair Display', Georgia, serif", fontWeight: 800, color: "#dce8f4", margin: 0 }}>SAGE BOUND</h1>
          <span style={{ color: "#1e3a54", fontSize: 11, letterSpacing: "0.05em" }}>QUANTUM NETWORK FEASIBILITY</span>
        </div>
        <p style={{ color: "#1a2a3a", fontSize: 10, margin: "3px 0 0", letterSpacing: "0.03em" }}>O(1) from hardware specs · No simulation · Flett 2026</p>
      </div>

      <div style={{ display: "flex", flexWrap: "wrap" }}>

        {/* ═══ LEFT PANEL ═══ */}
        <div style={{ width: 280, minWidth: 260, borderRight: "1px solid rgba(0,212,238,0.04)", padding: "16px 18px", background: "rgba(0,6,14,0.35)", flexShrink: 0 }}>

          {/* Presets */}
          <div style={{ marginBottom: 16 }}>
            <div style={{ color: "#2a4a64", fontSize: 10, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 7 }}>Platform</div>
            <div style={{ display: "flex", gap: 4 }}>
              {Object.entries(PRESETS).map(([k, p]) => (
                <button key={k} onClick={() => pick(k)} style={{
                  flex: 1, padding: "5px 2px", fontSize: 10, cursor: "pointer", fontFamily: "inherit",
                  background: preset === k ? "rgba(0,212,238,0.08)" : "rgba(10,20,30,0.5)",
                  border: `1px solid ${preset === k ? "rgba(0,212,238,0.25)" : "rgba(20,36,50,0.4)"}`,
                  borderRadius: 4, color: preset === k ? "#00d4ee" : "#3a5a7a",
                }}>{p.name}</button>
              ))}
            </div>
          </div>

          {/* Params */}
          <div style={{ marginBottom: 16 }}>
            <div style={{ color: "#2a4a64", fontSize: 10, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 10 }}>Hardware</div>
            <Slider label="Gate Fidelity" value={fGate} onChange={adj(setFGate)} min={0.990} max={0.9999} step={0.0001} />
            <Slider label="Memory T₂" value={t2} onChange={adj(setT2)} min={0.01} max={60} step={0.1} unit="s" />
            <Slider label="Gen Probability" value={pGen} onChange={adj(setPGen)} min={0.01} max={0.50} step={0.01} />
          </div>

          {/* Target */}
          <div style={{ marginBottom: 16 }}>
            <div style={{ color: "#2a4a64", fontSize: 10, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 10 }}>Target</div>
            <Slider label="Distance" value={dist} onChange={setDist} min={100} max={12000} step={100} unit="km" />
          </div>

          {/* Penalty */}
          <div style={{ padding: "8px 11px", background: "rgba(200,100,40,0.035)", border: "1px solid rgba(200,100,40,0.1)", borderRadius: 5, marginBottom: 8 }}>
            <div style={{ color: "#b06030", fontSize: 10, textTransform: "uppercase", letterSpacing: "0.07em", marginBottom: 2 }}>Stochastic Penalty</div>
            <div style={{ color: "#d8c0a8", fontSize: 15, fontWeight: 700 }}>(1 + 2/p) = {pen}×</div>
            <div style={{ color: "#4a3a2a", fontSize: 9, marginTop: 1 }}>Geometric retry decoherence cost</div>
          </div>

          {/* Wall */}
          <div style={{ padding: "8px 11px", background: wall < dist ? "rgba(255,71,87,0.04)" : "rgba(0,212,238,0.015)", border: `1px solid ${wall < dist ? "rgba(255,71,87,0.1)" : "rgba(0,212,238,0.05)"}`, borderRadius: 5 }}>
            <div style={{ color: wall < dist ? "#ff4757" : "#2a7a94", fontSize: 10, textTransform: "uppercase", letterSpacing: "0.07em", marginBottom: 2 }}>Sage Wall</div>
            <div style={{ color: "#c8d8e8", fontSize: 15, fontWeight: 700 }}>{wall >= 50000 ? ">50k" : wall.toLocaleString()} km</div>
            <div style={{ color: "#2a3a4a", fontSize: 9, marginTop: 1 }}>Hardware distance ceiling</div>
          </div>
        </div>

        {/* ═══ RIGHT PANEL ═══ */}
        <div style={{ flex: 1, minWidth: 300, padding: "16px 20px" }}>

          {/* Verdict */}
          <div style={{
            display: "flex", alignItems: "center", gap: 9, marginBottom: 16, padding: "10px 13px",
            background: ok ? "rgba(0,212,238,0.025)" : "rgba(255,71,87,0.04)",
            border: `1px solid ${ok ? "rgba(0,212,238,0.08)" : "rgba(255,71,87,0.13)"}`, borderRadius: 6,
          }}>
            <div style={{ width: 9, height: 9, borderRadius: "50%", flexShrink: 0, background: ok ? "#00d4ee" : "#ff4757", boxShadow: `0 0 8px ${ok ? "rgba(0,212,238,0.3)" : "rgba(255,71,87,0.3)"}` }} />
            <div>
              <div style={{ color: ok ? "#00d4ee" : "#ff4757", fontSize: 12, fontWeight: 600 }}>{ok ? "FEASIBLE" : "INFEASIBLE — BEYOND SAGE WALL"}</div>
              <div style={{ color: "#2a4a5a", fontSize: 10, marginTop: 1 }}>
                {ok ? `BB84 threshold at ${dist.toLocaleString()} km · N* = ${opt.minN} nodes · ${(dist / opt.minN).toFixed(0)} km spacing` : `Peak F = ${opt.bestF.toFixed(4)} at N = ${opt.bestN} — below S = ${S_THRESH}`}
              </div>
            </div>
          </div>

          {/* Stats row */}
          <div style={{ display: "flex", gap: 6, marginBottom: 16, flexWrap: "wrap" }}>
            <Stat label="Min Nodes N*" value={ok ? opt.minN : "—"} sub={ok ? `${(dist / opt.minN).toFixed(0)} km spacing` : "infeasible"} warn={!ok} />
            <Stat label="Peak Fidelity" value={opt.bestF.toFixed(4)} sub={`at N = ${opt.bestN}`} warn={opt.bestF < S_THRESH} />
            <Stat label="Per-Hop F" value={det.hopStoch.toFixed(4)} sub="stochastic" />
          </div>

          {/* Tab bar */}
          <div style={{ display: "flex", gap: 0, marginBottom: 12 }}>
            {[["fidelity", "F vs N"], ["distance", "F vs Distance"], ["budget", "Error Budget"], ["sensitivity", "Sensitivity"]].map(([k, lbl]) => (
              <button key={k} onClick={() => setTab(k)} style={{
                padding: "5px 12px", border: "none", cursor: "pointer", fontFamily: "inherit", fontSize: 11,
                background: tab === k ? "rgba(0,212,238,0.06)" : "transparent",
                borderBottom: `2px solid ${tab === k ? "#00d4ee" : "transparent"}`,
                color: tab === k ? "#00d4ee" : "#2a4a5a",
              }}>{lbl}</button>
            ))}
          </div>

          {/* Tab content */}
          <div style={{ background: "rgba(3,7,14,0.45)", border: "1px solid rgba(0,212,238,0.04)", borderRadius: 6, padding: 13, minHeight: 225 }}>

            {tab === "fidelity" && <div>
              <div style={{ color: "#2a4a64", fontSize: 10, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 8 }}>Fidelity vs Node Count — {dist.toLocaleString()} km</div>
              <NodeChart data={data} />
              <div style={{ color: "#1a2a38", fontSize: 9, marginTop: 5 }}>Cyan: stochastic floor (conservative) · Blue: deterministic ceiling · Red: BB84 threshold</div>
            </div>}

            {tab === "distance" && <div>
              <div style={{ color: "#2a4a64", fontSize: 10, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 8 }}>Best Achievable Fidelity vs Distance</div>
              <DistChart fGate={fGate} t2={t2} pGen={pGen} />
              <div style={{ color: "#1a2a38", fontSize: 9, marginTop: 5 }}>Each point: best F at optimal N · Cyan = feasible · Red = below threshold</div>
            </div>}

            {tab === "budget" && <div>
              <div style={{ color: "#2a4a64", fontSize: 10, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 12 }}>Log-Fidelity Error Budget</div>
              <Bar label="Gate Error · 2N·log(F_gate)" pct={gPct} val={det.gateBudget.toFixed(6)} color="cyan" />
              <Bar label="Decoherence · N·(s/cT₂)·(1+2/p)" pct={dPct} val={det.decoBudget.toFixed(6)} color="orange" />
              <div style={{ padding: "8px 10px", background: "rgba(0,212,238,0.015)", borderRadius: 5, border: "1px solid rgba(0,212,238,0.04)" }}>
                <div style={{ color: "#3a5a7a", fontSize: 10 }}>
                  log(F) = {(det.gateBudget + det.decoBudget).toFixed(6)} → <span style={{ color: "#6ab4d8" }}>F = {Math.exp(det.gateBudget + det.decoBudget).toFixed(6)}</span>
                </div>
                <div style={{ color: "#1a3040", fontSize: 9, marginTop: 2 }}>N={useN} · spacing={det.spacing.toFixed(1)} km · per-hop F={det.hopStoch.toFixed(5)}</div>
              </div>
              <div style={{ color: "#1a2a38", fontSize: 9, marginTop: 8 }}>
                {parseFloat(dPct) > 80 ? "⚠ Decoherence-dominated: prioritize memory T₂ or generation probability" :
                 parseFloat(gPct) > 80 ? "⚠ Gate-dominated: prioritize gate fidelity improvement" :
                 "Balanced error budget — both parameters contribute significantly"}
              </div>
            </div>}

            {tab === "sensitivity" && <div>
              <div style={{ color: "#2a4a64", fontSize: 10, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 12 }}>Hardware Roadmap Analysis</div>

              {/* Universal sensitivity */}
              <div style={{ padding: "10px 12px", background: "rgba(0,212,238,0.015)", borderRadius: 5, border: "1px solid rgba(0,212,238,0.04)", marginBottom: 12 }}>
                <div style={{ color: "#00b8d0", fontSize: 13, fontWeight: 600, marginBottom: 4, fontFamily: "'Playfair Display', serif" }}>∂ log F / ∂ log F_gate = 2</div>
                <div style={{ color: "#4a7090", fontSize: 11, lineHeight: 1.5 }}>Gate fidelity improvement δ at any node gives exactly 2δ improvement in total log-fidelity. Universal — independent of N, L, or topology.</div>
              </div>

              {/* What-if improvements */}
              {!ok && sens && (() => {
                const rows = [
                  { p: "F_gate", cur: fGate.toFixed(4), need: sens.nfg ? sens.nfg.toFixed(4) : ">0.9999", gap: sens.nfg ? `+${((sens.nfg - fGate) * 100).toFixed(2)}%` : "insufficient alone", c: "#00d4ee" },
                  { p: "p_gen", cur: pGen.toFixed(2), need: sens.npg ? sens.npg.toFixed(2) : ">0.50", gap: sens.npg ? `${(sens.npg / pGen).toFixed(1)}× current` : "insufficient alone", c: "#e07030" },
                  { p: "T₂", cur: `${t2.toFixed(1)}s`, need: sens.nt2 ? `${sens.nt2.toFixed(1)}s` : ">120s", gap: sens.nt2 ? `${(sens.nt2 / t2).toFixed(1)}× current` : "insufficient alone", c: "#50b840" },
                ];
                return <div>
                  <div style={{ color: "#6ab4d8", fontSize: 11, marginBottom: 7 }}>Required for {dist.toLocaleString()} km feasibility:</div>
                  {rows.map((r, i) => (
                    <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 7, padding: "6px 9px", background: "rgba(6,12,20,0.5)", borderRadius: 4 }}>
                      <div style={{ color: r.c, fontSize: 11, fontWeight: 600, width: 46 }}>{r.p}</div>
                      <div style={{ color: "#3a5a6a", fontSize: 10 }}>{r.cur}</div>
                      <div style={{ color: "#2a3a4a" }}>→</div>
                      <div style={{ color: "#c8d8e8", fontSize: 10, fontWeight: 600 }}>{r.need}</div>
                      <div style={{ color: "#2a3a4a", fontSize: 9, marginLeft: "auto" }}>{r.gap}</div>
                    </div>
                  ))}
                  <div style={{ color: "#1a2a38", fontSize: 9, marginTop: 5 }}>Each row: minimum single-parameter change holding others fixed.</div>
                </div>;
              })()}

              {ok && <div style={{ color: "#2a6a4a", fontSize: 11, padding: "9px 11px", background: "rgba(0,212,238,0.015)", borderRadius: 5 }}>
                Hardware is feasible at this distance. Increase distance or tighten threshold to reveal improvement targets.
              </div>}
            </div>}
          </div>

          {/* Footer */}
          <div style={{ marginTop: 12, borderTop: "1px solid rgba(0,212,238,0.03)", padding: "6px 0", display: "flex", justifyContent: "space-between", flexWrap: "wrap" }}>
            <span style={{ color: "#121e2a", fontSize: 9 }}>The Sage Bound · Flett 2026</span>
            <span style={{ color: "#121e2a", fontSize: 9 }}>BB84: S=0.851 · c=2×10⁵ km/s · T₂ = quantum memory coherence</span>
          </div>
        </div>
      </div>
    </div>
  );
}
