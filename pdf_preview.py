"""PDF 정보 조회와 첫 페이지 미리보기 생성

설치: python -m pip install PyMuPDF
실행: python pdf_preview.py sample.pdf --output preview.png

"""

import argparse
import json
from pathlib import Path

import pymupdf


def create_preview(pdf_path: Path, output_path: Path) -> dict:
    """첫 페이지를 최대 너비 600px의 PNG로 저장하고 문서 정보를 반환한다."""
    pdf_path = Path(pdf_path).resolve()
    output_path = Path(output_path).resolve()

    if not pdf_path.is_file():
        raise ValueError(f"파일을 찾을 수 없습니다: {pdf_path}")
    if output_path.suffix.lower() != ".png":
        raise ValueError("미리보기 저장 경로는 .png로 지정해주세요.")
    if pdf_path == output_path:
        raise ValueError("원본 파일과 미리보기 저장 경로는 달라야 합니다.")
    if output_path.exists():
        raise ValueError("저장 경로에 파일이 이미 있습니다. 다른 경로를 지정해주세요.")

    with pymupdf.open(pdf_path) as document:
        if not document.is_pdf:
            raise ValueError("PDF 파일만 지원합니다.")
        if document.needs_pass:
            raise ValueError("암호로 보호된 PDF는 아직 지원하지 않습니다.")
        if document.page_count == 0:
            raise ValueError("페이지가 없는 PDF입니다.")

        page = document[0]
        scale = min(600 / page.rect.width, 1)
        pixmap = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=False)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        # 기존 파일을 덮어쓰지 않도록 배타적으로 생성한다.
        with output_path.open("xb") as preview:
            preview.write(pixmap.tobytes("png"))

        return {
            "filename": pdf_path.name,
            "page_count": document.page_count,
            "size_bytes": pdf_path.stat().st_size,
            "preview_path": str(output_path),
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="PDF 첫 페이지 미리보기 생성")
    parser.add_argument("pdf", type=Path, help="미리보기를 만들 PDF 경로")
    parser.add_argument("--output", type=Path, default=Path("preview.png"))
    args = parser.parse_args()

    try:
        result = create_preview(args.pdf, args.output)
    except (ValueError, OSError, RuntimeError) as error:
        parser.exit(1, f"미리보기 생성 실패: {error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
