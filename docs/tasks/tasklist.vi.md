# AntiDeepFake - Danh sách Công việc theo Vai trò (Tasklist)

Tài liệu phân rã công việc cho 3 thành viên kỹ thuật, đồng bộ hoàn toàn với `docs/specs/spec-api-contract.vi.md` (v1.1 SSE) và `docs/validation/validation-plan.vi.md`.

---

## 1. Tóm tắt Phân công Vai trò

```text
+-----------------------+----------------------------------+----------------------------------+
|      KỸ SƯ AI         |   KỸ SƯ BACKEND 1 (PIPELINE)     |   KỸ SƯ BACKEND 2 (NỀN TẢNG)     |
+-----------------------+----------------------------------+----------------------------------+
| - Sightengine + Sem(1)| - Cắt ffmpeg thuần (bỏ moviepy)  | - FastAPI SSE & Direct CORS      |
| - google-genai STT    | - Ngữ cảnh trượt & Che PII       | - Supabase IPv4 Pooler & Storage |
| - OpenRouter Decisions| - Quote grounding & Dọn file tạm | - Lớp Cache tính toán sẵn        |
| - Chuẩn bị 3 clip mẫu | - Unit Test mock offline T01-T12 | - Docker non-root & Warm-up ping |
+-----------------------+----------------------------------+----------------------------------+
```

---

## 2. Danh sách Công việc của Kỹ sư AI (AI Engineer)

| Mã Task | Mô tả Công việc | Sprint | Mức ưu tiên | Tiêu chí Nghiệm thu (Acceptance Criteria) | Trạng thái |
|---|---|---|---|---|---|
| **AI-101** | Kết nối Sightengine + Semaphore + Dự phòng HF | Sprint 1 | P0 | Gửi 1 ảnh sắc nét/5s qua `Semaphore(1)` (giãn `1.1s`), trả `cv_score` (`[0.0, 1.0]`) hoặc `insufficient_visual_data`, có dự phòng HF `SigLIP2` | Chưa làm |
| **AI-102** | Kết nối `gemini-3.5-transcribe` (`google-genai`) | Sprint 1 | P0 | Dùng `files.upload()` + `interactions.create()` (`v1beta`), bắt buộc gọi `files.delete()` trong `finally` (`R08`) | Chưa làm |
| **AI-103** | Tích hợp OpenRouter Decisions API | Sprint 1 | P0 | Gửi tới `POST https://openrouter.ai/api/alpha/decisions` dùng từ điển `questions` (`choice`), cách ly lời thoại không tin cậy (`R07`) | Chưa làm |
| **AI-104** | Chuẩn bị 3 Video Thử nghiệm Chính thức | Sprint 1 | P0 | 3 file MP4: Ca 1 (Ghép mặt lừa đảo), Ca 2 (Người thật lừa đảo), Ca 3 (Mạng lag an toàn) | Chưa làm |
| **AI-105** | Viết Script Kiểm tra `--live` (`backend/smoke_test.py`) | Sprint 1 | P0 | Test đúng 1 ảnh, 1 audio, 1 state; xác minh gói Free Sightengine chạy được `models=deepfake` và kiểm tra `files.delete()` | Chưa làm |
| **AI-106** | Hiệu chỉnh Ngưỡng & Ngữ cảnh Trượt | Sprint 2 | P1 | Tinh chỉnh `CV_DEEPFAKE_THRESHOLD` (0.60) và `VERBAL_PRESSURE_THRESHOLD` (0.70); pass T01–T04 và T11 | Chưa làm |
| **AI-107** | Đo Độ trễ Thực tế & Kịch bản Demo 3 phút | Sprint 3 | P0 | Ghi nhận thông số `p50`/`p95` thực tế của từng API và viết lời thoại thuyết minh cho video demo | Chưa làm |

---

## 3. Danh sách Công việc của Kỹ sư Backend 1 (Trưởng nhóm Pipeline & Xử lý Video)

