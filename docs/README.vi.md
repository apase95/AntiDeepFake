# AntiDeepFake - Mục lục Tài liệu Dự án

Thư mục này lưu trữ toàn bộ đặc tả sản phẩm, hợp đồng API/dữ liệu, kế hoạch sprint, ma trận kiểm chứng và hướng dẫn phát triển cho dự án AntiDeepFake (TechDay '26 - MoMo).

---

## Cấu trúc Thư mục Tài liệu

```text
docs/
├── README.md & README.vi.md             # Mục lục và điều hướng tài liệu
├── specs/                               # Đặc tả Kỹ thuật & Hợp đồng Dữ liệu
│   ├── spec-product.md & .vi.md         # Phạm vi MVP, quy tắc kiểm thử (R01-R08), cơ chế lõi
│   ├── spec-architecture.md & .vi.md    # Kiến trúc 100% Serverless, bảo mật PII & dọn dẹp tạm
│   ├── spec-api-contract.md & .vi.md    # REST endpoints, Pydantic schemas, HTTP errors, SQL DDL
│   └── spec-demo.md & .vi.md            # Hướng dẫn 1 trang A4 cho Ban giám khảo với 3 test cases
├── sprints/                             # Kế hoạch Sprint (Agile/Scrum)
│   └── sprint-plan.md & .vi.md          # Lộ trình 3 sprint & Cổng nghiệm thu hướng tới hạn 03/12
├── tasks/                               # Danh sách Công việc theo Vai trò
│   └── tasklist.md & .vi.md             # Đầu việc chi tiết cho 1 Kỹ sư AI và 2 Kỹ sư Backend
├── validation/                          # Cổng Nghiệm thu & Ma trận Kiểm thử
│   └── validation-plan.md & .vi.md      # Gate 1 Offline, Gate 2 --live, Ma trận 10 kịch bản test
└── guidelines/                          # Quy chuẩn Kỹ thuật & Hướng dẫn Cài đặt
    ├── team-workflow.md & .vi.md        # Git branching, Conventional Commits, bảo mật & DoD
    └── development.md & .vi.md          # Cài đặt local, ffmpeg, unittest offline vs lệnh --live
```

---

## Điều hướng Nhanh

- **Phạm vi & Quy tắc Sản phẩm (R01–R08)**: `docs/specs/spec-product.vi.md` / `.md`
- **Kiến trúc Đám mây & Bảo mật Riêng tư**: `docs/specs/spec-architecture.vi.md` / `.md`
- **Hợp đồng API & Bảng SQL**: `docs/specs/spec-api-contract.vi.md` / `.md`
- **Hướng dẫn Demo Trực tuyến cho BGK**: `docs/specs/spec-demo.vi.md` / `.md`
- **Kế hoạch Kiểm chứng & Ma trận Test**: `docs/validation/validation-plan.vi.md` / `.md`
- **Kế hoạch 3 Sprint & Cổng Nghiệm thu**: `docs/sprints/sprint-plan.vi.md` / `.md`
- **Danh sách Task (1 AI, 2 Backend)**: `docs/tasks/tasklist.vi.md` / `.md`
- **Hướng dẫn Cài đặt & Chạy Local**: `docs/guidelines/development.vi.md` / `.md`
- **Quy trình Làm việc Nhóm & DoD**: `docs/guidelines/team-workflow.vi.md` / `.md`
