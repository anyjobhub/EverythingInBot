"""
PDF Tasks Module
Handles PDF processing tasks (merge, compress, OCR, etc.)
Replaces worker.tasks PDF functions after Celery removal
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


async def merge_pdfs(
    pdf_paths: list[str],
    output_path: str,
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Merge multiple PDF files into one
    
    Args:
        pdf_paths: List of PDF file paths to merge
        output_path: Output file path
        user_id: Telegram user ID for logging
    
    Returns:
        Dict with success status and output path
    """
    try:
        logger.info(f"Merging {len(pdf_paths)} PDFs for user {user_id}")
        
        from PyPDF2 import PdfMerger
        
        merger = PdfMerger()
        
        for pdf_path in pdf_paths:
            merger.append(pdf_path)
        
        merger.write(output_path)
        merger.close()
        
        return {
            "success": True,
            "output_path": output_path,
            "num_files": len(pdf_paths)
        }
    
    except Exception as e:
        logger.error(f"PDF merge error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def compress_pdf(
    input_path: str,
    output_path: Optional[str] = None,
    user_id: Optional[int] = None,
    quality: str = "medium"
) -> Dict[str, Any]:
    """
    Compress PDF file
    
    Args:
        input_path: Input PDF file path
        output_path: Output file path (optional)
        user_id: Telegram user ID for logging
        quality: Compression quality (low, medium, high)
    
    Returns:
        Dict with success status and file info
    """
    try:
        logger.info(f"Compressing PDF for user {user_id}")
        
        from PyPDF2 import PdfReader, PdfWriter
        
        if not output_path:
            output_path = input_path.replace(".pdf", "_compressed.pdf")
        
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
        
        # Compress
        for page in writer.pages:
            page.compress_content_streams()
        
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        original_size = Path(input_path).stat().st_size
        compressed_size = Path(output_path).stat().st_size
        reduction = ((original_size - compressed_size) / original_size) * 100
        
        return {
            "success": True,
            "output_path": output_path,
            "original_size": original_size,
            "compressed_size": compressed_size,
            "reduction_percent": round(reduction, 2)
        }
    
    except Exception as e:
        logger.error(f"PDF compression error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def ocr_pdf(
    input_path: str,
    user_id: Optional[int] = None,
    language: str = "eng"
) -> Dict[str, Any]:
    """
    Extract text from PDF using OCR
    
    Args:
        input_path: Input PDF file path
        user_id: Telegram user ID for logging
        language: OCR language (eng, hin, etc.)
    
    Returns:
        Dict with extracted text
    """
    try:
        logger.info(f"Performing OCR on PDF for user {user_id}")
        
        import pdfplumber
        
        text_content = []
        
        with pdfplumber.open(input_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    text_content.append(f"--- Page {page_num} ---\n{text}")
        
        full_text = "\n\n".join(text_content)
        
        return {
            "success": True,
            "text": full_text,
            "num_pages": len(text_content),
            "char_count": len(full_text)
        }
    
    except Exception as e:
        logger.error(f"PDF OCR error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def split_pdf(
    input_path: str,
    output_dir: str,
    user_id: Optional[int] = None,
    pages_per_file: int = 1
) -> Dict[str, Any]:
    """
    Split PDF into multiple files
    
    Args:
        input_path: Input PDF file path
        output_dir: Output directory
        user_id: Telegram user ID for logging
        pages_per_file: Number of pages per output file
    
    Returns:
        Dict with output file paths
    """
    try:
        logger.info(f"Splitting PDF for user {user_id}")
        
        from PyPDF2 import PdfReader, PdfWriter
        
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        output_files = []
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        for i in range(0, total_pages, pages_per_file):
            writer = PdfWriter()
            
            for j in range(i, min(i + pages_per_file, total_pages)):
                writer.add_page(reader.pages[j])
            
            output_path = f"{output_dir}/split_{i+1}-{min(i+pages_per_file, total_pages)}.pdf"
            
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            
            output_files.append(output_path)
        
        return {
            "success": True,
            "output_files": output_files,
            "num_files": len(output_files)
        }
    
    except Exception as e:
        logger.error(f"PDF split error: {e}")
        return {
            "success": False,
            "error": str(e)
        }
