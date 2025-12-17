# LAPORAN FINAL PROJECT
## MATA KULIAH BASIS DATA TERDISTRIBUSI

---

**"Implementasi Database Sharding pada Sistem Aplikasi Chat Menggunakan Apache ShardingSphere"**

Disusun Oleh :  
Kelompok 7

- Widya Fitriadi N.  
  232410102043  
- Thoriq Firdausi  
  232410102043  
- Fahriz Septian R.  
  232410102084

---

**PROGRAM STUDI TEKNOLOGI INFORMASI**  
**FAKULTAS ILMU KOMPUTER**  
**UNIVERSITAS JEMBER**  
2025

---

## DAFTAR ISI

- DAFTAR ISI	2  
- BAB 1 PENDAHULUAN	3  
  - 1.1 Latar Belakang	3  
  - 1.2 Tujuan	4  
  - 1.3 Batasan Masalah	5  
- BAB 2 DASAR TEORI	6  
  - 2.1 Konsep Dasar Sistem Terdistribusi	6  
    - A. Definisi dan Karakteristik Sistem Terdistribusi	6  
    - B. Teorema CAP	7  
  - 2.2 Basis Data Terdistribusi	8  
    - A. Arsitektur Basis Data Terdistribusi	8  
    - B. Fragmentasi Data	9  
    - C. Replikasi Data	10  
  - 2.3 Landasan Teknologi	11  
    - A. Sistem Manajemen Basis Data yang Digunakan (MySQL, PostgreSQL)	11  
    - B. Tools dan Fitur Terdistribusi	12  
- BAB 3 RANCANGAN	14  
- BAB 4 IMPLEMENTASI	16  
- PENUTUP	16  
- DAFTAR PUSTAKA	17

---

# BAB 1 PENDAHULUAN

## Latar Belakang

Perkembangan teknologi internet dan penetrasi smartphone telah mendorong pertumbuhan eksponensial aplikasi chat di seluruh dunia. Aplikasi seperti WhatsApp, WeChat, dan Telegram kini memiliki basis pengguna mencapai miliaran orang. Komunikasi melalui aplikasi chat ini melibatkan pertukaran pesan teks, suara, gambar, dan video secara real-time antar pengguna. Volume data yang sangat besar dan terus meningkat (termasuk riwayat pesan dan metadata pengguna) menimbulkan tantangan skalabilitas yang signifikan. Setiap platform chat harus melayani ribuan bahkan puluhan ribu operasi simultan per detik, seiring jumlah pengguna yang terus tumbuh. Kondisi ini menunjukkan bahwa arsitektur basis data konvensional berbasis server tunggal cenderung menghadapi batasan kinerja dan kapasitas penyimpanan. Memang, dokumentasi resmi Apache ShardingSphere mencatat bahwa “seiring skala data terus bertambah, basis data terdistribusi telah menjadi tren” dalam sistem modern [3], yang mencerminkan kebutuhan basis data terdistribusi untuk menangani beban kerja aplikasi chat skala besar.

Untuk mengatasi masalah tersebut, arsitektur basis data terdistribusi menjadi krusial. Basis data terdistribusi memungkinkan penyimpanan dan pemrosesan data dibagi di antara beberapa server atau node, sehingga kapasitas dan throughput sistem dapat ditingkatkan secara horizontal. Seperti dijelaskan Aswal (2020), aplikasi modern memerlukan sistem basis data terdistribusi agar dapat mengelola jumlah data yang sangat besar secara real time sambil menjaga skalabilitas dan kinerja sistem [1]. Salah satu teknik kunci dalam basis data terdistribusi adalah sharding, yaitu partisi data secara horizontal ke dalam beberapa potongan (shard). Setiap shard menyimpan subset data tertentu (misalnya berdasarkan rentang nilai kunci tertentu atau algoritma hashing) dan dapat beroperasi secara independen [2]. Dengan cara ini, beban kerja basis data dapat disebar paralel ke beberapa node, mengurangi bottleneck pada satu server. Pendekatan sharding terbukti esensial dalam mencapai skalabilitas dan kinerja yang dibutuhkan oleh aplikasi yang melayani jutaan pengguna [2].

Dalam implementasi sharding, Apache ShardingSphere dipilih sebagai solusi middleware basis data terdistribusi untuk proyek ini. Apache ShardingSphere adalah proyek open-source di bawah naungan Apache Software Foundation yang menyediakan mekanisme sharding data, elastisitas skala, dan transaksi terdistribusi di atas basis data SQL tradisional [3]. Dokumentasi resmi ShardingSphere menyebutkan bahwa komponennya menyediakan fungsi data scale-out (ekspansi horizontal), transaksi terdistribusi, dan pengelolaan data terdistribusi secara transparan [3]. Dengan ShardingSphere, aplikasi dapat menggunakan basis data baku (misalnya MySQL atau PostgreSQL) dan secara otomatis membagi data ke dalam beberapa node tanpa perubahan besar pada kode aplikasi. Keunggulan ShardingSphere meliputi kompatibilitas SQL yang luas, dukungan transaksi terdistribusi antar-shard, serta kemampuan menambah node database secara dinamis (scale-out) untuk menjaga kinerja saat beban meningkat [3].

Berdasarkan latar belakang di atas, tujuan umum proyek ini adalah merancang dan mengimplementasikan arsitektur basis data terdistribusi berbasis sharding pada sistem aplikasi chat menggunakan Apache ShardingSphere. Proyek ini berfokus pada peningkatan kemampuan skalabilitas dan ketersediaan sistem basis data chat seiring pertumbuhan pengguna. Secara khusus, dilakukan konfigurasi skema sharding (misalnya berdasarkan ID pengguna atau ID pesan) sehingga data pesan dapat dipecah ke beberapa shard. Dengan demikian, diharapkan sistem dapat menangani lonjakan lalu lintas pesan real-time dalam jumlah besar tanpa menurunkan waktu respons, sekaligus menjaga konsistensi data melalui dukungan transaksi terdistribusi [3]. Melalui implementasi ini, performa aplikasi chat diharapkan meningkat dengan kemampuan menambah kapasitas penyimpanan dan pemrosesan data secara elastis sesuai kebutuhan.

## Tujuan

Tujuan dari pembuatan proyek akhir ini adalah:

- Menerapkan database sharding pada sistem aplikasi chat menggunakan Apache ShardingSphere.
- Membagi data pesan secara horizontal ke beberapa server database agar lebih terdistribusi dan efisien.
- Mengukur dan menganalisis dampak sharding terhadap kinerja dan skalabilitas sistem aplikasi chat.

## Batasan Masalah

Batasan masalah dari proyek kami, antara lain:

- Proyek ini hanya membahas penerapan database sharding menggunakan Apache ShardingSphere, tanpa membahas teknik basis data terdistribusi lainnya seperti replikasi atau replikasi silang antar shard.
- Sistem aplikasi chat yang dikembangkan difokuskan pada pengiriman dan penyimpanan pesan teks, tanpa mencakup fitur media (gambar/audio) atau enkripsi end-to-end.
- Pengujian performa hanya dilakukan pada lingkungan simulasi berskala terbatas, tidak mencerminkan kondisi produksi dengan ribuan pengguna secara simultan.

---

# BAB 2 DASAR TEORI

## Konsep Dasar Sistem Terdistribusi

Sistem terdistribusi adalah suatu kesatuan sistem komputer yang komponennya tersebar di beberapa lokasi jaringan dan saling berkomunikasi melalui mekanisme pesan. Setiap node dalam sistem terdistribusi menjalankan proses-proses independen yang berkolaborasi untuk menyelesaikan tugas bersama. Dengan kata lain, pengguna atau aplikasi hanya melihat satu sistem utuh meski data dan prosesnya tersebar. Sistem terdistribusi dirancang untuk memberikan scalability (kemampuan bertumbuh) dengan menambah node baru, mengatasi batasan kapasitas satu mesin saja. Selanjutnya, sistem ini bersifat konkurensi, artinya banyak proses dapat berjalan bersamaan tanpa kesadaran waktu global (tidak ada clock global).

