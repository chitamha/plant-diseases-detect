# MUMMY MAZE - ĐỒ ÁN MÔN CƠ SỞ LẬP TRÌNH

> **Đồ án môn học: Cơ Sở Lập Trình**
> *Một tựa game giải đố chiến thuật được xây dựng với Python và Pygame.*

## 👥 Thành Viên Nhóm

Dự án được thực hiện bởi nhóm **TinyTech-67311** - Khóa K25 - Môn Cơ Sở Lập Trình: 

<table>
<tr>
<td align="center" width="25%">
<img src="https://github.com/identicons/1.png" width="100px;"/><br/>
<b>Huỳnh Văn Phú</b><br/>
<sub>MSSV: 25122036</sub><br/>
<br/>
<i>🎮 Game Logic & Core System</i><br/>
<i>🎯 Gameplay Programming</i>
</td>

<td align="center" width="25%">
<img src="https://github.com/identicons/2.png" width="100px;"/><br/>
<b>Hà Chí Tâm</b><br/>
<sub>MSSV:  25122039</sub><br/>
<br/>
<i>🤖 AI & Pathfinding Algorithm</i><br/>
<i>🧠 Enemy Behavior System</i>
</td>

<td align="center" width="25%">
<img src="https://github.com/identicons/3.png" width="100px;"/><br/>
<b>Thịnh</b><br/>
<sub>MSSV: 25122040</sub><br/>
<br/>
<i>🎨 UI/UX Design</i><br/>
<i>📋 Menu System</i>
</td>

<td align="center" width="25%">
<img src="https://github.com/identicons/4.png" width="100px;"/><br/>
<b>Ngô Phạm Hồng Thức</b><br/>
<sub>MSSV: 25122044</sub><br/>
<br/>
<i>🗺️ Level Design</i><br/>
<i>🎬 Assets Management</i>
</td>
</tr>
</table>

### 📊 Phân Công Công Việc

| Thành viên | Công việc chính | Đóng góp |
|------------|----------------|----------|
| **Huỳnh Văn Phú** | Core Game Logic, Player Controller, Game State Manager | 25% |
| **Hà Chí Tâm** | AI Pathfinding, Enemy System, Collision Detection | 25% |
| **Thịnh** | UI/UX, Menu System, Settings, Sound Manager | 25% |
| **Ngô Phạm Hồng Thức** | Level Design, Assets, Map Parser, Testing | 25% |

---

## 📖 Giới Thiệu (Overview)
**Mummy Maze** là dự án tái hiện tựa game giải đố kinh điển của PopCap.  Trong game, người chơi vào vai nhà thám hiểm **Explorer** bị kẹt trong kim tự tháp bí ẩn và phải tìm đường thoát ra ngoài trong khi tránh những xác ướp (Enemy/Mummy) đang rình rập.

Mỗi bước di chuyển của người chơi sẽ kích hoạt lượt đi của các Enemy theo thuật toán pathfinding, tạo nên những tình huống giải đố đầy thử thách. Game yêu cầu người chơi phải suy nghĩ chiến thuật để tránh bị bắt và tìm ra lối thoát.

### 🛠 Công Nghệ Sử Dụng

| Công nghệ | Phiên bản | Mục đích |
|-----------|-----------|----------|
| **Python** | 3.11+ | Ngôn ngữ lập trình chính |
| **Pygame** | 2.5.2 | Thư viện đồ họa và xử lý game |
| **Công cụ** | - | Công cụ hỗ trợ code game |
| **JSON** | Built-in | Lưu trữ dữ liệu user và progress |
| **Git/GitHub** | - | Quản lý mã nguồn và version control |

---

## ✨ Tính Năng Nổi Bật

### 🎮 Gameplay Features

#### 1. **Hệ Thống Di Chuyển**
- Di chuyển theo 4 hướng: Lên, Xuống, Trái, Phải
- Mỗi bước đi của Player kích hoạt lượt đi của tất cả Enemy
- Hệ thống collision detection chính xác

#### 2. **Algorithm Pathfinding**
- Thuật toán Di chuyển dựa trên chiến lược ưu tiên trục (Tham lam)
- Thuật toán Di chuyển bám theo người chơi bằng đường đi ngắn nhất (BFS)
- Thuật toán Di chuyển ngăn người chơi di chuyển đến lối thoát (BFS)

#### 3. **Hệ Thống Game Objects**
| Đối tượng | Biểu tượng | Chức năng |
|-----------|------------|-----------|
| **Explorer** | 🕵️‍♂️ | Nhân vật chính do người chơi điều khiển |
| **Enemy/Mummy** | 🧟 | Xác ướp tự động truy đuổi người chơi |
| **Key** | 🔑 | Chìa khóa để mở Gate |
| **Gate** | 🚪 | Cửa cần Key để mở |
| **Trap** | ⚠️ | Bẫy gây thua nếu va phải |
| **Stair/Exit** | 🪜 | Điểm thoát hiểm để chiến thắng |
| **Wall** | 🧱 | Tường chắn đường |

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

#### 9. **Visual & Audio**
- Sprite đẹp mắt cho tất cả game objects
- Animation mượt mà cho di chuyển và tương tác
- Background music và sound effects
- Hiệu ứng particle khi thắng/thua

#### 10. **Multiple Levels**
- Nhiều level với độ khó tăng dần
- Map được thiết kế thủ công, lưu trong `assets/map/`
- Mỗi level có bố trí Enemy và Trap khác nhau

---

## 📂 Cấu Trúc Dự Án

## 🚀 Cách Chạy Game

### 📦 Phương Án 1: Chạy File Executable (Khuyến nghị)

**✅ Dễ nhất - Không cần cài đặt Python! **

1. **Download** toàn bộ repository hoặc clone về máy: 
   ```bash
   git clone https://github.com/TinyTech-67311/MummyMaze.git
   cd MummyMaze
   ```

2. **Double-click** vào file `MummyMaze.exe` để chạy game

3. **Đảm bảo** các thư mục `assets/` và `font/` nằm cùng cấp với file `.exe`

> ⚠️ **Lưu ý**: Windows Defender có thể cảnh báo khi chạy file `.exe` từ nguồn không xác định. Chọn **"Run anyway"** để tiếp tục. 

### 🐍 Phương Án 2: Chạy từ Source Code Python

**Yêu cầu:**
- Python 3.10 hoặc 3.11
- pip (Python package manager)

**Các bước thực hiện:**

1. **Clone repository**
   ```bash
   git clone https://github.com/TinyTech-67311/MummyMaze.git
   cd MummyMaze
   ```

2. **Tạo virtual environment** (khuyến nghị)
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
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

## 🎯 Hướng Dẫn Chơi

### 📜 Luật Chơi

1. **Mục tiêu**: Điều khiển Explorer đến **Stair/Exit** (cầu thang) để hoàn thành level

2. **Di chuyển**: 
   - Mỗi lần bạn di chuyển 1 ô, tất cả Enemy cũng di chuyển 1 ô
   - Enemy sẽ tự động đuổi theo bạn theo đường đi ngắn nhất

3. **Thua cuộc khi**:
   - Va chạm với Enemy
   - Dẫm phải Trap
   - Không còn nước đi hợp lệ

4. **Chiến thắng khi**:
   - Đến được Stair/Exit
