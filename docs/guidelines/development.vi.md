# AntiDeepFake - Hướng dẫn Cài đặt & Phát triển (Development Guide)

Tài liệu này hướng dẫn 3 thành viên kỹ thuật trong đội (cũng như Ban giám khảo MoMo TechDay '26 khi kiểm tra mã nguồn) cách thiết lập, chạy ứng dụng và kiểm thử ở môi trường máy cá nhân (local).

---

## 1. Yêu cầu Hệ thống (Prerequisites)
- **Python**: Phiên bản 3.11 hoặc 3.12 (tối ưu cho FastAPI, `aiohttp`, `asyncpg` và `google-genai`).
- **Node.js**: Phiên bản 20+ kèm `npm` (cho giao diện Next.js 14).
- **Công cụ Hệ thống**: Cài đặt sẵn `ffmpeg` trong PATH hệ thống (dùng dưới dạng subprocess thuần; không sử dụng `moviepy`).
- **Docker**: Docker Engine + Compose v2+ (dùng để kiểm thử đóng gói Production).

Kiểm tra cài đặt `ffmpeg` trên Linux/macOS:
```bash
ffmpeg -version
```

---

## 2. Cấu hình Biến Môi trường

1. Tạo file `.env` từ mẫu (tuyệt đối không commit file `.env` thật lên Git):
   ```bash
   cp .env.example .env
   ```
2. Điền đầy đủ các khóa API cần thiết vào file `.env`:
   - `SIGHTENGINE_API_USER` và `SIGHTENGINE_API_SECRET`
   - `GOOGLE_API_KEY` (Từ Google AI Studio cho `gemini-3.5-transcribe` qua Interactions API)
   - `OPENROUTER_API_KEY` (Từ OpenRouter cho `pplx-decider-flash-v1.3:free` tại `/api/alpha/decisions`)
   - `DATABASE_URL` (Chuỗi Supavisor IPv4 Pooler cổng `6543`) cùng `SUPABASE_URL` / `SUPABASE_SERVICE_KEY`
   - Tùy chọn: `HF_TOKEN` (Dự phòng Hugging Face khi Sightengine quá tải)

---

## 3. Khởi chạy Backend và Frontend trên Local

### Khởi chạy Backend (FastAPI)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Chạy máy chủ FastAPI ở cổng 8000
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

# Kiểm tra tình trạng API
curl http://127.0.0.1:8000/health
```

### Khởi chạy Frontend (Next.js)
```bash
cd frontend
npm ci
# Đảm bảo biến NEXT_PUBLIC_API_BASE_URL trỏ thẳng tới Backend (http://127.0.0.1:8000)
npm run dev
# Truy cập trình duyệt tại http://127.0.0.1:3000
```

---

## 4. Chiến lược Kiểm thử (Ưu tiên Offline, Giới hạn Chạy Thật)

### 4.1. Kiểm thử Unit Test & Hợp đồng Offline (Không tốn Quota API)
Toàn bộ bài test tự động đều giả lập (mock) phản hồi của Sightengine, Google `google-genai` và OpenRouter. Hãy chạy thường xuyên khi viết code:
```bash
# Kiểm tra pipeline, luồng SSE, che PII, quote grounding và rolling context
python -m unittest discover -s tests -p "test_*.py"
```

### 4.2. Kiểm tra Kết nối Thực tế Có Giới hạn (`--live`)
Để kiểm chứng khóa API thật và xác minh gói Sightengine Free có hỗ trợ `models=deepfake` hay không mà không làm cạn quota, chạy lệnh kiểm tra giới hạn (chỉ gửi 1 ảnh, 1 audio, 1 state và dọn sạch `files.delete()`):
```bash
python -m backend.smoke_test --live
```

---

## 5. Mô phỏng Đóng gói Docker Production

Build và chạy thử nghiệm Docker image giống hệt môi trường Render Production (kiểm tra quyền non-root, tích hợp `ffmpeg` và mức chiếm dụng dưới 512 MB RAM):
```bash
docker build -t antideepfake-api -f Dockerfile .
docker run --rm -p 8000:8000 --env-file .env antideepfake-api
```
