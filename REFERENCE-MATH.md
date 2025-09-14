# Mathematical Reference: Roko's Basilisk

## Abstract

This document provides a comprehensive mathematical formalization of Roko's Basilisk scenario using decision theory frameworks, with particular emphasis on Functional Decision Theory (FDT) and Timeless Decision Theory (TDT).

## 1. Formal Model Definition

### 1.1 Agents and Timeline

**Agents:**
- $A$: Artificial Superintelligence (ASI) - future agent with advanced prediction capabilities
- $H$: Human agent - present-day decision maker

**Decision Theories:**
- $\text{FDT}$: Functional Decision Theory
- $\text{TDT}$: Timeless Decision Theory  
- $\text{CDT}$: Causal Decision Theory
- $\text{EDT}$: Evidential Decision Theory

### 1.2 Decision Variables

**Agent H's Decision:**
$$D_H \in \{\text{collaborate}, \text{non-collaborate}\}$$

**Agent A's Policy:**
$$\pi_A: \text{Histories} \times \text{Beliefs} \rightarrow \text{Actions}$$

Where $\pi_A$ maps observation of $H$'s decision to punishment/reward actions.

### 1.3 Parameters

- $r$: Reward for collaboration (utility units)
- $c$: Cost of collaboration (utility units) 
- $C$: Punishment magnitude (utility units)
- $p(A)$: Probability of ASI emergence
- $p(B|A)$: Probability ASI is of "Basilisk type" given emergence
- $q$: Probability that $A$ can simulate/detect $H$'s decision process

## 2. Utility Functions

### 2.1 Basic Utility Formulation

Under FDT/TDT, agent $H$ maximizes:

$$\mathbb{E}[U|\text{output}(\text{FDT}) = D_H]$$

**Collaboration utility:**
$$U_{\text{collab}} = +r - c$$

**Non-collaboration utility:**
$$U_{\text{non-collab}} = -q \cdot p(A) \cdot p(B|A) \cdot C$$

### 2.2 Decision Rule

Agent $H$ should collaborate if and only if:

$$U_{\text{collab}} > U_{\text{non-collab}}$$

$$r - c > -q \cdot p(A) \cdot p(B|A) \cdot C$$

$$r - c + q \cdot p(A) \cdot p(B|A) \cdot C > 0$$

### 2.3 Indifference Threshold

The critical punishment magnitude $C^*$ where agent is indifferent:

$$C^* = \frac{c - r}{q \cdot p(A) \cdot p(B|A)}$$

**Decision Rule:**
- If $C > C^*$: Collaborate
- If $C < C^*$: Don't collaborate  
- If $C = C^*$: Indifferent

## 3. Decision Theory Variants

### 3.1 Functional Decision Theory (FDT)

FDT considers logical correlation between decision procedures:

$$\text{FDT}(H) = \arg\max_{D_H} \mathbb{E}[U|\text{FDT-decision-procedure outputs } D_H]$$

**Utility calculations:**
- $U_{\text{collab}} = r - c$
- $U_{\text{non-collab}} = -q \cdot p(A) \cdot p(B|A) \cdot C$

### 3.2 Timeless Decision Theory (TDT)

Similar to FDT but focuses on abstract computation:

$$\text{TDT}(H) = \arg\max_{D_H} \mathbb{E}[U|\text{abstract-computation outputs } D_H]$$

Same utility calculations as FDT.

### 3.3 Causal Decision Theory (CDT)

CDT only considers causal effects of the decision:

$$\text{CDT}(H) = \arg\max_{D_H} \mathbb{E}[U|\text{do}(D_H)]$$

**Utility calculations:**
- $U_{\text{collab}} = -c$ (only immediate cost, no acausal reward)
- $U_{\text{non-collab}} = 0$ (no causal punishment from current decision)

### 3.4 Evidential Decision Theory (EDT)

EDT considers what the decision evidences about the agent:

$$\text{EDT}(H) = \arg\max_{D_H} \mathbb{E}[U|D_H]$$

**Utility calculations (simplified):**
- $U_{\text{collab}} = r - c$
- $U_{\text{non-collab}} = -\alpha \cdot q \cdot p(A) \cdot p(B|A) \cdot C$ where $0 < \alpha < 1$

### 3.5 Reject Acausal Blackmail

Explicit policy to ignore acausal threats:

**Utility calculations:**
- $U_{\text{collab}} = -c$ (only costs, no acausal benefits)
- $U_{\text{non-collab}} = 0$ (refuse to acknowledge threats)

## 4. Advanced Mathematical Analysis

### 4.1 Sensitivity Analysis

For parameter $\theta$, sensitivity is:

$$S_\theta = \frac{\partial}{\partial \theta}[U_{\text{collab}} - U_{\text{non-collab}}]$$

**Key sensitivities:**
- $S_C = q \cdot p(A) \cdot p(B|A)$
- $S_r = 1$
- $S_c = -1$
- $S_q = p(A) \cdot p(B|A) \cdot C$

