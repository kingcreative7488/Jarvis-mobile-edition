"""
file_processor.py — JARVIS Universal File Processor

Supported types:
  image   → describe, ocr, resize, convert, compress, crop
  pdf     → summarize, extract_text, extract_pages, to_word
  docx    → summarize, extract_text, reformat, translate_hint
  txt/md  → summarize, reformat, translate_hint, word_count
  csv     → analyze, filter, sort, convert, stats
  xlsx    → analyze, filter, convert, stats
  json    → validate, format, extract, convert
  code    → explain, review, fix, run, document
  audio   → transcribe, trim, convert, info
  video   → trim, extract_audio, extract_frame, info, compress
  zip     → list, extract
  pptx    → summarize, extract_text, to_pdf
"""

import os
import re
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime

# Model choice, timeout and fallback ladder all live in core/gemini.py.
from core import gemini

def _get_api_key() -> str:
    config_path = Path(__file__).resolve().parent.parent / "config" / "api_keys.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)["gemini_api_key"]


def _gemini_client(tier: str = gemini.SMART):
    """Summarising documents and reading images — the reasoning tier, with a
    long deadline because the input can be a whole file."""
    class _W:
        def generate_content(self, contents):
            resp = gemini.call(contents, tier=tier, timeout_ms=90000)
            if resp is None:
                raise RuntimeError("every Gemini model on the ladder failed")
            return resp

    return _W()


def _detect_type(path: Path) -> str:
    ext = path.suffix.lower().lstrip(".")
    image_exts = {"jpg", "jpeg", "png", "gif", "webp", "bmp", "tiff", "svg", "ico"}
    video_exts = {"mp4", "avi", "mov", "mkv", "wmv", "flv", "webm", "m4v", "3gp"}
    audio_exts = {"mp3", "wav", "ogg", "m4a", "aac", "flac", "wma", "opus"}
    code_exts  = {"py", "js", "ts", "jsx", "tsx", "html", "css", "java", "c",
                  "cpp", "cs", "go", "rs", "rb", "php", "swift", "kt", "sh",
                  "bash", "ps1", "lua", "r", "m", "sql", "yaml", "toml"}
    archive_exts = {"zip", "rar", "tar", "gz", "7z", "bz2", "xz"}

    if ext in image_exts:  return "image"
    if ext in video_exts:  return "video"
    if ext in audio_exts:  return "audio"
    if ext in code_exts:   return "code"
    if ext in archive_exts: return "archive"
    if ext == "pdf":       return "pdf"
    if ext in ("docx", "doc"): return "docx"
    if ext in ("txt", "md", "rst", "log"): return "text"
    if ext in ("csv", "tsv"): return "csv"
    if ext in ("xlsx", "xls", "ods"): return "excel"
    if ext == "json":      return "json"
    if ext == "xml":       return "xml"
    if ext in ("pptx", "ppt"): return "pptx"
    return "unknown"


def _file_size_str(path: Path) -> str:
    size = path.stat().st_size
    if size < 1024:        return f"{size} B"
    if size < 1024**2:     return f"{size/1024:.1f} KB"
    if size < 1024**3:     return f"{size/1024**2:.1f} MB"
    return f"{size/1024**3:.1f} GB"

def _output_path(src: Path, suffix: str, new_ext: str = None) -> Path:
    ext  = new_ext or src.suffix
    name = f"{src.stem}_{suffix}{ext}"
    return src.parent / name

