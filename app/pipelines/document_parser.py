import os
from pypdf import PdfReader
from app.utils.config import config
from app.utils.logger import get_logger
from app.pipelines.pii_scrubber import PIIScrubber

logger = get_logger(__name__)

class DocumentParser:
    def __init__(self):
        self.scrubber = PIIScrubber()
        self.chunk_size = config.CHUNK_SIZE
        self.chunk_overlap = config.CHUNK_OVERLAP

    def parse_pdf(self, file_path: str) -> dict:
        """
        Parse a PDF file into clean, scrubbed text chunks.
        Returns dict with metadata and chunks.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        logger.info(f"Parsing PDF: {file_path}")

        try:
            reader = PdfReader(file_path)
            full_text = ""

            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    full_text += f"\n--- Page {page_num + 1} ---\n"
                    full_text += page_text

            logger.info(
                f"Extracted {len(reader.pages)} pages, "
                f"{len(full_text)} characters"
            )

            # Scrub PII before chunking
            scrub_result = self.scrubber.scrub(full_text)
            clean_text = scrub_result["scrubbed_text"]

            # Chunk the text
            chunks = self._chunk_text(clean_text)

            logger.info(f"Created {len(chunks)} chunks")

            return {
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "total_pages": len(reader.pages),
                "total_characters": len(full_text),
                "total_chunks": len(chunks),
                "pii_entities_found": scrub_result["entities_found"],
                "chunks": chunks
            }

        except Exception as e:
            logger.error(f"Failed to parse PDF {file_path}: {e}")
            raise

    def parse_text(self, text: str, source_name: str = "manual_input") -> dict:
        """
        Parse raw text input directly.
        Used for clinical notes entered manually.
        """
        logger.info(f"Parsing text input: {source_name}")

        scrub_result = self.scrubber.scrub(text)
        clean_text = scrub_result["scrubbed_text"]
        chunks = self._chunk_text(clean_text)

        return {
            "file_path": None,
            "file_name": source_name,
            "total_pages": 1,
            "total_characters": len(text),
            "total_chunks": len(chunks),
            "pii_entities_found": scrub_result["entities_found"],
            "chunks": chunks
        }

    def _chunk_text(self, text: str) -> list[dict]:
        """
        Split text into overlapping chunks for better retrieval.
        """
        if not text.strip():
            return []

        chunks = []
        start = 0
        chunk_index = 0

        while start < len(text):
            end = start + self.chunk_size

            # Don't cut in the middle of a word
            if end < len(text):
                last_space = text.rfind(" ", start, end)
                if last_space > start:
                    end = last_space

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append({
                    "chunk_index": chunk_index,
                    "text": chunk_text,
                    "start_char": start,
                    "end_char": end,
                    "word_count": len(chunk_text.split())
                })
                chunk_index += 1

            # Move forward with overlap
            start = end - self.chunk_overlap

        return chunks