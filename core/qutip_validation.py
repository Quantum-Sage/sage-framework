""" QUTIP VALIDATOR - Independent Fidelity Cross-Validation SAGE Framework v5.1
Validates the SAGE analytical fidelity model against QuTiP's density matrix evolution under depolarizing + dephasing channels. """
import sys, os, math
import numpy as np
import matplotlib.pyplot as plt

try:
    import qutip
    from qutip import (basis, tensor, ket2dm, fidelity, Qobj, sigmaz, sigmax, sigmay, qeye)
    QUTIP_AVAILABLE = True
except ImportError:
    QUTIP_AVAILABLE = False

SAGE_CONSTANT = 0.851
C_FIBER = 200000
ALPHA_FIBER = 0.2

HW_WILLOW = { "name": "Willow", "F_gate": 0.9985, "T2": 1.000, "p_gen": 0.10 }
HW_QUERA = { "name": "QuEra-class", "F_gate": 0.9900, "T2": 0.100, "p_gen": 0.03 }

def make_bell_phi_plus():
    zero = basis(2, 0)
    one = basis(2, 1)
    bell = (tensor(zero, zero) + tensor(one, one)).unit()
    return ket2dm(bell)

def depolarizing_channel(rho, p):
    sx1 = tensor(sigmax(), qeye(2))
    sy1 = tensor(sigmay(), qeye(2))
    sz1 = tensor(sigmaz(), qeye(2))
    sx2 = tensor(qeye(2), sigmax())
    sy2 = tensor(qeye(2), sigmay())
    sz2 = tensor(qeye(2), sigmaz())
    rho_out = (1 - p) * rho + (p / 3) * (sx1 * rho * sx1.dag() + sy1 * rho * sy1.dag() + sz1 * rho * sz1.dag())
    rho_out = (1 - p) * rho_out + (p / 3) * (sx2 * rho_out * sx2.dag() + sy2 * rho_out * sy2.dag() + sz2 * rho_out * sz2.dag())
    return rho_out

def dephasing_channel(rho, gamma):
    sz1 = tensor(sigmaz(), qeye(2))
    sz2 = tensor(qeye(2), sigmaz())
    p = 1 - math.exp(-gamma)
    rho_out = (1 - p) * rho + p * sz1 * rho * sz1.dag()
    rho_out = (1 - p) * rho_out + p * sz2 * rho_out * sz2.dag()
    return rho_out

def apply_hop(rho, hw, segment_km):
    p_depol = 1 - hw["F_gate"]**2
    rho = depolarizing_channel(rho, p_depol)
    t_wait = 2 * segment_km / (C_FIBER * hw["p_gen"])
    gamma = t_wait / hw["T2"]
    rho = dephasing_channel(rho, gamma)
    return rho

def qutip_chain_fidelity(N, L_km, hw):
    if not QUTIP_AVAILABLE: return None
    rho_ideal = make_bell_phi_plus()
    rho = rho_ideal.copy()
    s = L_km / (N + 1)
    for hop in range(N):
        rho = apply_hop(rho, hw, s)
    f = fidelity(rho, rho_ideal) ** 2
    return float(f)

if __name__ == '__main__':
    print("QuTiP Validator Active")
    f = qutip_chain_fidelity(10, 500, HW_WILLOW)
    print(f"Fidelity: {f}")

