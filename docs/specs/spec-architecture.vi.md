# AntiDeepFake - Đặc tả Kiến trúc Kỹ thuật (Technical Architecture Specification)

> **Lưu ý Trạng thái**: Kiến trúc MVP đã tối ưu cho môi trường Production thực tế (né giới hạn Vercel 4.5MB, Render 512MB RAM, Sightengine 1 req/s và Supabase IPv4). Các con số hiệu năng là mục tiêu cần đo đạc trong Sprint 2/3, không phải cam kết SLA.

## 1. Kiến trúc Triển khai Production (Bản vẽ Draw.io Blueprint)

Hệ thống được tổ chức thành 4 phân tầng Serverless tối ưu hoàn toàn cho hạ tầng miễn phí:
1. **Phân tầng Frontend (Cloudflare + Vercel Hobby)**: Phân phối CDN, gửi ping đánh thức server (`GET /health`) khi tải trang, phát video từ Supabase và nhận luồng SSE Timeline 5 giây.
2. **Phân tầng Backend Compute (Render Docker - 512 MB RAM)**: FastAPI + `uvicorn` chạy quyền non-root, dùng `ffmpeg` thuần (loại bỏ `moviepy` tránh tràn RAM), trả dữ liệu stream SSE (`text/event-stream`), ngữ cảnh trượt, che PII và kiểm chứng câu trích.
3. **Phân tầng Dữ liệu & Lưu trữ Video (Supabase)**: PostgreSQL kết nối qua **IPv4 Supavisor Pooler (cổng 6543)** hoặc **`supabase-py` HTTPS**, cùng bucket `sample-videos`.
4. **Phân tầng AI Serverless Bên ngoài**: Sightengine (`1 keyframe/5s` + `Semaphore(1)` + fallback Hugging Face) + Google `gemini-3.5-transcribe` (Interactions API + `files.delete()`) + OpenRouter `pplx-decider-flash-v1.3:free` (`POST /api/alpha/decisions`).

```text
+---------------------------------------------------------------------------------------------------------------------------------------------------+
|                                                     TỔNG QUAN KIẾN TRÚC TRIỂN KHAI PRODUCTION                                                     |
+---------------------------------------------------------------------------------------------------------------------------------------------------+
|                                                                                                                                                   |
|  [Trình duyệt BGK / User] ---(1. Mở Web & Phát Video mẫu)---> [Frontend: Cloudflare + Vercel]                                                     |
|  [Trình duyệt BGK / User] ---(2. Upload CORS thẳng <=15MB)--> [Backend: Render Docker (Né giới hạn 4.5MB của Vercel)]                             |
|  [Trình duyệt BGK / User] <--(5. Luồng sự kiện SSE / 5s)----- [Backend: FastAPI StreamingResponse]                                                |
|                                                                     |                                                                             |
|  +------------------------------------+   +------------------------------------------------------+   +-----------------------------------------+  |
|  |           FRONTEND TIER            |   |               BACKEND COMPUTE TIER                   |   |          DATA & STORAGE TIER            |  |
|  |       (Cloudflare + Vercel)        |   |         (Render Free Tier - 512MB RAM)               |   |               (Supabase)                |  |
|  +-------------------------------------+  +------------------------------------------------------+   +-----------------------------------------+  |
|  | - Cloudflare (DNS + SSL + CDN)     |   | - FastAPI + Uvicorn (Cổng 8000, Non-root user)       |   | - Supabase Storage:                     |  |
|  | - Vercel Edge (Next.js 14 App):    |   | - Tiến trình ffmpeg thuần (Bỏ moviepy tránh OOM RAM) |   |   Bucket: sample-videos (3 video MP4)   |  |
|  |   * Ping GET /health đánh thức API |   | - Pipeline SSE 5 giây Tạm thời:                      |   | - Supabase PostgreSQL (IPv4 Pooler):    |  |
|  |   * Trình phát Video (từ Supabase) |   |   * Cắt .mp3 & 1 khung hình sắc nét nhất (.jpg)      |   |   * Thư viện: asyncpg / supabase-py     |  |
|  |   * Live SSE 5s Risk Timeline      |   |   * Rolling Context (lời 5s trước + 5s hiện tại)     |   |   * Cổng: 6543 (Tránh lỗi IPv6 5432)    |  |
|  |   * Nhãn cảnh báo Đỏ / Vàng        |   |   * Che PII & Kiểm chứng câu trích dẫn (Grounding)   |   |   * Bảng: test_cases, analysis_logs     |  |
|  +------------------------------------+   +--------------------------+---------------------------+   +-----------------------------------------+  |
|                                                                       |                                                   ^                       |
|                                                              (3. Gọi AI song song)                             (4. Đọc cache / Ghi metadata)      |
|                                                                       |                                                   |                       |
|                                                                       v                                                   |                       |
|                                           +------------------------------------------------------+                        |                       |
|                                           |             EXTERNAL SERVERLESS AI TIER              |                        |                       |
|                                           +------------------------------------------------------+                        |                       |
|                                           | - Sightengine CV: 1 ảnh/5s + Semaphore(1) 1.1s       | -----------------------+                       |
|                                           |   (Dự phòng tùy chọn: HuggingFace SigLIP2)           |                                                |
|                                           | - Gemini 3.5 Transcribe: Interactions + Files API    |                                                |
|                                           |   (Xóa file cloud bằng files.delete() ở finally)     |                                                |
|                                           | - OpenRouter Decider: POST /api/alpha/decisions      |                                                |
|                                           +------------------------------------------------------+                                                |
+---------------------------------------------------------------------------------------------------------------------------------------------------+
```

