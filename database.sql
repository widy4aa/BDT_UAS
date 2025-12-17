-- Database Schema for Chat Application
-- Generated from DBML diagram

-- Drop tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS room_members;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS users;

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create rooms table
CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    codename VARCHAR(8) UNIQUE NOT NULL, -- unique code for joining
    type VARCHAR(50) NOT NULL, -- 'dm' or 'group'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create room_members table (junction table for users and rooms)
CREATE TABLE room_members (
    room_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    UNIQUE (room_id, user_id),
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create messages table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    room_id INTEGER NOT NULL,
    sender_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX idx_room_members_room_id ON room_members(room_id);
CREATE INDEX idx_room_members_user_id ON room_members(user_id);
CREATE INDEX idx_messages_room_id ON messages(room_id);
CREATE INDEX idx_messages_sender_id ON messages(sender_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);

-- =============================================
-- SEEDER DATA
-- =============================================

-- Insert 4 users
INSERT INTO users (id, username, created_at) VALUES
(1, 'alice', '2025-01-01 10:00:00'),
(2, 'bob', '2025-01-02 11:30:00'),
(3, 'charlie', '2025-01-03 09:15:00'),
(4, 'diana', '2025-01-04 14:45:00');

-- Insert 6 rooms (3 DM rooms, 3 group rooms)
INSERT INTO rooms (id, codename, type, created_at) VALUES
(1, 'AB12DM01', 'dm', '2025-01-05 10:00:00'),      -- DM: Alice & Bob
(2, 'AC34DM02', 'dm', '2025-01-06 11:00:00'),      -- DM: Alice & Charlie
(3, 'BD56DM03', 'dm', '2025-01-07 12:00:00'),      -- DM: Bob & Diana
(4, 'GRP1ABC4', 'group', '2025-01-08 13:00:00'),   -- Group: Alice, Bob, Charlie
(5, 'ALLGRP05', 'group', '2025-01-09 14:00:00'),   -- Group: All users
(6, 'BCD6GRP6', 'group', '2025-01-10 15:00:00');   -- Group: Bob, Charlie, Diana

-- Insert room members
-- Room 1 (DM: Alice & Bob)
INSERT INTO room_members (room_id, user_id) VALUES
(1, 1), (1, 2);

-- Room 2 (DM: Alice & Charlie)
INSERT INTO room_members (room_id, user_id) VALUES
(2, 1), (2, 3);

-- Room 3 (DM: Bob & Diana)
INSERT INTO room_members (room_id, user_id) VALUES
(3, 2), (3, 4);

-- Room 4 (Group: Alice, Bob, Charlie)
INSERT INTO room_members (room_id, user_id) VALUES
(4, 1), (4, 2), (4, 3);

-- Room 5 (Group: All users)
INSERT INTO room_members (room_id, user_id) VALUES
(5, 1), (5, 2), (5, 3), (5, 4);

-- Room 6 (Group: Bob, Charlie, Diana)
INSERT INTO room_members (room_id, user_id) VALUES
(6, 2), (6, 3), (6, 4);

-- Insert messages
-- Room 1 messages (DM: Alice & Bob)
INSERT INTO messages (id, room_id, sender_id, content, created_at) VALUES
(1, 1, 1, 'Hai Bob, apa kabar?', '2025-01-05 10:05:00'),
(2, 1, 2, 'Hai Alice! Baik, kamu gimana?', '2025-01-05 10:06:00'),
(3, 1, 1, 'Baik juga, lagi ngerjain project nih', '2025-01-05 10:07:00'),
(4, 1, 2, 'Wah seru, project apa?', '2025-01-05 10:08:00');

-- Room 2 messages (DM: Alice & Charlie)
INSERT INTO messages (id, room_id, sender_id, content, created_at) VALUES
(5, 2, 1, 'Charlie, udah selesai tugasnya?', '2025-01-06 11:10:00'),
(6, 2, 3, 'Belum nih, masih setengah jalan', '2025-01-06 11:12:00'),
(7, 2, 1, 'Semangat ya!', '2025-01-06 11:13:00');

-- Room 3 messages (DM: Bob & Diana)
INSERT INTO messages (id, room_id, sender_id, content, created_at) VALUES
(8, 3, 2, 'Diana, jadi meeting besok?', '2025-01-07 12:15:00'),
(9, 3, 4, 'Jadi dong, jam 10 ya', '2025-01-07 12:16:00'),
(10, 3, 2, 'Oke siap!', '2025-01-07 12:17:00');

-- Room 4 messages (Group: Alice, Bob, Charlie)
INSERT INTO messages (id, room_id, sender_id, content, created_at) VALUES
(11, 4, 1, 'Halo semuanya!', '2025-01-08 13:30:00'),
(12, 4, 2, 'Halo Alice!', '2025-01-08 13:31:00'),
(13, 4, 3, 'Hai hai!', '2025-01-08 13:32:00'),
(14, 4, 1, 'Gimana progress project kita?', '2025-01-08 13:33:00'),
(15, 4, 2, 'Udah 70% nih', '2025-01-08 13:34:00'),
(16, 4, 3, 'Bagian saya udah selesai', '2025-01-08 13:35:00');

-- Room 5 messages (Group: All users)
INSERT INTO messages (id, room_id, sender_id, content, created_at) VALUES
(17, 5, 1, 'Selamat datang di grup!', '2025-01-09 14:30:00'),
(18, 5, 2, 'Makasih Alice!', '2025-01-09 14:31:00'),
(19, 5, 3, 'Akhirnya kita punya grup bareng', '2025-01-09 14:32:00'),
(20, 5, 4, 'Senang bisa gabung!', '2025-01-09 14:33:00'),
(21, 5, 1, 'Yuk kita diskusi project besar', '2025-01-09 14:34:00'),
(22, 5, 2, 'Siap!', '2025-01-09 14:35:00');

-- Room 6 messages (Group: Bob, Charlie, Diana)
INSERT INTO messages (id, room_id, sender_id, content, created_at) VALUES
(23, 6, 2, 'Guys, ada update terbaru', '2025-01-10 15:30:00'),
(24, 6, 3, 'Apa tuh Bob?', '2025-01-10 15:31:00'),
(25, 6, 4, 'Ceritain dong', '2025-01-10 15:32:00'),
(26, 6, 2, 'Deadline dimajuin jadi minggu depan', '2025-01-10 15:33:00'),
(27, 6, 3, 'Waduh, harus kerja keras nih', '2025-01-10 15:34:00'),
(28, 6, 4, 'Ayo semangat tim!', '2025-01-10 15:35:00');

-- Reset sequences to continue after seeder data
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
SELECT setval('rooms_id_seq', (SELECT MAX(id) FROM rooms));
SELECT setval('messages_id_seq', (SELECT MAX(id) FROM messages));
