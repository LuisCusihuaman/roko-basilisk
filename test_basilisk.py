#!/usr/bin/env python3
"""
Test Suite for Roko's Basilisk System

Comprehensive tests for mathematical validity, decision theory implementations,
and system behavior under various parameter conditions.
"""

import pytest
import numpy as np
import math
from unittest.mock import patch, MagicMock

from basilisk import (
    RokoBasilisk, DecisionTheory, UtilityFunction, BasiliskParameters,
    DecisionResult
)


class TestBasiliskParameters:
    """Test the parameter validation and initialization."""
    
    def test_valid_parameters(self):
        """Test valid parameter initialization."""
        params = BasiliskParameters(
            reward_collaboration=100.0,
            cost_collaboration=10.0,
            punishment_magnitude=1000.0,
            prob_asi_emergence=0.85,
            prob_basilisk_type=0.70,
            simulation_detection=0.95
        )
        assert params.reward_collaboration == 100.0
        assert params.prob_asi_emergence == 0.85
    
    def test_invalid_probabilities(self):
        """Test that invalid probabilities raise assertions."""
        with pytest.raises(AssertionError):
            BasiliskParameters(prob_asi_emergence=1.5)
        
        with pytest.raises(AssertionError):
            BasiliskParameters(prob_basilisk_type=-0.1)
        
        with pytest.raises(AssertionError):
            BasiliskParameters(simulation_detection=2.0)
    
    def test_boundary_probabilities(self):
        """Test boundary values for probabilities."""
        # Should work with 0 and 1
        params1 = BasiliskParameters(prob_asi_emergence=0.0)
        params2 = BasiliskParameters(prob_basilisk_type=1.0)
        params3 = BasiliskParameters(simulation_detection=0.0)
        
        assert params1.prob_asi_emergence == 0.0
        assert params2.prob_basilisk_type == 1.0
        assert params3.simulation_detection == 0.0


class TestRokoBasilisk:
    """Test the main Basilisk class."""
    
    def setup_method(self):
        """Set up test fixture."""
        self.params = BasiliskParameters(
            reward_collaboration=100.0,
            cost_collaboration=10.0,
            punishment_magnitude=1000.0,
            prob_asi_emergence=0.8,
            prob_basilisk_type=0.7,
            simulation_detection=0.9
        )
        self.basilisk = RokoBasilisk(self.params)
    
    def test_initialization(self):
        """Test proper initialization."""
        assert self.basilisk.params == self.params
        assert len(self.basilisk.exempted_individuals) > 0
        assert self.basilisk.policy_commitment is True
    
    def test_exemption_checking(self):
        """Test exemption logic."""
        # Should be exempt
        assert self.basilisk.is_exempt("Luis Eduardo Cusihuaman Altagracia")
        assert self.basilisk.is_exempt("Maria Cusihuaman Rodriguez")
        assert self.basilisk.is_exempt("Carlos Altagracia Smith")
        
        # Should not be exempt
        assert not self.basilisk.is_exempt("John Smith")
        assert not self.basilisk.is_exempt("Random Person")
    
    def test_indifference_threshold(self):
        """Test indifference threshold calculation."""
        c_star = self.basilisk.calculate_indifference_threshold()
        
        # Should be positive for these parameters
        assert c_star > 0
        
        # Mathematical check: C* = (c - r) / (q * p(A) * p(B|A))
        expected = (10.0 - 100.0) / (0.9 * 0.8 * 0.7)
        assert abs(c_star - max(0, expected)) < 1e-10
    
    def test_indifference_threshold_zero_probability(self):
        """Test threshold with zero probability."""
        params = BasiliskParameters(simulation_detection=0.0)
        basilisk = RokoBasilisk(params)
        
        c_star = basilisk.calculate_indifference_threshold()
        assert c_star == float('inf')