---

## 2. Phân bổ Công nghệ & Các Rào cản Đã Khắc phục

| Phân tầng | Thành phần | Dịch vụ / Model | Quy chuẩn Bảo vệ Production |
|---|---|---|---|
| **Frontend** | Web Hosting | Vercel (Hobby Tier) | Trình duyệt upload **thẳng qua CORS** tới Render (né trần 4.5 MB của Vercel Proxy); tự gửi `GET /health` khi mở web để đánh thức server ngủ. |
| **Backend** | Cắt Video | `ffmpeg` thuần (`subprocess`) | Chạy qua `asyncio.create_subprocess_exec` (~20 MB RAM); **loại bỏ hoàn toàn `moviepy`** để không sập RAM 512 MB của Render Free. |
| **Backend** | Điều phối API | FastAPI (`StreamingResponse`) | Trả dữ liệu SSE liên tục ngay khi xử lý xong từng block 5 giây; timeout tối đa 10 giây mỗi API. |
| **Storage** | Lưu trữ Video | Supabase Storage | Bucket công khai `sample-videos` chứa 3 video MP4 mẫu, không mất phí băng thông tải ra. |
| **Database**| Cơ sở dữ liệu | Supabase PostgreSQL | Kết nối qua **IPv4 Supavisor Pooler (cổng `6543`)** dùng `asyncpg` hoặc **`supabase-py` HTTPS** (tránh lỗi không hỗ trợ IPv6 của Render Free). |
| **AI (CV)** | Deepfake CV | Sightengine (`models=deepfake`) | Cắt **1 keyframe sắc nét nhất mỗi 5s** và xếp hàng tuần tự qua `asyncio.Semaphore(1)` (giãn cách `1.1s`) để tuân thủ giới hạn `1 req/s` gói Free; dự phòng HF `SigLIP2`. |
| **AI (STT)**| Chép lời | `gemini-3.5-transcribe` | Gọi qua `google-genai` SDK (`v1beta`) `files.upload()` + `interactions.create()`; bắt buộc gọi `files.delete()` trong `finally` (`R08`). |
| **AI (Logic)**| Quyết định | `pplx-decider-flash-v1.3:free` | Gọi qua OpenRouter Decisions API (`POST /api/alpha/decisions`) với từ điển `"questions"` và đọc kết quả từ `"answers"`. |

