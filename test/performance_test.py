"""
Performance Load Test - Database Sharding Comparison
Membandingkan performa Single Database vs Sharded Database (4 nodes)

Test Configuration:
- 300 concurrent users
- 100 chat rooms (distributed across shards)
- 20 messages per user = 6000 total operations
- Parallel execution with 50 concurrent workers
"""

import requests
import time
import argparse
import json
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import statistics

# Configuration
SINGLE_DB_URL = "http://localhost:5000"
MULTIPLE_DB_URL = "http://localhost:5001"

TOTAL_USERS = 300
TOTAL_ROOMS = 100
MESSAGES_PER_USER = 20
CONCURRENT_WORKERS = 50

# Thread-safe performance tracking
lock = threading.Lock()
performance_data = {
    "single": {"response_times": [], "errors": 0},
    "multiple": {"response_times": [], "errors": 0}
}


class VirtualUser:
    def __init__(self, user_id, base_url):
        self.user_id = user_id
        self.username = f"testuser_{user_id}_{random.randint(1000,9999)}"
        self.base_url = base_url
        self.session = requests.Session()
        self.room_id = None
        self.codename = None
    
    def register(self):
        try:
            resp = self.session.post(
                f"{self.base_url}/api/register",
                json={"username": self.username},
                timeout=30
            )
            return resp.status_code == 200
        except:
            return False
    
    def create_room(self):
        try:
            resp = self.session.post(
                f"{self.base_url}/api/rooms",
                json={"type": "group"},
                timeout=30
            )
            if resp.status_code == 200:
                data = resp.json()
                self.room_id = data["data"]["room_id"]
                self.codename = data["data"].get("codename")
                return self.room_id, self.codename
            return None, None
        except:
            return None, None
    
    def join_room_by_codename(self, codename):
        try:
            resp = self.session.post(
                f"{self.base_url}/api/rooms/join",
                json={"codename": codename},
                timeout=30
            )
            if resp.status_code == 200:
                data = resp.json()
                self.room_id = data["data"]["room_id"]
                self.codename = codename
                return True
            return False
        except:
            return False
    
    def send_message(self, db_type="single"):
        """Send a message to the room"""
        try:
            content = f"Message from {self.username} at {time.time()}"
            start_time = time.time()
            resp = self.session.post(
                f"{self.base_url}/api/rooms/{self.room_id}/messages",
                json={"content": content},
                timeout=30
            )
            elapsed = (time.time() - start_time) * 1000
            
            with lock:
                if resp.status_code == 200:
                    performance_data[db_type]["response_times"].append(elapsed)
                    return True
                else:
                    performance_data[db_type]["errors"] += 1
                    return False
        except:
            with lock:
                performance_data[db_type]["errors"] += 1
            return False


def calculate_percentiles(times):
    """Calculate P50, P95, P99 latencies"""
    if not times:
        return {"p50": 0, "p95": 0, "p99": 0, "avg": 0, "min": 0, "max": 0}
    
    sorted_times = sorted(times)
    n = len(sorted_times)
    
    return {
        "p50": sorted_times[int(n * 0.50)] if n > 0 else 0,
        "p95": sorted_times[int(n * 0.95)] if n > 0 else 0,
        "p99": sorted_times[int(n * 0.99)] if n > 0 else 0,
        "avg": statistics.mean(times) if times else 0,
        "min": min(times) if times else 0,
        "max": max(times) if times else 0
    }


def user_workload(user, room_info, db_type):
    """Execute workload for a single user - sending messages"""
    results = {"operations": 0, "success": 0}
    
    user.room_id = room_info["room_id"]
    user.codename = room_info["codename"]
    
    for _ in range(MESSAGES_PER_USER):
        results["operations"] += 1
        if user.send_message(db_type):
            results["success"] += 1
        time.sleep(random.uniform(0.005, 0.02))
    
    return results


