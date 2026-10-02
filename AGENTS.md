# Repository guide for agents

This is `adrian729/medieval-cutouts`, a public collection of medieval manuscript-style illustrations for reuse in other projects. It is an asset repository, not an application. Keep image files, the catalog, and documentation consistent when making changes. The user's current instructions take precedence over this guide.

## Structure

| Path | Purpose |
| --- | --- |
| `png/<name>.png` | Original PNG (transparent cutout or preserved scene), the source for all smaller versions. |
| `webp/<name>.webp` | Lossless WebP of the original, with matching dimensions and transparency. |
| `png/{128,256,512,768}/<name>.png` | Smaller PNG versions; folder name is the maximum/longest edge. |
| `webp/{128,256,512,768}/<name>.webp` | Matching smaller lossless WebPs. |
| `images.json` | Catalog: original paths, dimensions, byte sizes, variants, and selection metadata. |
| `README.md` | Usage examples, generated category index, and the image gallery. |
| `SELECTION.md` | Metadata vocabulary and guidance for selecting images and sizes. |
| `scripts/generate_sizes.py` | Generates and verifies smaller PNG/WebP pairs from cataloged originals. |
| `scripts/update_category_index.py` | Validates metadata and paths; generates the README category index. |
| `requirements.txt` | Pillow dependency for image conversion and resizing. |
| `sources/` | Retained supplied originals for documented corrections; reference material, not cutouts. |
| `EXTRACTION-PROMPTS.json` | Recorded correction prompts and methods, with retained source paths. |
| `AGENTS.md` | Canonical agent instructions; edit this file when conventions change. |
| `CLAUDE.md` | Imports this guide; do not duplicate the instructions there. |

Work inside this repository. The parent workspace can contain source images, unrelated files, and private configuration: do not bulk-copy or stage it. **Polyhymnia logos are explicitly excluded** and must stay outside this repository. Keep temporary previews and scratch files in ignored `tmp/` or a system temporary directory. Do not claim a license or historical provenance that has not been established.

## Image conventions

- Use descriptive lowercase hyphenated names, shared by the catalog `name` and every PNG/WebP filename.
- Preserve original image bytes during metadata edits, renames, and resizing. Only replace or edit an original when the task calls for an image change.
- Keep cutout backgrounds transparent. When the user requests an intact scene, preserve its background and border, including an opaque original if supplied. Verify visible RGB pixels and alpha when converting PNG to lossless WebP; invisible RGB beneath fully transparent pixels need not match.
- Generate smaller versions directly from the original PNG using Lanczos resampling. Preserve aspect ratio and alpha; never crop, stretch, or upscale as part of size generation.
- Available size limits are 128, 256, 512, and 768 pixels. The generator skips a limit when the original's longest edge is already equal to or smaller than it. Missing variants in that case are intentional.
- Never regenerate all image files for a description-only or filename-only change.

## Catalog conventions

`images.json` is a top-level array with one entry per image. Preserve existing fields when editing it. Each entry has:

- `name`, `png`, `webp`, `width`, `height`, `png_bytes`, `webp_bytes`.
- `variants`, ordered by increasing `max_dimension`. Each variant has `max_dimension`, `width`, `height`, `png`, `webp`, `png_bytes`, and `webp_bytes`.
- Exactly these six selection fields: `description`, `categories`, `subjects`, `facing`, `colors`, `composition`. Do not add instrument-specific fields or a new taxonomy without a requested schema change.

Use [`SELECTION.md`](SELECTION.md) for allowed values and definitions. Categories overlap: `animals`, `humans`, `hybrids`, `music`, `reading`, `fantasy`, and `royalty`. Specific instruments are ordinary subjects, such as `lute`, while `music` is their broad category. Reuse existing subject terms. Keep descriptions factual; qualify ambiguous creatures rather than confidently guessing a species. Inspect the actual cutout when adding visual metadata. Facing describes the head, not an instrument's direction.

If changing category or color vocabulary, update `SELECTION.md` and the constants in `scripts/update_category_index.py` together. Preserve selection metadata when running or changing the resize generator.

## Adding an image

1. Inspect the supplied illustration and prepare the requested transparent cutout, or preserve the supplied scene unchanged when requested. Choose a unique, accurate name and save the original as `png/<name>.png`; do not overwrite an unrelated asset.
2. Create `webp/<name>.webp` from that PNG with Pillow, using RGBA pixels and `format='WEBP', lossless=True, method=6, exact=True`. Verify dimensions, alpha, and visible pixels against the PNG. The existing `verify_pair` function in `scripts/generate_sizes.py` can perform this check.
3. Append a complete catalog entry with measured original dimensions and file byte sizes, the six selection fields, and an initially empty `variants` array. **The resize generator reads the catalog; it does not discover new PNGs automatically.**
4. Run `python3 scripts/generate_sizes.py --name <name>`. It fills `variants` and validates generated PNG/WebP pairs for that image. Without `--name`, it processes all cataloged images. If a corrected master is smaller, obsolete variants at or above its size are removed. Review changes rather than blindly staging them.
5. Add a row to the README's `## Images` gallery, matching its existing columns: preview, original PNG, original WebP, original dimensions, and links to available smaller WebPs. Choose an available small preview; do not link to skipped variants. Update the collection count in the README introduction.
6. Run `python3 scripts/update_category_index.py` to refresh categories, then the checks below. Inspect the new image on light and dark backgrounds and at a small display size.

The category updater only rewrites the block between `<!-- category-index:start -->` and `<!-- category-index:end -->`. It does **not** update the gallery or introduction count. Edit those separately. Do not hand-edit the generated category block.

## Correcting identities or names

User corrections apply to filenames and references as well as metadata. Breaking old external image links is currently acceptable; do not retain incorrect filenames or create compatibility copies solely to preserve them.

Rename the original and every existing variant in both formats without re-encoding. Update the catalog `name`, every path, subjects, description, and affected categories; update README gallery links, preview paths and alt text, and any guide examples. Refresh the generated category index. Search for stale names before finishing.

Confirmed identifications to preserve:

- `boar-lute-player`: a blue-gray boar playing a lute.
- `lizard-lute-player`: a gold lizard in blue clothing playing a lute.
- `fish-with-arms`: a fish with raised human arms.
- `donkey-rooster-lute-player`: a half-donkey, half-rooster hybrid playing a lute.
- `seated-rabbit`: its description includes its tired-looking expression and half-closed eye.
- `creature-in-gold-shape`: preserve the large pale curved body inside the gold form as opaque artwork. It is not background. Its supplied original is retained in `sources/`; the corrected extraction is capped at the source's 650px longest edge.

## Setup and validation

Run commands from the repository root. For image work, install the dependency in an ignored virtual environment if needed:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Use `.venv/bin/python` instead of `python3` below when using that environment.

For catalog or documentation changes:

```sh
python3 scripts/update_category_index.py
python3 scripts/update_category_index.py --check
git diff --check
```

The catalog check validates vocabulary, uniqueness, referenced files, variant ordering, and category-index consistency. It does not verify visual descriptions, actual pixel dimensions, or byte-size fields. Check those against the files when adding or replacing assets. The resize generator checks dimensions, no upscaling, matching visible pixels and alpha, and unchanged originals during generation.

For renames, verify that all expected variants moved, their bytes are unchanged, and no old paths or names remain. For documentation changes, check relative links and image preview paths. Review `git diff` and `git status` before committing; stage only intended files and preserve unrelated user changes. Commit and publish when the task authorizes it, without forcing a push or rewriting history.

Keep this guide current when repository structure or workflows change. Tools that do not load it automatically should be told to read `AGENTS.md` before editing.
