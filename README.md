# Intel Core Hybrid Architecture Scheduler Optimizer for Windows 10

Bộ công cụ CLI và tự động hóa chuyên sâu (Senior Windows Systems Engineering) dành cho hệ điều hành **Windows 10**, tối ưu hóa hoàn hảo cho các bộ vi xử lý **Intel Core thế hệ 12 (Alder Lake), thế hệ 13 (Raptor Lake) và thế hệ 14 (Raptor Lake Refresh)** với kiến trúc lai kết hợp nhân hiệu năng cao (**P-core**) và nhân tiết kiệm điện (**E-core**).

---

## 1. BẢN CHẤT VẤN ĐỀ TRÊN WINDOWS 10 (TECHNICAL ROOT CAUSE)

Khác với Windows 11 được thiết kế với cơ chế tích hợp sâu cùng phần cứng **Intel Thread Director (ITD)**, bộ lập lịch (Windows Scheduler) của **Windows 10 được phát triển từ thời kỳ vi xử lý đồng nhất (Homogeneous Cores)**. Khi chạy trên CPU kiến trúc lai (Heterogeneous big.LITTLE):

1. **Hiện tượng điều phối luồng sai lệch (Thread Misplacement):**
   - Windows 10 scheduler thường không nhận biết chính xác luồng nào của game đòi hỏi xung nhịp cao và IPC mạnh.
   - Rất nhiều game nặng (CS2, Valorant, Cyberpunk 2077, GTA V,...) hoặc các luồng render chính của game bị ném ngẫu nhiên sang **E-core**.
   - Hậu quả: Hiện tượng **tụt FPS đột ngột, giật khung hình (Micro-stuttering) và 1% Low FPS cực kỳ thấp**, dù GPU và CPU đều rất mạnh.
2. **Tranh chấp tài nguyên giữa Game và Ứng dụng nền:**
   - Discord, Chrome, Spotify, OBS, Riot Client chạy đè lên các luồng P-core làm gián đoạn bộ nhớ đệm L3 Cache của P-core, gây trễ khung hình (Frame latency spike).
3. **Các thiết lập Heterogeneous ẩn trong Windows 10:**
   - Mặc định, Windows 10 ẩn toàn bộ các thuộc tính điều phối năng lượng và luồng lai (`SCHEDPOLICY` và `SHORTSCHEDPOLICY`), đồng thời để mặc định ở mức `Automatic (0x5)` – vốn hoạt động rất kém trên Windows 10.

---

## 2. KIẾN TRÚC GIẢI PHÁP 2 TẦNG (TWO-TIER ARCHITECTURE)

Bộ công cụ này xử lý triệt để bài toán thông qua mô hình tối ưu 2 tầng:

```
+-----------------------------------------------------------------------------+
|                  INTEL HYBRID SCHEDULER OPTIMIZER (WIN 10)                  |
+-----------------------------------------------------------------------------+
                                       |
       +-------------------------------+-------------------------------+
       |                                                               |
[TẦNG 1: KERNEL SCHEDULER POLICY]                   [TẦNG 2: HARD PROCESS AFFINITY]
- Mở khóa GUID ẩn trong Powercfg                    - P/Invoke GetLogicalProcessorInfoEx
- 93b8b6dc-0698-4d1c-9ee4-0644e900c85d              - Tính toán Bitmask động (Dynamic Mask)
  -> Prefer performant processors (0x2)             - Game -> 100% P-Core (Mask: 0x0FFF, v.v.)
- bae08b81-2d5e-4688-ad6a-13243356654b              - Background Apps -> E-Core (Mask: 0xF000)
  -> Prefer efficiency processors (0x4)             - Watchdog Daemon thời gian thực (<0.01% CPU)
```

### Tầng 1: Heterogeneous Power Policy (Cấp độ OS Kernel Power Engine)
- Can thiệp vào hệ thống quản lý nguồn điện của vi xử lý (`54533251-82be-4824-96c1-47b60b740d00` / `SUB_PROCESSOR`).
- Mở khóa Registry `Attributes = 2` để hiển thị trong Windows Power Options.
- Thiết lập:
  - **Heterogeneous thread scheduling policy** = `2` (`Prefer performant processors`): Bắt buộc bộ lập lịch hệ điều hành luôn ưu tiên phân bổ các tác vụ nặng vào P-core trước tiên.
  - **Heterogeneous short running thread scheduling policy** = `4` (`Prefer efficiency processors`): Tự động điều hướng các luồng thực thi ngắn, tiến trình chạy chớp nhoáng ngầm sang E-core.

