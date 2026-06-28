import time
import subprocess

def test_startup():
    times = []
    print("Benchmarking Docker startup time...")
    # First execution to pull or warm cache
    try:
        subprocess.run(["docker", "run", "--rm", "python:3.12-slim", "python", "-c", "print('warmup')"], capture_output=True, check=True)
    except Exception as e:
        print(f"Error during warmup: {e}")
        return

    for i in range(5):
        start = time.perf_counter()
        res = subprocess.run(["docker", "run", "--rm", "python:3.12-slim", "python", "-c", "print('hello')"], capture_output=True)
        end = time.perf_counter()
        elapsed = end - start
        times.append(elapsed)
        print(f"Run {i+1}: {elapsed:.4f} seconds (Exit code: {res.returncode})")

    avg = sum(times) / len(times)
    print(f"\nAverage: {avg:.4f}s, Min: {min(times):.4f}s, Max: {max(times):.4f}s")

if __name__ == "__main__":
    test_startup()
