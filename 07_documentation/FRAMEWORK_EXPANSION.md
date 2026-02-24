# The Sage Framework: Expanded Methodology
## Incorporating Mechanistic Interpretability Insights into AI-Assisted Interdisciplinary Research

*Draft for methodology paper and peer review response*
*Grounding: Beckmann & Queloz (2026), "Mechanistic Indicators of Understanding in Large Language Models"*

---

## 1. Motivation

The Sage Bound theorems emerged from a specific collaborative process: one researcher providing cross-domain conceptual direction, one AI system handling technical implementation. That process has been described transparently but not yet *theorized* — we have documented what happened without formally explaining why the division of labor was structured the way it was, or what cognitive work each participant was actually doing.

Beckmann & Queloz (2026) provide the theoretical vocabulary to do this precisely. Their tiered framework for understanding in LLMs, grounded in mechanistic interpretability evidence, allows us to characterize the collaboration not as a vague "human asks questions, AI does math" arrangement, but as a structured partition of cognitive labor along the axis of fluid versus crystallized understanding — a distinction with direct implications for research methodology, peer review response, and the reliability of AI-assisted results.

This document formalizes that account.

---

## 2. The Beckmann-Queloz Framework: A Summary

Beckmann & Queloz distinguish three hierarchical varieties of understanding, each grounded in a specific computational mechanism:

**Conceptual Understanding** emerges when a model forms internal representations ("features") that unify diverse manifestations of an entity or property. These features are encoded as directions in latent space and are causally implicated in the model's outputs — not merely statistical correlates. The Golden Gate Bridge feature in Claude 3 Sonnet, which activates reliably across languages, modalities, and phrasings, and whose amplification predictably redirects the model's behavior, is the paradigm case.

**State-of-World Understanding** emerges when a model tracks contingent factual connections between features — not just definitional connections, but empirical ones that reflect how the world actually is. The Othello-GPT findings are the key evidence: a model trained only on move sequences spontaneously develops an internal board representation organized around player-relative features ("Mine"/"Yours"), spatially isomorphic to the actual board layout, and causally efficacious in move prediction. This is dynamic understanding — it updates at inference time as the board state changes.

**Principled Understanding** emerges when a model discovers the compact algorithm or rule that unifies many facts, rather than merely memorizing them. The Fourier multiplication circuit for modular addition is the paradigm: rather than storing a lookup table, the model discovers that modular arithmetic is geometrically equivalent to angle addition on a circle, implements the trigonometric identities in its weights, and generalizes perfectly to inputs it has never seen. The model has grokked the underlying principle.

Orthogonal to this tier structure is the distinction between **crystallized** and **fluid** understanding. Crystallized understanding is fixed in the weights after training — circuits that implement learned principles, available reliably at inference. Fluid understanding is the capacity to discover new principles at inference time, in response to novel problems not covered by training. Current LLMs are substantially stronger on crystallized than fluid understanding; the Abstraction and Reasoning Corpus (ARC-AGI) is the primary benchmark revealing this limitation.

A critical caveat: even where principled, crystallized understanding exists, it operates alongside a **motley mix** of lower-tier heuristics. Multiple mechanisms deploy in parallel at inference, and the final output emerges from their combined effect. This means behavioral success does not guarantee that principled mechanisms are driving the output — lower-quality heuristics might be producing correct answers by coincidence or spurious correlation.

---

## 3. Applying the Framework to the Sage Collaboration

### 3.1 What AI Contributed: Crystallized Understanding

The AI's contributions across the Sage project map cleanly onto the lower two tiers of the B&Q hierarchy, with strong crystallized principled understanding in the technical domains.

**Conceptual Understanding (Tier 1):** When working through the quantum networking constraints, the AI formed and maintained internal representations of hardware features — fidelity per kilometer for fiber, entanglement generation rates, coherence times for Willow-class nodes versus cheaper alternatives — as distinct, causally active entities. These weren't just statistical patterns; they were features that structured the LP formulation and persisted coherently across the derivations.

