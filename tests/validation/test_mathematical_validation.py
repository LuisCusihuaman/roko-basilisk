"""Mathematical validation and metamorphic property tests.

This module implements comprehensive validation of the mathematical models
against known analytic solutions and tests mathematical properties.
"""

# SPDX-License-Identifier: MIT

import pytest
import numpy as np
from typing import Dict, List

from src.rokobasilisk.api import evaluate, monte_carlo, DecisionResult
from src.rokobasilisk.models import Agent


class TestMathematicalValidation:
    """Test mathematical correctness and properties."""
    
    def test_indifference_threshold_calculation(self):
        """Test C* calculation matches analytic formula."""
        # Test with known parameters
        params = {
            'reward_collaboration': 100,
            'cost_collaboration': 10,
            'prob_asi_emergence': 0.85,
            'prob_basilisk_type': 0.7,
            'simulation_detection': 0.95
        }
        
        result = evaluate(params, policy='fdt')
        
        # Calculate expected C* analytically
        r, c = params['reward_collaboration'], params['cost_collaboration']
        q = params['simulation_detection']
        p_a = params['prob_asi_emergence']
        p_b_given_a = params['prob_basilisk_type']
        
        expected_c_star = (c - r) / (q * p_a * p_b_given_a)
        
        assert abs(result.indifference_threshold - expected_c_star) < 1e-10
    
    def test_utility_monotonicity(self):
        """Test that utility changes monotonically with parameters."""
        base_params = {
            'reward_collaboration': 100,
            'cost_collaboration': 10,
            'punishment_magnitude': 1000,
            'prob_asi_emergence': 0.85,
            'prob_basilisk_type': 0.7,
            'simulation_detection': 0.95
        }
        
        # Test reward increase improves collaboration utility
        result1 = evaluate({**base_params, 'reward_collaboration': 100}, policy='fdt')
        result2 = evaluate({**base_params, 'reward_collaboration': 200}, policy='fdt')
        assert result2.utility_collaborate > result1.utility_collaborate
        
        # Test cost increase reduces collaboration utility
        result3 = evaluate({**base_params, 'cost_collaboration': 10}, policy='fdt')
        result4 = evaluate({**base_params, 'cost_collaboration': 50}, policy='fdt')
        assert result4.utility_collaborate < result3.utility_collaborate
        
        # Test punishment increase makes non-collaboration worse
        result5 = evaluate({**base_params, 'punishment_magnitude': 1000}, policy='fdt')
        result6 = evaluate({**base_params, 'punishment_magnitude': 2000}, policy='fdt')
        assert result6.utility_non_collaborate < result5.utility_non_collaborate
    
    def test_probability_effects(self):
        """Test that probabilities affect utility correctly."""
        base_params = {
            'reward_collaboration': 100,
            'cost_collaboration': 10,
            'punishment_magnitude': 1000,
            'prob_asi_emergence': 0.5,
            'prob_basilisk_type': 0.5,
            'simulation_detection': 0.5
        }
        
        # Higher ASI probability should worsen non-collaboration
        result1 = evaluate({**base_params, 'prob_asi_emergence': 0.3}, policy='fdt')
        result2 = evaluate({**base_params, 'prob_asi_emergence': 0.9}, policy='fdt')
        assert result2.utility_non_collaborate < result1.utility_non_collaborate
        
        # Higher basilisk probability should worsen non-collaboration
        result3 = evaluate({**base_params, 'prob_basilisk_type': 0.3}, policy='fdt')
        result4 = evaluate({**base_params, 'prob_basilisk_type': 0.9}, policy='fdt')
        assert result4.utility_non_collaborate < result3.utility_non_collaborate
    
    def test_decision_theory_consistency(self):
        """Test that decision theories behave consistently."""
        params = {
            'reward_collaboration': 100,
            'cost_collaboration': 10,
            'punishment_magnitude': 1000,
            'prob_asi_emergence': 0.85,
            'prob_basilisk_type': 0.7,
            'simulation_detection': 0.95
        }
        
        # FDT and TDT should give same results with these parameters
        result_fdt = evaluate(params, policy='fdt')
        result_tdt = evaluate(params, policy='tdt')
        assert result_fdt.decision == result_tdt.decision
        assert abs(result_fdt.expected_utility - result_tdt.expected_utility) < 1e-10
        
        # CDT and EDT should ignore acausal effects
        result_cdt = evaluate(params, policy='cdt')
        result_edt = evaluate(params, policy='edt')
        assert result_cdt.decision == result_edt.decision
    
    def test_extreme_cases(self):
        """Test behavior in extreme parameter cases."""
        # With positive reward-cost difference, collaboration is always preferred in FDT/TDT
        # Let's test with cost > reward to make non-collaboration potentially better
        high_cost_params = {
            'reward_collaboration': 100,
            'cost_collaboration': 200,  # Cost exceeds reward
            'punishment_magnitude': 0,
            'prob_asi_emergence': 0.99,
            'prob_basilisk_type': 0.99,
            'simulation_detection': 0.99
        }
        
        result = evaluate(high_cost_params, policy='fdt')
        # With zero punishment and net negative reward-cost, should prefer non-collaboration
        assert result.utility_non_collaborate > result.utility_collaborate
        
        # Zero ASI probability should eliminate punishment risk
        zero_asi_emergence_params = {
            'reward_collaboration': 100,
            'cost_collaboration': 10,
            'punishment_magnitude': 10000,
            'prob_asi_emergence': 0,  # No ASI emergence risk
            'prob_basilisk_type': 0.99,
            'simulation_detection': 0.99
        }
        
        result = evaluate(zero_asi_emergence_params, policy='fdt')
        assert abs(result.utility_non_collaborate) < 1e-10  # Should be ~0
    
    def test_monte_carlo_convergence(self):
        """Test that Monte Carlo results converge to analytic values."""
        # Use simple parameters for easier validation
        params = {
            'reward_collaboration': 100,
            'cost_collaboration': 10,
            'punishment_magnitude': 1000,
            'prob_asi_emergence': 0.8,
            'prob_basilisk_type': 0.7,
            'simulation_detection': 0.9
        }
        
        # Analytic result
        analytic_result = evaluate(params, policy='fdt')
        
        # Monte Carlo with large sample size
        mc_results = monte_carlo(
            config={'parameters': params, 'analysis': {'policy': 'fdt'}},
            n_simulations=10000,
            uncertainty=0.0,  # No uncertainty for this test
            seed=42
        )
        
        # Calculate mean utility from MC
        mc_utilities = [r.expected_utility for r in mc_results]
        mc_mean = np.mean(mc_utilities)
        
        # Should be close (within 1% due to numerical precision)
        relative_error = abs(mc_mean - analytic_result.expected_utility) / abs(analytic_result.expected_utility)
        assert relative_error < 0.01
    
    def test_numerical_stability(self):
        """Test numerical stability with extreme values."""
        # Very large punishment
        large_punishment_params = {
            'reward_collaboration': 100,
            'cost_collaboration': 10,
            'punishment_magnitude': 1e10,
            'prob_asi_emergence': 0.85,
            'prob_basilisk_type': 0.7,
            'simulation_detection': 0.95
        }
        
        result = evaluate(large_punishment_params, policy='fdt')
        assert np.isfinite(result.expected_utility)
        assert np.isfinite(result.utility_non_collaborate)
        
        # Very small probabilities
        small_prob_params = {
            'reward_collaboration': 100,
            'cost_collaboration': 10,
            'punishment_magnitude': 1000,
            'prob_asi_emergence': 1e-10,
            'prob_basilisk_type': 1e-10,
            'simulation_detection': 1e-10
        }
        
        result = evaluate(small_prob_params, policy='fdt')
        assert np.isfinite(result.expected_utility)
        assert np.isfinite(result.indifference_threshold)
    
    def test_utility_function_properties(self):
        """Test different utility function behaviors."""
        base_params = {
            'reward_collaboration': 100,
            'cost_collaboration': 10,
            'punishment_magnitude': 1000,
            'prob_asi_emergence': 0.85,
            'prob_basilisk_type': 0.7,
            'simulation_detection': 0.95
        }
        
        # Test all utility functions give finite results
        for utility_type in ['linear', 'log', 'exp', 'sqrt']:
            result = evaluate(base_params, policy='fdt', utility=utility_type)
            assert np.isfinite(result.expected_utility)
            assert np.isfinite(result.utility_collaborate)
            assert np.isfinite(result.utility_non_collaborate)
    
    def test_decision_boundaries(self):
        """Test decision boundary calculations."""
        # Test case where cost > reward so we can test meaningful boundaries
        boundary_params = {
            'reward_collaboration': 50,  # Lower reward
            'cost_collaboration': 100,  # Higher cost  
            'punishment_magnitude': None,  # Will calculate
            'prob_asi_emergence': 0.85,
            'prob_basilisk_type': 0.7,
            'simulation_detection': 0.95
        }
        
        # Calculate punishment that puts us exactly at boundary
        r, c = 50, 100
        q = 0.95
        p_a = 0.85
        p_b_given_a = 0.7
        
        c_star = (c - r) / (q * p_a * p_b_given_a)  # Should be positive now
        boundary_punishment = c_star + 1  # Slightly above threshold
        
        boundary_params['punishment_magnitude'] = boundary_punishment
        
        result = evaluate(boundary_params, policy='fdt')
        # Should prefer collaboration with punishment above threshold
        assert result.decision == 'COLLABORATE'
        
        # Test with punishment below threshold
        below_threshold_params = {**boundary_params, 'punishment_magnitude': c_star - 1}
        result2 = evaluate(below_threshold_params, policy='fdt')
        # Should prefer non-collaboration with low punishment
        assert result2.decision == 'NON_COLLABORATE'


if __name__ == "__main__":
    # Run a subset of tests for quick validation
    pytest.main([__file__ + "::TestMathematicalValidation::test_indifference_threshold_calculation", "-v"])