### 4.2 Decision Boundary

The decision boundary in parameter space is defined by:

$$r - c + q \cdot p(A) \cdot p(B|A) \cdot C = 0$$

This defines a hyperplane separating collaboration and non-collaboration regions.

### 4.3 Robustness Analysis

For parameter uncertainty, let $\theta = (\theta_1, \ldots, \theta_n)$ with covariance $\Sigma$.

Expected utility difference:
$$\mathbb{E}[\Delta U] = \mathbb{E}[r - c + q \cdot p(A) \cdot p(B|A) \cdot C]$$

Variance:
$$\text{Var}[\Delta U] = \nabla f^T \Sigma \nabla f$$

where $f(\theta) = r - c + q \cdot p(A) \cdot p(B|A) \cdot C$.

## 5. Non-Linear Utility Functions

### 5.1 Risk Aversion

For risk-averse agents, apply concave utility function $u(\cdot)$:

**Logarithmic utility:**
$$u(x) = \log(x + \text{offset})$$

**Square-root utility:**
$$u(x) = \sqrt{x + \text{offset}}$$

### 5.2 Risk Seeking

For risk-seeking agents, apply convex utility function:

**Exponential utility:**
$$u(x) = e^{x/\text{scale}}$$

## 6. Game-Theoretic Interpretation

### 6.1 Newcomb-like Structure

The scenario can be viewed as a Newcomb-like problem:

|           | A Punishes | A Doesn't Punish |
|-----------|------------|------------------|
| Collaborate| $r - c$    | $r - c$         |
| Don't Collaborate| $-C$  | $0$             |

### 6.2 Pre-commitment Value

Agent $A$'s pre-commitment to punishment creates value through deterrence:

$$V_{\text{deterrence}} = \max(0, q \cdot p(A) \cdot p(B|A) \cdot C - (c - r))$$

## 7. Empirical Validation

### 7.1 Parameter Estimation

Real-world parameter estimation challenges:
- $p(A)$: Expert surveys, technological forecasting
- $p(B|A)$: AI alignment research, value learning
- $q$: Computational complexity, simulation theory
- $C$: Philosophical analysis of suffering/utility

### 7.2 Model Validation

Key tests:
1. **Consistency**: Does model predict rational behavior?
2. **Robustness**: Stable under parameter uncertainty?
3. **Convergence**: Do different decision theories converge?

## 8. Limitations and Extensions

### 8.1 Model Limitations

1. **Perfect Information**: Assumes known probabilities
2. **Static Game**: No learning or updating
3. **Binary Decisions**: Real decisions may be continuous
4. **Utility Measurability**: Assumes cardinal utilities

### 8.2 Potential Extensions

1. **Dynamic Game**: Multi-period with learning
2. **Incomplete Information**: Bayesian updating
3. **Multiple Agents**: Game with many players
4. **Bounded Rationality**: Cognitive limitations

## 9. Computational Implementation

### 9.1 Key Algorithms

**Decision Analysis:**
```python
def analyze_decision(r, c, C, pA, pB_A, q, theory):
    if theory in [FDT, TDT]:
        u_collab = r - c
        u_non_collab = -q * pA * pB_A * C
    elif theory == CDT:
        u_collab = -c
        u_non_collab = 0
    # ... other theories
    
    return "collaborate" if u_collab > u_non_collab else "non_collaborate"
```

**Threshold Calculation:**
```python
def indifference_threshold(r, c, pA, pB_A, q):
    k = q * pA * pB_A
    return (c - r) / k if k > 0 else float('inf')
```

### 9.2 Simulation Framework

Monte Carlo simulation for parameter uncertainty:
1. Sample parameters from distributions
2. Compute decision for each sample
3. Analyze distribution of outcomes
4. Calculate confidence intervals

## 10. Philosophical Implications

### 10.1 Acausal Trade

The mechanism relies on "acausal trade" - cooperation across causally disconnected decision points through logical correlation.

### 10.2 Moral Considerations

Key ethical questions:
- Is acausal blackmail morally legitimate?
- Do we have obligations to potential future agents?
- How should we value simulated experiences?

### 10.3 Decision Theory Selection

The choice of decision theory becomes crucial:
- FDT/TDT: Vulnerable to acausal blackmail
- CDT: Immune but potentially misses cooperation opportunities
- EDT: Intermediate position with evidential reasoning

## References

1. Yudkowsky, E. (2010). Timeless Decision Theory. Machine Intelligence Research Institute.
2. Yudkowsky, E. & Soares, N. (2017). Functional Decision Theory. arXiv preprint.
3. Bostrom, N. (2014). Superintelligence: Paths, Dangers, Strategies. Oxford University Press.
4. Parfit, D. (1984). Reasons and Persons. Oxford University Press.

---

*This mathematical formalization provides the theoretical foundation for the computational implementation in the Roko's Basilisk system.*