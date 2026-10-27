"""Compare a stopped VESA framebuffer with QEMU's unmodified screendump.

Only decodes BGRX and changes the image container to PNG; no pixels are drawn.
"""
from pathlib import Path
import argparse
import hashlib
import json
from PIL import Image

p = argparse.ArgumentParser()
p.add_argument('--vram', type=Path, required=True)
p.add_argument('--ppm', type=Path, required=True)
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
a.out.mkdir(parents=True, exist_ok=False)
raw = a.vram.read_bytes()
im = Image.open(a.ppm).convert('RGB')
assert im.size == (1024, 768)
assert len(raw) == 1024 * 768 * 4
decoded = Image.frombytes('RGB', im.size, raw, 'raw', 'BGRX')
actual = im.tobytes()
physical = decoded.tobytes()
different = [i // 3 for i in range(0, len(actual), 3)
             if actual[i:i + 3] != physical[i:i + 3]]
window = (195, 120, 835, 585)
window_different = [i for i in different if
                    window[0] <= i % 1024 < window[2] and
                    window[1] <= i // 1024 < window[3]]
assert not window_different, 'Window pixels differ from physical VESA VRAM'
im.save(a.out / 'verified-window.png')
record = {
    'ppm': str(a.ppm), 'vram': str(a.vram),
    'physical_address': '0xfd000000', 'format': '1024x768x32 BGRX',
    'ppm_sha256': hashlib.sha256(a.ppm.read_bytes()).hexdigest(),
    'vram_sha256': hashlib.sha256(raw).hexdigest(),
    'rgb_sha256': hashlib.sha256(actual).hexdigest(),
    'decoded_vram_rgb_sha256': hashlib.sha256(physical).hexdigest(),
    'different_pixels_whole_frame': len(different),
    'window_rectangle_xyxy': window,
    'different_pixels_window': len(window_different),
    'difference_bounds': ([min(i % 1024 for i in different),
                           min(i // 1024 for i in different),
                           max(i % 1024 for i in different),
                           max(i // 1024 for i in different)] if different else None),
    'png': str(a.out / 'verified-window.png'),
    'verification': 'Actual stopped framebuffer; no synthetic graphics or pixel modifications',
}
(a.out / 'framebuffer-verification.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record, indent=2))