Karakteristik penting lainnya meliputi ketersediaan tinggi (availability) dan toleransi kesalahan (fault tolerance): jika satu node gagal, sistem masih dapat terus beroperasi dengan node lain yang tersisa. Heterogenitas komponen juga lazim dijumpai, hardware, OS, atau middleware antar-node bisa berbeda, tetapi sistem tetap berfungsi sebagai satu kesatuan. Ciri khas lain adalah replikasi data dan layanan sering di duplicate pada beberapa node untuk meningkatkan keandalan dan kinerja. Akhirnya, sistem terdistribusi berusaha menampilkan transparansi kepada pengguna: detail lokasi fisik data disembunyikan (misalnya pengguna tidak perlu tahu di server mana data tersimpan).

### Definisi dan Karakteristik Sistem Terdistribusi

Sistem terdistribusi didefinisikan sebagai kumpulan komputer otonom yang dihubungkan oleh jaringan dan berinteraksi melalui pertukaran pesan. Setiap node memiliki memori lokal dan menjalankan proses secara mandiri, namun secara kolektif tujuan utamanya adalah menyelesaikan sebuah tugas bersama. Karakteristik utama yang membedakan sistem terdistribusi adalah sebagai berikut:

- **Skalabilitas**: Sistem dapat diperluas dengan menambah node baru tanpa mengubah rancangan aplikasi. Dengan menambahkan mesin, beban kerja dapat dibagi, sehingga throughput meningkat secara linear.
- **Konkurensi**: Banyak proses di berbagai node dapat berjalan simultan. Tidak adanya global clock mengakibatkan pengerjaan asinkron; tugas terpecah dan dikerjakan paralel oleh beberapa node.
- **Ketersediaan & Toleransi Kesalahan**: Apabila salah satu node atau jalur komunikasi gagal, node-node lain tetap dapat melayani permintaan. Sistem terdistribusi umumnya dirancang fault-tolerant, sehingga satu kegagalan tidak membuat seluruh sistem mati.
- **Heterogenitas**: Komponen dalam sistem bisa bermacam-macam platform (hardware/OS/middleware berbeda), namun tetap terintegrasi lewat standar komunikasi.
- **Replikasi**: Data dan layanan sering direplikasi atau digandakan di banyak node untuk meningkatkan kecepatan akses dan keandalan.
- **Transparansi**: Sistem menyembunyikan kompleksitas distribusi dari pengguna.

### Teorema CAP

Teorema CAP menyatakan bahwa dalam sistem terdistribusi modern hanya dua dari tiga sifat berikut yang dapat dipenuhi secara bersamaan: Konsistensi (Consistency), Ketersediaan (Availability), dan Toleransi Partisi (Partition Tolerance) [6].

**Tabel 2.1 Komponen Teorema CAP**

| Komponen | Deskripsi |
|----------|-----------|
| **Consistency (C)** | Setiap pembaruan data langsung terlihat pada semua node. Semua klien membaca data yang sama pada waktu yang sama. |
| **Availability (A)** | Setiap permintaan baca atau tulis dijawab sukses oleh node dalam sistem tanpa pengecualian. |
| **Partition Tolerance (P)** | Sistem tetap terus berjalan walau terjadi pemutusan atau gangguan komunikasi antar node. |

**Tabel 2.2 Kombinasi Teorema CAP**

| Kombinasi | Karakteristik | Contoh Sistem |
|-----------|---------------|---------------|
| CP | Konsisten dan tahan partisi, mengorbankan ketersediaan | MongoDB, HBase |
| AP | Tersedia dan tahan partisi, mengorbankan konsistensi | Cassandra, DynamoDB |
| CA | Konsisten dan tersedia, tidak tahan partisi | RDBMS Tradisional |

Teorema CAP mengatakan kita hanya bisa memilih maksimal dua sifat tersebut saat merancang sistem terdistribusi. Pada proyek ini, arsitektur sharding dengan Apache ShardingSphere cenderung mengadopsi model CP dimana konsistensi data dijaga melalui mekanisme routing yang deterministik.

## Basis Data Terdistribusi

Basis data terdistribusi adalah basis data dimana data disimpan pada beberapa lokasi fisik (site) yang berbeda dan setiap lokasi diatur oleh DBMS sendiri.

### Arsitektur Basis Data Terdistribusi

**Tabel 2.3 Jenis Arsitektur Basis Data Terdistribusi**

| Arsitektur | Deskripsi | Kelebihan | Kekurangan |
|------------|-----------|-----------|------------|
| **Client-Server** | Fungsi DBMS terpusat di server, klien sebagai antarmuka | Sederhana, mudah dikelola | Satu titik kegagalan |
| **Peer-to-Peer** | Banyak server bekerja sama setara | Tidak ada single point of failure | Kompleksitas tinggi |
| **Middleware** | Layer tambahan mengelola distribusi query | Transparan bagi aplikasi | Overhead middleware |

Pada proyek ini digunakan arsitektur **Middleware** dengan Apache ShardingSphere Proxy sebagai komponen yang mengelola routing query ke shard yang sesuai.

### Fragmentasi Data

**Tabel 2.4 Jenis Fragmentasi Data**

| Jenis Fragmentasi | Deskripsi | Contoh Penggunaan |
|-------------------|-----------|-------------------|
| **Horizontal** | Membagi tabel berdasarkan baris | Data pesan dibagi berdasarkan room_id |
| **Vertikal** | Membagi tabel berdasarkan kolom | Memisahkan kolom yang jarang diakses |
| **Campuran** | Kombinasi horizontal dan vertikal | Sistem kompleks dengan berbagai pola akses |

### Replikasi Data

Replikasi data adalah proses menyalin dan menyimpan salinan data yang sama di beberapa lokasi terpisah. Replikasi bertujuan untuk meningkatkan ketersediaan dan keandalan data [7].

## Landasan Teknologi

### Sistem Manajemen Basis Data yang Digunakan (PostgreSQL)

PostgreSQL merupakan sistem manajemen basis data relasional (RDBMS) open-source yang dipilih sebagai penyimpanan data pada proyek ini. PostgreSQL dikenal memiliki fitur lengkap, keandalan tinggi, dan performa yang baik untuk menangani beban kerja transaksional. PostgreSQL mendukung standar SQL secara komprehensif dan menyediakan fitur-fitur lanjutan seperti indexing, stored procedure, dan trigger yang berguna untuk optimasi query. Dalam konteks basis data terdistribusi, PostgreSQL dapat diintegrasikan dengan middleware seperti Apache ShardingSphere untuk mendukung arsitektur sharding. Setiap shard dalam sistem dapat menjalankan instance PostgreSQL independen yang menangani subset data tertentu, sementara middleware mengelola routing query secara transparan ke shard yang tepat.

### Apache ShardingSphere

Apache ShardingSphere merupakan ekosistem open-source yang menyediakan solusi basis data terdistribusi di atas RDBMS tradisional seperti PostgreSQL dan MySQL [3]. ShardingSphere terdiri dari beberapa komponen, salah satunya adalah ShardingSphere-Proxy yang digunakan pada proyek ini. ShardingSphere-Proxy bertindak sebagai database proxy yang menerima koneksi dari aplikasi dan melakukan routing query ke shard yang sesuai berdasarkan konfigurasi sharding rules [8]. Keunggulan ShardingSphere meliputi transparansi sharding (aplikasi tidak perlu mengetahui detail distribusi data), dukungan berbagai algoritma sharding (range, hash, modulo), dan kemampuan menangani transaksi terdistribusi. Konfigurasi ShardingSphere dilakukan melalui file YAML yang mendefinisikan data sources, sharding rules, dan algoritma yang digunakan [3].

### Konsep Sharding

