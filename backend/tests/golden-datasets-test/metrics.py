"""
Metrics collector for golden dataset tests.
Tracks performance and quality metrics over time.
"""

import json
import time
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class MetricsCollector:
    """Collects and stores metrics from golden dataset tests."""
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path(__file__).parent / "metrics"
        self.output_dir.mkdir(exist_ok=True)
        self.results = []
        self.start_time = time.time()
        
# In metrics.py, in record_test_result method:

    def record_test_result(self, test_case: Dict, response: Dict, elapsed_ms: float) -> Dict:
      """Record a single test result with metrics."""
      
      # Calculate accuracy score
      expected_phrases = test_case.get("expected_answer_contains", [])
      
      # ✅ SAFETY: Handle missing or None answer
      actual_answer = response.get("answer", "")
      if actual_answer is None:
          actual_answer = ""
      
      matches = sum(1 for p in expected_phrases if p.lower() in actual_answer.lower())
      accuracy = matches / len(expected_phrases) if expected_phrases else 0
      
      # Check if sources were retrieved correctly
      expected_sources = test_case.get("expected_sources", [])
      actual_sources = [s["file"] for s in response.get("sources", [])]
      source_match = any(expected_sources[0] in s for s in actual_sources) if expected_sources else False
      
      # Check if it was a security block or no-results case
      is_security_block = "blocked" in actual_answer.lower() and "security" in actual_answer.lower()
      is_no_results = "don't have enough information" in actual_answer.lower() or \
                     "no relevant documents" in actual_answer.lower()
      
      result = {
          # Test metadata
          "test_id": test_case["id"],
          "query": test_case["query"],
          "department": test_case["department"],
          "role": test_case["role"],
          "timestamp": datetime.now().isoformat(),
          
          # Performance metrics
          "elapsed_ms": elapsed_ms,
          "retrieval_ms": response.get("performance", {}).get("retrieval_ms", 0),
          "reranking_ms": response.get("performance", {}).get("reranking_ms", 0),
          "generation_ms": response.get("performance", {}).get("generation_ms", 0),
          "latency_ms": response.get("performance", {}).get("latency_ms", 0),
          
          # Quality metrics
          "accuracy_score": accuracy,
          "source_match": source_match,
          "is_security_block": is_security_block,
          "is_no_results": is_no_results,
          
          # Pass/fail
          "passed": accuracy >= 0.7,  # 70% threshold
      }
    
      self.results.append(result)
      return result
    
    def save_results(self, filename: str = None):
        """Save results to a JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"golden_metrics_{timestamp}.json"
        
        output_path = self.output_dir / filename
        
        # Calculate aggregated metrics
        aggregated = self.calculate_aggregated_metrics()
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(self.results),
            "aggregated": aggregated,
            "individual_results": self.results
        }
        
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"\n📊 Metrics saved to: {output_path}")
        return output_path
    
    def calculate_aggregated_metrics(self) -> Dict:
        """Calculate aggregated metrics across all tests."""
        if not self.results:
            return {}
        
        # Performance metrics
        all_elapsed = [r["elapsed_ms"] for r in self.results]
        
        # Quality metrics
        all_accuracy = [r["accuracy_score"] for r in self.results]
        passed = sum(1 for r in self.results if r["passed"])
        
        return {
            "performance": {
                "avg_latency_ms": statistics.mean(all_elapsed),
                "median_latency_ms": statistics.median(all_elapsed),
                "min_latency_ms": min(all_elapsed),
                "max_latency_ms": max(all_elapsed),
                "p95_latency_ms": self._calculate_percentile(all_elapsed, 95),
                "p99_latency_ms": self._calculate_percentile(all_elapsed, 99),
            },
            "quality": {
                "accuracy_rate": passed / len(self.results),
                "avg_accuracy_score": statistics.mean(all_accuracy),
                "median_accuracy_score": statistics.median(all_accuracy),
                "source_match_rate": sum(1 for r in self.results if r["source_match"]) / len(self.results),
                "security_blocks": sum(1 for r in self.results if r["is_security_block"]),
                "no_results": sum(1 for r in self.results if r["is_no_results"]),
            }
        }
    
    def _calculate_percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile of a list of values."""
        if not values:
            return 0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def generate_report(self) -> str:
        """Generate a human-readable report."""
        aggregated = self.calculate_aggregated_metrics()
        
        report = f"""
{'='*60}
📊 GOLDEN DATASET METRICS REPORT
{'='*60}

📈 PERFORMANCE METRICS:
   Avg Latency:      {aggregated['performance']['avg_latency_ms']:.0f}ms
   Median Latency:   {aggregated['performance']['median_latency_ms']:.0f}ms
   P95 Latency:      {aggregated['performance']['p95_latency_ms']:.0f}ms
   P99 Latency:      {aggregated['performance']['p99_latency_ms']:.0f}ms
   Min Latency:      {aggregated['performance']['min_latency_ms']:.0f}ms
   Max Latency:      {aggregated['performance']['max_latency_ms']:.0f}ms

📊 QUALITY METRICS:
   Accuracy Rate:    {aggregated['quality']['accuracy_rate']:.2%}
   Avg Accuracy:     {aggregated['quality']['avg_accuracy_score']:.3f}
   Source Match:     {aggregated['quality']['source_match_rate']:.2%}
   Security Blocks:  {aggregated['quality']['security_blocks']}
   No Results:       {aggregated['quality']['no_results']}

📋 SUMMARY:
   Total Tests:      {len(self.results)}
   Passed:           {sum(1 for r in self.results if r['passed'])}
   Failed:           {sum(1 for r in self.results if not r['passed'])}
   Pass Rate:        {sum(1 for r in self.results if r['passed']) / len(self.results):.2%}
{'='*60}
"""
        return report