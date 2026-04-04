"""
benchmark.py — Local latency benchmark for mocktailverse RAG pipeline
Mocks AWS I/O with realistic simulated latency, benchmarks processing logic.

NOTE: Local mock — not deployed prod. Real p95 depends on AWS cold starts + network.
Honest framing: "local mock benchmark on RAG pipeline — p95 includes simulated Bedrock + Search I/O"
"""

import time
import json
import statistics
import sys
import os
import importlib.util
from unittest.mock import MagicMock, patch

SIMULATED_BEDROCK_MS = 450   # Titan Text Lite typical
SIMULATED_SEARCH_MS  = 120   # DynamoDB/OpenSearch typical

# Minimal mock returns
def mock_bedrock_response():
    payload = json.dumps({'results': [{'outputText': 'Try a Mojito — rum, mint, lime, soda.'}]})
    m = MagicMock()
    m.read.return_value = payload.encode()
    return {'body': m}

def mock_search_response():
    results = [{'name': 'Mojito', 'relevance_score': 0.92, 'category': 'Cocktail',
                'alcoholic': 'Alcoholic', 'description': 'Classic rum cocktail',
                'ingredients': [{'name': 'rum', 'measure': '2 oz'}, {'name': 'mint', 'measure': '10 leaves'}],
                'instructions': 'Muddle mint, add rum and lime, top with soda.',
                'flavor_profile': ['refreshing', 'citrus'], 'occasions': ['summer'],
                'difficulty': 'Easy', 'prep_time_minutes': 5}]
    payload = json.dumps({'body': json.dumps({'results': results})}).encode()
    m = MagicMock()
    m.read.return_value = payload
    return {'Payload': m}

class FakeBedrock:
    def invoke_model(self, **kwargs):
        time.sleep(SIMULATED_BEDROCK_MS / 1000)
        return mock_bedrock_response()

class FakeLambda:
    def invoke(self, **kwargs):
        time.sleep(SIMULATED_SEARCH_MS / 1000)
        return mock_search_response()

# Load handler with mocked boto3
handler_path = os.path.join(os.path.dirname(__file__), '../lambdas/rag/handler.py')
spec = importlib.util.spec_from_file_location('handler', os.path.realpath(handler_path))
with patch('boto3.client', side_effect=lambda svc, **kw: FakeBedrock() if svc == 'bedrock-runtime' else FakeLambda()):
    handler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(handler)

handler.bedrock = FakeBedrock()
handler.lambda_client = FakeLambda()

# --- Run benchmark ---
QUESTIONS = [
    "What cocktail should I make with rum?",
    "Recommend a non-alcoholic drink",
    "What has mint in it?",
    "Best cocktail for summer parties",
    "Something refreshing with citrus",
]

N = 100
latencies = []
print(f"Running {N} invocations...\n")

for i in range(N):
    event = {'body': json.dumps({'question': QUESTIONS[i % len(QUESTIONS)], 'k': 3})}
    t0 = time.perf_counter()
    handler.lambda_handler(event, {})
    latencies.append((time.perf_counter() - t0) * 1000)

latencies.sort()
p50 = statistics.median(latencies)
p95 = latencies[int(0.95 * N) - 1]
p99 = latencies[int(0.99 * N) - 1]

print(f"Benchmark results ({N} invocations — local mock):")
print(f"  p50: {p50:.0f}ms")
print(f"  p95: {p95:.0f}ms  ← key number")
print(f"  p99: {p99:.0f}ms")
print(f"  min: {min(latencies):.0f}ms  max: {max(latencies):.0f}ms")
print(f"\nSimulated I/O: Bedrock {SIMULATED_BEDROCK_MS}ms + Search {SIMULATED_SEARCH_MS}ms = {SIMULATED_BEDROCK_MS+SIMULATED_SEARCH_MS}ms floor")
print("NOTE: Real deployed p95 will include cold starts + actual network. Deploy to get real number.")

results = {
    'n': N, 'p50_ms': round(p50), 'p95_ms': round(p95), 'p99_ms': round(p99),
    'min_ms': round(min(latencies)), 'max_ms': round(max(latencies)),
    'simulated_bedrock_ms': SIMULATED_BEDROCK_MS,
    'simulated_search_ms': SIMULATED_SEARCH_MS,
    'note': 'local mock benchmark — not deployed prod measurement'
}
out = os.path.join(os.path.dirname(__file__), 'benchmark_results.json')
with open(out, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved → scripts/benchmark_results.json")
