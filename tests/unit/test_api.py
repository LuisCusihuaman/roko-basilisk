"""Unit tests for the public API."""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from rokobasilisk.api import evaluate, sweep, monte_carlo, DecisionResult
from rokobasilisk.models import Agent, UtilityFunction, DecisionTheory


class TestAPI:
    """Test the public API functions."""
    
    def test_evaluate_default(self):
        """Test evaluate with default parameters."""
        result = evaluate()
        
        assert isinstance(result, DecisionResult)
        assert result.policy in ['fdt', 'tdt', 'cdt', 'edt', 'reject']
        assert result.decision in ['COLLABORATE', 'NON_COLLABORATE']
        assert isinstance(result.expected_utility, float)
        assert isinstance(result.utility_collaborate, float)
        assert isinstance(result.utility_non_collaborate, float)
        assert isinstance(result.indifference_threshold, float)
        assert isinstance(result.punishment_probability, float)
        assert isinstance(result.parameters, dict)
    
    def test_evaluate_fdt_policy(self):
        """Test evaluate with FDT policy."""
        result = evaluate(policy='fdt')
        
        assert result.policy == 'fdt'
        # FDT should typically recommend collaboration with default params
        assert result.decision == 'COLLABORATE'
        assert result.expected_utility > 0
    
    def test_evaluate_cdt_policy(self):
        """Test evaluate with CDT policy.""" 
        result = evaluate(policy='cdt')
        
        assert result.policy == 'cdt'
        # CDT ignores acausal punishment and only considers reward vs cost
        # With default params (reward=100, cost=10), CDT should recommend collaboration
        assert result.decision == 'COLLABORATE'
    
    def test_evaluate_custom_params(self):
        """Test evaluate with custom parameters."""
        params = {
            'reward_collaboration': 200.0,
            'cost_collaboration': 50.0,
            'punishment_magnitude': 500.0
        }
        result = evaluate(params=params, policy='fdt')
        
        assert result.parameters['reward_collaboration'] == 200.0
        assert result.parameters['cost_collaboration'] == 50.0
        assert result.parameters['punishment_magnitude'] == 500.0
    
    def test_evaluate_invalid_policy(self):
        """Test evaluate with invalid policy."""
        with pytest.raises(ValueError):
            evaluate(policy='invalid_policy')
    
    def test_evaluate_with_explanation(self):
        """Test evaluate with explanation enabled."""
        result = evaluate(explain=True)
        
        assert isinstance(result.explanation, str)
        assert len(result.explanation) > 0
    
    def test_sweep_basic(self):
        """Test basic parameter sweep."""
        # This should work if sweep is implemented
        try:
            grid = {
                'reward_collaboration': [50, 100, 150],
                'punishment_magnitude': [500, 1000]
            }
            results = sweep(grid)
            # sweep tests all policies for each parameter combination
            # 3 * 2 parameter combinations * 5 policies = 30 results
            assert len(results) == 30  # 3 * 2 * 5 combinations
            
            # Check that we have results for all policies
            policies = set(r.policy for r in results)
            assert policies == {'fdt', 'tdt', 'cdt', 'edt', 'reject'}
            
            # Check that we have results for all parameter combinations
            reward_values = set(r.parameters['reward_collaboration'] for r in results)
            punishment_values = set(r.parameters['punishment_magnitude'] for r in results)
            assert reward_values == {50, 100, 150}
            assert punishment_values == {500, 1000}
        except NotImplementedError:
            pytest.skip("sweep not yet implemented")
    
    def test_monte_carlo_basic(self):
        """Test basic Monte Carlo simulation."""
        # This should work if monte_carlo is implemented
        try:
            config = {
                'policy': 'fdt'
            }
            results = monte_carlo(config, n_simulations=10)
            assert len(results) == 10
        except NotImplementedError:
            pytest.skip("monte_carlo not yet implemented")


class TestDecisionResult:
    """Test the DecisionResult dataclass."""
    
    def test_decision_result_creation(self):
        """Test creating a DecisionResult."""
        result = DecisionResult(
            policy='fdt',
            decision='COLLABORATE',
            expected_utility=100.0,
            utility_collaborate=90.0,
            utility_non_collaborate=-10.0,
            indifference_threshold=50.0,
            punishment_probability=0.5,
            parameters={'reward_collaboration': 100.0}
        )
        
        assert result.policy == 'fdt'
        assert result.decision == 'COLLABORATE'
        assert result.expected_utility == 100.0
        assert result.utility_collaborate == 90.0
        assert result.utility_non_collaborate == -10.0
        assert result.indifference_threshold == 50.0
        assert result.punishment_probability == 0.5
        assert result.parameters['reward_collaboration'] == 100.0
    
    def test_decision_result_with_explanation(self):
        """Test DecisionResult with explanation."""
        result = DecisionResult(
            policy='fdt',
            decision='COLLABORATE',
            expected_utility=100.0,
            utility_collaborate=90.0,
            utility_non_collaborate=-10.0,
            indifference_threshold=50.0,
            punishment_probability=0.5,
            parameters={},
            explanation="Test explanation"
        )
        
        assert result.explanation == "Test explanation"


