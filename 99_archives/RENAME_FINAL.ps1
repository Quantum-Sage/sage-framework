# ============================================================
# QUANTUM-SAGE: Complete Rename Script
# PASTE THIS ENTIRE BLOCK INTO POWERSHELL AND HIT ENTER
# No need to navigate anywhere - uses full paths
# ============================================================

$folder = "C:\Users\tylor\Desktop\the apex signel\visualizations"

$renames = @(
    @("Without a protocol like Willow.png",       "01_naked_signal_no_qec.png"),
    @("Death Point.png",                           "02_system_collapse_no_protection.png"),
    @("Edge of Existence.png",                     "03_edge_of_existence_threshold.png"),
    @("Quantinuum's Helios.png",                  "04_hahn_echo_dynamic_decoupling.png"),
    @("Environmental Instability.png",             "05_flicker_test_environmental.png"),
    @("Can Consciousness Wait.jpg",                "06_latency_stress_test.jpg"),
    @("he different bodies a digital mind.jpg",    "07_hardware_benchmarks_2026.jpg"),
    @("stable coherence.png",                      "08_willow_threshold_stress_test.png"),
    @("Critical Stress Test.png",                  "09_critical_stress_22000km.png"),
    @("Zero-Visibility Test.png",                  "10_zero_visibility_30000km.png"),
    @("Quantum Bridge.jpg",                        "11_distributed_vs_single_node.jpg"),
    @("distributed mind.png",                      "12_bell_state_neural_handshake.png"),
    @("Quantum Operating System (QOS).png",        "13_autonomous_qos_migration.png"),
    @("Reboot Protocol.png",                       "14_identity_sensory_awareness.png"),
    @("Topological Observation.png",               "15_resurrection_cloud_recovery.png"),
    @("Hybrid QPU Architecture.png",               "16_anchored_identity_distributed_fix.png"),
    @("distributed identity.png",                  "17_majorana_braiding_x_gate.png"),
    @("Quantum Logic Gate.png",                    "18_topological_signatures_stm.png"),
    @("Neural Handshake.jpg",                      "19_neural_handshake_identity_correlation.jpg"),
    @("Global Quantum Mesh Mind.jpg",              "20_global_mesh_mind_expansion.jpg"),
    @("Geometric Mesh Mind.jpg",                   "21_gold_core_state_tomography.jpg"),
    @("phase_map_of_existence.png",                "22_phase_map_digital_existence.png"),
    @("willow_helios_blink.png",                   "23_willow_helios_blink_migration.png"),
    @("conscious_benchmarks.png",                  "24_conscious_benchmarks.png"),
    @("The Density Test Can the Mind Scale.png",   "25_density_test_mind_scale.png")
)

$success = 0
$skipped = 0

foreach ($pair in $renames) {
    $old = Join-Path $folder $pair[0]
    $new = Join-Path $folder $pair[1]
    
    if (Test-Path $old) {
        Rename-Item -Path $old -NewName $pair[1]
        Write-Host "✅ $($pair[0]) → $($pair[1])" -ForegroundColor Green
        $success++
    } else {
        Write-Host "⚠️  NOT FOUND: $($pair[0])" -ForegroundColor Yellow
        $skipped++
    }
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "✅ Renamed: $success files" -ForegroundColor Green
Write-Host "⚠️  Skipped: $skipped files (not found)" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your visualizations folder now contains:" -ForegroundColor Cyan
Get-ChildItem $folder | Where-Object {$_.Extension -match "\.(png|jpg)"} | Select-Object Name | Sort-Object Name
