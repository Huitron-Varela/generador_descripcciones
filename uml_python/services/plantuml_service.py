import zlib
import requests

PLANTUML_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"

def _encode6bit(b: int) -> str:
    return PLANTUML_ALPHABET[b & 0x3F]

def _append3bytes(b1: int, b2: int, b3: int) -> str:
    c1 = b1 >> 2
    c2 = ((b1 & 0x3) << 4) | (b2 >> 4)
    c3 = ((b2 & 0xF) << 2) | (b3 >> 6)
    c4 = b3 & 0x3F
    return _encode6bit(c1) + _encode6bit(c2) + _encode6bit(c3) + _encode6bit(c4)

def _plantuml_encode(data: bytes) -> str:
    res = []
    for i in range(0, len(data), 3):
        b1 = data[i]
        b2 = data[i + 1] if i + 1 < len(data) else 0
        b3 = data[i + 2] if i + 2 < len(data) else 0
        res.append(_append3bytes(b1, b2, b3))
    return "".join(res)

def render_svg(plantuml_code: str) -> bytes:
    compressor = zlib.compressobj(level=9, wbits=-15)
    compressed = compressor.compress(plantuml_code.encode("utf-8")) + compressor.flush()
    encoded = _plantuml_encode(compressed)
    url = f"https://www.plantuml.com/plantuml/svg/{encoded}"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.content