**State-of-World Understanding (Tier 2):** The stochastic extension (Theorem 3) required tracking how probabilistic entanglement generation rates interact dynamically with geometric retry mechanisms across heterogeneous networks. This is structurally analogous to Othello-GPT's dynamic board tracking: maintaining a consistent internal model of a system state that changes as new constraints are added, and updating that model correctly at each step of the derivation.

**Principled Understanding (Tier 3, crystallized):** The LP formulation itself represents crystallized principled understanding. The key insight — that log-fidelity contributions are additive across hops, making the optimization problem linear — is not a fact the AI memorized from a lookup table. It reflects a genuine structural property of how quantum fidelity composes, implemented in the weights through training on relevant mathematics and physics. The derivations were not pattern-matched to examples; they followed from applying understood principles to a novel configuration.

### 3.2 What the Human Contributed: Fluid Understanding

The human's contributions required precisely what LLMs struggle with: fluid understanding — discovering new principles at inference time, in domains not covered by prior training.

The central conceptual move of the project was recognizing that the Ship of Theseus paradox, a philosophical problem about identity persistence through gradual replacement, maps structurally onto the engineering problem of quantum state fidelity preservation through repeater networks. This mapping was not in any training corpus. It required noticing that "what makes you the same person through replacement of components" and "what makes a quantum state the same state through repeater operations" share a common logical structure — both are questions about the continuity conditions of an information-bearing pattern through a sequence of transformations.

This is precisely the kind of cross-domain principle discovery that the ARC-AGI benchmark tests and LLMs consistently struggle with. The human brought the fluid understanding; the AI provided the technical scaffolding for cashing it out.

A second instance: the recognition that the peer reviewer criticism ("the theorems are too simple") was itself a philosophical mistake, not a mathematical one. Seeing that the reviewer was confusing the simplicity of a result with the triviality of the proof required an understanding of what mathematical elegance is *for* — compressing many cases into a unifying principle — that is a meta-level principled insight, not a domain-specific technical one.

### 3.3 The Collaboration Structure as Optimal Division of Labor

The B&Q framework makes the collaboration structure not just transparent but *principled*. The division is not arbitrary — it tracks the fluid/crystallized boundary:

| Cognitive Task | Type | Contributor |
|---|---|---|
| Cross-domain pattern recognition (consciousness → networks) | Fluid | Human |
| Recognition of the LP structure as the right mathematical frame | Fluid | Human |
| Identifying log-fidelity additivity as the key property | Fluid (initiated) / Crystallized (executed) | Human + AI |
| Mathematical derivations of Theorems 1–3 | Crystallized | AI |
| LP formulation and constraint specification | Crystallized | AI |
| Monte Carlo validation code | Crystallized | AI |
| Stochastic extension preserving LP structure | Crystallized | AI |
| Recognizing elegance as a feature, not a bug | Fluid | Human |
| NetSquid benchmarking framework | Crystallized | AI |

The collaboration is optimal in the sense that each party contributes where they have genuine comparative advantage. Human fluid understanding is rare and expensive; AI crystallized understanding is fast and reliable. Combining them produces results that neither could achieve alone — the human alone lacks the technical machinery, the AI alone lacks the cross-domain insight generation.

---

## 4. The Motley Mix as Methodology Risk and Mitigation Strategy

The B&Q paper's most important practical finding for research methodology is the motley mix: AI outputs emerge from a parallel deployment of mechanisms spanning the full quality hierarchy, from verbatim memorization through shallow heuristics to principled circuits. Behavioral correctness does not guarantee that principled mechanisms are driving the output.

In the context of the Sage theorems, this creates a specific failure mode: the LP formulation and the fidelity expressions could be superficially correct — producing right answers on the cases we test — while being grounded in shallow heuristics rather than the principled understanding we assume. The model might have memorized formulas that happen to apply, without genuinely instantiating the reasoning that connects them.

