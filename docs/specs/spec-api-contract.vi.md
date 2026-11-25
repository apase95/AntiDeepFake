# AntiDeepFake - Đặc tả Hợp đồng API & Dữ liệu (v1.1 - SSE Streaming)

> **Chuẩn Kỹ thuật Dùng chung**: Hợp đồng giao tiếp thống nhất giữa Kỹ sư AI, Kỹ sư Backend Pipeline, Kỹ sư Backend Platform và Frontend Next.js.

## 1. Danh sách Các Endpoint API

| Phương thức & Đường dẫn | Mục đích & Quyền truy cập | Ghi chú Kỹ thuật |
|---|---|---|
| `GET /health` | Kiểm tra dịch vụ & Đánh thức Server | Trả về `200 {"status": "ok", "service": "api"}`. UI tự gọi khi mở web để đánh thức Render. |
| `GET /ready` | Kiểm tra sẵn sàng DB (Readiness) | Chạy `SELECT 1` vào Supabase qua **IPv4 Pooler (`6543`)** / HTTPS. Trả về `503` nếu lỗi DB. |
| `GET /api/v1/cases` | Lấy 3 kịch bản demo chính thức | Trả về thông tin mô tả, link video Supabase Storage và kết quả cache sẵn (`0ms`). |
| `POST /api/v1/analyze` | **Phân tích Video Stream SSE** | Trình duyệt gọi thẳng tới Render CORS (`multipart/form-data`, tối đa 15 MB / 30s). Trả về `text/event-stream` đẩy kết quả từng 5s. |
| `GET /api/v1/logs` | Xem lịch sử phân tích ẩn danh | Trả về 20 bản ghi `analysis_logs` gần nhất (không chứa PII hay video). |

> **Quy tắc Định tuyến Bắt buộc**: Trình duyệt **phải** gọi `POST /api/v1/analyze` trực tiếp tới URL HTTPS của Render (`NEXT_PUBLIC_API_BASE_URL`), tuyệt đối không đi qua Next.js API Proxy để tránh giới hạn 4.5 MB của Vercel Hobby Tier.

---

## 2. Hợp đồng Stream SSE (`POST /api/v1/analyze`)

Content-Type: `text/event-stream`

### 2.1. `event: window` (Đẩy về ngay lập tức khi xử lý xong mỗi block 5 giây)
```text
event: window
data: {"window_id":2,"start_sec":5,"end_sec":10,"cv_status":"evaluated","cv_score":0.88,"transcript_redacted":"Chuyển ngay giúp em [REDACTED_NUM] triệu, đừng gọi cho mẹ.","rolling_context_used":true,"verdict":"confirmed_scam","probability":0.94,"trigger_quote":"đừng gọi cho mẹ","recommended_action":"Cảnh báo khẩn cấp: Tạm dừng chuyển tiền và gọi số đã lưu để xác minh."}
```
- **Các giá trị hợp lệ của `cv_status`**: `"evaluated"`, `"insufficient_visual_data"`, `"provider_error"`.
- **Các giá trị hợp lệ của `verdict`**: `"normal"`, `"visual_alert_only"`, `"verbal_pressure_only"`, `"confirmed_scam"`, `"evaluation_incomplete"`.
- **Ràng buộc bất biến**:
  - `trigger_quote` phải là `null` hoặc là một chuỗi con đã kiểm chứng có tồn tại trong `transcript_redacted` (hoặc khối 5s liền trước).
  - `cv_score` nằm chặt trong khoảng `[0.0, 1.0]` hoặc `null` nếu `cv_status != "evaluated"`.

### 2.2. `event: summary` (Phát ra một lần sau khi hoàn tất toàn bộ video)
```text
event: summary
data: {"schema_version":"1.1","analysis_id":"adf_a1b2c3d4e5f6","duration_seconds":15,"overall_risk_level":"HIGH","processing_time_ms":3420,"total_windows":3}
```

