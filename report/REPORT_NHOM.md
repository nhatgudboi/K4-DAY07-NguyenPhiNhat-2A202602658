# BÁO CÁO LAB 07 - NHÓM 18
*Chủ đề: Dịch vụ & Nội quy Thư viện (University Library Services)*

---

## PHẦN 1. ĐÁNH GIÁ CHIẾN LƯỢC PHÂN RÃ VĂN BẢN (CHUNKING STRATEGIES)

Để tối ưu hóa Vector Store, nhóm đã tiến hành phân rã 5 tài liệu gốc bằng 4 chiến lược khác nhau. Dưới đây là bảng phân tích so sánh:

| Thành viên phụ trách | Tên Chiến lược | Số lượng Chunk sinh ra | Điểm Benchmark | Đánh giá & Nhận xét sơ bộ |
|---|---|:---:|:---:|---|
| **Tuấn (Data)** | `SentenceChunker` | 48 | **6/10** | Cắt theo từng câu nên số lượng chunk sinh ra nhiều nhất. Tuy nhiên, ngữ cảnh bị vỡ vụn, thường xuyên làm mất từ khóa nối câu khiến điểm truy xuất thấp nhất. |
| **Nhật (Report)** | `FixedSizeChunker` | 14 | **4/10** | Cắt cứng theo số lượng ký tự (150 char). Ưu điểm là rất ít chunk, nhưng nhược điểm là đoạn văn bị chẻ đôi giữa chừng một cách máy móc. Câu 4 và 5 bị cắt đứt đoạn chứa Keyword quan trọng nên lấy sai hoàn toàn. |
| **Khánh (Benchmark)** | `RecursiveChunker` | 31 | **8/10** | Cắt đệ quy rất linh hoạt, dung hòa tốt giữa số lượng chunk và ngữ cảnh. Lấy được điểm tuyệt đối ở 4/5 câu hỏi. |
| **Vĩ (Strategy)** | `HeadingChunker` | 32 | **9/10** | **Chiến lược xuất sắc nhất.** Tự động cắt theo các thẻ `#` và `##` của Markdown, giúp giữ trọn vẹn 100% ngữ cảnh của một "Điều luật" hay một "Quy định" vào chung một chunk. |

---

## PHẦN 2. KẾT QUẢ BENCHMARK (5 CÂU HỎI TRUY XUẤT)

Nhóm sử dụng bộ 5 câu hỏi chuẩn để test hệ thống. Điểm số dưới đây lấy từ chiến lược tốt nhất (`HeadingChunker` của Vĩ):

* **Câu 1 (Fact & Numbers):** *Sinh viên được mượn tối đa bao nhiêu tài liệu...* 
  * Kết quả: Đạt 1/2 điểm. (Hệ thống lấy đúng ý nhưng top-1 bị nhầm lẫn nhẹ sang quy định của giảng viên do không có filter).
* **Câu 2 (Conditions):** *Hạn ngạch được phép mượn tài liệu về nhà tối đa là bao nhiêu cuốn?*
  * Kết quả: Đạt 2/2 điểm tuyệt đối nhờ sử dụng Metadata Filter.
* **Câu 3 (Finance):** *Mức phí phạt trả sách quá hạn mỗi ngày là bao nhiêu?*
  * Kết quả: Đạt 2/2 điểm. Bốc chính xác `fpt-phi-thu-vien`.
* **Câu 4 (Facility):** *Thời gian sử dụng phòng học nhóm tối đa là bao lâu mỗi ca?*
  * Kết quả: Đạt 2/2 điểm. Trích xuất đúng con số `2 giờ` và `15 phút`.
* **Câu 5 (Channels):** *Mỗi cuốn sách được phép gia hạn tối đa mấy lượt?*
  * Kết quả: Đạt 2/2 điểm.

👉 **Tổng điểm hệ thống: 9/10 điểm.**

---

## PHẦN 3. BẰNG CHỨNG THỰC NGHIỆM A/B: METADATA FILTERING
*(Chứng minh sự cần thiết của lọc siêu dữ liệu trong kiến trúc Multi-tenant)*

**Câu hỏi Test:** *"Hạn ngạch được phép mượn tài liệu về nhà tối đa là bao nhiêu cuốn cùng một lúc?"*

* **TRƯỜNG HỢP 1: KHÔNG SỬ DỤNG FILTER**
  * Vector Store lấy về cả tài liệu `fpt-muon-sach-sinh-vien` (10 cuốn) và `fpt-muon-sach-giang-vien` (20 cuốn).
  * Tài liệu của giảng viên nằm chễm chệ ở Rank 2 với score khá cao (0.275). Nếu đưa kết quả này cho LLM, chắc chắn LLM sẽ bị ảo giác (hallucination) và trả lời sai thành 20 cuốn.
* **TRƯỜNG HỢP 2: CÓ SỬ DỤNG FILTER `{"audience": "student"}`**
  * Vector Store loại bỏ hoàn toàn tài liệu của giảng viên từ trước khi tính toán cosine similarity.
  * Hệ thống cô lập 100% dữ liệu, lấy về đúng tài liệu sinh viên (Score: 0.395).

**💡 Kết luận:** Bắt buộc phải triển khai tính năng Metadata Filtering để đảm bảo an toàn thông tin và tính chính xác, không cho phép sinh viên đọc chéo quy định của giảng viên.

---

## PHẦN 4. PHÂN TÍCH LỖI (FAILURE CASE ANALYSIS)

Nhóm đã phát hiện một rủi ro kiến trúc vô cùng lớn khi sử dụng `SentenceChunker` (Thuật toán của Tuấn).

**1. Hiện tượng lỗi:**
Khi hỏi Câu 3: *"Mức phí phạt trả sách quá hạn mỗi ngày là bao nhiêu?"*, chiến lược `SentenceChunker` đạt 0/2 điểm. Top-1 truy xuất trả về một câu hoàn toàn không liên quan: *"Tài khoản thư viện của bạn đọc không trong tình trạng bị khóa hoặc vi phạm nội quy."*

**2. Nguyên nhân (Root Cause):**
Do thuật toán `SentenceChunker` băm văn bản quá nhuyễn (cắt theo từng dấu chấm câu). Câu văn chứa con số "5.000 VNĐ" bị tách rời hoàn toàn khỏi câu văn chứa chữ "Mức phí phạt quá hạn". Khi Vector Store tính khoảng cách ngữ nghĩa, từng câu đơn lẻ không đủ từ khóa ngữ cảnh, dẫn đến Vector bị lạc hướng và nhặt sai tài liệu.

**3. Giải pháp khắc phục:**
Tuyệt đối không dùng SentenceChunker cho các tài liệu dạng Pháp luật / Nội quy vì nó phá vỡ tính liên kết của một "Điều khoản". Phải sử dụng `HeadingChunker` (Giữ nguyên văn bản từ thẻ Header này đến thẻ Header tiếp theo) để gom trọn vẹn ngữ cảnh vào một Vector duy nhất.
