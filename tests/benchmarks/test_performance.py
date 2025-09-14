"""Benchmark tests for performance analysis."""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from rokobasilisk.api import evaluate


@pytest.mark.benchmark
class TestBenchmarks:
    """Performance benchmarks for the system."""
    
    def test_single_evaluation_benchmark(self, benchmark):
        """Benchmark single evaluation performance."""
        result = benchmark(evaluate)
        assert result.policy in ['fdt', 'tdt', 'cdt', 'edt', 'reject']
    
    def test_fdt_evaluation_benchmark(self, benchmark):
        """Benchmark FDT evaluation specifically."""
        result = benchmark(evaluate, policy='fdt')
        assert result.policy == 'fdt'
    
    def test_multiple_policies_benchmark(self, benchmark):
        """Benchmark evaluation across all policies."""
        def evaluate_all_policies():
            policies = ['fdt', 'tdt', 'cdt', 'edt', 'reject']
            results = []
            for policy in policies:
                results.append(evaluate(policy=policy))
            return results
        
        results = benchmark(evaluate_all_policies)
        assert len(results) == 5
    
    def test_parameter_variation_benchmark(self, benchmark):
        """Benchmark with parameter variations."""
        def evaluate_with_variations():
            results = []
            for punishment in [500, 1000, 1500]:
                for reward in [50, 100, 150]:
                    params = {
                        'punishment_magnitude': punishment,
                        'reward_collaboration': reward
                    }
                    results.append(evaluate(params=params))
            return results
        
        results = benchmark(evaluate_with_variations)
        assert len(results) == 9


if __name__ == "__main__":
    pytest.main([__file__, "--benchmark-only"])