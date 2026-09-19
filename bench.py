import os
from pathlib import Path
import re

from src.embeddings import get_embedding_fn
from src.store import EmbeddingStore
from src.chunking import FixedSizeChunker
from src.models import Document

# 1. Khởi tạo
store = EmbeddingStore(collection_name="benchmark", embedding_fn=get_embedding_fn())
chunker = FixedSizeChunker(chunk_size=150, overlap=20)

# 2. Đọc file
data_dir = Path("data/thu_vien")
documents = []
for p in data_dir.glob("*.md"):
    content = p.read_text(encoding="utf-8")
    parts = content.split("---")
    
    if len(parts) >= 3:
        frontmatter = parts[1]
        body = "---".join(parts[2:]).strip()
        
        # Parse metadata
        metadata = {}
        for line in frontmatter.strip().split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                metadata[k.strip()] = v.strip()
                
        # Thêm doc_id gốc
        metadata["doc_id"] = p.stem
        
        # Chunk text
        chunks = chunker.chunk(body)
        for i, chunk_text in enumerate(chunks):
            doc = Document(
                id=f"{p.stem}#{i}",
                content=chunk_text,
                metadata=metadata
            )
            documents.append(doc)

store.add_documents(documents)
print(f"Đã nạp {store.get_collection_size()} chunks vào store.")

# 3. Chạy 5 câu benchmark
queries = [
    {
        "id": "Câu 1: Fact & Numbers",
        "q": "Sinh viên được mượn tối đa bao nhiêu tài liệu về nhà và thời hạn mượn sách tham khảo tiếng Việt, ngoại văn là bao lâu?",
        "filter": None
    },
    {
        "id": "Câu 2: A/B Testing đối tượng (CÓ FILTER)",
        "q": "Hạn ngạch được phép mượn tài liệu về nhà tối đa là bao nhiêu cuốn cùng một lúc?",
        "filter": {"audience": "student"}
    },
    {
        "id": "Câu 2: A/B Testing đối tượng (KHÔNG FILTER)",
        "q": "Hạn ngạch được phép mượn tài liệu về nhà tối đa là bao nhiêu cuốn cùng một lúc?",
        "filter": None
    },
    {
        "id": "Câu 3: Finance & Procedure",
        "q": "Mức phí phạt trả sách quá hạn mỗi ngày là bao nhiêu và có những phương thức thanh toán trực tuyến nào?",
        "filter": None
    },
    {
        "id": "Câu 4: Facility & Condition",
        "q": "Thời gian sử dụng phòng học nhóm tối đa là bao lâu mỗi ca và sau bao nhiêu phút không đến nhận phòng thì ca đặt sẽ bị hủy?",
        "filter": None
    },
    {
        "id": "Câu 5: Service & Channels",
        "q": "Mỗi cuốn sách được phép gia hạn tối đa mấy lượt và bạn đọc có thể thực hiện gia hạn qua những kênh nào?",
        "filter": None
    }
]

with open("ket_qua_benchmark.txt", "w", encoding="utf-8") as f:
    for q in queries:
        f.write(f"=== {q['id']} ===\n")
        f.write(f"Hỏi: {q['q']}\n")
        f.write(f"Filter: {q['filter']}\n")
        results = store.search_with_filter(q["q"], top_k=3, metadata_filter=q["filter"])
        for idx, r in enumerate(results, 1):
            f.write(f" Top {idx} (Score: {r['score']:.4f}) | Nguồn: {r['metadata'].get('doc_id')}\n")
            f.write(f" Content: {r['content'][:150]}...\n")
        f.write("\n")

print("Hoàn thành! Đã xuất kết quả ra ket_qua_benchmark.txt")