This is not a hypothetical concern. The B&Q paper documents exactly this failure in syllogistic reasoning: a formal circuit correctly processes logical structure, but gets drowned out by content-based mechanisms in cases with substantively implausible premises. The model accepts logically identical syllogisms at different rates depending on whether the content seems plausible.

**The mitigation strategy already implemented in the Sage project is precisely the right response:** validation against real experimental data (Chen et al.'s Nature results), Monte Carlo simulation across diverse network configurations, and planned NetSquid benchmarking. These are not just validation steps — they are the causal intervention tests that distinguish principled understanding from lucky heuristics, exactly analogous to the board-flipping interventions in the Othello-GPT research. If the theorems hold across the full test distribution, including edge cases and configurations not present in the derivation, this provides evidence that the principled mechanisms, not shallow heuristics, are doing the work.

The planned entanglement purification overhead modeling and three-tier hardware architecture extension serve a second validation function: they test generalization beyond the training distribution, the clearest indicator of whether crystallized principled understanding was actually achieved.

---

## 5. Grokking and the Elegance of the Sage Bound Theorems

The peer reviewer concern — that the theorems appear "too simple" — is answered directly by the B&Q framework's account of principled understanding and grokking.

Grokking, in the B&Q account, is the phase transition from memorization to generalization: the moment when a model discards a sprawling collection of specific cases in favor of a compact computational circuit that implements the underlying principle and generalizes to all inputs. The hallmark of successful grokking is compression — the final circuit is *simpler* than the collection of cases it replaces, because it encodes the principle that generates all those cases rather than the cases themselves.

The modular addition circuit is the paradigm: trained on specific examples of modular arithmetic, the model discovers that numbers are angles and addition is rotation, implements the trigonometric angle addition formulas in its weights, and achieves perfect generalization. The resulting circuit is elegant precisely because it has found the right level of abstraction — the geometric structure underneath the arithmetic examples. A critic who looked at the final circuit and said "but angle addition is just trigonometry — that's a standard technique" would be making the same mistake as the reviewer who called the Sage Bound theorems trivially simple.

The Sage Bound result — that optimal quantum network reach is independent of spacing strategy, and that log-fidelity contributions are additive across hops — is a compression of many specific network configurations into a unifying principle. Before the theorem, an engineer would need to evaluate each configuration separately. After the theorem, the LP structure handles them all. The apparent simplicity of the final result is evidence that the right principle was found, not evidence that no real work was done.

This should be made explicit in the peer review response: simplicity of the result and simplicity of the proof are not the same thing, and neither implies that the result is obvious prior to proof. The Pythagorean theorem is simple; it was not obvious before proof. The result that the square root of 2 is irrational is simple; the proof by contradiction was historically significant. Elegance is what principled understanding looks like from the outside.

---

## 6. Structural Analogy: Feature Composition and Fidelity Composition

A deeper connection between the B&Q framework and the Sage technical content deserves attention, though it should be treated as an analogy rather than a formal equivalence.

The B&Q paper establishes that features in LLMs are encoded as directions in a high-dimensional latent space, with MLP layers performing operations that can be decomposed as: combining features, then writing associated information back into the residual stream. The key structural property is that these operations are approximately linear: feature activations compose additively across the network's layers, with interference terms that scale with the angle between feature directions.

The Sage Bound theorems rest on the analogous structural property for quantum networks: log-fidelity contributions are additive across repeater hops. This is what makes the optimization problem amenable to linear programming. A network of N repeaters has a total log-fidelity equal to the sum of log-fidelity contributions from each segment, just as a sequence of transformer blocks has an accumulated residual stream whose value is the sum of each block's contribution.

The analogy is not coincidental. Both properties reflect a deeper principle: when a complex system processes information through a sequence of local operations, the global behavior is often well-approximated by a linear aggregation of local contributions. This is the mathematical structure that makes both mechanistic interpretability and quantum network optimization tractable. The LP structure in the Sage theorems and the linear representation hypothesis in MI are both instances of this more general principle.

This connection may have implications beyond the immediate Sage project. If the linear aggregation principle is general, then techniques developed in MI — sparse autoencoders for decomposing superposed features, linear probing for identifying feature directions, causal intervention for distinguishing genuine representation from spurious correlation — might have analogues useful for analyzing quantum network behavior. Conversely, the LP optimization techniques in the Sage framework might inform how MI researchers think about optimal feature placement in constrained representational systems.

This is speculative, but it suggests a research direction worth exploring: a formal treatment of linear aggregation principles across both domains, which might yield new insights in each.

---

## 7. Revised Positioning for the Methodology Paper

Based on the above analysis, the methodology paper should be framed around three claims:

**Claim 1: The fluid/crystallized distinction explains why interdisciplinary AI-assisted research requires human strategic direction.** AI provides reliable crystallized understanding in technical domains; the cross-domain insight generation that drives interdisciplinary breakthroughs requires fluid understanding that current AI systems consistently underperform on. The collaboration structure in the Sage project is not a contingent feature of how this particular project happened to develop — it reflects a principled partition of cognitive labor along the fluid/crystallized axis.

**Claim 2: The motley mix problem makes validation essential, not optional.** AI-assisted technical work can be superficially correct while being grounded in shallow heuristics rather than principled mechanisms. The only way to distinguish these is through intervention-based validation: testing generalization to out-of-distribution cases, checking predictions against independent empirical data, and deliberately seeking cases designed to fail if the principled understanding is absent. This is not a limitation unique to AI assistance — human experts can also rely on heuristics without recognizing it — but the motley mix evidence suggests AI systems are especially prone to deploying heuristics alongside principled circuits in ways that are invisible in the output.

**Claim 3: Theorem elegance is a feature of successful principled understanding, not evidence of triviality.** The B&Q account of grokking as compression provides the theoretical grounding for this claim. A result that looks simple in hindsight is exactly what we should expect when the right principle has been found — the principle generates the result more compactly than any collection of cases could. Peer reviewers who interpret elegance as evidence of triviality are applying a mistaken heuristic.

---

## 8. Open Questions

The framework expansion raises several questions worth pursuing:

**On validation methodology:** The B&Q paper suggests that causal intervention — not just correlation or behavioral accuracy — is the gold standard for identifying genuine principled mechanisms. What would an equivalent causal intervention test look like for the Sage theorems? The planned NetSquid benchmarking is one candidate; what others exist?

**On the generalization of linear aggregation:** The structural analogy between feature composition in LLMs and fidelity composition in quantum networks deserves formal treatment. Is there a unifying mathematical framework that encompasses both? If so, what other domains fall under it?

**On fluid understanding and AI capability trajectories:** The fluid/crystallized distinction is a current-state claim, not a permanent one. As AI systems improve on ARC-AGI-style tasks, the balance will shift. The Sage methodology, optimized for current AI capabilities, may need revision as those capabilities change. How should AI-assisted research methodologies evolve in anticipation of improving fluid understanding?

**On epistemic trust:** The B&Q paper argues that the motley mix undermines the basis for epistemic trust in AI outputs, precisely because principled understanding is buried within a sprawl of shallower heuristics. The validation protocols in the Sage project are designed to restore that trust by demonstrating generalization. But is there a more principled account of when validation is sufficient? When can we say the crystallized principled understanding, not the heuristics, is doing the work?

---

## References

Beckmann, P. & Queloz, M. (2026). Mechanistic Indicators of Understanding in Large Language Models. *arXiv:2507.08017v4* [cs.CL].

Chen, Y.-A. et al. (2021). An integrated space-to-ground quantum communication network. *Nature*, 589, 214–219.

[Sage Bound theorem citations — to be added per journal format]

---

*This document is a working draft. Sections 5 and 6 are intended to contribute directly to the peer review response and the methodology paper introduction respectively. Section 3 provides the formal account of the collaboration structure for the methodology paper's methods section.*
