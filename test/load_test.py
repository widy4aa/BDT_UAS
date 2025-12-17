"""
Load Test Script for Chat Application
- 50 virtual users
- 10 groups (5 users per group)
- Each user sends 10 messages to their group
"""

import requests
import time
import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
SINGLE_DB_URL = "http://localhost:5000"
MULTIPLE_DB_URL = "http://localhost:5001"

TOTAL_USERS = 50
USERS_PER_GROUP = 5
MESSAGES_PER_USER = 10

# Performance tracking
performance_data = {
    "single": {"write_times": [], "read_times": []},
    "multiple": {"write_times": [], "read_times": []}
}

class VirtualUser:
    def __init__(self, user_id, base_url):
        self.user_id = user_id
        self.username = f"user_{user_id}"
        self.base_url = base_url
        self.session = requests.Session()
        self.room_id = None
        self.codename = None
        self.is_creator = False
    
    def register(self):
        """Register user"""
        try:
            resp = self.session.post(
                f"{self.base_url}/api/register",
                json={"username": self.username},
                timeout=10
            )
            if resp.status_code == 200:
                return True
            elif resp.status_code == 400 and "already exists" in resp.text:
                # User already exists, try login
                return self.login()
            else:
                print(f"[{self.username}] Register failed: {resp.status_code} - {resp.text}")
                return False
        except Exception as e:
            print(f"[{self.username}] Register error: {e}")
            return False
    
    def login(self):
        """Login user"""
        try:
            resp = self.session.post(
                f"{self.base_url}/api/login",
                json={"username": self.username},
                timeout=10
            )
            return resp.status_code == 200
        except Exception as e:
            print(f"[{self.username}] Login error: {e}")
            return False
    
    def create_room(self):
        """Create a group room"""
        try:
            resp = self.session.post(
                f"{self.base_url}/api/rooms",
                json={"type": "group"},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                self.room_id = data["data"]["room_id"]
                self.codename = data["data"].get("codename")
                self.is_creator = True
                return self.room_id, self.codename
            else:
                print(f"[{self.username}] Create room failed: {resp.status_code}")
                return None, None
        except Exception as e:
            print(f"[{self.username}] Create room error: {e}")
            return None, None
    
    def join_room_by_codename(self, codename):
        """Join an existing room by codename"""
        try:
            resp = self.session.post(
                f"{self.base_url}/api/rooms/join",
                json={"codename": codename},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                self.room_id = data["data"]["room_id"]
                self.codename = codename
                return True
            else:
                print(f"[{self.username}] Join room failed: {resp.status_code} - {resp.text}")
                return False
        except Exception as e:
            print(f"[{self.username}] Join room error: {e}")
            return False
    
    def send_message(self, message_num, db_type="single"):
        """Send a message to the room"""
        try:
            content = f"Message {message_num} from {self.username}"
            start_time = time.time()
            resp = self.session.post(
                f"{self.base_url}/api/rooms/{self.room_id}/messages",
                json={"content": content},
                timeout=10
            )
            elapsed = (time.time() - start_time) * 1000  # Convert to ms
            
            if resp.status_code == 200:
                performance_data[db_type]["write_times"].append(elapsed)
                return True
            else:
                print(f"[{self.username}] Send msg failed: {resp.status_code} - {resp.text[:100]}")
                return False
        except Exception as e:
            print(f"[{self.username}] Send message error: {e}")
            return False
    
    def get_messages(self, db_type="single"):
        """Get messages from the room"""
        try:
            start_time = time.time()
            resp = self.session.get(
                f"{self.base_url}/api/rooms/{self.room_id}/messages",
                timeout=10
            )
            elapsed = (time.time() - start_time) * 1000  # Convert to ms
            
            if resp.status_code == 200:
                performance_data[db_type]["read_times"].append(elapsed)
                return resp.json().get("data", [])
            return []
        except Exception as e:
            print(f"[{self.username}] Get messages error: {e}")
            return []


def run_load_test(base_url, db_name, db_type="single"):
    """Run the load test"""
    print(f"\n{'='*60}")
    print(f"LOAD TEST: {db_name}")
    print(f"URL: {base_url}")
    print(f"Users: {TOTAL_USERS}, Groups: {TOTAL_USERS // USERS_PER_GROUP}, Messages/User: {MESSAGES_PER_USER}")
    print(f"{'='*60}\n")
    
    start_time = time.time()
    
    # Create all virtual users
    print("[1/5] Creating virtual users...")
    users = [VirtualUser(i+1, base_url) for i in range(TOTAL_USERS)]
    
    # Register all users
    print("[2/5] Registering users...")
    register_success = 0
    for user in users:
        if user.register():
            register_success += 1
    print(f"      Registered: {register_success}/{TOTAL_USERS}")
    
    if register_success < TOTAL_USERS:
        print("      Warning: Some users failed to register")
    
    # Create groups (5 users per group)
    print("[3/5] Creating groups and joining...")
    num_groups = TOTAL_USERS // USERS_PER_GROUP
    groups = []
    
    for g in range(num_groups):
        group_users = users[g * USERS_PER_GROUP : (g + 1) * USERS_PER_GROUP]
        
        # First user creates the room
        creator = group_users[0]
        room_id, codename = creator.create_room()
        
        if room_id and codename:
            groups.append({
                "room_id": room_id,
                "codename": codename,
                "users": group_users,
                "creator": creator
            })
            
            # Other users join the room using codename
            join_success = 1  # Creator is already joined
            for user in group_users[1:]:
                if user.join_room_by_codename(codename):
                    join_success += 1
            
            print(f"      Group {g+1}: Room {room_id} ({codename}) - {join_success}/{len(group_users)} joined")
        else:
            print(f"      Group {g+1}: FAILED to create room")
    
    # Send messages (WRITE operations)
    print(f"[4/5] WRITE: Sending messages ({MESSAGES_PER_USER} per user)...")
    total_messages = 0
    failed_messages = 0
    
    for group in groups:
        for user in group["users"]:
            for msg_num in range(1, MESSAGES_PER_USER + 1):
                if user.send_message(msg_num, db_type):
                    total_messages += 1
                else:
                    failed_messages += 1
        
        # Progress indicator
        group_idx = groups.index(group) + 1
        print(f"      Group {group_idx}/{len(groups)} complete")
    
    # Read messages (READ operations)
    print(f"[5/5] READ: Getting messages from all groups...")
    total_reads = 0
    for group in groups:
        for user in group["users"]:
            messages = user.get_messages(db_type)
            total_reads += 1
        group_idx = groups.index(group) + 1
        print(f"      Group {group_idx}/{len(groups)} read complete")
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Calculate stats
    write_times = performance_data[db_type]["write_times"]
    read_times = performance_data[db_type]["read_times"]
    
    avg_write = sum(write_times) / len(write_times) if write_times else 0
    avg_read = sum(read_times) / len(read_times) if read_times else 0
    min_write = min(write_times) if write_times else 0
    max_write = max(write_times) if write_times else 0
    min_read = min(read_times) if read_times else 0
    max_read = max(read_times) if read_times else 0
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY: {db_name}")
    print(f"{'='*60}")
    print(f"Total Users:     {TOTAL_USERS}")
    print(f"Total Groups:    {len(groups)}")
    print(f"Messages Sent:   {total_messages}")
    print(f"Messages Failed: {failed_messages}")
    print(f"Total Reads:     {total_reads}")
    print(f"Duration:        {duration:.2f} seconds")
    print(f"Throughput:      {total_messages/duration:.2f} msg/sec")
    print(f"\nWRITE Performance (ms):")
    print(f"  Avg: {avg_write:.2f}  Min: {min_write:.2f}  Max: {max_write:.2f}")
    print(f"READ Performance (ms):")
    print(f"  Avg: {avg_read:.2f}  Min: {min_read:.2f}  Max: {max_read:.2f}")
    print(f"{'='*60}\n")
    
    return {
        "db_name": db_name,
        "db_type": db_type,
        "users": TOTAL_USERS,
        "groups": len(groups),
        "messages_sent": total_messages,
        "messages_failed": failed_messages,
        "total_reads": total_reads,
        "duration": duration,
        "throughput": total_messages/duration if duration > 0 else 0,
        "group_room_ids": [g["room_id"] for g in groups],
        "write_times": write_times.copy(),
        "read_times": read_times.copy(),
        "avg_write_ms": avg_write,
        "avg_read_ms": avg_read,
        "min_write_ms": min_write,
        "max_write_ms": max_write,
        "min_read_ms": min_read,
        "max_read_ms": max_read
    }


def verify_sharding(room_ids):
    """Verify message distribution across shards"""
    print("\n" + "="*60)
    print("VERIFYING SHARD DISTRIBUTION")
    print("="*60)
    
    shard_distribution = {0: 0, 1: 0, 2: 0, 3: 0}
    
    for room_id in room_ids:
        shard = room_id % 4
        shard_distribution[shard] += 1
    
    print(f"\nRoom distribution by shard:")
    for shard, count in shard_distribution.items():
        bar = "█" * count
        print(f"  Shard {shard}: {count} rooms {bar}")
    
    return shard_distribution


def main():
    parser = argparse.ArgumentParser(description="Load test for chat application")
    parser.add_argument("--target", choices=["single", "multiple", "both"], 
                        default="both", help="Target database(s)")
    parser.add_argument("--users", type=int, default=50, help="Number of users")
    parser.add_argument("--group-size", type=int, default=5, help="Users per group")
    parser.add_argument("--messages", type=int, default=10, help="Messages per user")
    
    args = parser.parse_args()
    
    global TOTAL_USERS, USERS_PER_GROUP, MESSAGES_PER_USER
    TOTAL_USERS = args.users
    USERS_PER_GROUP = args.group_size
    MESSAGES_PER_USER = args.messages
    
    results = []
    
    if args.target in ["single", "both"]:
        # Reset performance data for single
        performance_data["single"] = {"write_times": [], "read_times": []}
        result = run_load_test(SINGLE_DB_URL, "SINGLE DATABASE", "single")
        results.append(result)
    
    if args.target in ["multiple", "both"]:
        # Reset performance data for multiple
        performance_data["multiple"] = {"write_times": [], "read_times": []}
        result = run_load_test(MULTIPLE_DB_URL, "MULTIPLE DATABASE (Sharded)", "multiple")
        results.append(result)
        
        # Verify sharding distribution
        verify_sharding(result["group_room_ids"])
    
    # Final comparison
    if len(results) == 2:
        print("\n" + "="*60)
        print("COMPARISON: Single vs Multiple Database")
        print("="*60)
        print(f"{'Metric':<20} {'Single':>15} {'Multiple':>15}")
        print("-"*50)
        print(f"{'Messages Sent':<20} {results[0]['messages_sent']:>15} {results[1]['messages_sent']:>15}")
        print(f"{'Total Reads':<20} {results[0]['total_reads']:>15} {results[1]['total_reads']:>15}")
        print(f"{'Duration (sec)':<20} {results[0]['duration']:>15.2f} {results[1]['duration']:>15.2f}")
        print(f"{'Throughput (msg/s)':<20} {results[0]['throughput']:>15.2f} {results[1]['throughput']:>15.2f}")
        print(f"{'Avg Write (ms)':<20} {results[0]['avg_write_ms']:>15.2f} {results[1]['avg_write_ms']:>15.2f}")
        print(f"{'Avg Read (ms)':<20} {results[0]['avg_read_ms']:>15.2f} {results[1]['avg_read_ms']:>15.2f}")
        print("="*60)
    
    # Save results to JSON for visualization
    if results:
        with open("load_test_results.json", "w") as f:
            # Convert to serializable format
            serializable_results = []
            for r in results:
                sr = r.copy()
                sr["group_room_ids"] = [str(rid) for rid in sr["group_room_ids"]]
                serializable_results.append(sr)
            json.dump(serializable_results, f, indent=2)
        print(f"\n✅ Results saved to: load_test_results.json")


if __name__ == "__main__":
    main()