#!/usr/bin/env python3
"""Build downscaled PNG/WebP variants, preserving original alpha."""

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
SIZES = (128, 256, 512, 768)


def digest(path):
    return hashlib.sha256(path.read_bytes()).digest()


def verify_pair(expected, png, webp):
    with Image.open(png) as saved_png, Image.open(webp) as saved_webp:
        actual_png = saved_png.convert('RGBA')
        actual_webp = saved_webp.convert('RGBA')
        assert actual_png.size == actual_webp.size == expected.size, png
        assert actual_png.tobytes() == expected.tobytes(), png
        alpha = expected.getchannel('A')
        assert actual_webp.getchannel('A').tobytes() == alpha.tobytes(), webp
        visible = alpha.point(lambda value: 255 if value else 0).convert('RGB')
        difference = ImageChops.difference(expected.convert('RGB'), actual_webp.convert('RGB'))
        assert ImageChops.multiply(difference, visible).getbbox() is None, webp


def main():
    originals = list((ROOT / 'png').glob('*.png')) + list((ROOT / 'webp').glob('*.webp'))
    hashes = {path: digest(path) for path in originals}
    catalog = json.loads((ROOT / 'images.json').read_text())
    count = 0
    for item in catalog:
        with Image.open(ROOT / item['png']) as image:
            original = image.convert('RGBA')
        assert original.size == (item['width'], item['height']), item['name']
        variants = []
        for limit in SIZES:
            # Each variant starts from the original. Never enlarge a smaller image.
            if max(original.size) <= limit:
                continue
            resized = original.copy()
            resized.thumbnail((limit, limit), Image.Resampling.LANCZOS, reducing_gap=3.0)
            assert max(resized.size) == limit, item['name']
            assert resized.width <= original.width and resized.height <= original.height
            # The short dimension can differ by one pixel due to integer rounding.
            ideal_short_edge = limit * min(original.size) / max(original.size)
            assert abs(min(resized.size) - ideal_short_edge) <= 1
            png = ROOT / 'png' / str(limit) / f"{item['name']}.png"
            webp = ROOT / 'webp' / str(limit) / f"{item['name']}.webp"
            png.parent.mkdir(parents=True, exist_ok=True)
            webp.parent.mkdir(parents=True, exist_ok=True)
            resized.save(png, format='PNG', optimize=True)
            resized.save(webp, format='WEBP', lossless=True, method=6, exact=True)
            verify_pair(resized, png, webp)
            variants.append({
                'max_dimension': limit,
                'width': resized.width,
                'height': resized.height,
                'png': png.relative_to(ROOT).as_posix(),
                'webp': webp.relative_to(ROOT).as_posix(),
                'png_bytes': png.stat().st_size,
                'webp_bytes': webp.stat().st_size,
            })
            count += 1
        item['variants'] = variants
    assert all(digest(path) == before for path, before in hashes.items()), 'Original modified'
    (ROOT / 'images.json').write_text(json.dumps(catalog, indent=2) + '\n')
    print(f'Generated and verified {count} PNG/WebP pairs ({count * 2} files).')
    print(f'All {len(hashes)} original files remain byte-for-byte unchanged.')
    pig = next(item for item in catalog if item['name'] == 'flying-pig')
    for variant in pig['variants']:
        print(f"Flying pig {variant['max_dimension']}px WebP: {variant['webp_bytes']:,} bytes (original: {pig['webp_bytes']:,})")


if __name__ == '__main__':
    main()