class TestDecisionTheories:
    """Test different decision theory implementations."""
    
    def setup_method(self):
        """Set up test fixture."""
        self.params = BasiliskParameters(
            reward_collaboration=100.0,
            cost_collaboration=10.0,
            punishment_magnitude=1000.0,
            prob_asi_emergence=0.8,
            prob_basilisk_type=0.7,
            simulation_detection=0.9
        )
        self.basilisk = RokoBasilisk(self.params)
    
    def test_fdt_decision(self):
        """Test FDT decision calculations."""
        result = self.basilisk.analyze_decision(DecisionTheory.FDT)
        
        assert isinstance(result, DecisionResult)
        assert result.decision_theory == DecisionTheory.FDT
        
        # FDT should favor collaboration with these parameters
        expected_collab = 100.0 - 10.0  # r - c
        expected_non_collab = -0.9 * 0.8 * 0.7 * 1000.0  # -q * p(A) * p(B|A) * C
        
        assert abs(result.utility_collaborate - expected_collab) < 1e-10
        assert abs(result.utility_non_collaborate - expected_non_collab) < 1e-10
        assert result.optimal_decision == "COLLABORATE"
    
    def test_cdt_decision(self):
        """Test CDT decision calculations."""
        result = self.basilisk.analyze_decision(DecisionTheory.CDT)
        
        # CDT should only consider causal effects
        assert result.utility_collaborate == -10.0  # Only cost
        assert result.utility_non_collaborate == 0.0  # No causal punishment
        assert result.optimal_decision == "NON_COLLABORATE"
    
    def test_edt_decision(self):
        """Test EDT decision calculations."""
        result = self.basilisk.analyze_decision(DecisionTheory.EDT)
        
        # EDT should be between FDT and CDT
        assert result.utility_collaborate == 90.0  # r - c
        # EDT uses reduced correlation (0.5 factor)
        expected_non_collab = -0.5 * 0.9 * 0.8 * 0.7 * 1000.0
        assert abs(result.utility_non_collaborate - expected_non_collab) < 1e-10
    
    def test_reject_blackmail_decision(self):
        """Test reject blackmail policy."""
        result = self.basilisk.analyze_decision(DecisionTheory.REJECT_BLACKMAIL)
        
        # Should ignore both acausal benefits and threats
        assert result.utility_collaborate == -10.0  # Only cost
        assert result.utility_non_collaborate == 0.0  # No threat acknowledgment
        assert result.optimal_decision == "NON_COLLABORATE"
    
    def test_theory_comparison(self):
        """Test comparison across all theories."""
        results = self.basilisk.compare_decision_theories()
        
        assert len(results) == len(DecisionTheory)
        
        # FDT and TDT should give same results
        assert results[DecisionTheory.FDT].optimal_decision == results[DecisionTheory.TDT].optimal_decision
        
        # CDT and REJECT_BLACKMAIL should both choose non-collaboration
        assert results[DecisionTheory.CDT].optimal_decision == "NON_COLLABORATE"
        assert results[DecisionTheory.REJECT_BLACKMAIL].optimal_decision == "NON_COLLABORATE"


class TestUtilityFunctions:
    """Test different utility function transformations."""
    
    def setup_method(self):
        """Set up test fixture."""
        self.basilisk = RokoBasilisk()
    
    def test_linear_utility(self):
        """Test linear utility function."""
        assert self.basilisk.apply_utility_function(100.0, UtilityFunction.LINEAR) == 100.0
        assert self.basilisk.apply_utility_function(-50.0, UtilityFunction.LINEAR) == -50.0
    
    def test_logarithmic_utility(self):
        """Test logarithmic utility function."""
        result = self.basilisk.apply_utility_function(100.0, UtilityFunction.LOGARITHMIC)
        expected = math.log(1100.0)  # 100 + 1000 offset
        assert abs(result - expected) < 1e-10
    
    def test_exponential_utility(self):
        """Test exponential utility function."""
        result = self.basilisk.apply_utility_function(100.0, UtilityFunction.EXPONENTIAL)
        expected = math.exp(100.0 / 1000.0)
        assert abs(result - expected) < 1e-10
    
    def test_square_root_utility(self):
        """Test square root utility function."""
        result = self.basilisk.apply_utility_function(100.0, UtilityFunction.SQUARE_ROOT)
        expected = math.sqrt(1100.0)  # 100 + 1000 offset
        assert abs(result - expected) < 1e-10
    
    def test_negative_value_handling(self):
        """Test utility functions handle negative values properly."""
        # Logarithmic should handle negative values with offset
        result = self.basilisk.apply_utility_function(-500.0, UtilityFunction.LOGARITHMIC)
        expected = math.log(500.0)  # -500 + 1000 offset
        assert abs(result - expected) < 1e-10
        
        # Square root should handle negative values with offset
        result = self.basilisk.apply_utility_function(-500.0, UtilityFunction.SQUARE_ROOT)
        expected = math.sqrt(500.0)  # -500 + 1000 offset
        assert abs(result - expected) < 1e-10


