# Bài Tập Nhóm — Search Engine / RAG Chatbot

## Mục Tiêu

Sau khi hoàn thành bài cá nhân, nhóm ngồi lại để xây dựng **1 trong 2 sản phẩm**:

---

## Yêu cầu 1:  Sản phẩm nhóm RAG Chatbot

Xây dựng chatbot trả lời câu hỏi về pháp luật ma tuý và tin tức liên quan.

**Yêu cầu:**
- Giao diện chat (Streamlit / Gradio / Chainlit)
- Trả lời có citation (dựa trên Task 10)
- Hỗ trợ follow-up questions (conversation memory)
- Hiển thị source documents đã dùng

**Stack gợi ý:**
```
Chainlit/Streamlit → Retrieval (Task 9) → Generation (Task 10) → Display
```

---

## Yêu cầu 2: RAG Evaluation Pipeline

Sử dụng **1 trong 3 framework** sau để evaluate pipeline RAG của nhóm:

### Framework lựa chọn

| Framework | Cài đặt | Đặc điểm |
|-----------|---------|-----------|
| [DeepEval](https://github.com/confident-ai/deepeval) | `pip install deepeval` | Nhiều metric built-in, dễ integrate với pytest |
| [RAGAS](https://github.com/explodinggradients/ragas) | `pip install ragas` | Chuẩn industry cho RAG eval, 3 trục chính |
| [TruLens](https://github.com/truera/trulens) | `pip install trulens` | Dashboard UI, feedback functions mạnh |

### Yêu cầu Evaluation

1. **Tạo Golden Dataset** — tối thiểu 15 cặp Q&A (question, expected_answer, expected_context)
2. **Chạy evaluation** trên toàn bộ golden dataset với các metrics sau:
   - **Faithfulness** — câu trả lời có bám đúng context không?
   - **Answer Relevance** — câu trả lời có đúng câu hỏi không?
   - **Context Recall** — retriever có lấy đủ evidence không?
   - **Context Precision** — trong context lấy về, bao nhiêu % thực sự hữu ích?
3. **So sánh A/B** — chạy eval trên ít nhất 2 config khác nhau (ví dụ: có reranking vs không reranking, hoặc hybrid vs dense-only)
4. **Báo cáo** — bảng điểm + phân tích worst performers + đề xuất cải tiến

### Code mẫu — DeepEval

```python
from deepeval import evaluate
from deepeval.metrics import (
    FaithfulnessMetric,
    AnswerRelevancyMetric,
    ContextualRecallMetric,
    ContextualPrecisionMetric,
)
from deepeval.test_case import LLMTestCase

# Tạo test cases từ golden dataset
test_cases = []
for item in golden_dataset:
    result = rag_pipeline.generate_with_citation(item["question"])
    test_case = LLMTestCase(
        input=item["question"],
        actual_output=result["answer"],
        expected_output=item["expected_answer"],
        retrieval_context=[c["content"] for c in result["sources"]],
    )
    test_cases.append(test_case)

# Chạy evaluation
metrics = [
    FaithfulnessMetric(threshold=0.7),
    AnswerRelevancyMetric(threshold=0.7),
    ContextualRecallMetric(threshold=0.7),
    ContextualPrecisionMetric(threshold=0.7),
]

results = evaluate(test_cases, metrics)
```

### Code mẫu — RAGAS

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
)
from datasets import Dataset

# Chuẩn bị data
eval_data = {
    "question": [],
    "answer": [],
    "contexts": [],
    "ground_truth": [],
}

for item in golden_dataset:
    result = rag_pipeline.generate_with_citation(item["question"])
    eval_data["question"].append(item["question"])
    eval_data["answer"].append(result["answer"])
    eval_data["contexts"].append([c["content"] for c in result["sources"]])
    eval_data["ground_truth"].append(item["expected_answer"])

dataset = Dataset.from_dict(eval_data)

# Chạy evaluation
result = evaluate(
    dataset,
    metrics=[faithfulness, answer_relevancy, context_recall, context_precision],
)
print(result.to_pandas())
```

### Code mẫu — TruLens

```python
from trulens.apps.custom import TruCustomApp, instrument
from trulens.core import Feedback
from trulens.providers.openai import OpenAI as TruOpenAI

provider = TruOpenAI()

# Define feedback functions
f_faithfulness = Feedback(provider.groundedness_measure_with_cot_reasons).on_output()
f_relevance = Feedback(provider.relevance).on_input_output()
f_context_relevance = Feedback(provider.context_relevance).on_input()

# Wrap RAG pipeline
tru_rag = TruCustomApp(
    rag_pipeline,
    app_name="DrugLaw_RAG",
    feedbacks=[f_faithfulness, f_relevance, f_context_relevance],
)

# Run evaluation
with tru_rag as recording:
    for item in golden_dataset:
        rag_pipeline.generate_with_citation(item["question"])

# View dashboard
from trulens.dashboard import run_dashboard
run_dashboard()
```

### Deliverable Evaluation

- [ ] File `group_project/evaluation/golden_dataset.json` — 15+ cặp Q&A
- [ ] File `group_project/evaluation/eval_pipeline.py` — script chạy evaluation
- [ ] File `group_project/evaluation/results.md` — bảng điểm + phân tích
- [ ] So sánh A/B ít nhất 2 configs

---

## Yêu Cầu Chung

1. **Tích hợp pipeline** từ bài cá nhân của các thành viên
2. **Demo hoạt động được** trong buổi trình bày (chạy local hoặc deploy)
3. **Evaluation pipeline** chạy được và có báo cáo kết quả
4. **Code push lên repository** chung của nhóm
5. **README** mô tả kiến trúc và phân công (điền bên dưới)

---

## Kiến Trúc Hệ Thống

```
+-----------------------------------------------------------------------+
|                       Streamlit UI Chatbot (app.py)                   |
|  - Custom CSS Dark Mode / Outfits Typography                         |
|  - st.session_state (Conversation History / Memory)                   |
+-----------------------------------+-----------------------------------+
                                    | (gửi Query + Lịch sử Chat)
                                    v
+-----------------------------------------------------------------------+
|                    Retrieval Pipeline (Task 9 & Task 10)              |
|  - Trích xuất 6 câu chat trước đó làm ngữ cảnh hội thoại cho LLM      |
|  - Gọi RAG Retrieval Pipeline cho query hiện tại                      |
+-----------------------------------+-----------------------------------+
                                    | (tìm kiếm song song)
                   +----------------+----------------+
                   |                                 |
                   v                                 v
+------------------+----------------+ +--------------+------------------+
|      Semantic Search (Task 5)     | |       Lexical Search (Task 6)    |
|   - ChromaDB (all-MiniLM-L6-v2)   | |   - BM25Okapi local index        |
+------------------+----------------+ +--------------+------------------+
                   |                                 |
                   +----------------+----------------+
                                    | (Candidates)
                                    v
+-----------------------------------------------------------------------+
|                         Reranker (Task 7)                             |
|  - Reciprocal Rank Fusion (RRF) gộp điểm & xếp hạng lại candidates    |
+-----------------------------------+-----------------------------------+
                                    | (Kiểm tra Threshold)
                                    |
            [Score >= 0.35] --------+-------- [Score < 0.35] (Fallback)
                   |                                 |
                   v                                 v
+------------------+----------------+ +--------------+------------------+
|       Top 5 Chunks (Hybrid)       | |     PageIndex Search (Task 8)    |
|   (Đã được RRF xếp hạng)           | |    - Vectorless search fallback |
+------------------+----------------+ +--------------+------------------+
                   |                                 |
                   +----------------+----------------+
                                    | (Top K Chunks)
                                    v
+-----------------------------------------------------------------------+
|                    Reorder for LLM (Lost in the Middle)               |
|  - Sắp xếp thứ tự chunks tối ưu: Chunks tốt nhất ở đầu và cuối        |
+-----------------------------------+-----------------------------------+
                                    | (Context được định dạng)
                                    v
+-----------------------------------------------------------------------+
|                         LLM Generation (Task 10)                      |
|  - GPT-4o-mini với prompt yêu cầu trích dẫn và chống ngụy tạo thông tin|
+-----------------------------------+-----------------------------------+
                                    | (Stream text phản hồi)
                                    v
+-----------------------------------------------------------------------+
|                     Giao diện Chatbot hiển thị                        |
|  - Nội dung trả lời có trích dẫn nguồn [1], [2], ...                  |
|  - st.expander hiển thị chi tiết nội dung chunk và Metadata           |
+-----------------------------------------------------------------------+
```

---

## Hướng Dẫn Chạy

```bash
# 1. Cấu hình các API Keys trong file .env ở thư mục gốc
# OPENAI_API_KEY=your_openai_key
# PAGEINDEX_API_KEY=your_pageindex_key

# 2. Chạy ứng dụng Streamlit từ thư mục gốc
streamlit run app.py
```
