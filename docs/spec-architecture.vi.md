# AntiDeepFake - Đặc tả Kiến trúc Kỹ thuật (Technical Architecture Specification)

## 1. Sơ đồ Kiến trúc Triển khai Production (Bản vẽ Draw.io Blueprint)

Hệ thống được tổ chức thành 4 phân tầng độc lập (Tiers) theo phong cách thiết kế Draw.io chuyên nghiệp:
1. **Phân tầng Frontend (Vercel & Cloudflare)**: Phân phối toàn cầu qua Edge CDN, xử lý SSL và giao diện người dùng thời gian thực.
2. **Phân tầng Backend Compute (Render & Docker)**: Container FastAPI siêu nhẹ tích hợp ffmpeg để bóc tách video 5 giây.
3. **Phân tầng Dữ liệu & Lưu trữ Video (Supabase)**: Lưu trữ video mẫu trên Supabase Storage và cơ sở dữ liệu Supabase PostgreSQL.
4. **Phân tầng AI Serverless Bên ngoài**: Hệ sinh thái 3 model (Sightengine CV + Google Gemini STT + OpenRouter PPLX Decider).

```text
+---------------------------------------------------------------------------------------------------------------------------------------------------+
|                                                     TỔNG QUAN KIẾN TRÚC TRIỂN KHAI PRODUCTION                                                     |
+---------------------------------------------------------------------------------------------------------------------------------------------------+
|                                                                                                                                                   |
|  [Ban Giám Khảo / User] ----(1. Chọn / Phát Video)----> [Frontend: Vercel + Cloudflare]                                                           |
|  [Ban Giám Khảo / User] <---(5. Cập nhật Timeline 5s)-- [Frontend: Next.js 14 App Router]                                                         |
|                                                                     |                                                                             |
|                                                            (2. Gửi block 5 giây)                                                                  |
|                                                                     |                                                                             |
|                                                                     v                                                                             |
|  +------------------------------------+   +------------------------------------------------------+   +-----------------------------------------+  |
|  |           FRONTEND TIER            |   |               BACKEND COMPUTE TIER                   |   |          DATA & STORAGE TIER            |  |
|  |       (Vercel & Cloudflare)        |   |                 (Render & Docker)                    |   |               (Supabase)                |  |
|  +------------------------------------+   +------------------------------------------------------+   +-----------------------------------------+  |
|  | - Cloudflare (DNS + SSL + CDN)     |   | - FastAPI Web Service (Cổng 8000)                    |   | - Supabase Storage:                     |  |
|  | - Vercel Edge Network              |   | - Docker Image (python:3.11-slim + ffmpeg)           |   |   Bucket: sample-videos (Chứa file MP4) |  |
|  | - Next.js 14 App Router:           |   | - Luồng xử lý Cửa sổ 5 giây:                         |   | - Supabase PostgreSQL Database:         |  |
|  |   * Trình phát Video (Player)      |   |   * Cắt keyframes hình ảnh bằng ffmpeg               |   |   Bảng: analysis_logs (Lưu kết quả)     |  |
|  |   * Live 5s Risk Timeline          |   |   * Bóc tách đoạn âm thanh bằng ffmpeg               |   |   Bảng: test_cases (Pre-cached demo)    |  |
|  |   * Khung cảnh báo (Alert Badges)  |   |   * Bộ điều phối song song (aiohttp async)           |   |   Bảng: user_sessions (Phiên làm việc)  |  |
|  +------------------------------------+   +--------------------------+---------------------------+   +-----------------------------------------+  |
|                                                                       |                                                   ^                       |
|                                                              (3. Gọi AI song song)                             (4. Ghi log / Đọc cache)           |
|                                                                       |                                                   |                       |
|                                                                       v                                                   |                       |
|                                           +------------------------------------------------------+                        |                       |
|                                           |             EXTERNAL SERVERLESS AI TIER              |                        |                       |
|                                           +------------------------------------------------------+                        |                       |
|                                           | - Sightengine Deepfake API: Điểm face-swap (0.0-1.0) | -----------------------+                       |
|                                           | - Google Gemini 3.5 Transcribe: Chép lời tiếng Việt  |                                                |
|                                           | - OpenRouter pplx-decider-flash: Quyết định Choice   |                                                |
|                                           +------------------------------------------------------+                                                |
+---------------------------------------------------------------------------------------------------------------------------------------------------+
```

---

## 2. Bảng Phân bổ Thành phần Công nghệ