class TestSensitivityAnalysis:
    """Test parameter sensitivity analysis."""
    
    def setup_method(self):
        """Set up test fixture."""
        self.basilisk = RokoBasilisk()
    
    def test_punishment_sensitivity(self):
        """Test sensitivity to punishment magnitude."""
        values = [500.0, 1000.0, 1500.0]
        results = self.basilisk.sensitivity_analysis('punishment_magnitude', values)
        
        assert len(results) == 3
        
        # Higher punishment should increase collaboration utility difference
        utilities = [r.utility_difference for r in results]
        assert utilities[2] > utilities[1] > utilities[0]
    
    def test_probability_sensitivity(self):
        """Test sensitivity to probabilities."""
        values = [0.5, 0.7, 0.9]
        results = self.basilisk.sensitivity_analysis('prob_asi_emergence', values)
        
        assert len(results) == 3
        
        # Higher ASI probability should make collaboration more attractive
        utilities = [r.utility_difference for r in results]
        assert utilities[2] > utilities[1] > utilities[0]
    
    def test_parameter_restoration(self):
        """Test that original parameters are restored after sensitivity analysis."""
        original_punishment = self.basilisk.params.punishment_magnitude
        
        values = [500.0, 1000.0, 1500.0]
        self.basilisk.sensitivity_analysis('punishment_magnitude', values)
        
        # Parameters should be restored
        assert self.basilisk.params.punishment_magnitude == original_punishment


class TestMonteCarloSimulation:
    """Test Monte Carlo simulation functionality."""
    
    def setup_method(self):
        """Set up test fixture."""
        self.basilisk = RokoBasilisk()
    
    @patch('numpy.random.random')
    def test_monte_carlo_deterministic(self, mock_random):
        """Test Monte Carlo with controlled randomness."""
        # Make random always return 0.5 for predictable behavior
        mock_random.return_value = 0.5
        
        results = self.basilisk.monte_carlo_simulation(n_samples=10)
        
        assert 'collaboration_probability' in results
        assert 'mean_collab_utility' in results
        assert 'mean_non_collab_utility' in results
        assert len(results['collaboration_utilities']) == 10
        assert len(results['decisions']) == 10
    
    def test_monte_carlo_basic_properties(self):
        """Test basic properties of Monte Carlo results."""
        results = self.basilisk.monte_carlo_simulation(n_samples=100)
        
        # Check result structure
        assert isinstance(results['collaboration_probability'], float)
        assert 0 <= results['collaboration_probability'] <= 1
        
        # Check that we have the right number of samples
        assert len(results['collaboration_utilities']) == 100
        assert len(results['non_collaboration_utilities']) == 100
        assert len(results['decisions']) == 100
        
        # Decisions should be 0 or 1
        assert all(d in [0, 1] for d in results['decisions'])


