# Dokumentasi Test Suite: Performance Testing untuk Database Sharding

## Daftar Isi

1. [Pendahuluan](#1-pendahuluan)
2. [Struktur Test Suite](#2-struktur-test-suite)
3. [Performance Test](#3-performance-test)
4. [Load Test](#4-load-test)
5. [Visualization Script](#5-visualization-script)
6. [Cara Menjalankan Test](#6-cara-menjalankan-test)
7. [Hasil Test](#7-hasil-test)
8. [Interpretasi Hasil](#8-interpretasi-hasil)

---

## 1. Pendahuluan

### 1.1 Tujuan Testing

Test suite ini dibuat untuk:
- Membandingkan performa **Single Database** vs **Sharded Database**
- Mengukur throughput, latency, dan response time
- Memvalidasi efektivitas strategi database sharding
- Menghasilkan visualisasi data performa

### 1.2 Metodologi Testing

| Aspek | Pendekatan |
|-------|------------|
| **Load Generation** | Virtual users dengan ThreadPoolExecutor |
| **Concurrency** | 50 concurrent workers |
| **Metrics** | Throughput, P50/P95/P99 latency |
| **Operations** | Message send (write-heavy) |
| **Comparison** | Side-by-side single vs sharded |

### 1.3 Prerequisites

```
Python 3.x
requests
matplotlib
numpy
```

**Aplikasi yang harus running:**
- Single Database: `http://localhost:5000`
- Sharded Database: `http://localhost:5001`

---

## 2. Struktur Test Suite

### 2.1 Directory Structure

```
test/
├── performance_test.py       # Heavy load test (300 users)
├── load_test.py             # Basic load test (50 users)
├── visualize_results.py     # Generate graphs from results
├── performance_results.json # Output dari performance_test.py
└── load_test_results.json   # Output dari load_test.py
```

### 2.2 File Descriptions

| File | Purpose | Output |
|------|---------|--------|
| `performance_test.py` | Heavy load test dengan 300 users | `performance_results.json` |
| `load_test.py` | Basic load test dengan 50 users | `load_test_results.json` |
| `visualize_results.py` | Generate comparison graphs | `performance_comparison.png` |

---

## 3. Performance Test

### 3.1 File: `performance_test.py`

**Deskripsi**: Heavy load test untuk membandingkan performa database under stress.

### 3.2 Default Configuration

```python
TOTAL_USERS = 300           # Total virtual users
TOTAL_ROOMS = 100           # Chat rooms to create
MESSAGES_PER_USER = 20      # Messages each user sends
CONCURRENT_WORKERS = 50     # Parallel execution threads

# Total Operations = 300 × 20 = 6,000 messages
```

### 3.3 Test Phases

```
Phase 1: Create Users
    │   - Register 300 users concurrently
    │   - Each user gets unique username
    ▼
Phase 2: Create Rooms
    │   - Create 100 chat rooms
    │   - Distribute across shards (room_id % 4)
    ▼
Phase 3: Assign Users to Rooms
    │   - Assign 300 users to 100 rooms
    │   - Each room gets ~3 users
    ▼
Phase 4: Execute Workload
    │   - Each user sends 20 messages
    │   - 50 concurrent workers
    │   - Track response times
    ▼
Results: Calculate metrics & generate JSON
```

### 3.4 VirtualUser Class

```python
class VirtualUser:
    """Simulates a real user interacting with the chat application"""
    
    def __init__(self, user_id, base_url):
        self.user_id = user_id
        self.username = f"testuser_{user_id}_{random.randint(1000,9999)}"
        self.base_url = base_url
        self.session = requests.Session()  # Persistent session
        self.room_id = None
        self.codename = None
    
    def register(self):
        """Register user via POST /api/register"""
        
    def create_room(self):
        """Create room via POST /api/rooms"""
        
    def join_room_by_codename(self, codename):
        """Join room via POST /api/rooms/join"""
        
    def send_message(self, db_type="single"):
        """
        Send message via POST /api/rooms/{room_id}/messages
        - Tracks response time
        - Thread-safe using lock
        """
```

### 3.5 Metrics Calculated

```python
def calculate_percentiles(times):
    """Calculate latency percentiles"""
    return {
        "p50": sorted_times[int(n * 0.50)],  # Median
        "p95": sorted_times[int(n * 0.95)],  # 95th percentile
        "p99": sorted_times[int(n * 0.99)],  # 99th percentile
        "avg": statistics.mean(times),       # Average
        "min": min(times),                   # Minimum
        "max": max(times)                    # Maximum
    }
```

### 3.6 Command Line Arguments

```bash
python performance_test.py [OPTIONS]

Options:
  --target {single,multiple,both}  Target database(s) [default: both]
  --users INT                      Number of users [default: 300]
  --rooms INT                      Number of rooms [default: 100]
  --messages INT                   Messages per user [default: 20]
  --workers INT                    Concurrent workers [default: 50]
```

### 3.7 Output Format

```json
[
  {
    "db_name": "SINGLE DATABASE",
    "db_type": "single",
    "total_users": 300,
    "total_rooms": 100,
    "total_duration": 256.15,
    "workload_duration": 233.78,
    "throughput": 25.66,
    "total_operations": 6000,
    "success": 6000,
    "perf_stats": {
      "p50": 1898.58,
      "p95": 2299.84,
      "p99": 2674.66,
      "avg": 1925.27,
      "min": 61.40,
      "max": 3835.60
    },
    "shard_distribution": {"0": 25, "1": 25, "2": 25, "3": 25},
    "response_times": [...]
  }
]
```

---

## 4. Load Test

### 4.1 File: `load_test.py`

**Deskripsi**: Basic load test dengan skala lebih kecil, mengukur READ dan WRITE operations.

### 4.2 Default Configuration

```python
TOTAL_USERS = 50            # Total virtual users
USERS_PER_GROUP = 5         # Users per chat group
MESSAGES_PER_USER = 10      # Messages each user sends

# Groups = 50 / 5 = 10 groups
# Total Messages = 50 × 10 = 500 messages
```

### 4.3 Test Phases

```
Phase 1: Create Virtual Users
    │   - Create 50 VirtualUser instances
    ▼
Phase 2: Register Users
    │   - POST /api/register for each user
    │   - If exists, try login instead
    ▼
Phase 3: Create Groups & Join
    │   - Create 10 groups (rooms)
    │   - First user creates, others join via codename
    ▼
Phase 4: WRITE - Send Messages
    │   - Each user sends 10 messages
    │   - Track write_times[]
    ▼
Phase 5: READ - Get Messages
    │   - Each user reads messages from their room
    │   - Track read_times[]
    ▼
Results: Summary & JSON output
```

### 4.4 Performance Tracking

```python
performance_data = {
    "single": {
        "write_times": [],  # Response times for send_message
        "read_times": []    # Response times for get_messages
    },
    "multiple": {
        "write_times": [],
        "read_times": []
    }
}
```

### 4.5 Shard Verification

```python
def verify_sharding(room_ids):
    """Verify message distribution across shards"""
    shard_distribution = {0: 0, 1: 0, 2: 0, 3: 0}
    
    for room_id in room_ids:
        shard = room_id % 4  # MOD algorithm
        shard_distribution[shard] += 1
    
    # Output:
    # Shard 0: 3 rooms ███
    # Shard 1: 2 rooms ██
    # Shard 2: 3 rooms ███
    # Shard 3: 2 rooms ██
```

### 4.6 Command Line Arguments

```bash
python load_test.py [OPTIONS]

Options:
  --target {single,multiple,both}  Target database(s) [default: both]
  --users INT                      Number of users [default: 50]
  --group-size INT                 Users per group [default: 5]
  --messages INT                   Messages per user [default: 10]
```

### 4.7 Output Format

```json
{
  "db_name": "SINGLE DATABASE",
  "db_type": "single",
  "users": 50,
  "groups": 10,
  "messages_sent": 500,
  "messages_failed": 0,
  "total_reads": 50,
  "duration": 45.23,
  "throughput": 11.05,
  "write_times": [...],
  "read_times": [...],
  "avg_write_ms": 125.50,
  "avg_read_ms": 88.30
}
```

---

## 5. Visualization Script

### 5.1 File: `visualize_results.py`

**Deskripsi**: Generate comparison graphs dari hasil performance test.

### 5.2 Input Requirements

- File: `performance_results.json`
- Format: Array dengan 2 objects (single, sharded)

### 5.3 Charts Generated

| Chart | Type | Description |
|-------|------|-------------|
| **Throughput Comparison** | Bar Chart | ops/sec comparison |
| **Response Time Metrics** | Grouped Bar | Avg, P50, P95, P99, Max |
| **Performance Gain** | Horizontal Bar | % improvement per metric |
| **Response Distribution** | Box Plot | Distribution comparison |
| **Response Histogram** | Histogram | Frequency distribution |
| **Summary Table** | Table | All metrics with winner |

### 5.4 Chart Details

**1. Throughput Comparison**
```python
# Bar chart comparing operations per second
databases = ['Single DB', 'Sharded DB\n(4 Nodes)']
throughputs = [single['throughput'], sharded['throughput']]
ax1.bar(databases, throughputs)
# Shows: 25.66 vs 50.67 ops/sec (+97% improvement)
```

**2. Response Time Metrics**
```python
# Grouped bar chart for all latency metrics
metrics = ['Avg', 'P50', 'P95', 'P99', 'Max']
# Compares single vs sharded for each metric
```

**3. Performance Gain**
```python
# Horizontal bar showing % improvement
improvement = ((single - sharded) / single * 100)
# Shows: Avg Response +49.7% faster
```

**4. Response Distribution (Box Plot)**
```python
# Box plot showing response time distribution
# Visualizes median, quartiles, outliers
```

**5. Response Histogram**
```python
# Overlapping histograms
# Shows frequency distribution of response times
```

**6. Summary Table**
```python
table_data = [
    ['Metric', 'Single DB', 'Sharded DB', 'Winner'],
    ['Throughput', '25.66 ops/s', '50.67 ops/s', 'Sharded'],
    ['Avg Response', '1925 ms', '968 ms', 'Sharded'],
    # ...
]
```

### 5.5 Output

```
performance_comparison.png (1600x1200, 150 DPI)
```

### 5.6 Color Scheme

```python
colors = {
    'single': '#e74c3c',   # Red
    'sharded': '#27ae60'   # Green
}
```

---

## 6. Cara Menjalankan Test

### 6.1 Prerequisites Check

```bash
# Pastikan kedua aplikasi running
curl http://localhost:5000/api/user  # Single DB
curl http://localhost:5001/api/user  # Sharded DB
```

### 6.2 Run Performance Test

```bash
cd test/

# Test both databases (default)
python performance_test.py

# Test specific database
python performance_test.py --target single
python performance_test.py --target multiple

# Custom parameters
python performance_test.py --users 500 --rooms 200 --messages 30 --workers 100
```

### 6.3 Run Load Test

```bash
# Basic test
python load_test.py

# Custom parameters
python load_test.py --users 100 --group-size 10 --messages 20
```

### 6.4 Generate Visualization

```bash
# After running performance_test.py
python visualize_results.py

# Output: performance_comparison.png
```

### 6.5 Full Test Sequence

```bash
# 1. Start applications
cd single_database && docker-compose up -d
cd multiple_database && docker-compose up -d

# 2. Wait for health checks
sleep 60

# 3. Run performance test
cd test
python performance_test.py --users 300 --rooms 100 --messages 20

# 4. Generate visualization
python visualize_results.py

# 5. View results
# - performance_results.json
# - performance_comparison.png
```

---

## 7. Hasil Test

### 7.1 Test Configuration Used

| Parameter | Value |
|-----------|-------|
| Total Users | 300 |
| Total Rooms | 100 |
| Messages per User | 20 |
| Total Operations | 6,000 |
| Concurrent Workers | 50 |

### 7.2 Performance Results

| Metric | Single DB | Sharded DB | Improvement |
|--------|-----------|------------|-------------|
| **Throughput** | 25.66 ops/sec | 50.67 ops/sec | **+97.4%** |
| **Avg Response** | 1,925 ms | 968 ms | **+49.7%** |
| **P50 Response** | 1,899 ms | 965 ms | **+49.2%** |
| **P95 Response** | 2,300 ms | 1,154 ms | **+49.8%** |
| **P99 Response** | 2,675 ms | 1,260 ms | **+52.9%** |
| **Max Response** | 3,836 ms | 1,921 ms | **+49.9%** |
| **Total Duration** | 256 sec | 129 sec | **+49.6%** |

### 7.3 Shard Distribution

```
Room Distribution (100 rooms):
┌─────────┬──────────┬─────────────────────────┐
│  Shard  │  Rooms   │  Visual                 │
├─────────┼──────────┼─────────────────────────┤
│ Shard 0 │    25    │ ████████████            │
│ Shard 1 │    25    │ ████████████            │
│ Shard 2 │    25    │ ████████████            │
│ Shard 3 │    25    │ ████████████            │
└─────────┴──────────┴─────────────────────────┘
```

### 7.4 Winner Summary

| Category | Winner |
|----------|--------|
| Throughput | ✅ Sharded DB |
| Avg Response | ✅ Sharded DB |
| P50 Latency | ✅ Sharded DB |
| P95 Latency | ✅ Sharded DB |
| P99 Latency | ✅ Sharded DB |
| Max Response | ✅ Sharded DB |

**Overall: SHARDED DATABASE WINS (6-0)**

---

## 8. Interpretasi Hasil

### 8.1 Mengapa Sharded DB Lebih Cepat?

```
Single Database:
┌────────────────────────────────────────────────────┐
│  50 concurrent requests                             │
│           │                                         │
│           ▼                                         │
│  ┌─────────────────┐                               │
│  │   PostgreSQL    │  ← All requests compete       │
│  │   (1 CPU)       │     for single resource       │
│  └─────────────────┘                               │
│                                                     │
│  Result: 25.66 ops/sec                             │
└────────────────────────────────────────────────────┘

Sharded Database:
┌────────────────────────────────────────────────────┐
│  50 concurrent requests                             │
│           │                                         │
│           ▼                                         │
│  ┌─────────────────────┐                           │
│  │  ShardingSphere     │  ← Routes by room_id % 4  │
│  └─────────┬───────────┘                           │
│      ┌─────┴─────┬─────────┬─────────┐            │
│      ▼           ▼         ▼         ▼            │
│  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐      │
│  │Shard 0│  │Shard 1│  │Shard 2│  │Shard 3│      │
│  └───────┘  └───────┘  └───────┘  └───────┘      │
│                                                     │
│  Result: 50.67 ops/sec (Parallel Processing)       │
└────────────────────────────────────────────────────┘
```

### 8.2 Key Insights

1. **Throughput Doubled (97%)**: Karena 4 database bekerja paralel
2. **Latency Halved (50%)**: Setiap shard hanya handle 25% load
3. **Consistent Performance**: P99 juga improved, bukan hanya average
4. **Linear Scaling**: 4 shards ≈ 2x improvement (tidak perfect karena overhead)

### 8.3 Overhead Analysis

```
Theoretical Maximum: 4x improvement (4 shards)
Actual Result: ~2x improvement

Overhead Sources:
- ShardingSphere routing latency
- Network hops (app → proxy → shard)
- Connection pool management
- Query parsing & rewriting
```

### 8.4 When to Use Each Approach

**Single Database:**
- < 100 concurrent users
- Simple application
- Development/testing
- Budget constraints

**Sharded Database:**
- > 300 concurrent users
- High throughput requirements
- Write-heavy workloads
- Need horizontal scaling

---

## 9. Troubleshooting

### 9.1 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Connection refused | App not running | Start docker-compose |
| Timeout errors | Slow database | Increase timeout in tests |
| High error rate | Resource exhaustion | Reduce concurrent workers |
| Inconsistent results | Cold start | Run warmup test first |

### 9.2 Debug Commands

```bash
# Check if apps are running
curl -s http://localhost:5000 | head
curl -s http://localhost:5001 | head

# Monitor database
docker stats chat_db
docker stats postgres_shard_0 postgres_shard_1 postgres_shard_2 postgres_shard_3

# View logs
docker logs chat_web
docker logs chat_web_sharded
```

### 9.3 Performance Tuning

```python
# Increase timeout for slow networks
timeout=30  # Default: 10

# Adjust concurrency
CONCURRENT_WORKERS = 50  # Lower if getting timeouts

# Add delay between operations
time.sleep(random.uniform(0.005, 0.02))
```

---

## 10. Kesimpulan

### 10.1 Summary

Test suite ini membuktikan bahwa **Database Sharding** memberikan:
- **97% peningkatan throughput**
- **50% pengurangan latency**
- **Konsistensi performa** pada high load

### 10.2 Files Generated

| File | Content |
|------|---------|
| `performance_results.json` | Raw test data |
| `load_test_results.json` | Basic test data |
| `performance_comparison.png` | Visual comparison |

### 10.3 Recommendation

Untuk production dengan karakteristik:
- High concurrency (300+ users)
- Write-heavy workload
- Growth expectations

**→ Gunakan Sharded Database Architecture**

---

*Dokumentasi ini dibuat pada 18 Desember 2025*
*Version: 1.0*
