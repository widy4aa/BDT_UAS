# Panduan Menjalankan Project BDT UAS
## Chat Application dengan Database Sharding

---

## 📋 Daftar Isi

1. [Prerequisites](#1-prerequisites)
2. [Struktur Project](#2-struktur-project)
3. [Menjalankan Single Database](#3-menjalankan-single-database)
4. [Menjalankan Multiple Database (Sharded)](#4-menjalankan-multiple-database-sharded)
5. [Menjalankan Performance Test](#5-menjalankan-performance-test)
6. [Generate Visualisasi](#6-generate-visualisasi)
7. [Troubleshooting](#7-troubleshooting)
8. [Membersihkan Environment](#8-membersihkan-environment)

---

## 1. Prerequisites

### Software yang Diperlukan

| Software | Versi | Download |
|----------|-------|----------|
| Docker Desktop | Latest | https://www.docker.com/products/docker-desktop |
| Python | 3.10+ | https://www.python.org/downloads/ |
| Git | Latest | https://git-scm.com/downloads |

### Verifikasi Instalasi

```powershell
# Cek Docker
docker --version
docker-compose --version

# Cek Python
python --version
pip --version
```

### Install Python Dependencies

```powershell
# Masuk ke folder test
cd test

# Install dependencies untuk testing
pip install requests matplotlib
```

---

## 2. Struktur Project

```
BDT_UAS/
├── database.sql              # Schema database
├── kesimpulan.md            # Hasil kesimpulan test
├── PANDUAN_MENJALANKAN.md   # File ini
│
├── single_database/         # Implementasi Single DB
│   ├── docker-compose.yml
│   ├── app.py
│   └── ...
│
├── multiple_database/       # Implementasi Sharded DB
│   ├── docker-compose.yml
│   ├── shardingsphere/
│   └── ...
│
└── test/                    # Test Scripts
    ├── performance_test.py
    ├── load_test.py
    └── visualize_results.py
```

---

## 3. Menjalankan Single Database

### Step 1: Masuk ke Folder

```powershell
cd single_database
```

### Step 2: Build dan Jalankan Container

```powershell
# Build images
docker-compose build

# Jalankan containers (background mode)
docker-compose up -d
```

### Step 3: Verifikasi Container Berjalan

```powershell
# Lihat status containers
docker-compose ps

# Expected output:
# NAME                    STATUS
# single_database-app-1   Up
# single_database-db-1    Up
```

### Step 4: Cek Aplikasi

Buka browser dan akses:
- **URL**: http://localhost:5000

### Step 5: Cek Logs (Optional)

```powershell
# Lihat logs semua containers
docker-compose logs

# Lihat logs aplikasi saja
docker-compose logs app

# Follow logs (real-time)
docker-compose logs -f
```

---

## 4. Menjalankan Multiple Database (Sharded)

### Step 1: Masuk ke Folder

```powershell
cd multiple_database
```

### Step 2: Build dan Jalankan Container

```powershell
# Build images
docker-compose build

# Jalankan containers (background mode)
docker-compose up -d
```

### Step 3: Tunggu ShardingSphere Ready

ShardingSphere membutuhkan waktu ~30-60 detik untuk startup.

```powershell
# Cek logs ShardingSphere
docker-compose logs shardingsphere

# Tunggu sampai muncul "ShardingSphere-Proxy start success"
docker-compose logs -f shardingsphere
```

### Step 4: Verifikasi Semua Container

```powershell
# Lihat status containers
docker-compose ps

# Expected output (6 containers):
# NAME                         STATUS
# multiple_database-app-1      Up
# multiple_database-postgres_0 Up
# multiple_database-postgres_1 Up
# multiple_database-postgres_2 Up
# multiple_database-postgres_3 Up
# multiple_database-shardingsphere Up
```

### Step 5: Cek Aplikasi

Buka browser dan akses:
- **URL**: http://localhost:5001

---

## 5. Menjalankan Performance Test

### Prerequisites

Pastikan **KEDUA** aplikasi sudah berjalan:
- Single Database di port **5000**
- Multiple Database di port **5001**

### Step 1: Masuk ke Folder Test

```powershell
cd test
```

### Step 2: Jalankan Performance Test

```powershell
python performance_test.py
```

### Output yang Diharapkan

```
================================================================================
                    PERFORMANCE TEST - HEAVY LOAD
================================================================================

Test Configuration:
  - Total Users: 300
  - Total Rooms: 100
  - Messages per User: 20
  - Total Operations: 6000
  - Concurrent Workers: 50

================================================================================
                         TESTING: Single Database
                              http://localhost:5000
================================================================================

Setting up test data...
Created 300 users
[####################] 100.0%
...

================================================================================
                    FINAL COMPARISON RESULTS
================================================================================
┌─────────────────────┬─────────────┬─────────────┬────────────────┬──────────┐
│ Metric              │ Single DB   │ Sharded DB  │ Difference     │ Winner   │
├─────────────────────┼─────────────┼─────────────┼────────────────┼──────────┤
│ Throughput          │ 25.66 ops/s │ 50.67 ops/s │ +97.4%         │ Sharded  │
...
```

### Step 3: Hasil Test

Setelah selesai, file `performance_results.json` akan dibuat otomatis.

---

## 6. Generate Visualisasi

### Step 1: Pastikan Performance Test Sudah Selesai

Cek file `performance_results.json` ada di folder `test/`.

```powershell
# Di folder test
dir performance_results.json
```

### Step 2: Jalankan Script Visualisasi

```powershell
python visualize_results.py
```

### Output yang Diharapkan

```
Loading performance results...
Found 6000 operations for Single Database
Found 6000 operations for Sharded Database

Creating performance comparison charts...

Chart saved to: performance_comparison.png

Summary:
- Single Database: 25.66 ops/sec avg, 1925ms avg response
- Sharded Database: 50.67 ops/sec avg, 968ms avg response
- Performance Improvement: 97.4% throughput increase
```

### Step 3: Lihat Hasil

Buka file `test/performance_comparison.png` untuk melihat grafik perbandingan.

---

## 7. Troubleshooting

### 7.1 Port Sudah Digunakan

**Error:**
```
Error starting userland proxy: Bind for 0.0.0.0:5000 failed: port is already allocated
```

**Solusi:**
```powershell
# Cari proses yang menggunakan port
netstat -ano | findstr :5000

# Kill proses berdasarkan PID
taskkill /PID <PID> /F

# Atau stop semua container yang berjalan
docker stop $(docker ps -q)
```

### 7.2 Container Tidak Bisa Start

**Error:**
```
Cannot start container: driver failed programming external connectivity
```

**Solusi:**
```powershell
# Restart Docker Desktop
# Atau jalankan di PowerShell Admin:
Restart-Service docker
```

### 7.3 ShardingSphere Tidak Connect ke Database

**Error:**
```
Cannot connect to database: Connection refused
```

**Solusi:**
```powershell
# Pastikan semua postgres container sudah running
docker-compose ps

# Restart ShardingSphere setelah postgres ready
docker-compose restart shardingsphere

# Tunggu 30-60 detik, lalu cek logs
docker-compose logs shardingsphere
```

### 7.4 Database Tidak Terinisialisasi

**Error:**
```
relation "users" does not exist
```

**Solusi:**
```powershell
# Hapus volume dan recreate
docker-compose down -v
docker-compose up -d
```

### 7.5 Test Gagal - Connection Refused

**Error:**
```
requests.exceptions.ConnectionError: Connection refused
```

**Solusi:**
```powershell
# Pastikan aplikasi sudah running
curl http://localhost:5000
curl http://localhost:5001

# Jika tidak bisa, restart containers
docker-compose restart
```

### 7.6 Out of Memory

**Error:**
```
Container killed due to OOM (Out of Memory)
```

**Solusi:**
1. Buka Docker Desktop → Settings → Resources
2. Increase Memory limit (minimal 4GB)
3. Restart Docker Desktop

### 7.7 Image Build Gagal

**Error:**
```
failed to solve: failed to compute cache key
```

**Solusi:**
```powershell
# Clear Docker cache
docker builder prune -f

# Rebuild tanpa cache
docker-compose build --no-cache
```

---

## 8. Membersihkan Environment

### 8.1 Stop Containers (Data Tetap Ada)

```powershell
# Di folder single_database
cd single_database
docker-compose stop

# Di folder multiple_database
cd multiple_database
docker-compose stop
```

### 8.2 Stop dan Hapus Containers

```powershell
# Hapus containers tapi data tetap ada
docker-compose down

# Hapus containers DAN volumes (data hilang)
docker-compose down -v
```

### 8.3 Hapus Semua Resources Project

```powershell
# Stop dan hapus semua (containers, networks, volumes)
docker-compose down -v --rmi local

# Atau hapus semua sekaligus
docker-compose down -v --rmi all --remove-orphans
```

### 8.4 Membersihkan Docker Secara Menyeluruh

```powershell
# Hapus semua containers yang stopped
docker container prune -f

# Hapus semua images yang tidak digunakan
docker image prune -a -f

# Hapus semua volumes yang tidak digunakan
docker volume prune -f

# Hapus semua networks yang tidak digunakan
docker network prune -f

# NUCLEAR OPTION - Hapus SEMUA Docker resources
docker system prune -a -f --volumes
```

### 8.5 Reset Total

Jika ingin memulai dari awal:

```powershell
# 1. Hapus semua Docker resources project
cd single_database
docker-compose down -v --rmi all

cd ../multiple_database
docker-compose down -v --rmi all

# 2. Hapus file hasil test
cd ../test
Remove-Item performance_results.json -ErrorAction SilentlyContinue
Remove-Item load_test_results.json -ErrorAction SilentlyContinue
Remove-Item performance_comparison.png -ErrorAction SilentlyContinue

# 3. Mulai ulang dari Step 3
```

---

## 9. Quick Start (TL;DR)

### Jalankan Semua dalam 5 Menit

```powershell
# Terminal 1: Single Database
cd single_database
docker-compose up -d

# Terminal 2: Multiple Database
cd multiple_database
docker-compose up -d

# Tunggu 60 detik untuk ShardingSphere ready

# Terminal 3: Run Test
cd test
python performance_test.py
python visualize_results.py

# Buka performance_comparison.png untuk lihat hasil
```

---

## 10. Referensi

- [Docker Documentation](https://docs.docker.com/)
- [Apache ShardingSphere](https://shardingsphere.apache.org/document/current/en/overview/)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

*Dokumentasi dibuat pada 18 Desember 2025*