### 2.3. `event: error` (Phát ra nếu xảy ra lỗi hệ thống giữa luồng stream)
```text
event: error
data: {"schema_version":"1.1","code":"provider_unavailable","message":"External evaluation timed out.","request_id":"req_9f8e7d6c"}
```

---

## 3. Dữ liệu Demo Cache Sẵn (`GET /api/v1/cases`)

```json
{
  "case_id": "case_1_faceswap_scam",
  "title": "Ca 1: Video Face-Swap + Ép chuyển tiền khẩn cấp",
  "description": "Kiểm thử tình huống kết hợp giả mạo khuôn mặt và thao túng tâm lý.",
  "video_url": "https://<project>.supabase.co/storage/v1/object/public/sample-videos/case1-faceswap-scam.mp4",
  "cached_analysis": {
    "schema_version": "1.1",
    "analysis_id": "demo_case_1",
    "duration_seconds": 15,
    "overall_risk_level": "HIGH",
    "processing_time_ms": 0,
    "windows": [
      {
        "window_id": 1,
        "start_sec": 0,
        "end_sec": 5,
        "cv_status": "evaluated",
        "cv_score": 0.85,
        "transcript_redacted": "Alo mẹ à, con đang ở ngoài đường.",
        "rolling_context_used": false,
        "verdict": "visual_alert_only",
        "probability": 0.81,
        "trigger_quote": null,
        "recommended_action": "Phát hiện chỉnh sửa hình ảnh; không dùng video để xác nhận danh tính."
      }
    ]
  }
}
```

---

## 4. Phản hồi Lỗi Trước khi Mở Stream (Mã Trạng thái HTTP)

Trước khi bắt đầu mở luồng SSE, các file không hợp lệ bị chặn ngay lập tức với khung JSON chuẩn (không stack trace, không PII):

```json
{
  "schema_version": "1.1",
  "code": "file_too_large",
  "message": "Video tải lên vượt quá dung lượng tối đa 15 MB.",
  "request_id": "req_9f8e7d6c"
}
```

| Mã HTTP | Mã `code` ổn định | Điều kiện kích hoạt & Cách xử lý |
|---|---|---|
| **400** | `invalid_media_format` | File tải lên không phải định dạng MP4/WebM hợp lệ hoặc bị hỏng header. |
| **413** | `file_too_large` | File vượt quá giới hạn 15 MB trước khi đưa vào xử lý. |
| **422** | `duration_exceeded` | Thời lượng video vượt quá 30 giây hoặc sai cấu trúc dữ liệu Pydantic. |
| **429** | `rate_limited` | Chạm giới hạn lượt gọi API AI bên ngoài hoặc giới hạn tốc độ tải lên. |
| **503** | `provider_unavailable` | Mất kết nối Supabase DB tại `/ready`. |

---

## 5. Cấu trúc Bảng Supabase PostgreSQL (SQL Schema)

Kết nối từ Render thông qua **Supavisor IPv4 Pooler (cổng `6543`)** dùng `asyncpg` (hoặc `supabase-py` HTTPS):

```sql
-- Bảng lưu 3 kịch bản demo chính thức đã tính toán sẵn (độ trễ 0ms)
CREATE TABLE IF NOT EXISTS test_cases (
    case_id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    video_url TEXT NOT NULL,
    cached_analysis JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Bảng lưu log ẩn danh (không lưu video gốc, không lưu PII chưa che)
CREATE TABLE IF NOT EXISTS analysis_logs (
    analysis_id VARCHAR(64) PRIMARY KEY,
    source_type VARCHAR(32) NOT NULL CHECK (source_type IN ('demo_case', 'user_upload')),
    duration_seconds INTEGER NOT NULL CHECK (duration_seconds > 0),
    window_count INTEGER NOT NULL CHECK (window_count > 0),
    overall_risk_level VARCHAR(16) NOT NULL CHECK (overall_risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'UNKNOWN')),
    max_cv_score FLOAT,
    processing_time_ms INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```
