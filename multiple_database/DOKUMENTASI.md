# Dokumentasi Sistem: Multiple Database (Sharded Chat Application)

## Daftar Isi

1. [Pendahuluan](#1-pendahuluan)
2. [Arsitektur Sistem](#2-arsitektur-sistem)
3. [Spesifikasi Teknis](#3-spesifikasi-teknis)
4. [Sharding Strategy](#4-sharding-strategy)
5. [Struktur Kode](#5-struktur-kode)
6. [Database Schema](#6-database-schema)
7. [API Reference](#7-api-reference)
8. [Deployment Guide](#8-deployment-guide)
9. [Performance Results](#9-performance-results)

---

## 1. Pendahuluan

### 1.1 Deskripsi Proyek

Sistem ini merupakan aplikasi chat real-time yang menggunakan **Database Sharding** untuk mendistribusikan data ke beberapa node database PostgreSQL. Dengan menggunakan **Apache ShardingSphere Proxy** sebagai middleware, sistem dapat menangani beban tinggi dengan throughput yang lebih baik dibandingkan single database.

### 1.2 Tujuan Sharding

- **Horizontal Scalability**: Menambah kapasitas dengan menambah node database
- **High Performance**: Distribusi beban ke multiple nodes
- **Load Balancing**: Meratakan workload antar database
- **Improved Throughput**: Parallel processing untuk write operations

### 1.3 Use Case

Aplikasi chat dengan karakteristik:
- High concurrency (300+ concurrent users)
- Write-heavy workload (message sending)
- Data growth yang cepat (millions of messages)
- Real-time requirements

---

## 2. Arsitektur Sistem

### 2.1 Diagram Arsitektur

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER                                   │
│                    (Web Browser - Port 5001)                            │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                                 │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                     Flask Application                            │   │
│   │                   (chat_web_sharded:5000)                       │   │
│   │                                                                  │   │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │   │
│   │  │  app.py  │  │ models.py│  │   db.py  │  │    config.py     │ │   │
│   │  │ (Routes) │  │ (Logic)  │  │(Database)│  │ (Configuration)  │ │   │
│   │  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │   │
│   └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      SHARDING PROXY LAYER                               │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │              Apache ShardingSphere Proxy 5.4.1                   │   │
│   │                     (Port 3307)                                  │   │
│   │                                                                  │   │
│   │  ┌─────────────────┐  ┌─────────────────────────────────────┐   │   │
│   │  │  server.yaml    │  │       config-sharding.yaml          │   │   │
│   │  │ (Server Config) │  │ (Sharding Rules & Data Sources)     │   │   │
│   │  └─────────────────┘  └─────────────────────────────────────┘   │   │
│   │                                                                  │   │
│   │  Sharding Algorithm: ds_${room_id % 4}                          │   │
│   └─────────────────────────────────────────────────────────────────┘   │
└────────────────┬──────────────┬──────────────┬──────────────┬───────────┘
                 │              │              │              │
                 ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATABASE LAYER (4 Shards)                        │
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Shard 0    │  │   Shard 1    │  │   Shard 2    │  │   Shard 3    │ │
│  │ (PostgreSQL) │  │ (PostgreSQL) │  │ (PostgreSQL) │  │ (PostgreSQL) │ │
│  │              │  │              │  │              │  │              │ │
│  │  - users ✓   │  │  - messages  │  │  - messages  │  │  - messages  │ │
│  │  - rooms ✓   │  │   (room_id   │  │   (room_id   │  │   (room_id   │ │
│  │  - room_     │  │    % 4 = 1)  │  │    % 4 = 2)  │  │    % 4 = 3)  │ │
│  │    members ✓ │  │              │  │              │  │              │ │
│  │  - messages  │  │              │  │              │  │              │ │
│  │   (room_id   │  │              │  │              │  │              │ │
│  │    % 4 = 0)  │  │              │  │              │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                                         │
│  ✓ = Primary table location (non-sharded tables only in ds_0)          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

```
1. User Request (Send Message)
        │
        ▼
2. Flask App receives request
        │
        ▼
3. models.py creates query
        │
        ▼
4. db.py sends to ShardingSphere (port 3307)
        │
        ▼
5. ShardingSphere parses SQL, extracts room_id
        │
        ▼
6. ShardingSphere calculates: shard = room_id % 4
        │
        ▼
7. Routes query to correct shard (ds_0, ds_1, ds_2, or ds_3)
        │
        ▼
8. PostgreSQL executes query
        │
        ▼
9. Result returns through same path
```

### 2.3 Network Topology

```
┌──────────────────────────────────────────────────────────────┐
│                     Docker Network: chat_network             │
│                                                              │
│  ┌────────────┐    ┌────────────────────┐    ┌────────────┐ │
│  │ chat_web   │───▶│ shardingsphere-    │───▶│ postgres-  │ │
│  │ :5000      │    │ proxy :3307        │    │ shard-0    │ │
│  └────────────┘    │                    │    └────────────┘ │
│       │            │  SQL Routing &     │    ┌────────────┐ │
│       │            │  Load Balancing    │───▶│ postgres-  │ │
│  Exposed:5001      │                    │    │ shard-1    │ │
│                    │                    │    └────────────┘ │
│                    │                    │    ┌────────────┐ │
│                    │                    │───▶│ postgres-  │ │
│                    │                    │    │ shard-2    │ │
│                    │                    │    └────────────┘ │
│                    │                    │    ┌────────────┐ │
│                    │                    │───▶│ postgres-  │ │
│                    └────────────────────┘    │ shard-3    │ │
│                                              └────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. Spesifikasi Teknis

### 3.1 Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| **Web Framework** | Flask | 3.0.0 |
| **Database** | PostgreSQL | 17 |
| **Sharding Proxy** | Apache ShardingSphere | 5.4.1 |
| **Database Driver** | psycopg | 3.2.3 |
| **Container** | Docker | Latest |
| **Base Image** | Ubuntu | 22.04 |
| **Language** | Python | 3.x |

### 3.2 Container Specifications

| Container | Image | Ports | Resources |
|-----------|-------|-------|-----------|
| `chat_web_sharded` | Custom (Ubuntu 22.04) | 5001:5000 | - |
| `sharding_proxy` | apache/shardingsphere-proxy:5.4.1 | 3307:3307 | - |
| `postgres_shard_0` | postgres:17 | - | 1 CPU, 100MB |
| `postgres_shard_1` | postgres:17 | - | 1 CPU, 100MB |
| `postgres_shard_2` | postgres:17 | - | 1 CPU, 100MB |
| `postgres_shard_3` | postgres:17 | - | 1 CPU, 100MB |

### 3.3 Connection Pool Configuration

```yaml
# Per Data Source (ShardingSphere)
connectionTimeoutMilliseconds: 30000
idleTimeoutMilliseconds: 60000
maxLifetimeMilliseconds: 1800000
maxPoolSize: 50
minPoolSize: 1
```

### 3.4 Database Credentials

```yaml
Username: chatuser
Password: chatpass
Databases: chat_shard_0, chat_shard_1, chat_shard_2, chat_shard_3
```

---

## 4. Sharding Strategy

### 4.1 Sharding Overview

| Table | Sharding Strategy | Sharding Key | Location |
|-------|-------------------|--------------|----------|
| `messages` | **Hash-based (MOD)** | `room_id` | ds_0, ds_1, ds_2, ds_3 |
| `users` | **Not Sharded** | - | ds_0 only |
| `rooms` | **Not Sharded** | - | ds_0 only |
| `room_members` | **Not Sharded** | - | ds_0 only |

### 4.2 Mengapa Hanya `messages` yang Di-shard?

1. **Volume Terbesar**: Messages adalah tabel dengan growth rate tertinggi
2. **Write-Heavy**: 90%+ operations adalah INSERT messages
3. **Natural Partitioning**: `room_id` sebagai natural partition key
4. **Query Pattern**: Messages selalu di-query berdasarkan `room_id`
5. **Avoid Complexity**: Sharding semua tabel menambah kompleksitas JOIN

### 4.3 Sharding Algorithm

```
Shard Number = room_id % 4

Example:
- room_id = 100 → 100 % 4 = 0 → ds_0
- room_id = 101 → 101 % 4 = 1 → ds_1
- room_id = 102 → 102 % 4 = 2 → ds_2
- room_id = 103 → 103 % 4 = 3 → ds_3
- room_id = 104 → 104 % 4 = 0 → ds_0 (cycle repeats)
```

### 4.4 ShardingSphere Configuration

```yaml
# config-sharding.yaml
rules:
- !SHARDING
  tables:
    messages:
      actualDataNodes: ds_${0..3}.messages
      databaseStrategy:
        standard:
          shardingColumn: room_id
          shardingAlgorithmName: messages_inline
    users:
      actualDataNodes: ds_0.users
    rooms:
      actualDataNodes: ds_0.rooms
    room_members:
      actualDataNodes: ds_0.room_members

  shardingAlgorithms:
    messages_inline:
      type: INLINE
      props:
        algorithm-expression: ds_${room_id % 4}
```

### 4.5 Data Distribution Visualization

```
Room IDs Distribution:
┌─────────────────────────────────────────────────────────┐
│                   100 Rooms Total                        │
├─────────────┬─────────────┬─────────────┬───────────────┤
│   Shard 0   │   Shard 1   │   Shard 2   │    Shard 3    │
│   (ds_0)    │   (ds_1)    │   (ds_2)    │    (ds_3)     │
├─────────────┼─────────────┼─────────────┼───────────────┤
│ room_id:    │ room_id:    │ room_id:    │  room_id:     │
│ 4,8,12,16.. │ 1,5,9,13..  │ 2,6,10,14.. │  3,7,11,15..  │
│ (% 4 = 0)   │ (% 4 = 1)   │ (% 4 = 2)   │  (% 4 = 3)    │
├─────────────┼─────────────┼─────────────┼───────────────┤
│   ~25%      │    ~25%     │    ~25%     │     ~25%      │
│  messages   │  messages   │  messages   │   messages    │
└─────────────┴─────────────┴─────────────┴───────────────┘
```

### 4.6 Keuntungan Strategi Ini

| Benefit | Description |
|---------|-------------|
| **Load Distribution** | Messages tersebar merata ke 4 shards |
| **Parallel Writes** | 4 database bisa write secara bersamaan |
| **No Hot Spots** | Tidak ada shard yang overloaded |
| **Simple JOINs** | users, rooms, room_members di satu tempat |
| **Predictable Routing** | Deterministic: selalu tahu di shard mana |

---

## 5. Struktur Kode

### 5.1 Directory Structure

```
multiple_database/
├── app.py                    # Flask application & API routes
├── models.py                 # Business logic & database operations
├── db.py                     # Database connection utilities
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container build instructions
├── docker-compose.yml        # Multi-container orchestration
├── init/                     # Database initialization scripts
│   ├── shard_0.sql          # Schema for shard 0 (primary)
│   ├── shard_1.sql          # Schema for shard 1
│   ├── shard_2.sql          # Schema for shard 2
│   └── shard_3.sql          # Schema for shard 3
├── shardingsphere/           # ShardingSphere configuration
│   ├── server.yaml          # Proxy server settings
│   └── config-sharding.yaml # Sharding rules & data sources
└── templates/                # HTML templates
    ├── base.html            # Base template
    ├── index.html           # Login/Register page
    ├── dashboard.html       # User dashboard
    └── chat.html            # Chat room interface
```

### 5.2 File: `app.py` - Flask Application

**Deskripsi**: Entry point aplikasi, mendefinisikan semua HTTP routes dan API endpoints.

**Komponen Utama**:

```python
# Helper Functions
def json_response(success, message, data=None, status=200):
    """Standardized JSON response format"""
    
def login_required(f):
    """Decorator untuk proteksi route yang butuh authentication"""
    
def get_current_user():
    """Ambil user yang sedang login dari session"""
```

**Routes**:

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Landing page |
| `/dashboard` | GET | User dashboard |
| `/room/<room_id>` | GET | Chat room page |
| `/api/register` | POST | Register user baru |
| `/api/login` | POST | Login user |
| `/api/logout` | POST | Logout user |
| `/api/rooms` | GET | Get user's rooms |
| `/api/rooms` | POST | Create new room |
| `/api/rooms/join` | POST | Join room by codename |
| `/api/rooms/<room_id>/messages` | GET | Get room messages |
| `/api/rooms/<room_id>/messages` | POST | Send message |

### 5.3 File: `models.py` - Business Logic

**Deskripsi**: Berisi semua database operations dan business logic.

**User Functions**:

```python
def create_user(username):
    """Create user baru dengan SERIAL ID"""
    query = "INSERT INTO users (username) VALUES (%s)"
    return execute_insert(query, (username,))

def get_user_by_id(user_id):
    """Get user by ID"""
    
def username_exists(username):
    """Check apakah username sudah ada"""
```

**Room Functions**:

```python
def create_room(room_type, creator_id):
    """
    Create room dengan codename unik (8 karakter random)
    Otomatis add creator sebagai member
    """
    codename = generate_codename()
    query = "INSERT INTO rooms (codename, type) VALUES (%s, %s)"
    room_id = execute_insert(query, (codename, room_type))
    add_room_member(room_id, creator_id)
    return room_id, codename

def get_room_by_codename(codename):
    """Get room by invite code"""
```

**Message Functions (SHARDED)**:

```python
def create_message(room_id, sender_id, content):
    """
    Create message - SHARDED by room_id
    ShardingSphere akan route ke shard yang benar
    berdasarkan room_id % 4
    """
    query = "INSERT INTO messages (room_id, sender_id, content) VALUES (%s, %s, %s)"
    return execute_insert(query, (room_id, sender_id, content))

def get_messages_by_room(room_id, limit=50):
    """
    Get messages - OPTIMIZED for sharding
    
    Strategi:
    1. Query messages (routed ke shard berdasarkan room_id)
    2. Batch fetch sender names (single query ke ds_0)
    3. Merge results
    
    Ini lebih efficient daripada JOIN cross-shard
    """
    # Get messages from shard
    messages = execute_query(
        "SELECT * FROM messages WHERE room_id = %s ORDER BY created_at ASC",
        (room_id,), fetch_all=True
    )
    
    # Batch fetch sender names (avoid N+1 query problem)
    sender_ids = list(set(msg['sender_id'] for msg in messages))
    if sender_ids:
        placeholders = ','.join(['%s'] * len(sender_ids))
        users_query = f"SELECT id, username FROM users WHERE id IN ({placeholders})"
        users = execute_query(users_query, tuple(sender_ids), fetch_all=True)
        sender_map = {u['id']: u['username'] for u in users}
    
    # Build result with sender names
    for msg in messages:
        msg['sender_name'] = sender_map.get(msg['sender_id'], 'Unknown')
    
    return messages
```

### 5.4 File: `db.py` - Database Connection

**Deskripsi**: Database connection pool dan query execution utilities.

```python
def get_connection():
    """
    Get database connection ke ShardingSphere Proxy
    Connection ini akan di-route oleh ShardingSphere
    ke shard yang tepat berdasarkan query
    """
    return psycopg.connect(
        host=DB_CONFIG['host'],      # shardingsphere-proxy
        port=DB_CONFIG['port'],      # 3307
        dbname=DB_CONFIG['database'], # sharding_db
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """Execute query dengan proper error handling"""
    
def execute_insert(query, params=None):
    """Execute INSERT dan return generated ID via RETURNING clause"""
```

### 5.5 File: `config.py` - Configuration

```python
# Semua config dari environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'chat_mono'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'dio')
}

SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
```

---

## 6. Database Schema

### 6.1 Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     users       │       │     rooms       │       │   room_members  │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK) BIGINT  │       │ id (PK) BIGINT  │       │ room_id (PK,FK) │
│ username        │       │ codename        │◄──────│ user_id (PK,FK) │
│ created_at      │◄──────│ type            │       └─────────────────┘
└─────────────────┘   │   │ created_at      │               │
        │             │   └─────────────────┘               │
        │             │           │                         │
        │             │           │                         │
        ▼             │           ▼                         │
┌─────────────────────┴───────────────────────────────────────────────┐
│                          messages (SHARDED)                          │
├─────────────────────────────────────────────────────────────────────┤
│ id (PK) BIGINT                                                       │
│ room_id (FK) BIGINT  ─── Sharding Key (room_id % 4)                 │
│ sender_id (FK) BIGINT                                                │
│ content TEXT                                                         │
│ created_at TIMESTAMP                                                 │
└─────────────────────────────────────────────────────────────────────┘
```

### 6.2 Table Definitions

**Table: `users`** (Location: ds_0 only)

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY,          -- Auto-generated by ShardingSphere
    username VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_users_username ON users(username);
```

**Table: `rooms`** (Location: ds_0 only)

```sql
CREATE TABLE rooms (
    id BIGINT PRIMARY KEY,          -- Auto-generated by ShardingSphere
    codename VARCHAR(8) NOT NULL UNIQUE,  -- 8-char invite code
    type VARCHAR(50) NOT NULL,      -- 'dm' or 'group'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_rooms_codename ON rooms(codename);
```

**Table: `room_members`** (Location: ds_0 only)

```sql
CREATE TABLE room_members (
    room_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    PRIMARY KEY (room_id, user_id)
);

-- Indexes
CREATE INDEX idx_room_members_room_id ON room_members(room_id);
CREATE INDEX idx_room_members_user_id ON room_members(user_id);
```

**Table: `messages`** (Location: ds_0, ds_1, ds_2, ds_3 - SHARDED)

```sql
CREATE TABLE messages (
    id BIGINT PRIMARY KEY,
    room_id BIGINT NOT NULL,        -- Sharding Key
    sender_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes (di setiap shard)
CREATE INDEX idx_messages_room_id ON messages(room_id);
CREATE INDEX idx_messages_sender_id ON messages(sender_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_room_created ON messages(room_id, created_at DESC);
```

---

## 7. API Reference

### 7.1 Authentication APIs

#### POST `/api/register`

Register user baru.

**Request:**
```json
{
    "username": "john_doe"
}
```

**Response (Success):**
```json
{
    "success": true,
    "message": "Registration successful",
    "data": {
        "user_id": 1,
        "username": "john_doe"
    }
}
```

#### POST `/api/login`

Login dengan username.

**Request:**
```json
{
    "username": "john_doe"
}
```

**Response (Success):**
```json
{
    "success": true,
    "message": "Login successful",
    "data": {
        "user_id": 1,
        "username": "john_doe"
    }
}
```

### 7.2 Room APIs

#### POST `/api/rooms`

Create room baru.

**Request:**
```json
{
    "type": "group"  // "dm" or "group"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Room created",
    "data": {
        "room_id": 42,
        "codename": "ABC12DEF",
        "type": "group",
        "message": "Share this code with others: ABC12DEF"
    }
}
```

#### POST `/api/rooms/join`

Join room dengan codename.

**Request:**
```json
{
    "codename": "ABC12DEF"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Joined room successfully",
    "data": {
        "room_id": 42,
        "codename": "ABC12DEF"
    }
}
```

### 7.3 Message APIs

#### GET `/api/rooms/{room_id}/messages`

Get messages dalam room.

**Response:**
```json
{
    "success": true,
    "message": "Messages fetched",
    "data": [
        {
            "id": 1,
            "room_id": 42,
            "sender_id": 1,
            "sender_name": "john_doe",
            "content": "Hello everyone!",
            "created_at": "2025-12-18T10:30:00"
        }
    ]
}
```

#### POST `/api/rooms/{room_id}/messages`

Send message ke room. **Operasi ini di-shard berdasarkan room_id**.

**Request:**
```json
{
    "content": "Hello everyone!"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Message sent",
    "data": {
        "id": 123,
        "room_id": 42,
        "sender_id": 1,
        "sender_name": "john_doe",
        "content": "Hello everyone!",
        "created_at": "2025-12-18T10:30:00"
    }
}
```

---

## 8. Deployment Guide

### 8.1 Prerequisites

- Docker & Docker Compose
- Port 5001 available (web app)
- Port 3307 available (ShardingSphere)
- Minimum 2GB RAM

### 8.2 Quick Start

```bash
# 1. Navigate to directory
cd multiple_database

# 2. Start all containers
docker-compose up -d

# 3. Wait for health checks (60-90 seconds)
docker-compose ps

# 4. Access application
# Open: http://localhost:5001
```

### 8.3 Startup Order

Docker Compose akan start dalam urutan ini:

1. **postgres-shard-0, 1, 2, 3** (parallel) - Wait for healthy
2. **shardingsphere-proxy** - Wait for all shards healthy, then start
3. **chat_web** - Wait for ShardingSphere healthy

### 8.4 Verify Deployment

```bash
# Check container status
docker-compose ps

# Expected output:
# NAME                STATUS
# postgres_shard_0    healthy
# postgres_shard_1    healthy
# postgres_shard_2    healthy
# postgres_shard_3    healthy
# sharding_proxy      healthy
# chat_web_sharded    running

# Check ShardingSphere logs
docker logs sharding_proxy

# Check app logs
docker logs chat_web_sharded
```

### 8.5 Stopping & Cleanup

```bash
# Stop all containers
docker-compose down

# Stop and remove volumes (reset data)
docker-compose down -v
```

---

## 9. Performance Results

### 9.1 Test Configuration

| Parameter | Value |
|-----------|-------|
| Total Users | 300 |
| Total Rooms | 100 |
| Messages per User | 20 |
| Total Operations | 6,000 |
| Concurrent Workers | 50 |

### 9.2 Performance Comparison

| Metric | Single DB | Sharded DB (4 nodes) | Improvement |
|--------|-----------|---------------------|-------------|
| **Throughput** | 25.66 ops/sec | 50.67 ops/sec | **+97.4%** |
| **Avg Response** | 1,925 ms | 968 ms | **+49.7% faster** |
| **P50 Response** | 1,899 ms | 965 ms | **+49.2% faster** |
| **P95 Response** | 2,300 ms | 1,154 ms | **+49.8% faster** |
| **P99 Response** | 2,675 ms | 1,260 ms | **+52.9% faster** |
| **Total Time** | 256 sec | 129 sec | **+49.6% faster** |

### 9.3 Key Findings

1. **Throughput Doubled**: Dari 25.66 ke 50.67 ops/sec (+97.4%)
2. **Latency Halved**: Response time berkurang ~50% di semua percentile
3. **Consistent Performance**: P99 latency juga improved, menunjukkan konsistensi
4. **Linear Scaling**: 4 shards memberikan ~2x improvement

### 9.4 Visualization

![Performance Comparison](test/performance_comparison.png)

---

## 10. Troubleshooting

### 10.1 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| ShardingSphere not starting | Shards not healthy | Wait longer, check shard logs |
| Connection refused | Wrong port | Verify DB_PORT=3307 |
| Query timeout | Connection pool exhausted | Increase maxPoolSize |
| Messages not saving | Wrong shard routing | Check room_id in query |

### 10.2 Debug Commands

```bash
# Check ShardingSphere SQL routing
docker logs sharding_proxy 2>&1 | grep "Logic SQL"

# Connect directly to shard
docker exec -it postgres_shard_0 psql -U chatuser -d chat_shard_0

# Check message distribution
SELECT COUNT(*) FROM messages;  # Run on each shard
```

---

## 11. Kesimpulan

Implementasi Database Sharding dengan Apache ShardingSphere memberikan:

1. **2x Throughput Improvement**: Dari ~26 ke ~51 ops/sec
2. **50% Latency Reduction**: Response time lebih cepat
3. **Horizontal Scalability**: Mudah menambah shard baru
4. **Transparent Routing**: Aplikasi tidak perlu tahu tentang sharding
5. **Production Ready**: Menggunakan teknologi proven (ShardingSphere)

Arsitektur ini cocok untuk aplikasi dengan karakteristik:
- Write-heavy workload
- High concurrency
- Data growth yang cepat
- Natural partition key (room_id, user_id, dll)

---

*Dokumentasi ini dibuat pada 18 Desember 2025*
*Version: 1.0*
