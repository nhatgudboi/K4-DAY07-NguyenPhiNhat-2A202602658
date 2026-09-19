# BÁO CÁO CÁ NHÂN LAB 07
*Sinh viên: Nguyễn Phi Nhật (Nhật - Số 4)*
*Vai trò: Report & Demo Lead*

## 1. Khởi động (Warm-up)

**Câu 1: Cosine similarity**
* Cosine similarity cao (gần 1.0) có nghĩa là góc giữa hai vector rất nhỏ, biểu thị hai đoạn text có chung một ý nghĩa (semantic meaning) kể cả khi chúng sử dụng từ vựng khác nhau.
* Ví dụ cặp tương đồng cao: "Tài liệu này cho mượn mấy ngày?" và "Sinh viên được đem sách về nhà trong bao lâu?". (Dù khác từ vựng nhưng cùng chung mục đích hỏi về thời hạn).
* Lý do phù hợp với text embedding: Vector sinh ra từ text thường có số chiều rất lớn. So sánh bằng góc (Cosine) sẽ loại trừ được yếu tố "độ dài" (magnitude) của câu, giúp việc so sánh tập trung vào "hướng" (ngữ nghĩa) của câu.

**Câu 2: Bài toán chunking**
* Với tài liệu 10.000 ký tự, `chunk_size` = 500, `overlap` = 50.
* Số lượng chunk sinh ra: `ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = 23` chunks.
* Nếu tăng overlap lên 100 thì số lượng chunk = `ceil(9900 / 400) = 25` chunks.
* Lý do muốn overlap lớn: Để đảm bảo khi tài liệu bị cắt, các thông tin liên quan nối tiếp giữa đoạn trước và đoạn sau không bị đứt đoạn, giúp LLM có đầy đủ ngữ cảnh để trả lời các câu hỏi phức tạp.

## 2. Dữ liệu (Data)
Tôi phụ trách thu thập dữ liệu về Dịch vụ Thư viện. Tổng số tài liệu: 5 tài liệu. Schema như sau:
* `audience`: Đối tượng áp dụng (student, faculty, all)
* `department`: Đơn vị quản lý (thu_vien)
* `category`: Phân loại thông tin (muon_tra, tai_chinh, co_so_vat_chat, dich_vu)

## 3. Hoàn thiện mã nguồn (Code)
Tôi đã hoàn thiện các file `chunking.py`, `store.py` và `agent.py`.
Kết quả chạy test:
```text
============================= test session starts =============================
collected 42 items

tests/test_agent.py ........                                             [ 19%]
tests/test_chunking.py .................                                 [ 59%]
tests/test_store.py ..............                                       [ 92%]
tests/test_main.py ...                                                   [100%]

============================= 42 passed in 0.45s ==============================
```

## 4. Chiến lược và Benchmark cá nhân
Tôi phụ trách thử nghiệm chiến lược: **`FixedSizeChunker(chunk_size=150, overlap=20)`**

Kết quả:
* **Câu 1 (Fact & Numbers):** 1/2 điểm (Top 2 chứa thông tin đúng).
* **Câu 2 (Conditions - Có Filter):** 2/2 điểm (Top 1 là tài liệu sinh viên).
* **Câu 3 (Finance):** 1/2 điểm (Top 2 chứa thông tin phạt).
* **Câu 4 (Facility):** 0/2 điểm (Lấy sai hoàn toàn).
* **Câu 5 (Channels):** 0/2 điểm (Lấy sai hoàn toàn).

**👉 Tổng điểm cá nhân: 4/10 điểm.**

**Nhận xét chiến lược cá nhân:**
Thuật toán chia chữ cố định cắt văn bản rất máy móc. Đặc biệt ở câu 4 và 5, phần quan trọng chứa từ khóa bị tách lìa ra khỏi ngữ cảnh nên thuật toán không thể truy xuất đúng thông tin. Điều này càng chứng tỏ giá trị của các thuật toán phức tạp hơn như `RecursiveChunker` hay `HeadingChunker`.