| Mã Task | Mô tả Công việc | Sprint | Mức ưu tiên | Tiêu chí Nghiệm thu (Acceptance Criteria) | Trạng thái |
|---|---|---|---|---|---|
| **BE1-201** | Cắt Video 5s bằng `ffmpeg` Thuần & Dọn Tạm | Sprint 1 | P0 | Dùng `asyncio.create_subprocess_exec("ffmpeg", ...)` (không `moviepy`), lưu tạm `/tmp/adf_<uuid>/`, xóa sạch trong `finally` (`R08`) | Chưa làm |
| **BE1-202** | Xây dựng Bộ lọc Che Dữ liệu Nhạy cảm (`R05`) | Sprint 1 | P0 | Regex thay thế SĐT, số tài khoản, CCCD và OTP thành `[REDACTED_NUM]` trước khi gọi OpenRouter | Chưa làm |
| **BE1-203** | Ngữ cảnh Trượt & Kiểm chứng Câu trích (`R01`, `R06`) | Sprint 1 | P0 | Ghép `previous_transcript + current_transcript` đã che PII làm State; xác minh `trigger_quote` tồn tại trong transcript (`T07`, `T11`) | Chưa làm |
| **BE1-204** | Xây dựng Generator Stream Async cho Từng Block 5s | Sprint 1 | P0 | Async generator chạy song song CV/STT trong mỗi block 5s và đẩy dần từng `WindowEvaluation` ra ngoài | Chưa làm |
| **BE1-205** | Xử lý Timeout, Rate-Limit & Fallback | Sprint 2 | P1 | Giới hạn timeout 10s/API, retry hữu hạn, trả về `evaluation_incomplete` / `provider_error` an toàn (`T10`) | Chưa làm |
| **BE1-206** | Viết Bộ Unit Test Mock Offline (Gate 1) | Sprint 2 | P0 | Bộ `unittest` giả lập toàn bộ kịch bản `T01`–`T12` (gồm cả kiểm tra mock gọi `files.delete()`) không tốn chi phí | Chưa làm |
| **BE1-207** | Đo Kiểm Giới hạn RAM 512 MB trên Render | Sprint 3 | P1 | Kiểm tra mức RAM khi có upload 15 MB đồng thời, đảm bảo luôn nằm dưới ngưỡng an toàn 400 MB | Chưa làm |

---

## 4. Danh sách Công việc của Kỹ sư Backend 2 (Trưởng nhóm Nền tảng, Database & Triển khai)

| Mã Task | Mô tả Công việc | Sprint | Mức ưu tiên | Tiêu chí Nghiệm thu (Acceptance Criteria) | Trạng thái |
|---|---|---|---|---|---|
| **BE2-301** | Khởi tạo Supabase DB (IPv4 Pooler `6543`) | Sprint 1 | P0 | Chạy SQL DDL (`test_cases`, `analysis_logs`); kết nối bằng `asyncpg` qua Supavisor IPv4 Pooler (`6543`) hoặc `supabase-py` HTTPS | Chưa làm |
| **BE2-302** | Cấu hình Supabase Storage Bucket | Sprint 1 | P0 | Tạo bucket công khai `sample-videos`, upload 3 clip mẫu và kiểm tra stream range-request + CORS | Chưa làm |
| **BE2-303** | Dựng FastAPI & Bộ Kiểm tra Trước Stream | Sprint 1 | P0 | Cài đặt `/health`, `/ready`, bật CORS (`APP_ORIGIN`), chuẩn hóa JSON lỗi (`400`, `413` > 15MB, `422` > 30s, `429`, `503`) | Chưa làm |
| **BE2-304** | Xây dựng API SSE `/analyze` & Dữ liệu Mẫu | Sprint 2 | P0 | Cài đặt `POST /api/v1/analyze` (`StreamingResponse` `text/event-stream` phát `window` + `summary`), `GET /api/v1/cases`, `GET /api/v1/logs` | Chưa làm |
| **BE2-305** | Nạp Cache Tính toán Sẵn cho 3 Ca Demo | Sprint 2 | P0 | Chạy phân tích sẵn 3 video mẫu và lưu kết quả JSON vào bảng `test_cases` để demo với độ trễ 0ms | Chưa làm |
| **BE2-306** | Đóng gói Docker Non-Root & Deploy Render | Sprint 2 | P0 | Viết `Dockerfile` (`python:3.11-slim` + `ffmpeg`, không cài `moviepy`, quyền non-root), triển khai lên Render HTTPS | Chưa làm |
| **BE2-307** | Tích hợp Next.js Vercel Direct-CORS & SSE | Sprint 2 | P1 | Nối Video Player + SSE Stream Reader + Warm-up ping `GET /health` khi mở trang; né trần 4.5 MB của Vercel Proxy | Chưa làm |
| **BE2-308** | Đóng gói Mã nguồn `.zip` & Hoàn thiện `README` | Sprint 3 | P0 | Xuất file `.zip` sạch sẽ, liệt kê đầy đủ thư viện và API AI trong `README.md` trước hạn 03/12 | Chưa làm |