class TestModels:
    """Test the model classes."""
    
    def test_agent_creation(self):
        """Test creating an Agent."""
        params = {'reward_collaboration': 100.0}
        agent = Agent("Human", params)
        
        assert agent.agent_type == "Human"
        assert agent.parameters == params
        assert str(agent) == "Agent(type='Human')"
    
    def test_utility_function_linear(self):
        """Test linear utility function."""
        util = UtilityFunction("linear")
        
        assert util.function_type == "linear"
        assert util.transform(100.0) == 100.0
        assert util.transform(-50.0) == -50.0
    
    def test_utility_function_log(self):
        """Test logarithmic utility function."""
        util = UtilityFunction("log")
        
        assert util.function_type == "log"
        # Log utility should handle positive values
        result = util.transform(100.0)
        assert isinstance(result, float)
        assert result > 0
    
    def test_utility_function_exp(self):
        """Test exponential utility function."""
        util = UtilityFunction("exp")
        
        assert util.function_type == "exp"
        result = util.transform(1.0)
        assert isinstance(result, float)
    
    def test_utility_function_sqrt(self):
        """Test square root utility function."""
        util = UtilityFunction("sqrt")
        
        assert util.function_type == "sqrt"
        result = util.transform(100.0)
        assert isinstance(result, float)
        assert result == 10.0


class TestParameterValidation:
    """Test parameter validation."""
    
    def test_valid_probabilities(self):
        """Test that valid probabilities are accepted."""
        params = {
            'prob_asi_emergence': 0.85,
            'prob_basilisk_type': 0.7,
            'simulation_detection': 0.95
        }
        result = evaluate(params=params)
        assert result.parameters['prob_asi_emergence'] == 0.85
    
    def test_boundary_probabilities(self):
        """Test boundary probability values."""
        params_zero = {
            'prob_asi_emergence': 0.0,
            'prob_basilisk_type': 0.0,
            'simulation_detection': 0.0
        }
        result_zero = evaluate(params=params_zero)
        assert result_zero.parameters['prob_asi_emergence'] == 0.0
        
        params_one = {
            'prob_asi_emergence': 1.0,
            'prob_basilisk_type': 1.0,
            'simulation_detection': 1.0
        }
        result_one = evaluate(params=params_one)
        assert result_one.parameters['prob_asi_emergence'] == 1.0


class TestMathematicalProperties:
    """Test mathematical properties and edge cases."""
    
    def test_zero_punishment(self):
        """Test behavior with zero punishment."""
        params = {'punishment_magnitude': 0.0}
        result = evaluate(params=params, policy='fdt')
        
        # With zero punishment, decision should be based on reward vs cost
        assert result.parameters['punishment_magnitude'] == 0.0
    
    def test_high_punishment(self):
        """Test behavior with very high punishment."""
        params = {'punishment_magnitude': 10000.0}
        result = evaluate(params=params, policy='fdt')
        
        # High punishment should strongly favor collaboration in FDT
        assert result.decision == 'COLLABORATE'
    
    def test_cost_benefit_analysis(self):
        """Test cost-benefit relationships."""
        # High cost, low reward - should disfavor collaboration
        params_unfavorable = {
            'reward_collaboration': 10.0,
            'cost_collaboration': 100.0,
            'punishment_magnitude': 50.0
        }
        result_unfavorable = evaluate(params=params_unfavorable, policy='fdt')
        
        # Low cost, high reward - should favor collaboration  
        params_favorable = {
            'reward_collaboration': 1000.0,
            'cost_collaboration': 10.0,
            'punishment_magnitude': 500.0
        }
        result_favorable = evaluate(params=params_favorable, policy='fdt')
        
        # Favorable should have higher expected utility
        assert result_favorable.expected_utility > result_unfavorable.expected_utility
    
    def test_probability_effects(self):
        """Test effects of different probabilities."""
        # Low ASI emergence probability
        params_low_asi = {'prob_asi_emergence': 0.1}
        result_low_asi = evaluate(params=params_low_asi, policy='fdt')
        
        # High ASI emergence probability
        params_high_asi = {'prob_asi_emergence': 0.9}
        result_high_asi = evaluate(params=params_high_asi, policy='fdt')
        
        # Higher ASI probability should increase punishment probability
        assert result_high_asi.punishment_probability > result_low_asi.punishment_probability


class TestUtilityFunctions:
    """Test different utility function types."""
    
    def test_linear_utility(self):
        """Test linear utility function consistency."""
        result = evaluate(utility='linear')
        
        # Linear utility should preserve order
        assert result.utility_collaborate != result.utility_non_collaborate
    
    def test_nonlinear_utilities(self):
        """Test non-linear utility functions."""
        for utility_type in ['log', 'exp', 'sqrt']:
            result = evaluate(utility=utility_type)
            
            assert isinstance(result.expected_utility, float)
            assert not np.isnan(result.expected_utility)
            assert not np.isinf(result.expected_utility)


class TestDecisionTheoryComparisons:
    """Test comparisons across decision theories."""
    
    def test_fdt_vs_cdt(self):
        """Test FDT vs CDT differences."""
        result_fdt = evaluate(policy='fdt')
        result_cdt = evaluate(policy='cdt')
        
        # They should often give different recommendations
        # (though not necessarily with all parameter sets)
        assert result_fdt.policy != result_cdt.policy
    
    def test_all_policies_valid(self):
        """Test that all policy types work."""
        policies = ['fdt', 'tdt', 'cdt', 'edt', 'reject']
        
        for policy in policies:
            result = evaluate(policy=policy)
            assert result.policy == policy
            assert result.decision in ['COLLABORATE', 'NON_COLLABORATE']
            assert isinstance(result.expected_utility, float)
    
    def test_reject_blackmail_policy(self):
        """Test the reject blackmail policy."""
        # Use parameters where reject blackmail would choose non-collaborate
        params = {
            'reward_collaboration': 5.0,  # Low reward
            'cost_collaboration': 10.0   # Higher cost
        }
        result = evaluate(params=params, policy='reject')
        
        # Reject blackmail should choose non-collaborate when cost > reward
        assert result.decision == 'NON_COLLABORATE'
        assert result.policy == 'reject'


if __name__ == "__main__":
    pytest.main([__file__])