Sharding adalah teknik pemartisian horizontal yang membagi satu basis data besar menjadi beberapa bagian (shard) yang lebih kecil dan menyimpannya pada node database yang berbeda [2]. Setiap shard memiliki struktur skema yang identik namun menyimpan subset data yang berbeda berdasarkan nilai sharding key. Sharding key merupakan kolom yang digunakan untuk menentukan distribusi data ke shard tertentu. Terdapat beberapa strategi sharding yang umum digunakan, antara lain range-based sharding yang membagi data berdasarkan rentang nilai, hash-based sharding yang menggunakan fungsi hash untuk distribusi data, dan modulo-based sharding yang menggunakan operasi modulo untuk menentukan shard tujuan. Pada proyek ini, diterapkan modulo-based sharding dengan ekspresi room_id % 4 untuk mendistribusikan data pesan ke empat shard PostgreSQL secara merata.

---

# BAB 3 RANCANGAN

## Analisis kebutuhan fungsional dan non-fungsional

Analisis kebutuhan merupakan tahap awal yang penting dalam perancangan sistem aplikasi chat dengan arsitektur basis data terdistribusi. Pada tahap ini dilakukan identifikasi terhadap kebutuhan fungsional yang menggambarkan fitur dan layanan yang harus disediakan oleh sistem, serta kebutuhan non-fungsional yang menentukan kualitas dan batasan operasional sistem. Analisis ini menjadi landasan dalam menentukan arsitektur sharding yang tepat menggunakan Apache ShardingSphere pada sistem aplikasi chat yang dikembangkan.

### Kebutuhan Fungsional

**Tabel 3.1 Kebutuhan Fungsional Sistem**

| Kode | Kebutuhan | Deskripsi |
|------|-----------|----------|
| F-01 | Registrasi | Pengguna dapat mendaftarkan akun baru dengan username unik |
| F-02 | Login | Pengguna dapat masuk ke sistem menggunakan username |
| F-03 | Buat Room | Pengguna dapat membuat room chat baru (DM/Group) |
| F-04 | Join Room | Pengguna dapat bergabung ke room menggunakan codename |
| F-05 | Leave Room | Pengguna dapat meninggalkan room |
| F-06 | Kirim Pesan | Pengguna dapat mengirim pesan teks ke room |
| F-07 | Baca Pesan | Pengguna dapat membaca riwayat pesan dalam room |
| F-08 | Lihat Room | Pengguna dapat melihat daftar room yang diikuti |

Sistem aplikasi chat yang dikembangkan harus mampu menyediakan layanan autentikasi pengguna yang mencakup fitur registrasi dan login. Pengguna dapat mendaftarkan akun baru dengan memasukkan username yang bersifat unik, dan selanjutnya dapat melakukan login ke dalam sistem menggunakan username tersebut. Proses autentikasi ini menjadi pintu masuk bagi pengguna untuk mengakses seluruh fitur aplikasi chat.

Fitur pengelolaan room chat merupakan kebutuhan fungsional berikutnya yang harus dipenuhi. Sistem harus menyediakan kemampuan bagi pengguna untuk membuat room chat baru dengan tipe direct message (DM) untuk komunikasi dua orang atau tipe group untuk komunikasi lebih dari dua orang. Setiap room chat memiliki kode unik yang dapat digunakan oleh pengguna lain untuk bergabung ke dalam room tersebut. Pengguna juga dapat melihat daftar room yang diikuti dan meninggalkan room kapan saja.

Fungsi inti dari aplikasi chat adalah pengiriman dan pembacaan pesan. Sistem harus memungkinkan pengguna yang tergabung dalam suatu room untuk mengirimkan pesan teks dan membaca pesan yang dikirim oleh anggota room lainnya. Seluruh pesan yang dikirimkan harus tersimpan secara persisten dalam basis data dan dapat diakses kembali sebagai riwayat percakapan. Penyimpanan pesan dilakukan secara terdistribusi dengan mekanisme sharding berdasarkan room_id, sehingga data pesan tersebar ke beberapa node database sesuai dengan algoritma sharding yang ditentukan.

### Kebutuhan Non Fungsional

**Tabel 3.2 Kebutuhan Non-Fungsional Sistem**

| Kode | Kebutuhan | Deskripsi | Target |
|------|-----------|-----------|--------|
| NF-01 | Skalabilitas | Sistem dapat di-scale secara horizontal | Mendukung penambahan shard |
| NF-02 | Ketersediaan | Sistem beroperasi kontinu | Uptime > 99% |
| NF-03 | Performa | Response time yang optimal | < 2 detik per operasi |
| NF-04 | Konsistensi | Data tersimpan dengan benar di shard yang sesuai | 100% akurat |
| NF-05 | Keandalan | Sistem mampu menangani beban tinggi | 50+ concurrent users |

Skalabilitas merupakan kebutuhan non-fungsional utama yang harus dipenuhi oleh sistem. Arsitektur basis data harus dirancang agar mampu menangani peningkatan jumlah pengguna dan volume pesan tanpa mengalami penurunan kinerja yang signifikan. Dengan penerapan sharding menggunakan Apache ShardingSphere, sistem dapat melakukan scale-out secara horizontal dengan menambahkan node database baru ketika kapasitas penyimpanan atau beban kerja meningkat [3].

Ketersediaan dan keandalan sistem juga menjadi aspek penting yang harus diperhatikan. Sistem harus mampu beroperasi secara kontinu dan memberikan respons terhadap permintaan pengguna dalam waktu yang wajar. Arsitektur terdistribusi dengan empat shard PostgreSQL memungkinkan distribusi beban kerja sehingga tidak terjadi bottleneck pada satu server tunggal. Meskipun proyek ini tidak mengimplementasikan replikasi, struktur sharding yang diterapkan sudah memberikan dasar bagi peningkatan ketersediaan sistem.

Konsistensi data dan performa merupakan dua aspek yang saling berkaitan dalam sistem basis data terdistribusi. Sistem harus menjamin bahwa data yang disimpan pada setiap shard tetap konsisten dan dapat diakses dengan benar melalui mekanisme routing query yang disediakan oleh ShardingSphere. Dari sisi performa, sistem ditargetkan mampu menangani operasi baca dan tulis secara konkuren dari banyak pengguna dengan waktu respons yang optimal. Pengujian kinerja dilakukan untuk memvalidasi bahwa arsitektur sharding memberikan peningkatan throughput dan penurunan latency dibandingkan dengan arsitektur single database.

## Perancangan konseptual dan logical

Perancangan konseptual merupakan tahap abstraksi tingkat tinggi yang menggambarkan struktur data dan hubungan antar entitas dalam sistem aplikasi chat. Pada tahap ini dilakukan identifikasi entitas-entitas utama beserta atribut dan relasinya tanpa mempertimbangkan aspek implementasi fisik basis data. Perancangan konseptual menjadi dasar bagi perancangan logical yang selanjutnya akan ditransformasikan ke dalam skema basis data relasional yang siap diimplementasikan dengan mekanisme sharding.

Sistem aplikasi chat yang dikembangkan terdiri dari empat entitas utama, yaitu User, Room, RoomMember, dan Message. Entitas User merepresentasikan pengguna aplikasi dengan atribut id sebagai primary key, username yang bersifat unik, dan created_at sebagai timestamp pembuatan akun. Entitas Room merepresentasikan ruang percakapan dengan atribut id sebagai primary key, codename sebagai kode unik untuk bergabung ke room, type yang menunjukkan jenis room (dm atau group), dan created_at sebagai timestamp pembuatan room. Entitas RoomMember merupakan entitas asosiatif yang menghubungkan User dan Room dengan atribut room_id dan user_id sebagai composite primary key. Entitas Message merepresentasikan pesan yang dikirim dalam room dengan atribut id sebagai primary key, room_id sebagai foreign key ke Room, sender_id sebagai foreign key ke User, content sebagai isi pesan, dan created_at sebagai timestamp pengiriman.

