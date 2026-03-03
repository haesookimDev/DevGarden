import fitz  # PyMuPDF

from app.parsers.base import DocumentParser, ParsedDocument


class PDFParser(DocumentParser):
    def parse(self, file_data: bytes) -> ParsedDocument:
        doc = fitz.open(stream=file_data, filetype="pdf")
        text_parts = []
        images = []

        for page in doc:
            text_parts.append(page.get_text())

            for img_info in page.get_images(full=True):
                xref = img_info[0]
                base_image = doc.extract_image(xref)
                if base_image:
                    images.append(base_image["image"])

        return ParsedDocument(
            text="\n\n".join(text_parts),
            images=images,
            metadata={"title": doc.metadata.get("title", ""), "author": doc.metadata.get("author", "")},
            page_count=len(doc),
        )
