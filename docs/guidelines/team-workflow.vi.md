# AntiDeepFake - Quy trình Làm việc & Quy chuẩn Kỹ thuật (Team Workflow)

Tài liệu này quy định quy trình phát triển, phối hợp nhóm và Tiêu chuẩn Hoàn thành (Definition of Done) cho đội ngũ 3 kỹ sư.

---

## 1. Chiến lược Phân nhánh Git & Quy chuẩn Commit

### 1.1. Quy ước Phân nhánh (Branching Strategy)
- **`main`**: Nhánh Production chính thức. Mỗi khi merge vào `main`, Render (Backend) và Vercel (Frontend) sẽ tự động kích hoạt tiến trình triển khai. Không push trực tiếp lên `main` trong các đợt tích hợp lớn.
- **`feature/<vai-trò>-<tên-tính-năng>`**: Các nhánh làm việc riêng cho từng tính năng.
  - Ví dụ:
    - `feature/ai-sightengine-connector`
    - `feature/be1-video-windowing`
    - `feature/be2-supabase-storage`
- **`fix/<tên-lỗi>`**: Nhánh sửa lỗi khẩn cấp.

### 1.2. Chuẩn Thông điệp Commit (Conventional Commits)
Mỗi commit bắt buộc tuân theo cấu trúc: `<loại>(<phạm-vi>): <mô tả ngắn bằng thể mệnh lệnh>`
- `feat`: Tính năng mới (ví dụ: `feat(pipeline): add ffmpeg 5s chunking logic`).
- `fix`: Sửa lỗi (ví dụ: `fix(auth): handle missing sightengine credentials gracefully`).
- `docs`: Cập nhật tài liệu (ví dụ: `docs(specs): update product specification`).
- `chore`: Cấu hình, công cụ hoặc thư viện phụ thuộc (ví dụ: `chore(docker): optimize dockerfile build layers`).

---

## 2. Chính sách Bảo mật & Quản trị Khóa Bí mật

1. **Tuyệt đối Không Commit Khóa API lên Git**:
   - Tệp `.env` chứa các API key thực tế (Sightengine, Google, OpenRouter, mật khẩu Database) đã được chặn hoàn toàn bởi `.gitignore`.
   - Không được dán API key trực tiếp vào các tệp markdown, commit message hoặc pull request.
2. **Đồng bộ Biến Môi trường**:
   - Bất cứ khi nào thêm một biến môi trường mới vào code, phải lập tức cập nhật tệp `.env.example` với giá trị placeholder mẫu và chú thích rõ ràng.
3. **Cấu hình trên Môi trường Đám mây (Production)**:
   - Các API key thực tế khi chạy production được điền trực tiếp vào mục **Environment** trên Dashboard của Render và Vercel.

---

## 3. Tiêu chuẩn Hoàn thành (Definition of Done - DoD)

Một nhiệm vụ hoặc nhánh tính năng chỉ được coi là "Hoàn thành" khi thỏa mãn 4 tiêu chí sau:
1. **Kiểm tra Schema (Schema Validation)**: Toàn bộ dữ liệu JSON đầu vào và đầu ra đều được kiểm tra hợp lệ qua các schema của `Pydantic` mà không gây lỗi runtime.
2. **Thời gian Xử lý (SLA Hiệu năng)**: Toàn bộ chu trình xử lý một khối 5 giây (Bóc tách âm thanh + Soi Deepfake + Quyết định Choice) phải hoàn tất trong vòng **dưới 1.5 giây**.
3. **Cơ chế Dự phòng (Graceful Fallback)**: Khi một API bên ngoài bị lỗi mạng, timeout hoặc hết hạn mức, hệ thống phải bắt lỗi ngoại lệ, ghi log và trả về trạng thái dự phòng an toàn (`insufficient_visual_data` hoặc `safe`) thay vì làm sập server.
4. **Chất lượng Code**: Code được viết gọn gàng, có type hints của Python và chú thích hàm rõ ràng.

---

## 4. Giao thức Phối hợp & Bàn giao Công việc Hằng ngày

- **Họp nhanh đầu ngày (Daily Standup - 15 Phút)**:
  - Hôm qua bạn đã hoàn thành công việc gì?
  - Hôm nay bạn dự định làm gì?
  - Có vướng mắc hay phụ thuộc nào giữa AI, Pipeline và Nền tảng cần hỗ trợ không?
- **Quy trình Bàn giao Tích hợp**:
  - Kỹ sư AI bàn giao các hàm kết nối API và template prompt đã test chuẩn cho Kỹ sư Backend 1.
  - Kỹ sư Backend 1 đóng gói pipeline hoàn chỉnh và bàn giao cho Kỹ sư Backend 2.
  - Kỹ sư Backend 2 mở endpoint REST API và kiểm thử tích hợp toàn diện với giao diện Next.js.
