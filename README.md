# MUMMY MAZE - ĐỒ ÁN MÔN CƠ SỞ LẬP TRÌNH
> *Một tựa game giải đố chiến thuật được xây dựng với Python và Pygame.*

## 👥 Thành Viên Nhóm

Dự án được thực hiện bởi nhóm **Nhóm 10** - Khóa K25 - Môn Cơ Sở Lập Trình: 
- Ngô Phạm Hồng Thức - 25122044
- Hà Chí Tâm - 25122039
- Huỳnh Văn Phú - 25122036
- Đặng Lê Hưng Thịnh - 25122042

## 📖 Giới Thiệu (Overview)
**Mummy Maze** là dự án tái hiện tựa game giải đố kinh điển của PopCap.  Trong game, người chơi vào vai nhà thám hiểm **Explorer** bị kẹt trong kim tự tháp bí ẩn và phải tìm đường thoát ra ngoài trong khi tránh những xác ướp (Enemy/Mummy) đang rình rập.

Mỗi bước di chuyển của người chơi sẽ kích hoạt lượt đi của các Enemy theo thuật toán pathfinding, tạo nên những tình huống giải đố đầy thử thách. Game yêu cầu người chơi phải suy nghĩ chiến thuật để tránh bị bắt và tìm ra lối thoát.

### 🛠 Công Nghệ Sử Dụng

| Công nghệ | Phiên bản | Mục đích |
|-----------|-----------|----------|
| **Python** | 3.12+ | Ngôn ngữ lập trình chính |
| **Pygame** | 2.5.2 | Thư viện đồ họa và xử lý game |
| **Git/GitHub** | - | Quản lý mã nguồn và version control |

---

## ✨ Tính Năng Nổi Bật

### 🎮 Gameplay Features

#### 1. **Hệ Thống Di Chuyển**
- Di chuyển theo 4 hướng: Lên, Xuống, Trái, Phải bằng cách Click chuột hoặc Nhấn phím
- Mỗi bước đi của Player kích hoạt lượt đi của tất cả Enemy
- Hệ thống collision detection chính xác

#### 2. **Algorithm Pathfinding**
- Thuật toán Di chuyển dựa trên chiến lược ưu tiên trục (Tham lam)
- Thuật toán Di chuyển bám theo người chơi bằng đường đi ngắn nhất (BFS)
- Thuật toán Di chuyển ngăn người chơi di chuyển đến lối thoát (BFS)

#### 3. **Hệ Thống Game Objects**
| Đối tượng | Chức năng |
|-----------|------------|
| **Explorer** | Nhân vật chính do người chơi điều khiển |
| **Enemy/Mummy** | Xác ướp tự động truy đuổi người chơi |
| **Key** | Chìa khóa để mở/đóng Gate |
| **Gate** | Cửa cần Key để mở/đóng |
| **Trap** | Bẫy gây thua nếu va phải |
| **Stair/Exit** | Điểm thoát hiểm để chiến thắng |
| **Wall** | Tường chắn đường |

### 💾 System Features

#### 4. **User Management System**
- Hệ thống đăng nhập/đăng ký với username và password
- Lưu trữ thông tin người dùng trong `users.json`
- Mỗi user có profile riêng biệt

#### 5. **Progress Tracking**
- Tự động lưu tiến độ level của người chơi
- Theo dõi level đã hoàn thành trong `progress.json`
- Có thể tiếp tục chơi từ level đã đạt được

#### 6. **Undo/Redo System**
- Sử dụng cấu trúc **Stack** để lưu lịch sử di chuyển
- Hoàn tác không giới hạn số lượng bước
- Redo để phục hồi nước đi đã hoàn tác

### 🎨 UI/UX Features

#### 8. **Menu System**
- Homepage với các tùy chọn: Play, Music Button, Play Button
- Level Selection để chọn màn chơi
- Thanh Menu hỗ trợ người chơi: Undo Move, Reset Maze, World Map, Quit Game và Quit to Main
- Màn hình kết quả với các lựa chọn: Undo Move, Reset Maze, World Map, Quit to Main

#### 9. **Multiple Levels**
- Nhiều level với độ khó tăng dần
- Map được thiết kế thủ công, lưu trong `assets/map/`
- Mỗi level có bố trí Enemy và Trap khác nhau

---

## 🚀 Cách Chạy Game

> Trước khi khởi động Game, chúng ta hãy cài đặt Git Bash để clone repository về máy.

### Cài đặt Git Bash

**Bước 1: Tải bộ cài đặt**
```bash
1. Truy cập trang chủ chính thức của Git: https://git-scm.com/downloads
2. Nhấn vào nút "Download for Windows".
3. Chọn phiên bản "64-bit Git for Windows Setup".
```
**Bước 2: Chạy file cài đặt**
```bash
1. Mở file ".exe" vừa tải. 
2. Có thể bấm Next liên tục để cài đặt theo mặc định.
```
**Bước 3: Kiểm tra cài đặt**
```bash
1. Nhấn chuột phải vào màn hình Desktop hoặc một thư mục bất kỳ.
2. Kiểm tra xem có dòng "Open Git Bash Here" trong menu hay không.
3. Nếu có, cài đặt hoàn tất. Ngược lại, hãy làm lại Bước 1.
```

> Sau khi cài đặt xong, chúng ta có 2 phương án để khởi động Game.

### 📦 Phương Án 1: Chạy File Executable (Khuyến nghị)

1. **Clone repository về máy bằng Git Bash**
   ```bash
   Khởi động Git Bash và gõ câu lệnh sau:
   git clone https://github.com/TinyTech-67311/MummyMaze.git
   ```
2. **Khởi động Game**
   ```bash
   Bước 1: Trên cửa sổ Git Bash đó, hãy vào thư mục Mummy Maze bằng cách gõ câu lệnh sau:
   cd Mummy Maze
   Bước 2: Khởi động Game, hãy gõ câu lệnh sau:
   start MummyMaze.exe
   ```
### 🐍 Phương Án 2: Chạy từ Source Code Python

**Yêu cầu:**
- Python 3.12 hoặc 3.13
- pip (Python package manager)

**Các bước thực hiện:**

1. **Clone repository về máy bằng Git Bash**
   ```bash
   Khởi động Git Bash và gõ những câu lệnh sau:
   git clone https://github.com/TinyTech-67311/MummyMaze.git
   cd MummyMaze/source
   ```

2. **Tạo virtual environment** (khuyến nghị)
   ```bash
   Khởi tạo môi trường ảo:
   python -m venv venv

   Kích hoạt môi trường ảo:
   # Windows
   . venv/Scripts/activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Cài đặt dependencies**
   ```bash
   pip install pygame
   ```

4. **Chạy game**
   ```bash
   python main.py
   ```

---