### Tầng 2: Rule-Based CPU Affinity Bitmask Lock & Priority Steering
- Quét thông tin Topology trực tiếp qua Win32 API Kernel `GetLogicalProcessorInformationEx`:
  - Phân tích cờ `EfficiencyClass` và `SMT/HyperThreading` của từng Core.
  - Tính toán động **P-Core Affinity Mask** và **E-Core Affinity Mask** (tương thích mọi dòng CPU từ i5-12400, i5-13400, i5-13600K, i7-13700K, i9-13900K đến i9-14900K, CPU Laptop dòng H/HX).
- **Hard Affinity Lock:**
  - Game trong `HighPriority_Games`: Khóa 100% vào các luồng P-core (CPU 0 -> CPU `[(P-core x 2) - 1]`), cách ly hoàn toàn khỏi E-core, nâng Process Priority lên `High`.
  - Ứng dụng trong `Background_Apps` (Discord, Chrome, Spotify, OBS, Steam,...): Đẩy toàn bộ sang E-core, hạ Process Priority xuống `BelowNormal`.
- Hai chế độ điều hành:
  1. **Quick Apply:** Quét và gán 1 lần cho toàn bộ tiến trình đang mở.
  2. **Watchdog Daemon:** Vòng lặp ngầm thông minh định kỳ (3 giây), có bộ nhớ đệm PID Cache (< 0.01% CPU overhead), tự động phát hiện và gán ngay lập tức khi người dùng bật game.
  3. **Windows Scheduled Task:** Tùy chọn cài đặt Watchdog tự chạy ngầm cùng Windows khi đăng nhập với quyền Administrator ẩn (`-WindowStyle Hidden`).

---

## 3. CÁC TÍNH NĂNG CHÍNH

- **Tự động nhận diện phần cứng & Topology:**
  - Nhận diện model chip, nhận diện thế hệ Intel (Gen 12, 13, 14, Core Ultra).
  - Bảng hiển thị trực quan chi tiết từng Core (P-Core/E-Core, SMT, ID luồng logic, Hex Mask).
- **Tự động nâng quyền UAC Administrator:**
  - Tự kiểm tra quyền hạn; nếu chưa phải Admin, script tự bật hộp thoại UAC để xin quyền.
- **Bảo vệ chống crash Anti-Cheat:**
  - Bắt lỗi thông minh đối với các game có Anti-Cheat cấp Kernel (Vanguard, Easy Anti-Cheat). Nếu game chặn thay đổi Affinity từ user-mode, công cụ sẽ ghi nhận cảnh báo và dựa vào Tầng 1 (Kernel Power Policy) để điều phối thay thế.
- **🎨 Color Studio (Chỉnh Màu Game Riêng Biệt & 0ms Zero-Bleed) [MỚI]:**
  - **Lấy cảm hứng từ vibranceGUI nhưng tinh chỉnh sâu hơn:** Tích hợp trực tiếp công nghệ Digital Vibrance từ NVIDIA Driver qua native NVAPI kết hợp Win32 Hardware Gamma Ramp.
  - **Khắc phục triệt để hiện tượng lem màu (Zero-Bleed):** Không sử dụng vòng lặp polling 200-500ms như vibranceGUI, mà sử dụng cơ chế lắng nghe sự kiện WinEvent Hook `EVENT_SYSTEM_FOREGROUND` phản hồi 0ms. Khi người dùng Alt-Tab sang Desktop, Discord, Chrome,... màu sắc màn hình lập tức trở về chuẩn desktop neutral.
  - **Cách ly đa màn hình (Multi-Monitor Isolation):** Chỉ áp dụng biến đổi màu trên màn hình hiển thị game, giữ nguyên 100% màu chuẩn cho các màn hình phụ (Discord, OBS, chat stream).
  - **Bộ tinh chỉnh sâu (Deeper Visual Tuning):**
    - *Digital Vibrance (50% - 100%):* Đẩy độ rực rỡ màu sắc qua driver NVIDIA.
    - *Black Equalizer / Shadow Boost (0.50x - 2.00x):* Rọi sáng các góc tối, đường hầm trong game FPS mà không làm cháy sáng các vùng trời.
    - *Contrast & Brightness (-0.50 -> +0.50):* Tăng độ sắc nét và tách bạch hình ảnh.
    - *Cân bằng kênh màu RGB Gain (0.50x - 1.50x):* Nâng Red Gain để làm viền đỏ địch phát sáng rõ rệt (Valorant/CS2) hoặc cân chỉnh Blue Gain chống mỏi mắt.
  - **100% Anti-Cheat Safe:** Hoạt động hoàn toàn ở tầng Driver GPU và Win32 Display layer, tuyệt đối không tiêm DLL, không can thiệp DirectX/Direct3D, an toàn tuyệt đối với Valve Anti-Cheat (VAC), Riot Vanguard, Easy Anti-Cheat (EAC), BattlEye.