def run_performance_test(base_url, db_name, db_type="single"):
    """Run performance load test"""
    print(f"\n{'='*70}")
    print(f"PERFORMANCE TEST: {db_name}")
    print(f"{'='*70}")
    print(f"URL: {base_url}")
    print(f"Users: {TOTAL_USERS} | Rooms: {TOTAL_ROOMS} | Messages/User: {MESSAGES_PER_USER}")
    print(f"Total Operations: {TOTAL_USERS * MESSAGES_PER_USER}")
    print(f"Concurrent Workers: {CONCURRENT_WORKERS}")
    print(f"{'='*70}\n")
    
    performance_data[db_type] = {"response_times": [], "errors": 0}
    
    start_time = time.time()
    
    # Phase 1: Create users
    print("[1/4] Creating users...")
    users = []
    with ThreadPoolExecutor(max_workers=CONCURRENT_WORKERS) as executor:
        def create_user(i):
            user = VirtualUser(i, base_url)
            if user.register():
                return user
            return None
        
        futures = [executor.submit(create_user, i) for i in range(TOTAL_USERS)]
        for future in as_completed(futures):
            user = future.result()
            if user:
                users.append(user)
    
    print(f"      Registered: {len(users)}/{TOTAL_USERS}")
    
    # Phase 2: Create rooms
    print(f"[2/4] Creating {TOTAL_ROOMS} rooms...")
    rooms = []
    creators = users[:TOTAL_ROOMS]
    
    with ThreadPoolExecutor(max_workers=CONCURRENT_WORKERS) as executor:
        def create_room(user):
            room_id, codename = user.create_room()
            if room_id and codename:
                return {"room_id": room_id, "codename": codename, "creator": user}
            return None
        
        futures = [executor.submit(create_room, u) for u in creators]
        for future in as_completed(futures):
            room = future.result()
            if room:
                rooms.append(room)
    
    print(f"      Created: {len(rooms)} rooms")
    
    # Shard distribution (for sharded DB)
    shard_dist = defaultdict(int)
    for room in rooms:
        shard = int(room["room_id"]) % 4
        shard_dist[shard] += 1
    print(f"      Shard distribution: {dict(shard_dist)}")
    
    # Phase 3: Assign users to rooms
    print("[3/4] Assigning users to rooms...")
    user_room_assignments = []
    for i, user in enumerate(users):
        room = rooms[i % len(rooms)]
        user_room_assignments.append((user, room))
    
    with ThreadPoolExecutor(max_workers=CONCURRENT_WORKERS) as executor:
        def join_room(assignment):
            user, room = assignment
            if user != room["creator"]:
                user.join_room_by_codename(room["codename"])
            return True
        
        futures = [executor.submit(join_room, a) for a in user_room_assignments]
        for future in as_completed(futures):
            future.result()
    
    # Phase 4: Execute workload
    print(f"[4/4] Executing workload ({CONCURRENT_WORKERS} concurrent workers)...")
    
    workload_start = time.time()
    total_results = {"operations": 0, "success": 0}
    
    with ThreadPoolExecutor(max_workers=CONCURRENT_WORKERS) as executor:
        futures = []
        for user, room in user_room_assignments:
            futures.append(executor.submit(user_workload, user, room, db_type))
        
        completed = 0
        for future in as_completed(futures):
            result = future.result()
            total_results["operations"] += result["operations"]
            total_results["success"] += result["success"]
            
            completed += 1
            if completed % 50 == 0:
                print(f"      Progress: {completed}/{len(users)} users completed")
    
    workload_duration = time.time() - workload_start
    total_duration = time.time() - start_time
    
    # Calculate stats
    perf_stats = calculate_percentiles(performance_data[db_type]["response_times"])
    error_rate = (1 - total_results["success"] / total_results["operations"]) * 100 if total_results["operations"] > 0 else 0
    throughput = total_results["success"] / workload_duration if workload_duration > 0 else 0
    
    # Print results
    print(f"\n{'='*70}")
    print(f"RESULTS: {db_name}")
    print(f"{'='*70}")
    print(f"\n📊 OVERVIEW:")
    print(f"   Total Duration:    {total_duration:.2f} sec")
    print(f"   Workload Duration: {workload_duration:.2f} sec")
    print(f"   Throughput:        {throughput:.2f} ops/sec")
    
    print(f"\n📝 RESPONSE TIME ({total_results['operations']} operations):")
    print(f"   Success: {total_results['success']}")
    print(f"   Avg:     {perf_stats['avg']:.2f} ms")
    print(f"   P50:     {perf_stats['p50']:.2f} ms")
    print(f"   P95:     {perf_stats['p95']:.2f} ms")
    print(f"   P99:     {perf_stats['p99']:.2f} ms")
    print(f"   Min:     {perf_stats['min']:.2f} ms")
    print(f"   Max:     {perf_stats['max']:.2f} ms")
    
    print(f"\n🗄️  DATA DISTRIBUTION:")
    for shard, count in sorted(shard_dist.items()):
        bar = "█" * (count // 2)
        print(f"   Shard {shard}: {count} rooms {bar}")
    
    print(f"{'='*70}\n")
    
    return {
        "db_name": db_name,
        "db_type": db_type,
        "total_users": len(users),
        "total_rooms": len(rooms),
        "total_duration": total_duration,
        "workload_duration": workload_duration,
        "throughput": throughput,
        "error_rate": error_rate,
        "total_operations": total_results["operations"],
        "success": total_results["success"],
        "perf_stats": perf_stats,
        "shard_distribution": dict(shard_dist),
        "response_times": performance_data[db_type]["response_times"].copy()
    }


def print_comparison(single, multiple):
    """Print side-by-side comparison"""
    print("\n" + "="*70)
    print("📊 PERFORMANCE COMPARISON: Single DB vs Sharded DB")
    print("="*70)
    
    def get_winner(s_val, m_val, lower_is_better=True):
        if lower_is_better:
            return "✅ SHARDED" if m_val < s_val else "❌ SINGLE"
        else:
            return "✅ SHARDED" if m_val > s_val else "❌ SINGLE"
    
    print(f"\n{'Metric':<25} {'Single DB':>15} {'Sharded DB':>15} {'Winner':>15}")
    print("-"*70)
    
    w = get_winner(single['throughput'], multiple['throughput'], False)
    print(f"{'Throughput (ops/sec)':<25} {single['throughput']:>15.2f} {multiple['throughput']:>15.2f} {w:>15}")
    
    w = get_winner(single['perf_stats']['avg'], multiple['perf_stats']['avg'], True)
    print(f"{'Avg Response (ms)':<25} {single['perf_stats']['avg']:>15.2f} {multiple['perf_stats']['avg']:>15.2f} {w:>15}")
    
    w = get_winner(single['perf_stats']['p50'], multiple['perf_stats']['p50'], True)
    print(f"{'P50 Response (ms)':<25} {single['perf_stats']['p50']:>15.2f} {multiple['perf_stats']['p50']:>15.2f} {w:>15}")
    
    w = get_winner(single['perf_stats']['p95'], multiple['perf_stats']['p95'], True)
    print(f"{'P95 Response (ms)':<25} {single['perf_stats']['p95']:>15.2f} {multiple['perf_stats']['p95']:>15.2f} {w:>15}")
    
    w = get_winner(single['perf_stats']['p99'], multiple['perf_stats']['p99'], True)
    print(f"{'P99 Response (ms)':<25} {single['perf_stats']['p99']:>15.2f} {multiple['perf_stats']['p99']:>15.2f} {w:>15}")
    
    w = get_winner(single['perf_stats']['max'], multiple['perf_stats']['max'], True)
    print(f"{'Max Response (ms)':<25} {single['perf_stats']['max']:>15.2f} {multiple['perf_stats']['max']:>15.2f} {w:>15}")
    
    print("="*70)
    
    # Calculate improvement percentages
    avg_improvement = ((single['perf_stats']['avg'] - multiple['perf_stats']['avg']) / single['perf_stats']['avg'] * 100) if single['perf_stats']['avg'] > 0 else 0
    p99_improvement = ((single['perf_stats']['p99'] - multiple['perf_stats']['p99']) / single['perf_stats']['p99'] * 100) if single['perf_stats']['p99'] > 0 else 0
    throughput_improvement = ((multiple['throughput'] - single['throughput']) / single['throughput'] * 100) if single['throughput'] > 0 else 0
    
    print(f"\n🎯 SHARDING PERFORMANCE GAIN:")
    print(f"   Throughput:    {throughput_improvement:+.1f}%")
    print(f"   Avg Response:  {avg_improvement:+.1f}% faster")
    print(f"   P99 Response:  {p99_improvement:+.1f}% faster")
    
    # Determine overall winner
    wins_sharded = 0
    wins_single = 0
    
    if multiple['throughput'] > single['throughput']:
        wins_sharded += 1
    else:
        wins_single += 1
    
    if multiple['perf_stats']['avg'] < single['perf_stats']['avg']:
        wins_sharded += 1
    else:
        wins_single += 1
        
    if multiple['perf_stats']['p99'] < single['perf_stats']['p99']:
        wins_sharded += 1
    else:
        wins_single += 1
    
    print(f"\n🏆 OVERALL RESULT:")
    if wins_sharded > wins_single:
        print(f"   SHARDED DATABASE WINS! ({wins_sharded}-{wins_single})")
        print(f"   Sharding provides better performance under heavy load.")
    elif wins_single > wins_sharded:
        print(f"   Single Database wins ({wins_single}-{wins_sharded})")
    else:
        print(f"   TIE - Both perform similarly")


def main():
    parser = argparse.ArgumentParser(description="Performance Load Test - Database Comparison")
    parser.add_argument("--target", choices=["single", "multiple", "both"], default="both",
                        help="Target database(s) to test")
    parser.add_argument("--users", type=int, default=300, help="Number of concurrent users")
    parser.add_argument("--rooms", type=int, default=100, help="Number of chat rooms")
    parser.add_argument("--messages", type=int, default=20, help="Messages per user")
    parser.add_argument("--workers", type=int, default=50, help="Concurrent worker threads")
    
    args = parser.parse_args()
    
    global TOTAL_USERS, TOTAL_ROOMS, MESSAGES_PER_USER, CONCURRENT_WORKERS
    TOTAL_USERS = args.users
    TOTAL_ROOMS = args.rooms
    MESSAGES_PER_USER = args.messages
    CONCURRENT_WORKERS = args.workers
    
    print("\n" + "="*70)
    print("      PERFORMANCE LOAD TEST - DATABASE SHARDING COMPARISON")
    print("="*70)
    print(f"\nTest Configuration:")
    print(f"  - Users: {TOTAL_USERS}")
    print(f"  - Rooms: {TOTAL_ROOMS}")
    print(f"  - Messages/User: {MESSAGES_PER_USER}")
    print(f"  - Total Operations: {TOTAL_USERS * MESSAGES_PER_USER}")
    print(f"  - Concurrent Workers: {CONCURRENT_WORKERS}")
    
    results = []
    
    if args.target in ["single", "both"]:
        result = run_performance_test(SINGLE_DB_URL, "SINGLE DATABASE", "single")
        if result:
            results.append(result)
    
    if args.target in ["multiple", "both"]:
        result = run_performance_test(MULTIPLE_DB_URL, "SHARDED DATABASE (4 nodes)", "multiple")
        if result:
            results.append(result)
    
    # Print comparison if both tests ran
    if len(results) == 2:
        print_comparison(results[0], results[1])
    
    # Save results to JSON
    if results:
        with open("performance_results.json", "w") as f:
            for r in results:
                r["response_times"] = r["response_times"][:100]  # Truncate for file size
            json.dump(results, f, indent=2)
        print(f"\n✅ Results saved to: performance_results.json")


if __name__ == "__main__":
    main()
