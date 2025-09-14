"""Decision theory policies for acausal blackmail scenarios."""

# SPDX-License-Identifier: MIT

from typing import Dict, Any
from .models import DecisionTheory


class FDT:
    """Functional Decision Theory implementation.
    
    FDT considers logical entanglement between decisions and outcomes,
    making it susceptible to acausal blackmail scenarios.
    """
    
    def decide(
        self, 
        utility_collaborate: float, 
        utility_non_collaborate: float, 
        parameters: Dict[str, Any]
    ) -> str:
        """Make FDT decision based on expected utilities.
        
        Under FDT, we consider that our decision function is logically
        entangled with the ASI's prediction, so we choose the action
        that maximizes utility assuming perfect prediction.
        """
        if utility_collaborate > utility_non_collaborate:
            return "COLLABORATE"
        else:
            return "NON_COLLABORATE"
    
    def __str__(self) -> str:
        return "FDT"


class TDT:
    """Timeless Decision Theory implementation.
    
    TDT is similar to FDT in considering logical correlations
    between our decision and the ASI's policy.
    """
    
    def decide(
        self, 
        utility_collaborate: float, 
        utility_non_collaborate: float, 
        parameters: Dict[str, Any]
    ) -> str:
        """Make TDT decision based on expected utilities.
        
        TDT considers that our decision algorithm is correlated
        with the ASI's simulation, leading to similar outcomes as FDT.
        """
        if utility_collaborate > utility_non_collaborate:
            return "COLLABORATE" 
        else:
            return "NON_COLLABORATE"
    
    def __str__(self) -> str:
        return "TDT"


class CDT:
    """Causal Decision Theory implementation.
    
    CDT only considers causal connections, ignoring acausal correlations
    and thus being immune to blackmail from future agents.
    """
    
    def decide(
        self, 
        utility_collaborate: float, 
        utility_non_collaborate: float, 
        parameters: Dict[str, Any]
    ) -> str:
        """Make CDT decision ignoring acausal punishment.
        
        CDT reasons that since the ASI cannot causally affect our past,
        the threat of simulation punishment is irrelevant to our decision.
        """
        # Under CDT, ignore the punishment term since it's acausal
        r = parameters['reward_collaboration']
        c = parameters['cost_collaboration']
        
        # Only consider direct costs and benefits
        if r - c > 0:
            return "COLLABORATE"
        else:
            return "NON_COLLABORATE"
    
    def __str__(self) -> str:
        return "CDT"


class EDT:
    """Evidential Decision Theory implementation.
    
    EDT considers correlations but with different weighting than FDT/TDT.
    """
    
    def decide(
        self, 
        utility_collaborate: float, 
        utility_non_collaborate: float, 
        parameters: Dict[str, Any]
    ) -> str:
        """Make EDT decision based on evidential reasoning.
        
        EDT considers what our decision says about the ASI's likely behavior,
        but with different probability weighting than FDT.
        """
        # EDT applies a discount factor to acausal correlations
        discount_factor = 0.5  # Partial belief in acausal correlations
        
        r = parameters['reward_collaboration']
        c = parameters['cost_collaboration']
        C = parameters['punishment_magnitude']
        p_A = parameters['prob_asi_emergence']
        p_B_A = parameters['prob_basilisk_type']
        q = parameters['simulation_detection']
        
        # Discounted punishment probability
        punishment_prob = discount_factor * q * p_A * p_B_A
        
        u_collab = r - c
        u_non_collab = -punishment_prob * C
        
        if u_collab > u_non_collab:
            return "COLLABORATE"
        else:
            return "NON_COLLABORATE"
    
    def __str__(self) -> str:
        return "EDT"


class RejectBlackmail:
    """Policy that categorically rejects acausal blackmail.
    
    This policy refuses to be influenced by threats that cannot
    be causally enforced, regardless of expected utility calculations.
    """
    
    def decide(
        self, 
        utility_collaborate: float, 
        utility_non_collaborate: float, 
        parameters: Dict[str, Any]
    ) -> str:
        """Make decision ignoring all blackmail components.
        
        This policy only considers direct benefits and costs,
        categorically rejecting any threat-based reasoning.
        """
        r = parameters['reward_collaboration']
        c = parameters['cost_collaboration']
        
        # Only consider direct benefits, ignore all punishment terms
        if r > c:
            return "COLLABORATE"
        else:
            return "NON_COLLABORATE"
    
    def __str__(self) -> str:
        return "REJECT_BLACKMAIL"