import uuid
from io import BytesIO
from pathlib import Path
from PIL import Image

import streamlit as st

UPLOAD_DIR = Path("uploads")
ALLOWED_EXT = {".jpg", ".jpeg", ".png"}
SIZES = ["S", "M", "L", "XL", "XXL", "XXXL"]

# All product images are resized to this fixed dimension on upload
PRODUCT_IMG_SIZE = (600, 600)
def _resize_to_uniform(image_bytes: bytes, target_size: tuple[int, int] = PRODUCT_IMG_SIZE) -> bytes:
    """Resize and center-crop an image to exactly target_size pixels."""
    img = Image.open(BytesIO(image_bytes))
    img = img.convert("RGB")
    # Scale so the smaller dimension matches the target, then center-crop
    src_w, src_h = img.size
    tgt_w, tgt_h = target_size
    scale = max(tgt_w / src_w, tgt_h / src_h)
    new_w, new_h = int(src_w * scale), int(src_h * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    # Center crop to exact target
    left = (new_w - tgt_w) // 2
    top = (new_h - tgt_h) // 2
    img = img.crop((left, top, left + tgt_w, top + tgt_h))
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()
def save_image(uploaded_file) -> str:
    ext = Path(uploaded_file.name).suffix.lower()
    if ext not in ALLOWED_EXT:
        raise ValueError("Only JPG, JPEG and PNG files are allowed.")
    UPLOAD_DIR.mkdir(exist_ok=True)
    # Always save as .jpg after resize
    filename = f"{uuid.uuid4().hex}.jpg"
    resized = _resize_to_uniform(uploaded_file.getbuffer())
    (UPLOAD_DIR / filename).write_bytes(resized)   
    return filename


def delete_image(filename: str):
    path = UPLOAD_DIR / filename
    if path.exists():
        path.unlink()


def show_image(filename: str, **kwargs):
    path = UPLOAD_DIR / filename
    if path.exists():
         # Always display at uniform size by resizing through Pillow
        try:
            img = Image.open(path).convert("RGB")
            src_w, src_h = img.size
            tgt_w, tgt_h = PRODUCT_IMG_SIZE
            scale = max(tgt_w / src_w, tgt_h / src_h)
            new_w, new_h = int(src_w * scale), int(src_h * scale)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            left = (new_w - tgt_w) // 2
            top = (new_h - tgt_h) // 2
            img = img.crop((left, top, left + tgt_w, top + tgt_h))
            st.image(img, **kwargs)
        except Exception:
            st.image(str(path), **kwargs)
    else:
        st.caption("🖼️ Image not found")


def money(value) -> str:
    return f"₹{float(value):,.2f}"


def inject_css():
    st.markdown(
        """
        <style>
                }
        /* ── Dashboard metrics ── */
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, #FDF6F0, #F0E6DC);
            border: 1px solid rgba(198,123,92,0.2);
            border-radius: 1rem;
            padding: 1rem;
            box-shadow: 0 3px 12px rgba(92,64,51,0.08);
            transition: transform .3s ease;
        }
        [data-testid="stMetric"]:hover {
            transform: translateY(-3px);
        }
        [data-testid="stMetricValue"] {
            color: #C67B5C !important;
            font-weight: 700 !important;
        }
        /* ── Footer ── */
        footer { visibility: hidden; }
        /* ── Scrollbar ── */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #F0E6DC; }
        ::-webkit-scrollbar-thumb { background: #C67B5C; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #B5654A; }
        </style>
        """,
        unsafe_allow_html=True,
    )