def _process_image(path: Path, action: str, params: dict, speak=None) -> str:
    try:
        from PIL import Image
    except ImportError:
        return "Pillow is not installed. Run: pip install Pillow"

    action = action or "describe"

    if action in ("describe", "ocr", "analyze", "read", "extract_text"):
        try:
            model  = _gemini_client()
            img    = Image.open(path)
            prompt = {
                "describe": "Describe this image in detail.",
                "ocr":      "Extract all text visible in this image. Return only the text, formatted clearly.",
                "analyze":  "Analyze this image thoroughly: objects, colors, composition, any text, context.",
                "read":     "Read all text in this image, preserving structure and formatting.",
                "extract_text": "Extract all text from this image.",
            }.get(action, "Describe this image.")

            if params.get("instruction"):
                prompt = params["instruction"]

            response = model.generate_content([prompt, img])
            result   = response.text.strip()

            if len(result) > 500 and params.get("save", True):
                out = _output_path(path, "result", ".txt")
                out.write_text(result, encoding="utf-8")
                return f"{result[:300]}...\n\nFull result saved to: {out}"
            return result
        except Exception as e:
            return f"AI image analysis failed: {e}"

    if action == "resize":
        width  = int(params.get("width",  0))
        height = int(params.get("height", 0))
        scale  = float(params.get("scale", 0))
        try:
            img = Image.open(path)
            w, h = img.size
            if scale:
                new_size = (int(w * scale), int(h * scale))
            elif width and height:
                new_size = (width, height)
            elif width:
                new_size = (width, int(h * width / w))
            elif height:
                new_size = (int(w * height / h), height)
            else:
                return "Please specify width, height, or scale."
            out = _output_path(path, f"resized_{new_size[0]}x{new_size[1]}")
            img.resize(new_size, Image.LANCZOS).save(out)
            return f"Resized from {w}x{h} to {new_size[0]}x{new_size[1]}. Saved: {out.name}"
        except Exception as e:
            return f"Resize failed: {e}"

    if action == "convert":
        fmt = params.get("format", "png").lower().strip(".")
        fmt_map = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG",
                   "webp": "WEBP", "bmp": "BMP", "tiff": "TIFF"}
        pil_fmt = fmt_map.get(fmt, fmt.upper())
        try:
            img = Image.open(path).convert("RGB") if fmt == "jpg" else Image.open(path)
            out = _output_path(path, "converted", f".{fmt}")
            img.save(out, pil_fmt)
            return f"Converted to {fmt.upper()}. Saved: {out.name}"
        except Exception as e:
            return f"Convert failed: {e}"

    if action == "compress":
        quality = int(params.get("quality", 70))
        try:
            img = Image.open(path).convert("RGB")
            out = _output_path(path, f"compressed_q{quality}", ".jpg")
            img.save(out, "JPEG", quality=quality, optimize=True)
            before = _file_size_str(path)
            after  = _file_size_str(out)
            return f"Compressed: {before} → {after}. Saved: {out.name}"
        except Exception as e:
            return f"Compress failed: {e}"

    if action == "info":
        try:
            img = Image.open(path)
            return (f"Image info: {img.format}, {img.size[0]}x{img.size[1]}px, "
                    f"mode: {img.mode}, size: {_file_size_str(path)}")
        except Exception as e:
            return f"Info failed: {e}"

    return _process_image(path, "describe", {"instruction": f"{action}: {params}"})

