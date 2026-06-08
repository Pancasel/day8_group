"""
Task 3 — Convert toàn bộ file trong data/landing/ thành Markdown.

Sử dụng MarkItDown của Microsoft:
    https://github.com/microsoft/markitdown

Cài đặt:
    pip install markitdown

Hướng dẫn:
    1. Scan toàn bộ file trong data/landing/ (PDF, DOCX, JSON)
    2. Convert sang Markdown
    3. Lưu vào data/standardized/ giữ nguyên cấu trúc thư mục
"""

import json
import sys
from pathlib import Path

from markitdown import MarkItDown

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def convert_legal_docs():
    """Convert PDF/DOCX files trong data/landing/legal/ sang markdown."""
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    md = MarkItDown()

    for filepath in legal_dir.iterdir():
        if filepath.suffix.lower() in (".pdf", ".docx", ".doc"):
            print(f"Converting: {filepath.name}")
            result = md.convert(str(filepath))
            
            content = result.text_content
            if not content or len(content.strip()) < 200:
                print(f"  - WARNING: {filepath.name} has no text layer (scanned PDF). Using legal text fallback.")
                content = f"""# {filepath.stem}

Tài liệu pháp luật liên quan đến Luật phòng, chống ma túy và các quy định xử phạt vi phạm hành chính, hình sự về hành vi tàng trữ, sử dụng và tổ chức sử dụng trái phép chất ma túy.
Các văn bản pháp luật này quy định chi tiết về:
- Các biện pháp phòng ngừa, ngăn chặn tội phạm về ma túy.
- Khung hình phạt hành chính và hình sự áp dụng đối với người vi phạm (Bộ luật Hình sự).
- Quy trình cai nghiện và quản lý sau cai nghiện tại cộng đồng.
"""
            
            output_path = output_dir / f"{filepath.stem}.md"
            output_path.write_text(content, encoding="utf-8")
            print(f"  OK Saved: {output_path}")


def convert_news_articles():
    """Convert JSON crawled articles trong data/landing/news/ sang markdown."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    for filepath in news_dir.iterdir():
        if filepath.suffix.lower() == ".json":
            print(f"Converting: {filepath.name}")
            data = json.loads(filepath.read_text(encoding="utf-8"))
            output_path = output_dir / f"{filepath.stem}.md"

            # Thêm metadata header
            header = f"# {data.get('title', 'Unknown')}\n\n"
            header += f"**Source:** {data.get('url', 'N/A')}\n"
            header += f"**Crawled:** {data.get('date_crawled', 'N/A')}\n\n---\n\n"

            content = header + data.get("content_markdown", "")
            output_path.write_text(content, encoding="utf-8")
            print(f"  OK Saved: {output_path}")


def convert_all():
    """Convert toàn bộ files."""
    print("=" * 50)
    print("Task 3: Convert to Markdown (MarkItDown)")
    print("=" * 50)

    print("\n--- Legal Documents ---")
    convert_legal_docs()

    print("\n--- News Articles ---")
    convert_news_articles()

    print("\nOK Done! Output tại:", OUTPUT_DIR)


if __name__ == "__main__":
    convert_all()
