#!/usr/bin/env python3
"""Validate selection metadata and refresh the README category index."""

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {
    'animals': 'Animals',
    'humans': 'Humans',
    'hybrids': 'Hybrids',
    'music': 'Music',
    'reading': 'Reading',
    'fantasy': 'Fantasy',
    'royalty': 'Royalty',
}
COLORS = {'black', 'blue', 'brown', 'cream', 'gold', 'gray', 'green',
          'orange', 'pink', 'purple', 'red', 'white', 'yellow'}
FACING = {'left', 'right', 'front', 'mixed', 'unclear'}
COMPOSITION = {'single-figure', 'multiple-figures', 'framed-scene'}
START = '<!-- category-index:start -->'
END = '<!-- category-index:end -->'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(catalog):
    require(isinstance(catalog, list) and catalog, 'Catalog must be a nonempty array')
    names = set()
    for item in catalog:
        name = item['name']
        require(name not in names, f'Duplicate name: {name}')
        names.add(name)
        description = item['description']
        require(isinstance(description, str) and description.strip(), f'{name}: description')
        for key, allowed in [('categories', set(CATEGORIES)), ('colors', COLORS),
                             ('subjects', None)]:
            values = item[key]
            require(isinstance(values, list) and values, f'{name}: empty {key}')
            require(all(isinstance(value, str) and re.fullmatch(r'[a-z]+(?:-[a-z]+)*', value)
                        for value in values), f'{name}: invalid {key} tags')
            require(len(values) == len(set(values)), f'{name}: duplicate {key} tags')
            if allowed is not None:
                require(set(values) <= allowed, f'{name}: unknown {key} tags')
        require(item['facing'] in FACING, f'{name}: facing')
        require(item['composition'] in COMPOSITION, f'{name}: composition')
        limits = [variant['max_dimension'] for variant in item['variants']]
        require(limits == sorted(set(limits)), f'{name}: variant order')
        for entry in [item, *item['variants']]:
            for key in ('png', 'webp'):
                path = ROOT / entry[key]
                require(path.resolve().is_relative_to(ROOT), f'{name}: path outside repo')
                require(path.is_file() and path.suffix == f'.{key}', f'{name}: missing {path}')


def category_index(catalog):
    groups = {tag: [item for item in catalog if tag in item['categories']]
              for tag in CATEGORIES}
    lines = [START, '## Browse by category', '',
             'Categories overlap. See [the selection guide](SELECTION.md) for tag meanings and size selection.', '',
             '| Category | Images |', '| --- | --- |']
    for tag, label in CATEGORIES.items():
        lines.append(f'| [{label}](#{tag}) | {len(groups[tag])} |')
    for tag, label in CATEGORIES.items():
        lines.extend(['', f'### {label}', '', '<details>',
                      f'<summary>Show {len(groups[tag])} images</summary>', ''])
        for item in groups[tag]:
            lines.append(f"- [{item['name']}]({item['webp']}) — {item['description']}")
        lines.extend(['', '</details>'])
    lines.extend(['', END])
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Validate without writing files')
    args = parser.parse_args()
    catalog = json.loads((ROOT / 'images.json').read_text())
    validate(catalog)
    path = ROOT / 'README.md'
    readme = path.read_text()
    require(readme.count(START) == readme.count(END) == 1, 'README needs one category index block')
    start, end = readme.index(START), readme.index(END) + len(END)
    require(start < end - len(END), 'Category index markers out of order')
    updated = readme[:start] + category_index(catalog) + readme[end:]
    if args.check:
        require(updated == readme, 'README index is stale; run scripts/update_category_index.py')
    else:
        path.write_text(updated)
    print(f'Validated {len(catalog)} images across {len(CATEGORIES)} categories; README index is current.')


if __name__ == '__main__':
    main()
