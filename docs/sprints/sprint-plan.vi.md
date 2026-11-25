# AntiDeepFake - Kế hoạch Sprint (Agile/Scrum)

## 1. Cơ cấu Đội ngũ & Thiết lập Quy trình
- **Quy mô đội ngũ**: 3 Kỹ sư
  - **1 Kỹ sư AI (AI Engineer)**: Phụ trách thiết kế prompt/tiêu chí, Sightengine (`1 ảnh/5s` + Semaphore + dự phòng HF), Google `gemini-3.5-transcribe` (`google-genai` Interactions + `files.delete()`), OpenRouter `POST /api/alpha/decisions`, và chuẩn bị 3 clip mẫu.
  - **Kỹ sư Backend 1 (Trưởng nhóm Pipeline)**: Phụ trách module `ffmpeg` subprocess thuần (không dùng `moviepy`), điều phối async (`aiohttp`), ngữ cảnh trượt (`prev + curr`), che PII, kiểm chứng câu trích (Quote Grounding) và dọn dẹp kép.
  - **Kỹ sư Backend 2 (Trưởng nhóm Nền tảng & Tích hợp)**: Phụ trách FastAPI SSE streaming (`spec-api-contract.vi.md`), Supabase (IPv4 Pooler cổng `6543` / `supabase-py` + Storage), tầng cache tính sẵn, Docker non-root, triển khai Render + Vercel CORS trực tiếp và warm-up ping.
- **Cột mốc mục tiêu**: Hạn chót nộp bài Vòng Sơ loại MoMo TechDay '26 (**03/12/2026**).
- **Tài liệu chuẩn đối chiếu**: Tuân thủ nghiêm ngặt `docs/specs/spec-api-contract.vi.md` và `docs/validation/validation-plan.vi.md`.

---

## 2. Lộ trình Tổng quan & Cổng Nghiệm thu (Exit Gates)

| Sprint | Thời gian | Trọng tâm Thực hiện | Cổng Nghiệm thu Bắt buộc (Exit Gate) |
|---|---|---|---|
| **Sprint 1** | 25/11 - 28/11 | Pipeline Lõi, Guardrail & Kết nối AI | **Gate 1 + Gate 2**: Unit test offline pass 100%; Lệnh `--live` pass Sightengine, `google-genai` và `/api/alpha/decisions` |
| **Sprint 2** | 29/11 - 01/12 | SSE Streaming, Cache & Triển khai Cloud | **Gate 3 (Một phần)**: Render & Vercel live CORS trực tiếp; 3 video cache phát 0ms; Upload MP4 trả sự kiện SSE từng 5s |
| **Sprint 3** | 02/12 - 03/12 | Kiểm thử Ma trận, Quay Video & Nộp bài | **Gate 3 (Đầy đủ)**: Pass trọn bộ 12 kịch bản (`T01`–`T12`); Hoàn tất Video MP4 3 phút, Slide 10 trang và PDF 1 trang A4 |

---

## 3. Kế hoạch Chi tiết Từng Sprint

### Sprint 1: Pipeline Lõi, Guardrail & Kết nối Model AI (25/11 - 28/11)
- **Mục tiêu**: Xây dựng bộ cắt video 5s bằng `ffmpeg` thuần, kết nối đúng chuẩn API AI, ngữ cảnh trượt, che PII, kiểm chứng câu trích và bảng Supabase IPv4.
- **Sản phẩm bàn giao**:
  - Module `ffmpeg` subprocess (`asyncio.create_subprocess_exec`) tách `.mp3` và 1 keyframe `.jpg` sắc nét nhất trong `/tmp/adf_<uuid>/` kèm xóa tự động trong `finally`.
  - Kết nối Sightengine (`1 ảnh/5s` + `Semaphore(1)` giãn cách `1.1s`), Google `gemini-3.5-transcribe` (`files.upload` + `interactions.create` + `files.delete()`) và OpenRouter `POST /api/alpha/decisions` (từ điển `questions`).
  - Bộ ghép Ngữ cảnh trượt (`prev + curr` transcript) + Lọc Regex PII (`[REDACTED_NUM]`) + Quote Grounding (`R05`, `R06`).
  - Bảng Supabase (`test_cases`, `analysis_logs`) kết nối qua IPv4 Pooler (`6543`) / HTTPS và bucket `sample-videos`.
  - Bộ Unit Test offline + kịch bản `--live` smoke test có giới hạn quota.
- **Cổng nghiệm thu Sprint 1**: Pass 100% `unittest` offline; chạy `--live` kiểm chứng được quyền dùng `models=deepfake` trên Sightengine, xóa file `google-genai` và phản hồi `/api/alpha/decisions`.

### Sprint 2: Đóng gói SSE API, Cache Dữ liệu & Triển khai Đám mây (29/11 - 01/12)
- **Mục tiêu**: Đóng gói endpoint stream SSE theo `spec-api-contract.vi.md`, chạy Docker dưới 512 MB RAM trên Render, nối Supabase và giao diện Next.js trên Vercel.
- **Sản phẩm bàn giao**:
  - Các REST/SSE endpoints: `/health` (ping đánh thức), `/ready` (check DB IPv4), `/api/v1/cases`, `/api/v1/analyze` (`text/event-stream` SSE, upload thẳng CORS né trần 4.5 MB của Vercel, chặn 15 MB / 30s), và `/api/v1/logs`.
  - Lưu sẵn `cached_analysis` JSON vào bảng `test_cases` trên Supabase cho 3 video mẫu (độ trễ 0ms).
  - `Dockerfile` quyền non-root (`python:3.11-slim` + `ffmpeg`, không cài `moviepy`) deploy lên Render.
  - Giao diện Video Player + Live 5s SSE Timeline trên Vercel (tự bắn ping `/health` khi mở trang) định tuyến qua Cloudflare.
- **Cổng nghiệm thu Sprint 2**: Ban giám khảo mở URL Vercel, xem mượt Ca 1–3 từ Supabase Storage và upload thử MP4 thẳng lên Render thấy nhãn Timeline nhảy từng 5 giây.

### Sprint 3: Kiểm thử Biên, Đo Đạc Hiệu Năng & Hồ sơ Dự thi (02/12 - 03/12)
- **Mục tiêu**: Chạy toàn bộ 12 kịch bản kiểm thử (`T01`–`T12`), đo hiệu năng/RAM thực tế và hoàn tất hồ sơ dự thi MoMo TechDay '26.
- **Sản phẩm bàn giao**:
  - Chạy và ghi nhận bằng chứng cho 12 kịch bản (gồm ngữ cảnh trượt `T11` và kiểm tra dọn dẹp kép cục bộ + Google Files `T12`).
  - Đo đạc trung thực `p50`/`p95` cho từng block 5 giây và đảm bảo RAM Render luôn dưới 400 MB.
  - Quay Video MP4 tối đa 3 phút trình diễn sản phẩm thực tế đang chạy.
  - Hoàn thiện Slide PDF 10 trang, Tài liệu hướng dẫn 1 trang A4 và tệp `.zip` mã nguồn kèm `README.md` chuẩn xác.
- **Cổng nghiệm thu Sprint 3**: Nộp đầy đủ hồ sơ lên cổng TechDay '26 trước hạn chót 03/12.