Relasi antar entitas dimodelkan sebagai berikut. Entitas User dan Room memiliki relasi many-to-many yang dihubungkan melalui entitas RoomMember, dimana satu pengguna dapat menjadi anggota banyak room dan satu room dapat memiliki banyak anggota. Entitas Message memiliki relasi many-to-one dengan entitas Room, dimana satu room dapat memiliki banyak pesan tetapi satu pesan hanya terkait dengan satu room. Entitas Message juga memiliki relasi many-to-one dengan entitas User melalui atribut sender_id, dimana satu pengguna dapat mengirim banyak pesan.

Pada perancangan logical, skema konseptual ditransformasikan ke dalam empat tabel relasional yaitu users, rooms, room_members, dan messages. Tabel users, rooms, dan room_members dirancang sebagai tabel referensi yang disimpan pada satu node utama (shard 0) karena ukuran datanya relatif kecil dan sering diakses untuk keperluan join query. Sementara itu, tabel messages dirancang sebagai tabel yang akan di-shard secara horizontal berdasarkan kolom room_id. Pemilihan room_id sebagai sharding key didasarkan pada pola akses data aplikasi chat, dimana pesan-pesan dalam satu room cenderung diakses bersamaan. Dengan strategi ini, seluruh pesan dalam satu room akan tersimpan pada shard yang sama, sehingga query pembacaan pesan tidak memerlukan akses lintas shard dan dapat dieksekusi dengan efisien.

### ERD

**Tabel 3.3 Atribut Entitas Sistem**

| Entitas | Atribut | Tipe Data | Keterangan |
|---------|---------|-----------|------------|
| **User** | id | BIGINT | Primary Key |
| | username | VARCHAR(255) | Unique, Not Null |
| | created_at | TIMESTAMP | Default: Current Timestamp |
| **Room** | id | BIGINT | Primary Key |
| | codename | VARCHAR(8) | Unique, Not Null |
| | type | VARCHAR(50) | 'dm' atau 'group' |
| | created_at | TIMESTAMP | Default: Current Timestamp |
| **RoomMember** | room_id | BIGINT | Foreign Key → Room |
| | user_id | BIGINT | Foreign Key → User |
| **Message** | id | BIGINT | Primary Key |
| | room_id | BIGINT | Foreign Key → Room, **Sharding Key** |
| | sender_id | BIGINT | Foreign Key → User |
| | content | TEXT | Isi pesan |
| | created_at | TIMESTAMP | Default: Current Timestamp |

**Tabel 3.4 Relasi Antar Entitas**

| Entitas 1 | Relasi | Entitas 2 | Keterangan |
|-----------|--------|-----------|------------|
| User | Many-to-Many | Room | Melalui RoomMember |
| Message | Many-to-One | Room | Satu room memiliki banyak pesan |
| Message | Many-to-One | User | Satu user dapat mengirim banyak pesan |

**Gambar 3.1 Entity Relationship Diagram (ERD)**

```
┌─────────────┐       ┌──────────────────┐       ┌─────────────┐
│    USER     │       │   ROOM_MEMBER    │       │    ROOM     │
├─────────────┤       ├──────────────────┤       ├─────────────┤
│ id (PK)     │◄──────│ user_id (FK)     │       │ id (PK)     │
│ username    │       │ room_id (FK)     │──────►│ codename    │
│ created_at  │       └──────────────────┘       │ type        │
└─────────────┘                                  │ created_at  │
      ▲                                          └─────────────┘
      │                                                 ▲
      │         ┌─────────────────┐                     │
      │         │    MESSAGE      │                     │
      │         ├─────────────────┤                     │
      └─────────│ sender_id (FK)  │                     │
                │ room_id (FK)    │─────────────────────┘
                │ id (PK)         │
                │ content         │
                │ created_at      │
                └─────────────────┘
```

Entity Relationship Diagram (ERD) sistem aplikasi chat menggambarkan hubungan antar entitas dalam basis data. Entitas User terhubung dengan entitas Room melalui entitas asosiatif RoomMember dalam relasi many-to-many, dimana satu pengguna dapat bergabung ke banyak room dan satu room dapat memiliki banyak anggota. Entitas Message terhubung dengan entitas Room dalam relasi many-to-one (satu room memiliki banyak pesan) dan terhubung dengan entitas User dalam relasi many-to-one melalui atribut sender_id (satu pengguna dapat mengirim banyak pesan). Primary key pada setiap entitas menggunakan tipe BIGINT untuk mengakomodasi pertumbuhan data dalam skala besar pada arsitektur terdistribusi.


## Perancangan fisikal terdistribusi

**Gambar 3.2 Arsitektur Fisik Sistem Terdistribusi**

```
                              ┌─────────────────────┐
                              │   Flask Application │
                              │     (Port 5001)     │
                              └──────────┬──────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │   ShardingSphere    │
                              │       Proxy         │
                              │    (Port 3307)      │
                              └──────────┬──────────┘
                                         │
            ┌────────────────────────────┼────────────────────────────┐
            │                            │                            │
            ▼                            ▼                            ▼
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   PostgreSQL ds_0   │    │   PostgreSQL ds_1   │    │   PostgreSQL ds_2   │
│  (Primary Shard)    │    │      (Shard 1)      │    │      (Shard 2)      │
│  - users            │    │  - messages         │    │  - messages         │
│  - rooms            │    │    (room_id%4=1)    │    │    (room_id%4=2)    │
│  - room_members     │    └─────────────────────┘    └─────────────────────┘
│  - messages         │
│    (room_id%4=0)    │    ┌─────────────────────┐
└─────────────────────┘    │   PostgreSQL ds_3   │
                           │      (Shard 3)      │
                           │  - messages         │
                           │    (room_id%4=3)    │
                           └─────────────────────┘
```

Arsitektur fisik sistem basis data terdistribusi pada proyek ini mengadopsi model middleware dengan Apache ShardingSphere Proxy sebagai komponen sentral yang mengelola distribusi data ke beberapa node database PostgreSQL. Arsitektur ini terdiri dari tiga lapisan utama, yaitu lapisan aplikasi (Flask application), lapisan middleware (ShardingSphere Proxy), dan lapisan penyimpanan data (PostgreSQL shards). Seluruh komponen dijalankan dalam lingkungan container Docker yang terhubung melalui jaringan virtual internal, sehingga memudahkan pengelolaan dan isolasi antar komponen.

Apache ShardingSphere Proxy berperan sebagai database gateway yang menerima seluruh koneksi dan query dari aplikasi Flask. Proxy ini berjalan pada port 3307 dan menyediakan antarmuka protokol PostgreSQL, sehingga aplikasi dapat terhubung seolah-olah berkomunikasi dengan satu database tunggal. Ketika menerima query, ShardingSphere Proxy melakukan parsing dan analisis terhadap query tersebut, kemudian menentukan shard mana yang menjadi target berdasarkan sharding key yang terdapat dalam query. Untuk query INSERT pada tabel messages, proxy menghitung nilai room_id modulo 4 untuk menentukan shard tujuan. Untuk query SELECT, proxy dapat mengeksekusi query pada satu shard spesifik jika sharding key disertakan dalam klausa WHERE, atau melakukan broadcast ke seluruh shard jika sharding key tidak tersedia [3][8].

Lapisan penyimpanan data terdiri dari empat node database PostgreSQL yang masing-masing berperan sebagai shard independen. Setiap shard diidentifikasi dengan nama ds_0, ds_1, ds_2, dan ds_3, dan masing-masing menjalankan instance PostgreSQL versi 17 dalam container terpisah. Shard ds_0 memiliki peran khusus sebagai primary shard yang menyimpan tabel referensi (users, rooms, room_members), sementara seluruh shard menyimpan tabel messages sesuai dengan hasil kalkulasi sharding. Setiap container PostgreSQL dibatasi penggunaan resource sebesar 1 CPU dan 100MB RAM untuk mensimulasikan kondisi resource terbatas dan mengamati perilaku sistem dalam kondisi tersebut.