| Phân tầng | Thành phần | Công nghệ / Nền tảng | Vai trò và Trách nhiệm |
|---|---|---|---|
| **Frontend** | DNS & CDN | Cloudflare Free Plan | Quản lý tên miền, chống DDoS, cấp chứng chỉ SSL và tối ưu bộ nhớ đệm |
| **Frontend** | Web Hosting | Vercel (Hobby Tier) | Chạy Next.js 14 App Router, hiển thị giao diện phát video và timeline rủi ro |
| **Backend** | Compute | Render / Docker | Chạy container Python 3.11-slim tích hợp ffmpeg để trích xuất ảnh và âm thanh 5s |
| **Backend** | Điều phối API | FastAPI + aiohttp | Điều phối các luồng gọi API bất đồng bộ không nghẽn và tổng hợp kết quả |
| **Storage** | Lưu trữ Video | Supabase Storage | Bucket công khai `sample-videos` lưu trữ 3 video MP4 mẫu, miễn phí băng thông |
| **Database**| Cơ sở dữ liệu | Supabase PostgreSQL | Lưu trữ lịch sử phân tích, kết quả tính toán sẵn (cache) và phiên làm việc |
| **AI (CV)** | Deepfake CV | Sightengine REST API | Mô hình thị giác chuyên biệt nhận diện face-swap, trả về xác suất chuẩn (0.0 - 1.0) |
| **AI (STT)**| Chép lời | Google Gemini 3.5 Transcribe | Mô hình STT tiếng Việt độ trễ thấp có mốc thời gian từng từ |
| **AI (Logic)**| Quyết định | OpenRouter pplx-decider-flash | Mô hình System One đánh giá câu hỏi Choice để đưa ra nhãn cảnh báo chính xác |

---

## 3. Trình tự Luồng Dữ liệu (Sequential Data Flow)

1. **Bước 1: Tải và Phát Video**: Ban giám khảo truy cập ứng dụng web trên Vercel. Video mẫu được phát trực tiếp từ **Supabase Storage** (Bucket `sample-videos`) với tốc độ cao.
2. **Bước 2: Cắt lát 5 giây (Windowing)**: Trình duyệt hoặc Backend chia luồng video thành các khối 5 giây (dùng `ffmpeg` để tách ra file âm thanh `.mp3` và 2 - 3 khung hình `.jpg`).
3. **Bước 3: Gọi AI song song (Parallel AI Inference)**:
   - Gửi âm thanh tới **Google Gemini 3.5 Transcribe** -> Nhận transcript tiếng Việt.
   - Gửi ảnh khung hình tới **Sightengine API** -> Nhận `deepfake_score`.
4. **Bước 4: Quyết định Rủi ro**:
   - Đóng gói nội dung nói và điểm số deepfake thành chuỗi State.
   - Gửi tới **OpenRouter (`pplx-decider-flash-v1.3:free`)** với câu hỏi lựa chọn (Choice Question).
   - Decision Model trả về xác suất và nhãn quyết định (`normal`, `visual_alert_only`, `verbal_pressure_only`, `confirmed_scam`).
5. **Bước 5: Cập nhật Timeline**: Backend lưu log vào **Supabase PostgreSQL** và đẩy kết quả JSON về giao diện để cập nhật màu sắc mốc 5 giây trên thanh Timeline.

---

## 4. Hướng dẫn Bố cục để Vẽ lại trên Draw.io

Khi vẽ lại trên giao diện Draw.io:
- **Phía trên bên trái**: Biểu tượng người dùng / Ban giám khảo (Actor: User / Judge).
- **Phía trên bên phải**: Biểu tượng lập trình viên (Actor: DevOps với mũi tên git push tới Vercel/Render).
- **Khung bao ngoài lớn**: Đặt tên "AntiDeepFake Cloud Ecosystem".
- **Hàng 1 - Cột 1**: "Frontend Tier" (Logo Vercel hình tam giác, Logo Cloudflare đám mây, Logo Next.js).
- **Hàng 1 - Cột 2**: "Backend Serverless Compute" (Logo Render / Logo cá voi Docker, Logo FastAPI, Icon ffmpeg).
- **Hàng 1 - Cột 3**: "Data & Video Storage Tier" (Logo Supabase màu xanh ngọc, Icon Bucket Storage chứa video MP4, Icon con voi PostgreSQL).
- **Khung đáy lớn**: "Managed AI Services" (Logo Sightengine, Logo Google AI Studio, Logo OpenRouter / Perplexity).
- **Mũi tên liên kết**: Mũi tên nét liền cho luồng dữ liệu (1 đến 5), mũi tên nét đứt cho luồng triển khai CI/CD.