---

## 3. Hợp đồng OpenRouter Decisions API (`/api/alpha/decisions`)

Khác với các LLM chat thông thường, `perplexity/pplx-decider-flash-v1.3:free` gọi trực tiếp vào endpoint Decisions API của OpenRouter (`https://openrouter.ai/api/alpha/decisions`):

```json
{
  "model": "perplexity/pplx-decider-flash-v1.3:free",
  "state": {
    "previous_transcript": "Alo mẹ à, con đang có việc gấp ở ngoài đường.",
    "current_transcript": "Chuyển ngay giúp em [REDACTED_NUM] triệu, đừng gọi cho mẹ.",
    "cv_status": "evaluated",
    "cv_score": 0.88
  },
  "questions": {
    "risk_verdict": {
      "type": "choice",
      "instructions": "Đánh giá rủi ro lừa đảo dựa trên lời nói hiện tại, ngữ cảnh trước đó và điểm số deepfake.",
      "criteria": {
        "normal": "Trò chuyện bình thường, không đòi tiền, không đe dọa hoặc ngăn xác minh",
        "visual_alert_only": "Hình ảnh có dấu hiệu ghép mặt nhưng lời nói hoàn toàn bình thường",
        "verbal_pressure_only": "Lời nói đòi tiền gấp, xin OTP hoặc ngăn gọi người thân, dù hình ảnh bình thường",
        "confirmed_scam": "Hành vi lừa đảo rõ ràng từ lời nói ép chuyển tiền và ngăn xác minh, hoặc cả hai nhánh cùng gắn cờ"
      }
    }
  }
}
```

- **Đường dẫn đọc kết quả**: `response["answers"]["risk_verdict"]["choice"]` và `response["answers"]["risk_verdict"]["probabilities"][verdict]`.

---

## 4. Ranh giới Tin cậy, Ngữ cảnh Trượt & Dọn dẹp Kép

1. **Upload Trực tiếp & Bí mật Phía Server**:
   - Trình duyệt gửi `POST /api/v1/analyze` thẳng tới Render HTTPS (đã bật CORS `APP_ORIGIN`), giữ toàn bộ khóa API bí mật trên server Render.
2. **Ngữ cảnh Trượt (Rolling Context) & Che PII (`R01`, `R05`)**:
   - Trước khi gửi cho OpenRouter, bộ lọc Regex thay thế chuỗi số tài khoản/SĐT/OTP bằng `[REDACTED_NUM]`.
   - Luôn gửi kèm `previous_transcript` (đã che PII) cùng với `current_transcript` vào `state` để bắt được các câu lừa đảo bị cắt ngang tại mốc 5 giây.
3. **Kiểm chứng Câu trích (`R06`)**:
   - Mọi `trigger_quote` đều phải được đối chiếu tồn tại trong `current_transcript` (hoặc `previous_transcript`) trước khi đẩy ra giao diện.
4. **Dọn dẹp Tạm thời Kép (`R08`)**:
   - Cả thư mục tạm trên đĩa (`/tmp/adf_<uuid>/`) VÀ tệp âm thanh tạm vừa upload lên Google Files API (`client.files.delete()`) đều bị xóa ngay lập tức trong khối `finally` ngay sau khi hoàn tất.
   - Bảng `analysis_logs` trên Supabase chỉ lưu thông số metadata ẩn danh.

---

## 5. Mục tiêu Hiệu năng Cần Đo đạc (Không phải SLA)

- **Mục tiêu Độ trễ Mỗi Khối 5 giây**: `p50` dưới `1.5 giây`, `p95` dưới `3.0 giây` (tính cả thời gian giãn cách `1.1s` của Sightengine Free và vòng upload/xóa tệp Google Files API).
- **Yêu cầu Đo đạc Thực tế**: Ghi nhận thời gian từng chặng (`ffmpeg`, Sightengine, Gemini Interactions API, OpenRouter Decisions API) trong quá trình chạy Gate 2 và Gate 3.