### Fragmentasi Data

**Tabel 3.5 Konfigurasi Data Source**

| Data Source | Host | Port | Database | Keterangan |
|-------------|------|------|----------|------------|
| ds_0 | postgres-shard-0 | 5432 | chat_shard_0 | Primary Shard |
| ds_1 | postgres-shard-1 | 5432 | chat_shard_1 | Shard 1 |
| ds_2 | postgres-shard-2 | 5432 | chat_shard_2 | Shard 2 |
| ds_3 | postgres-shard-3 | 5432 | chat_shard_3 | Shard 3 |

**Tabel 3.6 Distribusi Tabel pada Shard**

| Tabel | Tipe | Lokasi | Sharding Key |
|-------|------|--------|-------------|
| users | Reference | ds_0 | - |
| rooms | Reference | ds_0 | - |
| room_members | Reference | ds_0 | - |
| messages | Sharded | ds_0, ds_1, ds_2, ds_3 | room_id |

Fragmentasi data pada sistem ini menerapkan teknik fragmentasi horizontal (horizontal partitioning) pada tabel messages. Fragmentasi horizontal membagi baris-baris data dalam satu tabel ke beberapa fragmen berdasarkan nilai kolom tertentu, dimana setiap fragmen memiliki struktur skema yang identik namun menyimpan subset data yang berbeda [7]. Pada implementasi ini, kolom room_id dipilih sebagai sharding key dengan algoritma INLINE yang menggunakan ekspresi ds_${room_id % 4}. Dengan algoritma ini, pesan dengan room_id bernilai 0, 4, 8, 12, dan seterusnya akan disimpan pada shard ds_0. Pesan dengan room_id bernilai 1, 5, 9, 13, dan seterusnya akan disimpan pada shard ds_1, dan demikian seterusnya untuk shard ds_2 dan ds_3.

Pemilihan strategi fragmentasi berbasis modulo memberikan distribusi data yang relatif merata ke seluruh shard, dengan asumsi nilai room_id terdistribusi secara uniform. Keuntungan dari pendekatan ini adalah kesederhanaan kalkulasi routing dan prediktabilitas lokasi data. Ketika aplikasi melakukan query pesan untuk room tertentu, ShardingSphere dapat langsung menghitung shard target tanpa perlu melakukan lookup ke tabel routing. Namun demikian, pendekatan ini memiliki keterbatasan dalam hal rebalancing data ketika jumlah shard berubah, karena perubahan jumlah shard akan mengubah hasil kalkulasi modulo dan memerlukan migrasi data antar shard.

Tabel referensi (users, rooms, room_members) tidak difragmentasi dan disimpan secara utuh pada shard ds_0. Keputusan ini diambil berdasarkan pertimbangan bahwa ukuran tabel referensi relatif kecil dibandingkan tabel messages, dan data pada tabel referensi sering diakses untuk operasi join dengan tabel messages. Dengan menyimpan tabel referensi pada satu lokasi, kompleksitas query lintas shard dapat diminimalkan dan konsistensi data referensi lebih mudah dijaga.


## Perancangan query dan algoritma

**Gambar 3.3 Alur Routing Query pada ShardingSphere**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         APLIKASI FLASK                                  │
│                    INSERT INTO messages (room_id=5, ...)                │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      SHARDINGSPHERE PROXY                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │  1. Parse SQL   │─►│ 2. Extract Key  │─►│ 3. Calculate    │         │
│  │                 │  │   (room_id=5)   │  │   5 % 4 = 1     │         │
│  └─────────────────┘  └─────────────────┘  └────────┬────────┘         │
│                                                      │                  │
│                                         ┌────────────▼────────────┐     │
│                                         │ 4. Route to ds_1        │     │
│                                         └────────────┬────────────┘     │
└──────────────────────────────────────────────────────┼──────────────────┘
                                                       │
                                                       ▼
                                          ┌─────────────────────┐
                                          │   PostgreSQL ds_1   │
                                          │   INSERT executed   │
                                          └─────────────────────┘
