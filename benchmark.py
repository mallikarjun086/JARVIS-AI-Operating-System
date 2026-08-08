#!/usr/bin/env python3
"""
JARVIS AI OS — Performance Benchmark Script.
Measures API response times, throughput, and identifies bottlenecks.

Usage:
  python benchmark.py --url http://localhost:8000 --token <JWT_TOKEN>
  python benchmark.py --url http://localhost:8000 --login --email operator@jarvis.ai --password SecurePass123!
"""
import argparse
import asyncio
import time
from typing import Any, Dict, List, Optional

try:
    import httpx
    import statistics
except ImportError:
    print("Install dependencies: pip install httpx")
    raise

BENCHMARK_ENDPOINTS = [
    ("GET", "/api/v1/health", None, "Health Probe"),
    ("GET", "/api/v1/readiness", None, "Readiness Probe"),
    ("GET", "/api/v1/metrics", None, "Prometheus Metrics"),
    ("GET", "/api/v1/ai/providers/status", None, "AI Provider Status"),
    ("GET", "/api/v1/tools/list", None, "Tool Registry List"),
]


async def get_token(base_url: str, email: str, password: str) -> Optional[str]:
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        resp = await client.post("/api/v1/auth/login", data={"username": email, "password": password})
        if resp.status_code == 200:
            return resp.json().get("access_token")
        print(f"Login failed: {resp.status_code} {resp.text}")
        return None


async def benchmark_endpoint(
    client: httpx.AsyncClient,
    method: str,
    path: str,
    body: Optional[Dict],
    label: str,
    n_requests: int = 10,
) -> Dict[str, Any]:
    latencies: List[float] = []
    errors = 0
    for _ in range(n_requests):
        try:
            start = time.perf_counter()
            if method == "GET":
                r = await client.get(path)
            else:
                r = await client.post(path, json=body)
            elapsed_ms = (time.perf_counter() - start) * 1000
            if r.status_code < 400:
                latencies.append(elapsed_ms)
            else:
                errors += 1
        except Exception:
            errors += 1

    if not latencies:
        return {"endpoint": label, "path": path, "error": "All requests failed", "error_count": errors}

    return {
        "endpoint": label,
        "path": f"{method} {path}",
        "requests": n_requests,
        "errors": errors,
        "p50_ms": round(statistics.median(latencies), 2),
        "p95_ms": round(sorted(latencies)[int(len(latencies) * 0.95)], 2) if len(latencies) > 1 else round(latencies[0], 2),
        "min_ms": round(min(latencies), 2),
        "max_ms": round(max(latencies), 2),
        "avg_ms": round(statistics.mean(latencies), 2),
    }


async def run_benchmarks(base_url: str, token: Optional[str], n: int = 10) -> None:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    print(f"\n{'='*70}")
    print(f"  JARVIS AI OS — Performance Benchmark")
    print(f"  Target: {base_url} | Requests per endpoint: {n}")
    print(f"{'='*70}\n")

    results = []
    async with httpx.AsyncClient(base_url=base_url, headers=headers, timeout=15.0) as client:
        for method, path, body, label in BENCHMARK_ENDPOINTS:
            print(f"  Benchmarking: {label}...", end="", flush=True)
            result = await benchmark_endpoint(client, method, path, body, label, n)
            results.append(result)
            p50 = result.get("p50_ms", "ERR")
            print(f"  p50={p50}ms")

    # Summary table
    print(f"\n{'─'*70}")
    print(f"  {'Endpoint':<30} {'p50ms':>8} {'p95ms':>8} {'min':>8} {'max':>8} {'errors':>6}")
    print(f"{'─'*70}")
    for r in results:
        if "error" in r:
            print(f"  {r['endpoint']:<30} {'FAILED':>8}")
        else:
            print(f"  {r['endpoint']:<30} {r['p50_ms']:>8} {r['p95_ms']:>8} {r['min_ms']:>8} {r['max_ms']:>8} {r['errors']:>6}")
    print(f"{'─'*70}")

    # Warnings
    slow = [r for r in results if r.get("p50_ms", 0) > 500]
    if slow:
        print(f"\n  ⚠️  SLOW ENDPOINTS (p50 > 500ms): {[r['endpoint'] for r in slow]}")
    else:
        print(f"\n  ✓  All endpoints within acceptable latency (<500ms p50)")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="JARVIS AI OS Performance Benchmark")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of JARVIS backend")
    parser.add_argument("--token", help="JWT Bearer token")
    parser.add_argument("--login", action="store_true", help="Login to get token")
    parser.add_argument("--email", default="operator@jarvis.ai", help="Login email")
    parser.add_argument("--password", default="SecurePass123!", help="Login password")
    parser.add_argument("--n", type=int, default=10, help="Number of requests per endpoint")
    args = parser.parse_args()

    token = args.token

    async def _run():
        nonlocal token
        if args.login or not token:
            print("  Authenticating...")
            token = await get_token(args.url, args.email, args.password)
            if token:
                print(f"  ✓ Token acquired")
            else:
                print("  ✗ Authentication failed — running unauthenticated benchmarks")
        await run_benchmarks(args.url, token, n=args.n)

    asyncio.run(_run())


if __name__ == "__main__":
    main()
