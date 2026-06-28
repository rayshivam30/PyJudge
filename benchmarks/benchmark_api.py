import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_url(url):
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(url) as response:
            status_code = response.getcode()
            response.read() # read body
            latency = time.perf_counter() - start
            return True, latency
    except Exception as e:
        latency = time.perf_counter() - start
        return False, latency

def run_benchmark(url, concurrent_clients, total_requests):
    print(f"Starting benchmark on {url}...")
    print(f"Concurrency: {concurrent_clients}, Total Requests: {total_requests}")

    start_time = time.perf_counter()
    latencies = []
    success_count = 0
    failure_count = 0

    with ThreadPoolExecutor(max_workers=concurrent_clients) as executor:
        futures = [executor.submit(fetch_url, url) for _ in range(total_requests)]
        for future in as_completed(futures):
            success, latency = future.result()
            latencies.append(latency)
            if success:
                success_count += 1
            else:
                failure_count += 1

    total_time = time.perf_counter() - start_time
    rps = total_requests / total_time

    avg_latency = sum(latencies) / len(latencies)
    min_latency = min(latencies)
    max_latency = max(latencies)

    # Sort to find percentiles
    latencies.sort()
    p50 = latencies[int(len(latencies) * 0.5)]
    p90 = latencies[int(len(latencies) * 0.9)]
    p99 = latencies[int(len(latencies) * 0.99)]

    print(f"\nResults:")
    print(f"  Total time: {total_time:.4f} seconds")
    print(f"  Successful requests: {success_count}")
    print(f"  Failed requests: {failure_count}")
    print(f"  Requests per second (RPS): {rps:.2f}")
    print(f"  Latency:")
    print(f"    Average: {avg_latency*1000:.2f} ms")
    print(f"    Min: {min_latency*1000:.2f} ms")
    print(f"    Max: {max_latency*1000:.2f} ms")
    print(f"    50th percentile (Median): {p50*1000:.2f} ms")
    print(f"    90th percentile: {p90*1000:.2f} ms")
    print(f"    99th percentile: {p99*1000:.2f} ms")

if __name__ == "__main__":
    run_benchmark("http://127.0.0.1:8000/health", concurrent_clients=50, total_requests=1000)
