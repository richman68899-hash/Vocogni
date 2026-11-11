"""Pure presentation helpers for Vocogni's learner profile.

Kept independent of Streamlit so escaping, icon markup, and avatar initials
can be tested in the lightweight unit-test environment.
"""

from __future__ import annotations

import html
from typing import Any


def display_profile_value(value: Any) -> str:
    """Format a profile value as safe text for an HTML fragment."""
    if value is None:
        text = "Not specified"
    elif isinstance(value, list):
        text = ", ".join(str(item) for item in value) if value else "Not specified"
    else:
        text = str(value).strip() or "Not specified"
    return html.escape(text)


def profile_icon_svg(name: str) -> str:
    """Return a small, consistent, decorative line icon for profile sections."""
    icons = {
        "user": (
            '<circle cx="12" cy="8" r="3.5"/>'
            '<path d="M5 20c.6-3.2 3-5 7-5s6.4 1.8 7 5"/>'
        ),
        "book": (
            '<path d="M3.5 5.5A2.5 2.5 0 0 1 6 3h5v17H6a2.5 2.5 0 0 0-2.5 2z"/>'
            '<path d="M20.5 5.5A2.5 2.5 0 0 0 18 3h-5v17h5a2.5 2.5 0 0 1 2.5 2z"/>'
        ),
        "target": (
            '<circle cx="12" cy="12" r="8.5"/>'
            '<circle cx="12" cy="12" r="4.8"/>'
            '<circle cx="12" cy="12" r="1.3"/>'
        ),
        "spark": (
            '<path d="m12 3 1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/>'
            '<path d="m19 15 .9 2.1L22 18l-2.1.9L19 21l-.9-2.1L16 18l2.1-.9z"/>'
        ),
        "shield": (
            '<path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11z"/>'
            '<path d="m9 12 2 2 4-4"/>'
        ),
    }
    paths = icons.get(name, icons["spark"])
    return (
        '<svg class="vc-profile-icon-art" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="1.7" '
        'stroke-linecap="round" stroke-linejoin="round" '
        'aria-hidden="true" focusable="false">'
        + paths + '</svg>'
    )


def profile_initials(name: Any) -> str:
    """Create a stable, privacy-light avatar monogram from the display name."""
    clean = str(name or "").strip()
    if not clean:
        return "L"
    parts = clean.split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return clean[:1].upper()

def process_profile_avatar(image_bytes: bytes, max_bytes: int = 4 * 1024 * 1024) -> str:
    """Validate an uploaded image and return a centered circular WebP data URI.

    The image is center-cropped to a square, resized to 256px, and given a
    transparent circular mask. Only the processed image is stored in the
    learner profile; the original upload is never retained.
    """
    import base64
    import io

    from PIL import Image, ImageOps, UnidentifiedImageError

    if not isinstance(image_bytes, (bytes, bytearray)) or not image_bytes:
        raise ValueError("Choose an image file to upload.")
    if len(image_bytes) > max_bytes:
        raise ValueError("Image must be 4 MB or smaller.")

    try:
        with Image.open(io.BytesIO(image_bytes)) as source:
            if source.format not in {"JPEG", "PNG", "WEBP"}:
                raise ValueError("Use a JPG, PNG, or WebP image.")
            source = ImageOps.exif_transpose(source)
            source.thumbnail((4096, 4096))
            image = source.convert("RGBA")
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValueError("That image could not be read. Try another file.") from exc

    width, height = image.size
    if not width or not height:
        raise ValueError("The uploaded image has invalid dimensions.")

    side = min(width, height)
    left = (width - side) // 2
    top = (height - side) // 2
    image = image.crop((left, top, left + side, top + side))
    image = image.resize((256, 256), Image.Resampling.LANCZOS)

    mask = Image.new("L", (256, 256), 0)
    from PIL import ImageDraw
    ImageDraw.Draw(mask).ellipse((1, 1, 255, 255), fill=255)
    image.putalpha(mask)

    output = io.BytesIO()
    image.save(output, format="WEBP", quality=88, method=6)
    encoded = base64.b64encode(output.getvalue()).decode("ascii")
    return "data:image/webp;base64," + encoded