- **🖥️ Display & Hz Studio (Chỉnh Resolution & Tần Số Quét) [MỚI]:**
  - **Quản lý toàn diện 170 Display Modes:** Quét toàn bộ phần cứng màn hình (AOC 24" 240Hz), tự động nhận diện và phân loại thông minh các độ phân giải:
    - *🌟 Esport 4:3 (Stretched):* `1280x960 @ 240Hz (CS2 Standard)`, `1440x1080 @ 240Hz (HD Stretched)`, `1024x768 @ 240Hz (Classic Pro)`.
    - *🖥️ Chuẩn 16:9 (Native Widescreen):* `1920x1080 @ 240Hz (Full HD)`, `1600x900 @ 240Hz`, `1280x720 @ 240Hz`.
    - *📐 Cạnh Tranh 16:10:* `1680x1050 @ 240Hz`, `1440x900 @ 240Hz`.
  - **Khóa & Ép Tần Số Quét Tối Đa (Max Hz Enforcer):** 1-Click đưa màn hình lên `240Hz` tối đa của phần cứng, ngăn ngừa triệt để lỗi tự tụt về `60Hz` của Windows 10 sau khi update driver hay cắm lại dây DisplayPort.
  - **Bộ đếm ngược an toàn 15 giây (15-Second Safety Revert Guard):** Khi thử nghiệm độ phân giải mới trong giao diện, hệ thống hiển thị đếm ngược 15 giây. Nếu không bấm xác nhận, màn hình sẽ tự động hoàn tác về độ phân giải cũ, chống 100% nguy cơ đen màn hình hoặc Out of Range.
  - **Đồng bộ tự động theo Game (0ms Zero-Bleed Sync):** Tự động chuyển độ phân giải (như `1280x960 4:3 @ 240Hz`) khi vào CS2, và ngay lập tức trả về `1920x1080 @ 240Hz` Native khi Alt-Tab ra Desktop hoặc thoát game.
- **An toàn & Sao lưu (Backup & 1-Click Revert):**
  - Tự động sao lưu Power Scheme và Registry trước khi thay đổi vào thư mục `Backups/`.
  - Tính năng Revert khôi phục toàn bộ thiết lập về mặc định của Windows 10 và trả lại toàn bộ Cores cho ứng dụng.
- **Giao diện CLI chuyên nghiệp:**
  - Bảng điều khiển màu sắc trực quan (Xanh: Tối ưu/Thành công, Vàng: Cảnh báo, Đỏ: Lỗi).

---

## 4. HƯỚNG DẪN SỬ DỤNG NHANH (QUICK START)

### Cách 1: Khởi động Ứng dụng Desktop App (.exe) (Khuyến nghị số 1)
Nhấp đúp chuột trực tiếp vào file:
```
IntelHybridOptimizer.exe
```
- Ứng dụng có sẵn **UAC Manifest**, Windows sẽ tự động hỏi cấp quyền Administrator khi mở.
- Giao diện **Modern Dark UI** trực quan, hiển thị toàn bộ thông số CPU, thanh trạng thái Power Plan và Topology chi tiết.
- Tích hợp **Khay hệ thống (System Tray)**: Khi bạn thu nhỏ hoặc đóng cửa sổ, ứng dụng sẽ tự động ẩn xuống cạnh đồng hồ Windows và chạy ngầm Watchdog giám sát thời gian thực.
- Khi bạn mở bất kỳ game nào (CS2, Valorant, GTA V,...), ứng dụng sẽ tự động hiện thông báo Balloon Tip: *"Phát hiện Game! Đã khóa vào 100% P-Core."*

### Cách 2: Khởi động 1-Click qua Launcher .bat
Nhấp đúp chuột vào:
```
Run_Optimizer.bat
```
Script sẽ tự động kiểm tra và ưu tiên mở ứng dụng `IntelHybridOptimizer.exe` (hoặc mở script PowerShell nếu máy không có .NET runtime).

### Cách 3: Chạy qua PowerShell CLI Menu
Mở PowerShell với quyền Administrator:
```powershell
Set-Location "C:\Users\lehie\Documents\win 10 for intel"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\IntelHybridOptimizer.ps1
```

### Cách 4: Chế độ Dòng Lệnh Tự Động (CLI Automation)
Bạn có thể gọi trực tiếp file `.exe` hoặc `.ps1` từ Command Prompt / PowerShell:
```cmd
# Kiểm tra CPU & Topology
IntelHybridOptimizer.exe --check

# Tối ưu Power Policy
IntelHybridOptimizer.exe --apply

# Quick Apply Affinity ngay lập tức
IntelHybridOptimizer.exe --quick

# Khôi phục cài đặt gốc Windows 10
IntelHybridOptimizer.exe --revert
```

---

## 5. CẤU HÌNH FILE `config.json`

File `config.json` nằm cùng thư mục với script, cho phép bạn dễ dàng thêm các tựa game hoặc ứng dụng nền yêu thích:

```json
{
  "Settings": {
    "WatchdogIntervalSeconds": 3,
    "AutoSetProcessPriority": true,
    "GameProcessPriority": "High",
    "BackgroundProcessPriority": "BelowNormal",
    "LoggingLevel": "Detailed"
  },
  "HighPriority_Games": [
    "cs2.exe",
    "valorant.exe",
    "Cyberpunk2077.exe",
    "dota2.exe",
    "GTA5.exe",
    "League of Legends.exe",
    "BlackMythWukong.exe",
    "helldivers2.exe"
  ],
  "Background_Apps": [
    "discord.exe",
    "chrome.exe",
    "msedge.exe",
    "spotify.exe",
    "obs64.exe",
    "Steam.exe"
  ]
}
```

Bạn cũng có thể thêm game/app trực tiếp thông qua **Tùy chọn [6]** trong Menu CLI của công cụ.

---

## 6. CÁC TÙY CHỌN TRONG MENU CHÍNH

```
================================================================================
        INTEL CORE HYBRID SCHEDULER OPTIMIZER CHO WINDOWS 10 (CLI)            
       Khắc phục triệt để tụt FPS & giật lag trên Intel Gen 12 / 13 / 14        
================================================================================
 [+] CPU Model       : 13th Gen Intel(R) Core(TM) i5-13400F
 [+] Kiến trúc CPU   : Intel Core Gen 13 (Raptor Lake)
 [+] Topology Phần cứng: 10 Nhân vật lý | 16 Luồng logic
     -> P-Core (Hiệu năng): 6 Cores (12 Threads) | Mask: 0xFFF
     -> E-Core (Tiết kiệm): 4 Cores (4 Threads)  | Mask: 0xF000
 [+] Power Scheme    : Revision - Ultra Performance
 [+] Thread Sched    : Prefer performant processors (0x2) [TỐI ƯU]
 [+] Short Thread    : Prefer efficiency processors (0x4) [TỐI ƯU]
 [+] Startup Watchdog: Ready (Đã cài đặt)
================================================================================
 [1] Xem chi tiết bảng phân bố Core Topology & Luồng logic
 [2] Mở khóa & Kích hoạt Heterogeneous Power Policy (Khuyến nghị)
 [3] Quick Apply: Gán CPU Affinity ngay cho các Game & App đang chạy
 [4] Chạy Watchdog Daemon (Giám sát thời gian thực trực tiếp trên màn hình)
 [5] Cài đặt / Gỡ bỏ Watchdog tự khởi động ngầm cùng Windows (Scheduled Task)
 [6] Quản lý danh sách Game & Background Apps (config.json)
 [7] Sao lưu cấu hình hiện tại (Backup Power Scheme & Registry)
 [8] Khôi phục cài đặt gốc ban đầu của Windows 10 (Revert / Reset All)
 [0] Thoát chương trình
================================================================================
```

---

## 7. CÂU HỎI THƯỜNG GẶP (FAQ)

**Q: Công cụ này có gây hại cho CPU hoặc làm mất bảo hành không?**  
*A: Hoàn toàn không. Công cụ chỉ sử dụng các Windows API chính thống của Microsoft (`powercfg`, Win32 `SetProcessAffinityMask`), không ép xung (overclock) hay can thiệp điện áp (voltage).*

**Q: CPU của tôi là i5-12400F (thuần 6 P-Core, không có E-Core) thì có dùng được không?**  
*A: Có. Công cụ tự động phát hiện CPU không có E-core (`EcoreCount = 0`), tự động thích ứng để tối ưu hóa Power Policy và giữ nguyên toàn bộ các luồng P-core mà không gây lỗi.*

**Q: Làm thế nào để quay lại mặc định ban đầu của Windows?**  
*A: Chọn **[8]** trong Menu CLI hoặc chạy `.\IntelHybridOptimizer.ps1 -Revert`. Mọi thiết lập Power Plan và Affinity sẽ được trả về trạng thái xuất xưởng của Windows 10.*
