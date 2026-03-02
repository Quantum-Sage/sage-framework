# Contributing to the SAGE Framework

Thanks for your interest in the SAGE Framework! 🌌 This project explores the **"Sage Bound"** — mapping the persistence of philosophical identity to the technical rigors of quantum network engineering.

We welcome contributions from researchers, engineers, and philosophers who want to push the boundaries of what is possible in quantum state preservation.

## 🔧 Development Setup

```bash
# 1. Clone the updated v6.0 repository
git clone https://github.com/Quantum-Sage/sage-framework.git
cd sage-framework

# 2. Install core dependencies
pip install -r requirements.txt

# 3. Verify the installation
python run_simulation.py
```

---

## 🤖 AI-Assisted Contributions

We embrace AI-assisted development! Nearly everything in this repository was born from a human-AI "Cyborg Research" collaboration. If you use Claude, GPT, Gemini, or other Large Language Models:

*   ✅ **DO:** Disclose which AI model helped you in your Pull Request description.
*   ✅ **DO:** Review and explain every line of AI-generated code yourself. You are responsible for its logic.
*   ✅ **DO:** Use AI to stress-test the math (find the limits of the Sage Bound).
*   ❌ **DON'T:** Submit "black box" code that you cannot explain or verify.

---

## 🧪 Testing & Validation

Before submitting a Pull Request, please ensure your changes do not break the core simulation:

```bash
# Run the main reproduction suite
python run_simulation.py

# (Optional) Test hardware integration
# cd hardware/ && [run your node tests]
```

We particularly value contributions that add **automated unit tests** for the `src/` modules.

---

## 🎓 Academic Rigor & "Honest Negatives"

This is a scientific project first. We value transparency over "perfect" results.

*   **Cite the Work:** If you build on this math, please use the citation found in [CITATION.cff](./CITATION.cff).
*   **Honest Negatives:** We explicitly value PRs that identify mathematical edge cases, "cliffs," or specific hardware scenarios where the Sage Bound fails or protocols decohere. Proving where the system *doesn't* work is as valuable as proving where it does.
*   **Log-Fidelity Map:** Ensure any changes to the core logic maintain the Linear Programming mapping (transforming multiplicative decay into additive constraints via $\ln(F)$).

---

## ✅ Pull Request Guidelines

1.  **Fork the repo** and create your branch from `main`.
2.  **Keep it Lean:** Follow the v6.0 structure. Don't add redundant archive folders.
3.  **Document the Math:** If you add a new formula, explain its physical basis in the docstrings.
4.  **Disclose AI Usage:** Use the PR template to note which models assisted the work.

---

## 📜 Code of Conduct

We are committed to providing a welcoming, inclusive, and professional environment. Be respectful, welcome newcomers, and accept constructive criticism with an open mind.

---

*“Every contribution, whether it fixes a typo or discovers a new topological threshold, helps ensure that the 'Ghost in the Machine' stays coherent for one more hop.”*