def _process_pdf(path: Path, action: str, params: dict, speak=None) -> str:
    action = action or "summarize"

    def _extract_pdf_text(max_chars=50000) -> str:
        text = ""
        try:
            import pdfplumber
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    text += (page.extract_text() or "") + "\n"
        except ImportError:
            try:
                import PyPDF2
                with open(path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
            except ImportError:
                return ""
        return text[:max_chars]

    if action in ("summarize", "extract_text", "translate_hint", "analyze", "reformat"):
        text = _extract_pdf_text()
        if not text.strip():
            return "Could not extract text from PDF (may be scanned/image-based)."

        if action == "extract_text":
            out = _output_path(path, "text", ".txt")
            out.write_text(text, encoding="utf-8")
            return f"Text extracted ({len(text)} chars). Saved: {out.name}"

        prompt_map = {
            "summarize":      f"Summarize this PDF document concisely:\n\n{text}",
            "analyze":        f"Analyze this document thoroughly:\n\n{text}",
            "translate_hint": f"What language is this document in and what does it say? Summarize:\n\n{text}",
            "reformat":       f"Reformat this text cleanly with proper structure:\n\n{text}",
        }
        try:
            model    = _gemini_client()
            response = model.generate_content(prompt_map.get(action, f"Analyze:\n\n{text}"))
            result   = response.text.strip()
            if len(result) > 600 and params.get("save", True):
                out = _output_path(path, action, ".txt")
                out.write_text(result, encoding="utf-8")
                return f"{result[:400]}...\n\nFull result saved: {out.name}"
            return result
        except Exception as e:
            return f"AI analysis failed: {e}"

    if action == "info":
        try:
            import pdfplumber
            with pdfplumber.open(path) as pdf:
                pages = len(pdf.pages)
            return f"PDF: {pages} pages, size: {_file_size_str(path)}"
        except Exception:
            return f"PDF size: {_file_size_str(path)}"

    if action == "to_word":
        text = _extract_pdf_text()
        if not text:
            return "Could not extract text to convert."
        try:
            from docx import Document
            doc  = Document()
            doc.add_heading(path.stem, 0)
            for para in text.split("\n\n"):
                if para.strip():
                    doc.add_paragraph(para.strip())
            out = _output_path(path, "converted", ".docx")
            doc.save(out)
            return f"Converted to Word document. Saved: {out.name}"
        except ImportError:
            return "python-docx not installed. Run: pip install python-docx"

    return f"Unknown PDF action: '{action}'. Try: summarize, extract_text, info, to_word"

def _process_text_doc(path: Path, file_type: str, action: str,
                       params: dict, speak=None) -> str:
    action = action or "summarize"

    def _read_content() -> str:
        if file_type == "docx":
            try:
                from docx import Document
                doc  = Document(path)
                return "\n".join(p.text for p in doc.paragraphs)
            except ImportError:
                return "python-docx not installed."
            except Exception as e:
                return f"Read failed: {e}"
        else:
            return path.read_text(encoding="utf-8", errors="ignore")

    content = _read_content()
    if not content.strip():
        return "File appears to be empty."

    if action == "word_count":
        words = len(content.split())
        chars = len(content)
        lines = content.count("\n")
        return f"Word count: {words} words, {chars} characters, {lines} lines."

    if action == "extract_text":
        if file_type != "txt":
            out = _output_path(path, "extracted", ".txt")
            out.write_text(content, encoding="utf-8")
            return f"Text extracted. Saved: {out.name}"
        return content[:2000]

    instruction = params.get("instruction", "")
    prompt_map  = {
        "summarize":  f"Summarize this document concisely:\n\n{content[:40000]}",
        "analyze":    f"Analyze this document:\n\n{content[:40000]}",
        "reformat":   f"Reformat this text with clean structure, proper headings and paragraphs:\n\n{content[:40000]}",
        "fix":        f"Fix grammar, spelling and style issues in this text:\n\n{content[:40000]}",
        "translate_hint": f"What language is this and what does it say? Summarize:\n\n{content[:10000]}",
        "to_bullet":  f"Convert this text into a clear bullet-point summary:\n\n{content[:40000]}",
        "custom":     f"{instruction}\n\n{content[:40000]}",
    }

    if action not in prompt_map:

        action  = "custom"
        instruction = action

    try:
        model    = _gemini_client()
        response = model.generate_content(prompt_map[action])
        result   = response.text.strip()
        if len(result) > 600 and params.get("save", True):
            out = _output_path(path, action, ".txt")
            out.write_text(result, encoding="utf-8")
            return f"{result[:400]}...\n\nFull result saved: {out.name}"
        return result
    except Exception as e:
        return f"AI processing failed: {e}"


def _process_data(path: Path, file_type: str, action: str,
                  params: dict, speak=None) -> str:
    try:
        import pandas as pd
    except ImportError:
        return "pandas not installed. Run: pip install pandas openpyxl"

    action = action or "analyze"

    try:
        if file_type == "csv":
            df = pd.read_csv(path, encoding="utf-8", errors="replace")
        else:
            df = pd.read_excel(path)
    except Exception as e:
        return f"Could not read file: {e}"

    if action == "info":
        return (f"Rows: {len(df)}, Columns: {len(df.columns)}\n"
                f"Columns: {', '.join(df.columns.tolist())}\n"
                f"Size: {_file_size_str(path)}")

    if action == "stats":
        try:
            desc = df.describe(include="all").to_string()
            return f"Statistics:\n{desc[:2000]}"
        except Exception as e:
            return f"Stats failed: {e}"

    if action == "analyze":
        preview = df.head(50).to_string()
        prompt  = (f"Analyze this dataset. Columns: {list(df.columns)}\n"
                   f"Rows: {len(df)}\nPreview:\n{preview}\n\n"
                   f"Give insights, patterns, and notable findings.")
        try:
            model    = _gemini_client()
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"AI analysis failed: {e}"

    if action in ("convert", "to_csv", "to_excel", "to_json"):
        fmt = {"to_csv": "csv", "to_excel": "xlsx", "to_json": "json",
               "convert": params.get("format", "csv")}.get(action, "csv")
        try:
            if fmt == "csv":
                out = _output_path(path, "converted", ".csv")
                df.to_csv(out, index=False, encoding="utf-8")
            elif fmt == "xlsx":
                out = _output_path(path, "converted", ".xlsx")
                df.to_excel(out, index=False)
            elif fmt == "json":
                out = _output_path(path, "converted", ".json")
                df.to_json(out, orient="records", force_ascii=False, indent=2)
            return f"Converted to {fmt.upper()}. Saved: {out.name}"
        except Exception as e:
            return f"Convert failed: {e}"

    if action == "filter":
        col       = params.get("column", "")
        value     = params.get("value", "")
        condition = params.get("condition", "equals")
        if not col or col not in df.columns:
            return f"Column '{col}' not found. Available: {', '.join(df.columns)}"
        try:
            if condition == "equals":     filtered = df[df[col] == value]
            elif condition == "contains": filtered = df[df[col].astype(str).str.contains(str(value), case=False)]
            elif condition == "gt":       filtered = df[df[col] > float(value)]
            elif condition == "lt":       filtered = df[df[col] < float(value)]
            else:                         filtered = df[df[col] == value]
            out = _output_path(path, "filtered", ".csv")
            filtered.to_csv(out, index=False)
            return f"Filtered: {len(filtered)} rows match. Saved: {out.name}"
        except Exception as e:
            return f"Filter failed: {e}"

    if action == "sort":
        col = params.get("column", df.columns[0])
        asc = params.get("ascending", True)
        try:
            sorted_df = df.sort_values(col, ascending=asc)
            out = _output_path(path, "sorted", path.suffix)
            sorted_df.to_csv(out, index=False)
            return f"Sorted by '{col}'. Saved: {out.name}"
        except Exception as e:
            return f"Sort failed: {e}"

    preview = df.head(30).to_string()
    try:
        model    = _gemini_client()
        response = model.generate_content(
            f"Task: {action}\nDataset ({len(df)} rows, cols: {list(df.columns)}):\n{preview}"
        )
        return response.text.strip()
    except Exception as e:
        return f"Processing failed: {e}"


def _process_json(path: Path, action: str, params: dict, speak=None) -> str:
    action = action or "analyze"
    try:
        content = path.read_text(encoding="utf-8")
        data    = json.loads(content)
    except Exception as e:
        return f"Invalid JSON: {e}"

    if action == "validate":
        return f"Valid JSON. Type: {type(data).__name__}, size: {_file_size_str(path)}"

    if action == "format":
        out = _output_path(path, "formatted", ".json")
        out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return f"Formatted JSON saved: {out.name}"

    if action in ("analyze", "summarize", "extract"):
        preview = json.dumps(data, indent=2, ensure_ascii=False)[:8000]
        prompt  = f"Task: {action} this JSON data:\n{preview}"
        if params.get("instruction"):
            prompt = f"{params['instruction']}\n\nJSON data:\n{preview}"
        try:
            model    = _gemini_client()
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"AI processing failed: {e}"

    if action == "to_csv":
        try:
            import pandas as pd
            if isinstance(data, list):
                df  = pd.DataFrame(data)
                out = _output_path(path, "converted", ".csv")
                df.to_csv(out, index=False)
                return f"Converted to CSV. Saved: {out.name}"
            return "JSON must be an array of objects to convert to CSV."
        except ImportError:
            return "pandas not installed."

    return _process_json(path, "analyze", {"instruction": action})

def _process_code(path: Path, action: str, params: dict, speak=None) -> str:
    action  = action or "explain"
    content = path.read_text(encoding="utf-8", errors="ignore")
    ext     = path.suffix.lstrip(".")

    if action == "run":
        if ext == "py":
            try:
                result = subprocess.run(
                    ["python", str(path)],
                    capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30
                )
                out = result.stdout or result.stderr
                return f"Output:\n{out[:2000]}" if out else "No output."
            except subprocess.TimeoutExpired:
                return "Execution timed out (30s)."
            except Exception as e:
                return f"Run failed: {e}"
        return f"Direct execution not supported for .{ext} files."

    if action == "info":
        lines = content.count("\n")
        words = len(content.split())
        r