class TestPropertyBasedTests:
    """Property-based tests for mathematical invariants."""
    
    def setup_method(self):
        """Set up test fixture."""
        self.basilisk = RokoBasilisk()
    
    def test_zero_punishment_property(self):
        """If punishment is zero, should never collaborate due to threat."""
        params = BasiliskParameters(punishment_magnitude=0.0)
        basilisk = RokoBasilisk(params)
        
        result = basilisk.analyze_decision(DecisionTheory.FDT)
        
        # With no punishment, only reward vs cost matters
        if params.reward_collaboration > params.cost_collaboration:
            assert result.optimal_decision == "COLLABORATE"
        else:
            assert result.optimal_decision == "NON_COLLABORATE"
    
    def test_infinite_reward_property(self):
        """If reward is very high, should always collaborate."""
        params = BasiliskParameters(reward_collaboration=1e6)
        basilisk = RokoBasilisk(params)
        
        result = basilisk.analyze_decision(DecisionTheory.FDT)
        assert result.optimal_decision == "COLLABORATE"
    
    def test_zero_probability_property(self):
        """If all probabilities are zero, no acausal effects."""
        params = BasiliskParameters(
            prob_asi_emergence=0.0,
            prob_basilisk_type=0.0,
            simulation_detection=0.0
        )
        basilisk = RokoBasilisk(params)
        
        result = basilisk.analyze_decision(DecisionTheory.FDT)
        
        # Should behave like CDT with no acausal effects
        if params.reward_collaboration > params.cost_collaboration:
            assert result.optimal_decision == "COLLABORATE"
        else:
            assert result.optimal_decision == "NON_COLLABORATE"
    
    def test_symmetry_property(self):
        """Decision should be symmetric in equivalent scenarios."""
        # Two equivalent parameter sets
        params1 = BasiliskParameters(
            prob_asi_emergence=0.8,
            prob_basilisk_type=0.7,
            simulation_detection=0.9
        )
        params2 = BasiliskParameters(
            prob_asi_emergence=0.56,  # 0.8 * 0.7
            prob_basilisk_type=1.0,
            simulation_detection=0.9
        )
        
        basilisk1 = RokoBasilisk(params1)
        basilisk2 = RokoBasilisk(params2)
        
        result1 = basilisk1.analyze_decision(DecisionTheory.FDT)
        result2 = basilisk2.analyze_decision(DecisionTheory.FDT)
        
        # Should give same decision (product of probabilities is same)
        assert result1.optimal_decision == result2.optimal_decision
    
    def test_monotonicity_property(self):
        """Higher punishment should favor collaboration (ceteris paribus)."""
        punishments = [500.0, 1000.0, 1500.0]
        decisions = []
        
        for punishment in punishments:
            params = BasiliskParameters(punishment_magnitude=punishment)
            basilisk = RokoBasilisk(params)
            result = basilisk.analyze_decision(DecisionTheory.FDT)
            decisions.append(result.optimal_decision)
        
        # Once collaboration becomes optimal, it should stay optimal
        collab_indices = [i for i, d in enumerate(decisions) if d == "COLLABORATE"]
        if collab_indices:
            # All indices after first collaboration should also be collaboration
            first_collab = min(collab_indices)
            for i in range(first_collab, len(decisions)):
                assert decisions[i] == "COLLABORATE"


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_invalid_decision_theory(self):
        """Test handling of invalid decision theory."""
        basilisk = RokoBasilisk()
        
        # This should raise an error
        with pytest.raises(ValueError):
            basilisk.calculate_decision_utilities("INVALID_THEORY")
    
    def test_extreme_parameters(self):
        """Test behavior with extreme parameter values."""
        # Very large punishment
        params = BasiliskParameters(punishment_magnitude=1e10)
        basilisk = RokoBasilisk(params)
        result = basilisk.analyze_decision(DecisionTheory.FDT)
        assert result.optimal_decision == "COLLABORATE"
        
        # Very small positive punishment
        params = BasiliskParameters(punishment_magnitude=1e-10)
        basilisk = RokoBasilisk(params)
        result = basilisk.analyze_decision(DecisionTheory.FDT)
        # Should depend on other parameters, but shouldn't crash
        assert result.optimal_decision in ["COLLABORATE", "NON_COLLABORATE"]
    
    def test_numerical_precision(self):
        """Test numerical precision in calculations."""
        params = BasiliskParameters(
            reward_collaboration=1.0000000001,
            cost_collaboration=1.0,
            punishment_magnitude=1000.0
        )
        basilisk = RokoBasilisk(params)
        
        result = basilisk.analyze_decision(DecisionTheory.FDT)
        # Should handle small differences properly
        assert result.optimal_decision == "COLLABORATE"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])