```

Perancangan query pada sistem basis data terdistribusi dengan sharding memerlukan pemahaman tentang bagaimana query diproses dan diarahkan ke shard yang tepat. Apache ShardingSphere menyediakan mekanisme routing query secara transparan, dimana aplikasi dapat mengirimkan query SQL standar dan middleware akan menangani proses distribusi ke shard tujuan. Algoritma routing yang digunakan bergantung pada keberadaan sharding key dalam query dan jenis operasi yang dilakukan.

Pada operasi INSERT untuk tabel messages, ShardingSphere melakukan proses routing berdasarkan nilai sharding key yang disertakan dalam query. Ketika aplikasi mengirimkan query INSERT dengan menyertakan nilai room_id, ShardingSphere Proxy akan mengekstrak nilai tersebut dan menghitung shard tujuan menggunakan algoritma yang telah dikonfigurasi. Proses routing mengikuti langkah-langkah sebagai berikut: pertama, proxy melakukan parsing terhadap query untuk mengidentifikasi tabel target dan nilai kolom; kedua, proxy memeriksa apakah tabel tersebut merupakan tabel yang di-shard dan mengidentifikasi sharding key; ketiga, proxy menghitung shard tujuan dengan menerapkan ekspresi ds_${room_id % 4}; keempat, proxy meneruskan query ke node database shard yang sesuai. Dengan mekanisme ini, data pesan secara otomatis terdistribusi ke shard yang ditentukan tanpa intervensi dari aplikasi.

Operasi SELECT pada tabel messages memiliki dua skenario routing yang berbeda tergantung pada keberadaan sharding key dalam klausa WHERE. Skenario pertama adalah single-shard query, dimana query menyertakan kondisi room_id dalam klausa WHERE. Pada skenario ini, ShardingSphere dapat langsung menghitung shard target dan mengirimkan query hanya ke satu shard, sehingga eksekusi query menjadi efisien. Skenario kedua adalah broadcast query, dimana query tidak menyertakan sharding key atau memerlukan data dari seluruh shard. Pada skenario ini, ShardingSphere akan mengirimkan query ke seluruh shard secara paralel, mengumpulkan hasil dari masing-masing shard, dan melakukan penggabungan (merge) hasil sebelum mengembalikan response ke aplikasi. Query SELECT yang mengambil pesan berdasarkan room_id tertentu akan dieksekusi sebagai single-shard query, sedangkan query agregasi tanpa filter room_id akan dieksekusi sebagai broadcast query.

Sharding key berperan sebagai penentu utama dalam algoritma routing query. Pemilihan room_id sebagai sharding key didasarkan pada karakteristik pola akses aplikasi chat, dimana operasi pembacaan dan penulisan pesan selalu melibatkan konteks room tertentu. Dengan menempatkan seluruh pesan dari satu room pada shard yang sama, operasi query yang paling sering dilakukan (menampilkan riwayat pesan dalam room) dapat dieksekusi tanpa memerlukan koordinasi lintas shard. ShardingSphere menerapkan algoritma hash-based sharding dengan fungsi modulo untuk menentukan distribusi data. Algoritma ini memiliki kompleksitas O(1) untuk kalkulasi routing, sehingga tidak menambah overhead signifikan pada waktu eksekusi query. Konsistensi routing dijamin oleh sifat deterministik dari fungsi modulo, dimana nilai room_id yang sama akan selalu menghasilkan shard tujuan yang sama.


## Lingkungan implementasi

Lingkungan implementasi merupakan aspek penting yang menentukan keberhasilan pengembangan dan pengujian sistem basis data terdistribusi. Pemilihan perangkat keras dan perangkat lunak yang tepat akan mempengaruhi kemudahan pengembangan, konsistensi lingkungan antar pengembang, serta validitas hasil pengujian. Pada proyek ini, lingkungan implementasi dirancang untuk mendukung pengembangan aplikasi chat dengan arsitektur sharding menggunakan teknologi containerization.

### Perangkat keras dan jaringan

Pengembangan dan pengujian sistem dilakukan pada komputer laptop dengan spesifikasi yang memadai untuk menjalankan beberapa container Docker secara bersamaan. Laptop digunakan sebagai lingkungan pengembangan tunggal yang mensimulasikan arsitektur terdistribusi melalui virtualisasi container. Seluruh komponen sistem (aplikasi Flask, ShardingSphere Proxy, dan empat instance PostgreSQL) berjalan pada satu mesin fisik namun terisolasi dalam container terpisah. Komunikasi antar container dilakukan melalui jaringan virtual Docker (bridge network) yang mensimulasikan komunikasi jaringan antar node dalam sistem terdistribusi sesungguhnya. Pendekatan ini memungkinkan pengujian arsitektur sharding tanpa memerlukan infrastruktur multi-server yang kompleks.

### Perangkat lunak

**Tabel 3.7 Daftar Perangkat Lunak**

| Komponen | Teknologi | Versi | Keterangan |
|----------|-----------|-------|------------|
| Database | PostgreSQL | 17 | RDBMS untuk setiap shard |
| Sharding Proxy | Apache ShardingSphere | 5.4.1 | Middleware routing query |
| Backend | Python Flask | 3.0.0 | REST API aplikasi |
| DB Driver | psycopg | 3.2.3 | Koneksi ke PostgreSQL |
| Container | Docker | Latest | Virtualisasi container |
| Orchestration | Docker Compose | Latest | Multi-container management |
| IDE | Visual Studio Code | Latest | Development environment |

PostgreSQL versi 17 dipilih sebagai sistem manajemen basis data relasional untuk seluruh shard. PostgreSQL merupakan RDBMS open-source yang memiliki fitur lengkap, performa tinggi, dan kompatibilitas yang baik dengan Apache ShardingSphere. Setiap shard menjalankan instance PostgreSQL independen dalam container Docker dengan konfigurasi yang identik, memastikan konsistensi perilaku antar shard. PostgreSQL juga menyediakan fitur indexing yang mendukung optimasi query pada tabel messages yang di-shard.

Python versi 3.13 digunakan sebagai bahasa pemrograman untuk mengembangkan aplikasi backend dan script pengujian. Framework Flask dipilih untuk membangun REST API aplikasi chat karena kesederhanaan dan fleksibilitasnya. Library psycopg versi 3 digunakan sebagai database driver untuk koneksi ke ShardingSphere Proxy. Python juga digunakan untuk mengembangkan script performance testing dengan memanfaatkan library concurrent.futures untuk simulasi beban konkuren dan matplotlib untuk visualisasi hasil pengujian.

Docker digunakan sebagai platform containerization untuk menjalankan seluruh komponen sistem dalam lingkungan yang terisolasi dan reproducible. Docker Compose digunakan untuk mendefinisikan dan mengelola multi-container application, termasuk konfigurasi jaringan, volume, dan resource limits. Penggunaan Docker memungkinkan simulasi arsitektur terdistribusi pada satu mesin dan memastikan konsistensi lingkungan antara pengembangan dan pengujian. Setiap container PostgreSQL dikonfigurasi dengan batasan resource (1 CPU, 100MB RAM) untuk mensimulasikan kondisi resource terbatas.

Visual Studio Code (VSCode) digunakan sebagai Integrated Development Environment (IDE) untuk pengembangan kode aplikasi dan konfigurasi sistem. VSCode menyediakan fitur-fitur produktivitas seperti syntax highlighting, debugging, dan integrasi dengan terminal untuk menjalankan perintah Docker. Ekstensi Docker dan Python pada VSCode memudahkan pengelolaan container dan pengembangan aplikasi dalam satu lingkungan terintegrasi.

---

# BAB 4 IMPLEMENTASI

## Implementasi skema dan data

Implementasi skema dan data merupakan tahap realisasi dari perancangan logical dan fisikal yang telah disusun pada bab sebelumnya. Pada tahap ini, skema tabel diterapkan pada setiap node database shard dan konfigurasi sharding didefinisikan pada Apache ShardingSphere Proxy. Implementasi dilakukan dengan memperhatikan konsistensi skema antar shard serta kesesuaian dengan aturan fragmentasi data yang telah dirancang.

Skema tabel aplikasi chat terdiri dari empat tabel utama yaitu users, rooms, room_members, dan messages. Tabel users memiliki kolom id bertipe BIGINT sebagai primary key, kolom username bertipe VARCHAR(255) dengan constraint UNIQUE dan NOT NULL, serta kolom created_at bertipe TIMESTAMP dengan nilai default CURRENT_TIMESTAMP. Tabel rooms memiliki kolom id bertipe BIGINT sebagai primary key, kolom codename bertipe VARCHAR(8) dengan constraint UNIQUE dan NOT NULL untuk kode bergabung ke room, kolom type bertipe VARCHAR(50) untuk menandai jenis room (dm atau group), dan kolom created_at. Tabel room_members merupakan tabel asosiatif dengan composite primary key yang terdiri dari kolom room_id dan user_id bertipe BIGINT. Tabel messages memiliki kolom id bertipe BIGINT sebagai primary key, kolom room_id dan sender_id bertipe BIGINT sebagai foreign key, kolom content bertipe TEXT untuk menyimpan isi pesan, dan kolom created_at untuk timestamp pengiriman.

Penerapan skema pada setiap shard dilakukan melalui SQL initialization script yang dieksekusi saat container PostgreSQL pertama kali dijalankan. Setiap shard (ds_0, ds_1, ds_2, ds_3) memiliki file inisialisasi tersendiri (shard_0.sql, shard_1.sql, shard_2.sql, shard_3.sql) yang memuat perintah CREATE TABLE untuk membuat struktur tabel yang identik. Seluruh shard memiliki tabel messages dengan skema yang sama untuk mendukung fragmentasi horizontal. Shard ds_0 sebagai primary shard memiliki tambahan data pada tabel users, rooms, dan room_members yang berfungsi sebagai tabel referensi. Index dibuat pada kolom-kolom yang sering digunakan dalam query, meliputi index pada username di tabel users, codename di tabel rooms, room_id dan user_id di tabel room_members, serta room_id, sender_id, dan created_at di tabel messages.

### Implementasi fragmentasi data

Implementasi fragmentasi data dilakukan melalui konfigurasi sharding rules pada Apache ShardingSphere Proxy. Konfigurasi didefinisikan dalam file config-sharding.yaml yang memuat definisi data sources dan sharding rules. Empat data source didefinisikan dengan nama ds_0, ds_1, ds_2, dan ds_3, masing-masing mengarah ke instance PostgreSQL yang berjalan pada container terpisah. Setiap data source dikonfigurasi dengan parameter koneksi meliputi URL JDBC, username, password, dan pengaturan connection pool seperti maxPoolSize sebesar 50 koneksi dan connection timeout sebesar 30 detik.

Sharding rules mendefinisikan tabel mana yang akan difragmentasi dan algoritma yang digunakan. Tabel messages dikonfigurasi sebagai sharded table dengan actualDataNodes yang mencakup ds_0.messages hingga ds_3.messages, menandakan bahwa tabel ini tersebar di keempat shard. Database strategy menggunakan algoritma standard sharding dengan room_id sebagai sharding column. Algoritma sharding yang digunakan bertipe INLINE dengan ekspresi ds_${room_id % 4}, yang berarti nilai room_id akan dimodulo dengan 4 untuk menentukan shard tujuan. Tabel users, rooms, dan room_members dikonfigurasi dengan actualDataNodes hanya pada ds_0, sehingga data pada tabel-tabel ini tidak difragmentasi dan tersimpan seluruhnya pada shard utama.

Verifikasi implementasi fragmentasi dilakukan dengan melakukan operasi INSERT pesan ke beberapa room dengan room_id yang berbeda, kemudian memeriksa distribusi data pada masing-masing shard. Pesan dengan room_id bernilai kelipatan 4 (0, 4, 8, ...) tersimpan pada shard ds_0, room_id dengan sisa bagi 1 (1, 5, 9, ...) tersimpan pada shard ds_1, room_id dengan sisa bagi 2 (2, 6, 10, ...) tersimpan pada shard ds_2, dan room_id dengan sisa bagi 3 (3, 7, 11, ...) tersimpan pada shard ds_3. Hasil verifikasi menunjukkan bahwa fragmentasi data berjalan sesuai dengan konfigurasi yang telah ditentukan.


## Pengujian fungsionalitas dan kinerja

Pengujian sistem dilakukan dalam dua tahap, yaitu pengujian fungsionalitas untuk memvalidasi kebenaran fitur aplikasi dan pengujian kinerja untuk mengukur performa sistem dalam menangani beban kerja. Pengujian fungsionalitas memastikan bahwa seluruh fitur aplikasi chat berjalan sesuai dengan kebutuhan yang telah didefinisikan, sedangkan pengujian kinerja membandingkan performa arsitektur single database dengan sharded database.

### Pengujian Fungsionalitas

Pengujian fungsionalitas mencakup validasi fitur autentikasi, pengelolaan room, dan pengiriman pesan. Fitur registrasi diuji dengan membuat akun pengguna baru menggunakan username unik, kemudian memverifikasi bahwa data pengguna tersimpan dengan benar pada tabel users di shard ds_0. Fitur login diuji dengan melakukan autentikasi menggunakan username yang telah terdaftar dan memastikan session pengguna tercipta dengan benar. Pengujian pengelolaan room mencakup pembuatan room baru (tipe dm dan group), bergabung ke room menggunakan codename, dan meninggalkan room. Seluruh operasi room diverifikasi dengan memeriksa data pada tabel rooms dan room_members.

Pengujian fitur pengiriman pesan dilakukan dengan mengirim pesan ke berbagai room dengan room_id yang berbeda, kemudian memverifikasi bahwa pesan tersimpan pada shard yang sesuai berdasarkan algoritma sharding. Pengujian pembacaan pesan memastikan bahwa riwayat percakapan dalam suatu room dapat diambil dengan benar melalui query yang diarahkan ke shard yang tepat oleh ShardingSphere. Pengujian integritas data dilakukan dengan memverifikasi bahwa setiap shard hanya menyimpan pesan dengan room_id yang sesuai dengan aturan fragmentasi (room_id % 4).

### Pengujian Kinerja

Pengujian kinerja dilakukan menggunakan script pengujian berbasis Python yang mensimulasikan beban kerja konkuren pada sistem. Script pengujian menggunakan library concurrent.futures dengan ThreadPoolExecutor untuk menjalankan operasi secara paralel dari banyak virtual user. Konfigurasi pengujian meliputi 300 virtual user, 100 room chat, 20 pesan per user, sehingga total operasi yang dieksekusi adalah 6.000 operasi pengiriman pesan. Pengujian dilakukan dengan 50 concurrent worker yang mengeksekusi operasi secara paralel untuk mensimulasikan kondisi high concurrency.

Skenario pengujian membandingkan dua arsitektur database yang berbeda. Skenario pertama adalah single database, dimana seluruh data disimpan pada satu instance PostgreSQL tunggal yang berjalan pada port 5000. Skenario kedua adalah sharded database, dimana data pesan didistribusikan ke empat shard PostgreSQL melalui Apache ShardingSphere Proxy yang berjalan pada port 5001. Kedua skenario dijalankan dengan konfigurasi pengujian yang identik untuk memastikan validitas perbandingan. Setiap skenario dieksekusi secara bergantian dengan jeda waktu untuk memastikan kondisi sistem telah kembali ke keadaan awal.

Metrik kinerja yang diamati dalam pengujian meliputi throughput, response time, dan distribusi latency. Throughput diukur dalam satuan operasi per detik (ops/sec), menunjukkan kapasitas sistem dalam menangani permintaan. Response time diukur dalam milidetik (ms) dengan beberapa statistik deskriptif meliputi nilai rata-rata (average), median (P50), persentil ke-95 (P95), persentil ke-99 (P99), nilai minimum, dan nilai maksimum. Metrik P95 dan P99 penting untuk memahami tail latency, yaitu waktu respons pada kondisi terburuk yang dialami oleh sebagian kecil permintaan. Total durasi pengujian juga dicatat untuk mengukur waktu keseluruhan yang dibutuhkan untuk menyelesaikan seluruh operasi.

**Tabel 4.1 Konfigurasi Pengujian Kinerja**

| Parameter | Nilai |
|-----------|-------|
| Total Virtual Users | 300 |
| Total Rooms | 100 |
| Pesan per User | 20 |
| Total Operasi | 6.000 |
| Concurrent Workers | 50 |

**Tabel 4.2 Hasil Perbandingan Kinerja Single DB vs Sharded DB**

| Metrik | Single Database | Sharded Database | Peningkatan |
|--------|-----------------|------------------|-------------|
| **Throughput** | 25,66 ops/sec | 50,67 ops/sec | **+97,4%** |
| **Avg Response Time** | 1.925 ms | 968 ms | **-49,7%** |
| **P50 (Median)** | 1.899 ms | 965 ms | **-49,2%** |
| **P95 Latency** | 2.300 ms | 1.154 ms | **-49,8%** |
| **P99 Latency** | 2.675 ms | 1.260 ms | **-52,9%** |
| **Max Response Time** | 3.836 ms | 1.921 ms | **-49,9%** |
| **Total Duration** | 256 detik | 129 detik | **-49,6%** |

**Tabel 4.3 Distribusi Data pada Shard**

| Shard | Jumlah Room | Persentase |
|-------|-------------|------------|
| ds_0 | 25 | 25% |
| ds_1 | 25 | 25% |
| ds_2 | 25 | 25% |
| ds_3 | 25 | 25% |

Hasil pengujian kinerja menunjukkan perbedaan signifikan antara kedua arsitektur. Arsitektur single database mencatat throughput sebesar 25,66 ops/sec dengan rata-rata response time 1.925 ms dan total durasi pengujian 256 detik. Arsitektur sharded database mencatat throughput sebesar 50,67 ops/sec dengan rata-rata response time 968 ms dan total durasi pengujian 129 detik. Perbandingan ini menunjukkan peningkatan throughput sebesar 97,4% dan penurunan latency sebesar 49,7% pada arsitektur sharded database. Metrik P99 juga menunjukkan perbaikan dari 2.675 ms pada single database menjadi 1.260 ms pada sharded database, mengindikasikan peningkatan konsistensi response time pada kondisi beban tinggi.

**Gambar 4.1 Grafik Perbandingan Kinerja**

*Lihat file: test/performance_comparison.png*


## Analisis hasil implementasi

**Tabel 4.4 Ringkasan Hasil Pengujian**

| Kategori | Pemenang | Margin |
|----------|----------|--------|
| Throughput | ✅ Sharded DB | +97,4% |
| Avg Response Time | ✅ Sharded DB | -49,7% |
| P50 Latency | ✅ Sharded DB | -49,2% |
| P95 Latency | ✅ Sharded DB | -49,8% |
| P99 Latency | ✅ Sharded DB | -52,9% |
| Max Response Time | ✅ Sharded DB | -49,9% |

**Hasil Keseluruhan: SHARDED DATABASE MENANG (6-0)**

Hasil pengujian kinerja menunjukkan bahwa arsitektur sharded database memberikan peningkatan performa yang signifikan dibandingkan dengan arsitektur single database pada skenario beban kerja tinggi. Peningkatan throughput sebesar 97,4% (dari 25,66 ops/sec menjadi 50,67 ops/sec) mengindikasikan bahwa kapasitas sistem dalam menangani permintaan hampir dua kali lipat dengan penerapan sharding. Penurunan rata-rata response time sebesar 49,7% (dari 1.925 ms menjadi 968 ms) menunjukkan bahwa waktu yang dibutuhkan untuk memproses setiap operasi berkurang secara substansial. Perbaikan pada metrik P99 dari 2.675 ms menjadi 1.260 ms mengindikasikan bahwa tail latency, yaitu waktu respons pada kondisi terburuk, juga mengalami penurunan signifikan sehingga konsistensi layanan meningkat.

Keunggulan arsitektur sharding dapat dijelaskan melalui prinsip distribusi beban kerja dalam sistem terdistribusi. Pada arsitektur single database, seluruh operasi baca dan tulis diproses oleh satu instance database yang memiliki keterbatasan resource (CPU, memory, I/O). Ketika beban kerja meningkat dengan 50 concurrent worker yang mengirimkan permintaan secara bersamaan, terjadi contention pada resource database yang menyebabkan antrian permintaan dan peningkatan latency [1]. Sebaliknya, pada arsitektur sharded database, operasi tulis didistribusikan ke empat shard berdasarkan nilai room_id. Setiap shard hanya menangani sekitar 25% dari total operasi tulis, sehingga beban kerja terbagi secara merata dan mengurangi contention pada masing-masing node [2].

Distribusi data pada pengujian menunjukkan bahwa 100 room terdistribusi ke empat shard dengan komposisi yang relatif seimbang. Shard ds_0 menyimpan pesan dari 25 room, demikian pula shard ds_1, ds_2, dan ds_3 masing-masing menyimpan pesan dari 25 room. Distribusi yang merata ini merupakan hasil dari karakteristik algoritma modulo yang diterapkan pada sharding key room_id. Keseimbangan distribusi data berkontribusi pada optimalisasi performa karena tidak ada shard yang mengalami hotspot atau overload dibandingkan shard lainnya. Kondisi ini sesuai dengan prinsip load balancing dalam sistem terdistribusi dimana beban kerja harus tersebar merata untuk mencapai performa optimal [5].

Arsitektur sharding menunjukkan keunggulan pada kondisi beban kerja tinggi dengan operasi yang dapat dipartisi berdasarkan sharding key. Pada aplikasi chat, operasi pengiriman dan pembacaan pesan selalu terkait dengan room tertentu, sehingga penggunaan room_id sebagai sharding key sangat efektif. Query yang menyertakan room_id dalam klausa WHERE dapat dieksekusi pada satu shard saja (single-shard query), menghindari overhead koordinasi lintas shard. Kondisi ini sesuai dengan rekomendasi pemilihan sharding key yang mengikuti pola akses data aplikasi [4][8].

Namun demikian, arsitektur sharding memiliki keterbatasan pada kondisi tertentu. Query yang tidak menyertakan sharding key akan dieksekusi sebagai broadcast query ke seluruh shard, yang dapat meningkatkan latency karena memerlukan koordinasi dan penggabungan hasil dari banyak node. Operasi agregasi atau reporting yang memerlukan data dari seluruh room akan mengalami overhead ini. Selain itu, kompleksitas arsitektur meningkat dengan adanya middleware ShardingSphere yang menjadi single point of failure jika tidak dikonfigurasi dengan high availability. Overhead koneksi melalui proxy juga menambah latency pada setiap operasi, meskipun pada pengujian ini overhead tersebut terkompensasi oleh keuntungan distribusi beban [3].

Hasil implementasi ini mengkonfirmasi teori bahwa sharding efektif untuk meningkatkan skalabilitas sistem basis data dengan beban kerja tinggi dan data yang dapat dipartisi secara logis [2]. Peningkatan performa yang dicapai mendekati skala linear terhadap jumlah shard, dimana empat shard menghasilkan throughput hampir dua kali lipat dibandingkan single database. Faktor yang menyebabkan peningkatan tidak mencapai empat kali lipat meliputi overhead routing query melalui ShardingSphere, overhead koordinasi pada operasi yang melibatkan tabel referensi, dan keterbatasan resource pada lingkungan pengujian yang menggunakan container dengan resource terbatas. Meskipun demikian, hasil pengujian menunjukkan bahwa penerapan sharding menggunakan Apache ShardingSphere berhasil meningkatkan performa aplikasi chat secara signifikan dan memvalidasi efektivitas arsitektur basis data terdistribusi untuk aplikasi dengan karakteristik write-heavy workload.


---

# PENUTUP

## Kesimpulan

Proyek ini telah berhasil mengimplementasikan arsitektur basis data terdistribusi dengan teknik sharding pada sistem aplikasi chat menggunakan Apache ShardingSphere dan PostgreSQL. Implementasi mencakup perancangan skema database dengan empat tabel utama (users, rooms, room_members, messages), konfigurasi empat shard PostgreSQL sebagai node penyimpanan data, dan penerapan Apache ShardingSphere Proxy sebagai middleware yang mengelola routing query secara transparan. Fragmentasi horizontal diterapkan pada tabel messages dengan menggunakan room_id sebagai sharding key dan algoritma modulo (room_id % 4) untuk menentukan distribusi data ke masing-masing shard.

Hasil pengujian kinerja membuktikan efektivitas arsitektur sharding dalam meningkatkan performa sistem. Perbandingan antara arsitektur single database dan sharded database pada skenario beban kerja tinggi (300 virtual user, 6.000 operasi, 50 concurrent worker) menunjukkan peningkatan throughput sebesar 97,4% dari 25,66 ops/sec menjadi 50,67 ops/sec. Rata-rata response time mengalami penurunan sebesar 49,7% dari 1.925 ms menjadi 968 ms. Metrik tail latency (P99) juga membaik dari 2.675 ms menjadi 1.260 ms, mengindikasikan peningkatan konsistensi waktu respons pada kondisi beban tinggi. Total durasi pengujian berkurang dari 256 detik menjadi 129 detik, menunjukkan efisiensi waktu pemrosesan yang lebih baik.

Apache ShardingSphere terbukti menjadi solusi middleware yang efektif untuk implementasi database sharding tanpa memerlukan perubahan signifikan pada kode aplikasi. Mekanisme routing query yang transparan memungkinkan aplikasi Flask terhubung ke ShardingSphere Proxy seolah-olah berkomunikasi dengan satu database tunggal, sementara distribusi data ke empat shard dilakukan secara otomatis berdasarkan konfigurasi sharding rules. Kemampuan ShardingSphere dalam menangani single-shard query dan broadcast query memberikan fleksibilitas dalam mengeksekusi berbagai jenis operasi database. Hasil implementasi ini mengkonfirmasi bahwa teknik sharding merupakan pendekatan yang valid untuk meningkatkan skalabilitas dan performa sistem basis data pada aplikasi dengan karakteristik write-heavy workload dan volume data yang besar.


---

# DAFTAR PUSTAKA

[1] S. Aswal, “Distributed Database Systems for Large-Scale Data Management,” Int. J. of Computer Trends and Technology, vol. 11, no. 4, pp. 2260–2269, Dec. 2020.  
[2] S. Solat, “Sharding Distributed Databases: A Critical Review,” arXiv preprint arXiv:2404.04384, Apr. 2024.  
[3] Apache ShardingSphere Project, ShardingSphere Documentation, v5.1.2, 17-Jul-2022.  
[4] R. Kundalia, “Sharding with Spring Boot,” Medium, 2024.  
[5] Tessy Ardiansyah, Lecture Notes – Basis Data Terdistribusi, PENS.  
[6] IBM Indonesia, “Apa yang dimaksud dengan teorema CAP?”, IBM.com, 2023.  
[7] Tutorialspoint, “Data Fragmentation, Replication, and Allocation Techniques for Distributed Database”.  
[8] I. M. Antunes, “A Guide to ShardingSphere”, Baeldung.com, 2024.  
[9] Oracle MySQL Documentation, MySQL 8.4 Reference Manual – Replication.