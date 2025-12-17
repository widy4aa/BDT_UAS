# Dokumentasi Sistem: Single Database (Monolithic Chat Application)

## Daftar Isi

1. [Pendahuluan](#1-pendahuluan)
2. [Arsitektur Sistem](#2-arsitektur-sistem)
3. [Spesifikasi Teknis](#3-spesifikasi-teknis)
4. [Struktur Kode](#4-struktur-kode)
5. [Database Schema](#5-database-schema)
6. [API Reference](#6-api-reference)
7. [Deployment Guide](#7-deployment-guide)
8. [Performance Results](#8-performance-results)
9. [Perbandingan dengan Sharded Database](#9-perbandingan-dengan-sharded-database)

---

## 1. Pendahuluan

### 1.1 Deskripsi Proyek

Sistem ini merupakan aplikasi chat real-time yang menggunakan arsitektur **Single Database (Monolithic)**. Seluruh data disimpan dalam satu instance PostgreSQL, memberikan kesederhanaan dalam pengembangan dan deployment.

### 1.2 Karakteristik Single Database

| Aspek | Karakteristik |
|-------|---------------|
| **Simplicity** | Mudah dikembangkan dan di-maintain |
| **ACID Compliance** | Full transaction support |
| **JOINs** | Efficient cross-table queries |
| **Consistency** | Strong consistency guarantee |
| **Scalability** | Vertical scaling (upgrade hardware) |

### 1.3 Use Case

Aplikasi ini cocok untuk:
- Small to medium scale applications
- Development dan testing environment
- Aplikasi dengan traffic moderate
- Baseline comparison untuk distributed systems

---

## 2. Arsitektur Sistem

### 2.1 Diagram Arsitektur

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER                                   │
│                    (Web Browser - Port 5000)                            │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                                 │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                     Flask Application                            │   │
│   │                      (chat_web:5000)                            │   │
│   │                                                                  │   │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │   │
│   │  │  app.py  │  │ models.py│  │   db.py  │  │    config.py     │ │   │
│   │  │ (Routes) │  │ (Logic)  │  │(Database)│  │ (Configuration)  │ │   │
│   │  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │   │
│   └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  │ Direct Connection
                                  │ (No Middleware)
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATABASE LAYER                                    │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                   PostgreSQL 17 (Single Instance)                │   │
│   │                         (chat_db:5432)                          │   │
│   │                                                                  │   │
│   │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐ │   │
│   │  │   users    │  │   rooms    │  │   room_    │  │  messages  │ │   │
│   │  │            │  │            │  │  members   │  │            │ │   │
│   │  └────────────┘  └────────────┘  └────────────┘  └────────────┘ │   │
│   │                                                                  │   │
│   │  Resource Limits: 1 CPU Core, 100MB RAM                         │   │
│   └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

```
1. User Request (Send Message)
        │
        ▼
2. Flask App receives request (app.py)
        │
        ▼
3. models.py processes business logic
        │
        ▼
4. db.py creates database connection
        │
        ▼
5. Direct query to PostgreSQL
        │
        ▼
6. PostgreSQL executes query
        │
        ▼
7. Result returns to client
```

### 2.3 Network Topology (Docker)

```
┌──────────────────────────────────────────────────────────────┐
│                     Docker Default Network                    │
│                                                              │
│  ┌────────────┐                            ┌────────────┐   │
│  │   chat_    │    Direct PostgreSQL       │   chat_    │   │
│  │    web     │───────Connection──────────▶│    db      │   │
│  │  :5000     │        (Port 5432)         │  (postgres)│   │
│  └────────────┘                            └────────────┘   │
│       │                                                      │
│  Exposed:5000                                               │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 2.4 Perbandingan dengan Multiple Database

| Aspect | Single Database | Multiple Database (Sharded) |
|--------|-----------------|----------------------------|
| **Components** | 2 containers | 6 containers |
| **Middleware** | None | ShardingSphere Proxy |
| **Complexity** | Simple | Complex |
| **JOINs** | Native, efficient | Cross-shard, slower |
| **Scalability** | Vertical | Horizontal |
| **Throughput** | Limited by single node | Distributed |

---

## 3. Spesifikasi Teknis

### 3.1 Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| **Web Framework** | Flask | 3.0.0 |
| **Database** | PostgreSQL | 17 |
| **Database Driver** | psycopg | 3.2.3 |
| **Container** | Docker | Latest |
| **Base Image** | Ubuntu | 22.04 |
| **Language** | Python | 3.x |

### 3.2 Container Specifications

| Container | Image | Ports | Resources |
|-----------|-------|-------|-----------|
| `chat_web` | Custom (Ubuntu 22.04) | 5000:5000 | Unlimited |
| `chat_db` | postgres:17 | - (internal) | **1 CPU, 100MB RAM** |

### 3.3 Database Configuration

```yaml
# docker-compose.yml
db:
  image: postgres:17
  container_name: chat_db
  environment:
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: dio
    POSTGRES_DB: chat_mono
  deploy:
    resources:
      limits:
        cpus: "1.0"
        memory: 100M
```

### 3.4 Resource Constraints (Untuk Testing)

Database sengaja dibatasi resource-nya untuk mensimulasikan kondisi yang fair dalam perbandingan dengan sharded database:

- **CPU**: 1 core (sama dengan per-shard di multiple database)
- **Memory**: 100MB (sama dengan per-shard di multiple database)

---

## 4. Struktur Kode

### 4.1 Directory Structure

```
single_database/
├── app.py                    # Flask application & API routes
├── models.py                 # Business logic & database operations
├── db.py                     # Database connection utilities
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container build instructions
├── docker-compose.yml        # Container orchestration
└── templates/                # HTML templates
    ├── base.html            # Base template
    ├── index.html           # Login/Register page
    ├── dashboard.html       # User dashboard
    └── chat.html            # Chat room interface
```

### 4.2 File: `app.py` - Flask Application

**Deskripsi**: Entry point aplikasi Flask, mendefinisikan semua HTTP routes dan API endpoints.

**Helper Functions**:

```python
def json_response(success, message, data=None, status=200):
    """
    Standardized JSON response format
    Returns: {"success": bool, "message": str, "data": any}
    """
    
def login_required(f):
    """
    Decorator untuk route yang membutuhkan authentication
    Redirect ke index jika belum login
    """
    
def get_current_user():
    """
    Ambil data user yang sedang login dari session
    Returns: user dict atau None
    """
```

**Routes Overview**:

| Route | Method | Auth | Description |
|-------|--------|------|-------------|
| `/` | GET | No | Landing page |
| `/dashboard` | GET | Yes | User dashboard |
| `/room/<room_id>` | GET | Yes | Chat room page |
| `/api/register` | POST | No | Register user |
| `/api/login` | POST | No | Login user |
| `/api/logout` | POST | No | Logout user |
| `/api/rooms` | GET | Yes | Get user's rooms |
| `/api/rooms` | POST | Yes | Create room |
| `/api/rooms/join` | POST | Yes | Join room |
| `/api/rooms/<id>/messages` | GET | Yes | Get messages |
| `/api/rooms/<id>/messages` | POST | Yes | Send message |

### 4.3 File: `models.py` - Business Logic

**Deskripsi**: Berisi semua operasi database dan business logic dalam functional style (tanpa OOP).

**User Functions**:

```python
def create_user(username):
    """
    Create user baru
    - Uses SERIAL for auto-increment ID
    - Returns: user_id
    """
    query = "INSERT INTO users (username) VALUES (%s)"
    return execute_insert(query, (username,))

def get_user_by_id(user_id):
    """Get user by ID - returns dict"""
    
def get_user_by_username(username):
    """Get user by username - returns dict"""
    
def username_exists(username):
    """Check if username exists - returns bool"""
```

**Room Functions**:

```python
def create_room(room_type, creator_id):
    """
    Create room baru dengan codename unik
    
    Steps:
    1. Generate random 8-char codename
    2. Ensure codename is unique
    3. Insert room to database
    4. Add creator as first member
    
    Returns: (room_id, codename)
    """
    codename = generate_codename()
    while get_room_by_codename(codename):
        codename = generate_codename()
    
    query = "INSERT INTO rooms (codename, type) VALUES (%s, %s)"
    room_id = execute_insert(query, (codename, room_type))
    add_room_member(room_id, creator_id)
    
    return room_id, codename

def get_rooms_by_user(user_id):
    """
    Get all rooms for a user
    Uses JOIN untuk efficient query
    """
    query = """
        SELECT r.* FROM rooms r
        JOIN room_members rm ON r.id = rm.room_id
        WHERE rm.user_id = %s
        ORDER BY r.created_at DESC
    """
    return execute_query(query, (user_id,), fetch_all=True)
```

**Message Functions**:

```python
def create_message(room_id, sender_id, content):
    """
    Create message baru
    Simple INSERT - tidak ada sharding logic
    """
    query = "INSERT INTO messages (room_id, sender_id, content) VALUES (%s, %s, %s)"
    return execute_insert(query, (room_id, sender_id, content))

def get_messages_by_room(room_id, limit=50):
    """
    Get messages dengan sender name
    
    Menggunakan JOIN untuk mendapatkan username
    - Efficient dalam single database
    - Tidak perlu batch query seperti sharded version
    """
    query = """
        SELECT m.*, u.username as sender_name
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.room_id = %s
        ORDER BY m.created_at ASC
        LIMIT %s
    """
    return execute_query(query, (room_id, limit), fetch_all=True)
```

### 4.4 File: `db.py` - Database Connection

**Deskripsi**: Database connection utilities menggunakan psycopg3.

```python
def get_connection():
    """
    Get database connection langsung ke PostgreSQL
    - Tidak ada middleware/proxy
    - Direct connection ke chat_db:5432
    """
    return psycopg.connect(
        host=DB_CONFIG['host'],      # db (docker service name)
        port=DB_CONFIG['port'],      # 5432
        dbname=DB_CONFIG['database'], # chat_mono
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """
    Execute query dengan proper error handling
    
    Features:
    - Auto-commit
    - Rollback on error
    - dict_row factory (returns dict instead of tuple)
    """
    
def execute_insert(query, params=None):
    """
    Execute INSERT dan return generated ID
    
    Menggunakan RETURNING clause PostgreSQL
    untuk mendapatkan auto-generated ID
    """
    cursor.execute(query + " RETURNING id", params)
    result = cursor.fetchone()
    return result['id'] if result else None
```

### 4.5 File: `config.py` - Configuration

```python
import os

# Database Configuration dari Environment Variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'chat_mono'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'dio')
}

# Flask Secret Key untuk session
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
```

---

## 5. Database Schema

### 5.1 Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     users       │       │     rooms       │       │   room_members  │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK) SERIAL  │       │ id (PK) SERIAL  │       │ room_id (FK)    │
│ username UNIQUE │       │ codename UNIQUE │◄──────│ user_id (FK)    │
│ created_at      │◄──────│ type            │       │ UNIQUE(r,u)     │
└─────────────────┘   │   │ created_at      │       └─────────────────┘
        │             │   └─────────────────┘               │
        │             │           │                         │
        │             │           │                         │
        └─────────────┴───────────┼─────────────────────────┘
                                  │
                                  ▼
                      ┌─────────────────────┐
                      │      messages       │
                      ├─────────────────────┤
                      │ id (PK) SERIAL      │
                      │ room_id (FK)        │
                      │ sender_id (FK)      │
                      │ content TEXT        │
                      │ created_at          │
                      └─────────────────────┘
```

### 5.2 Table Definitions

**Table: `users`**

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index untuk pencarian username
CREATE INDEX idx_users_username ON users(username);
```

**Table: `rooms`**

```sql
CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    codename VARCHAR(8) UNIQUE NOT NULL,  -- 8-char invite code
    type VARCHAR(50) NOT NULL,            -- 'dm' or 'group'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index untuk pencarian codename
CREATE INDEX idx_rooms_codename ON rooms(codename);
```

**Table: `room_members`**

```sql
CREATE TABLE room_members (
    room_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    UNIQUE (room_id, user_id),
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes untuk JOIN operations
CREATE INDEX idx_room_members_room_id ON room_members(room_id);
CREATE INDEX idx_room_members_user_id ON room_members(user_id);
```

**Table: `messages`**

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    room_id INTEGER NOT NULL,
    sender_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes untuk query performance
CREATE INDEX idx_messages_room_id ON messages(room_id);
CREATE INDEX idx_messages_sender_id ON messages(sender_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
```

### 5.3 Foreign Key Relationships

| From Table | From Column | To Table | To Column | On Delete |
|------------|-------------|----------|-----------|-----------|
| room_members | room_id | rooms | id | CASCADE |
| room_members | user_id | users | id | CASCADE |
| messages | room_id | rooms | id | CASCADE |
| messages | sender_id | users | id | CASCADE |

---

## 6. API Reference

### 6.1 Authentication APIs

#### POST `/api/register`

Register user baru.

**Request:**
```json
{
    "username": "john_doe"
}
```

**Response (Success - 200):**
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

**Response (Error - 400):**
```json
{
    "success": false,
    "message": "Username already exists"
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

**Response (Success - 200):**
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

#### POST `/api/logout`

Logout user dan clear session.

**Response:**
```json
{
    "success": true,
    "message": "Logout successful"
}
```

### 6.2 Room APIs

#### GET `/api/rooms`

Get all rooms untuk current user.

**Response:**
```json
{
    "success": true,
    "message": "Rooms fetched",
    "data": [
        {
            "id": 1,
            "codename": "ABC12DEF",
            "type": "group",
            "created_at": "2025-12-18T10:00:00"
        }
    ]
}
```

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

### 6.3 Message APIs

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

Send message ke room.

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

## 7. Deployment Guide

### 7.1 Prerequisites

- Docker & Docker Compose
- Port 5000 available
- Minimum 512MB RAM

### 7.2 Quick Start

```bash
# 1. Navigate to directory
cd single_database

# 2. Start all containers
docker-compose up -d

# 3. Wait for database to be ready (check health)
docker-compose ps

# 4. Access application
# Open: http://localhost:5000
```

### 7.3 Startup Order

Docker Compose akan start dalam urutan:

1. **chat_db** (PostgreSQL) - Wait until healthy
2. **chat_web** (Flask) - Start after db is healthy

### 7.4 Verify Deployment

```bash
# Check container status
docker-compose ps

# Expected output:
# NAME        STATUS
# chat_db     healthy
# chat_web    running

# Check database logs
docker logs chat_db

# Check app logs
docker logs chat_web
```

### 7.5 Database Initialization

Schema diinisialisasi otomatis saat container pertama kali start:
- File `../database.sql` di-mount ke `/docker-entrypoint-initdb.d/`
- PostgreSQL menjalankan script ini saat inisialisasi

### 7.6 Stopping & Cleanup

```bash
# Stop all containers
docker-compose down

# Stop and remove volumes (reset data)
docker-compose down -v
```

---

## 8. Performance Results

### 8.1 Test Configuration

| Parameter | Value |
|-----------|-------|
| Total Users | 300 |
| Total Rooms | 100 |
| Messages per User | 20 |
| Total Operations | 6,000 |
| Concurrent Workers | 50 |
| Database Resources | 1 CPU, 100MB RAM |

### 8.2 Single Database Performance

| Metric | Value |
|--------|-------|
| **Throughput** | 25.66 ops/sec |
| **Avg Response** | 1,925 ms |
| **P50 Response** | 1,899 ms |
| **P95 Response** | 2,300 ms |
| **P99 Response** | 2,675 ms |
| **Max Response** | 3,836 ms |
| **Total Duration** | 256 sec |

### 8.3 Bottleneck Analysis

```
┌─────────────────────────────────────────────────────────────┐
│                  Single Database Bottleneck                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   50 Concurrent Requests                                     │
│           │                                                  │
│           ▼                                                  │
│   ┌───────────────┐                                         │
│   │   Flask App   │ ← No bottleneck (unlimited resources)   │
│   └───────┬───────┘                                         │
│           │                                                  │
│           ▼                                                  │
│   ┌───────────────┐                                         │
│   │  PostgreSQL   │ ← BOTTLENECK: 1 CPU, 100MB RAM         │
│   │  (Single)     │                                         │
│   │               │   - All queries compete for resources   │
│   │  ████████████ │   - Lock contention on writes          │
│   │  CPU: 100%    │   - I/O wait on disk                   │
│   └───────────────┘                                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 8.4 Why Single Database is Slower

1. **Single Point of Processing**: Semua query diproses oleh 1 CPU core
2. **Lock Contention**: Write operations saling blocking
3. **Limited Memory**: 100MB buffer pool tidak cukup untuk caching
4. **I/O Bottleneck**: Single disk I/O channel
5. **No Parallelism**: Tidak bisa distribute workload

---

## 9. Perbandingan dengan Sharded Database

### 9.1 Performance Comparison

| Metric | Single DB | Sharded DB (4 nodes) | Difference |
|--------|-----------|---------------------|------------|
| **Throughput** | 25.66 ops/sec | 50.67 ops/sec | **-49%** |
| **Avg Response** | 1,925 ms | 968 ms | **+99%** |
| **P50 Response** | 1,899 ms | 965 ms | **+97%** |
| **P95 Response** | 2,300 ms | 1,154 ms | **+99%** |
| **P99 Response** | 2,675 ms | 1,260 ms | **+112%** |
| **Total Time** | 256 sec | 129 sec | **+98%** |

### 9.2 Visual Comparison

```
Throughput (ops/sec):
Single DB   │████████████████████████████░░░░░░░░░░░░░░░░░░░░│ 25.66
Sharded DB  │████████████████████████████████████████████████│ 50.67
                                                              ↑ +97%

Avg Response Time (ms):
Single DB   │████████████████████████████████████████████████│ 1,925
Sharded DB  │████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░│ 968
                                                              ↑ -50%
```

### 9.3 Architectural Comparison

| Aspect | Single Database | Sharded Database |
|--------|-----------------|------------------|
| **Containers** | 2 (web + db) | 6 (web + proxy + 4 shards) |
| **Complexity** | Simple | Complex |
| **JOINs** | Native, efficient | Cross-shard (slower) |
| **Write Throughput** | Limited | Distributed |
| **Consistency** | Strong (ACID) | Eventual (per-shard) |
| **Failure Domain** | Single point of failure | Partial availability |
| **Scaling** | Vertical only | Horizontal |

### 9.4 Code Differences

**Getting Messages - Single DB:**
```python
# Simple JOIN - efficient
def get_messages_by_room(room_id, limit=50):
    query = """
        SELECT m.*, u.username as sender_name
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.room_id = %s
        ORDER BY m.created_at ASC
        LIMIT %s
    """
    return execute_query(query, (room_id, limit))
```

**Getting Messages - Sharded DB:**
```python
# Two queries needed - messages sharded, users not
def get_messages_by_room(room_id, limit=50):
    # Query 1: Get messages from shard (based on room_id)
    messages = execute_query(
        "SELECT * FROM messages WHERE room_id = %s",
        (room_id,)
    )
    
    # Query 2: Batch fetch sender names from ds_0
    sender_ids = set(msg['sender_id'] for msg in messages)
    users = execute_query(
        f"SELECT id, username FROM users WHERE id IN ({placeholders})",
        tuple(sender_ids)
    )
    
    # Merge results
    sender_map = {u['id']: u['username'] for u in users}
    for msg in messages:
        msg['sender_name'] = sender_map.get(msg['sender_id'])
    
    return messages
```

---

## 10. Kapan Menggunakan Single Database?

### ✅ Gunakan Single Database Ketika:

1. **Small to Medium Scale**
   - < 100 concurrent users
   - < 10,000 messages per day
   - < 1GB database size

2. **Development & Testing**
   - Rapid prototyping
   - Local development
   - Unit testing

3. **Simple Requirements**
   - Tidak butuh horizontal scaling
   - Budget terbatas
   - Tim kecil

4. **Strong Consistency Required**
   - Financial transactions
   - Critical data integrity
   - Complex transactions

### ❌ Hindari Single Database Ketika:

1. **High Traffic**
   - > 1,000 concurrent users
   - > 100,000 operations per day

2. **Rapid Data Growth**
   - Millions of messages
   - Terabytes of data

3. **High Availability Required**
   - 99.99% uptime SLA
   - Zero downtime deployments

---

## 11. Kesimpulan

### 11.1 Summary

Single Database architecture memberikan:

| Pro | Con |
|-----|-----|
| ✅ Simple architecture | ❌ Limited scalability |
| ✅ Easy to develop | ❌ Single point of failure |
| ✅ Efficient JOINs | ❌ Lower throughput |
| ✅ Strong consistency | ❌ Higher latency under load |
| ✅ Lower operational cost | ❌ Vertical scaling only |

### 11.2 Performance Summary

- **Throughput**: 25.66 ops/sec (vs 50.67 sharded)
- **Avg Latency**: 1,925 ms (vs 968 ms sharded)
- **Conclusion**: Single database ~50% slower than sharded under heavy load

### 11.3 Recommendation

Untuk aplikasi chat dengan karakteristik **write-heavy** dan **high concurrency**, pertimbangkan untuk migrate ke **sharded architecture** ketika:
- User base > 500 concurrent users
- Message volume > 50,000/day
- Response time requirement < 500ms

---

*Dokumentasi ini dibuat pada 18 Desember 2025*
*Version: 1.0*
