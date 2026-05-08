#!/usr/bin/env python3
"""
Generate SVG-based figure-matrices questions and APPEND them to questions.json.
Preserves all existing question IDs.
Run: python gen_svg_questions.py
"""
import json, math, os

OUT = os.path.join(os.path.dirname(__file__), "questions.json")

# ─── SVG SHAPE HELPERS ────────────────────────────────────────────
# Each helper draws at center (sz/2, sz/2) within a sz×sz cell (default 52).

def _circle(cx, cy, r, fill, color):
    if fill == 'solid':
        return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{color}"/>'
    if fill == 'outline':
        return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" stroke="{color}" stroke-width="3"/>'
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="3" stroke-dasharray="4,2.5"/>')


def _square(cx, cy, r, fill, color):
    s = r * 1.72; ox, oy = cx - s / 2, cy - s / 2
    base = f'x="{ox:.1f}" y="{oy:.1f}" width="{s:.1f}" height="{s:.1f}" rx="3"'
    if fill == 'solid':
        return f'<rect {base} fill="{color}"/>'
    if fill == 'outline':
        return f'<rect {base} fill="none" stroke="{color}" stroke-width="3"/>'
    return f'<rect {base} fill="none" stroke="{color}" stroke-width="3" stroke-dasharray="4,2.5"/>'


def _triangle(cx, cy, r, fill, color):
    pts = f'{cx:.1f},{cy - r:.1f} {cx - r:.1f},{cy + r * 0.6:.1f} {cx + r:.1f},{cy + r * 0.6:.1f}'
    if fill == 'solid':
        return f'<polygon points="{pts}" fill="{color}"/>'
    if fill == 'outline':
        return f'<polygon points="{pts}" fill="none" stroke="{color}" stroke-width="3"/>'
    return f'<polygon points="{pts}" fill="none" stroke="{color}" stroke-width="3" stroke-dasharray="4,2.5"/>'


def _diamond(cx, cy, r, fill, color):
    pts = f'{cx:.1f},{cy - r:.1f} {cx + r:.1f},{cy:.1f} {cx:.1f},{cy + r:.1f} {cx - r:.1f},{cy:.1f}'
    if fill == 'solid':
        return f'<polygon points="{pts}" fill="{color}"/>'
    if fill == 'outline':
        return f'<polygon points="{pts}" fill="none" stroke="{color}" stroke-width="3"/>'
    return f'<polygon points="{pts}" fill="none" stroke="{color}" stroke-width="3" stroke-dasharray="4,2.5"/>'


def _star(cx, cy, r, fill, color):
    pts = []
    for i in range(10):
        a = math.radians(i * 36 - 90)
        ri = r if i % 2 == 0 else r * 0.42
        pts.append(f'{cx + ri * math.cos(a):.1f},{cy + ri * math.sin(a):.1f}')
    pstr = ' '.join(pts)
    if fill == 'solid':
        return f'<polygon points="{pstr}" fill="{color}"/>'
    return f'<polygon points="{pstr}" fill="none" stroke="{color}" stroke-width="2.5"/>'


def _cross(cx, cy, r, fill, color):
    t = r * 0.33
    if fill == 'solid':
        return (f'<rect x="{cx-t:.1f}" y="{cy-r:.1f}" width="{t*2:.1f}" height="{r*2:.1f}" fill="{color}"/>'
                f'<rect x="{cx-r:.1f}" y="{cy-t:.1f}" width="{r*2:.1f}" height="{t*2:.1f}" fill="{color}"/>')
    return (f'<rect x="{cx-t:.1f}" y="{cy-r:.1f}" width="{t*2:.1f}" height="{r*2:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="2"/>'
            f'<rect x="{cx-r:.1f}" y="{cy-t:.1f}" width="{r*2:.1f}" height="{t*2:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="2"/>')


SHAPE_FNS = {
    'circle': _circle, 'square': _square, 'triangle': _triangle,
    'diamond': _diamond, 'star': _star, 'cross': _cross,
}
COLORS = {
    'blue': '#4a7cf7', 'teal': '#2dd6a0', 'orange': '#f5a623',
    'pink': '#ff6b9d', 'purple': '#a855f7',
}
FILL_LABELS = {'solid': 'filled', 'outline': 'hollow', 'dashed': 'dashed'}
SHAPE_LABELS = {
    'circle': 'circle', 'square': 'square', 'triangle': 'triangle',
    'diamond': 'diamond', 'star': 'star', 'cross': 'cross',
}


def cell(shape, fill, color_key, sz=52, count=1):
    """Draw `count` copies of shape in a sz×sz cell."""
    fn = SHAPE_FNS[shape]
    color = COLORS.get(color_key, color_key)
    cx, cy = sz / 2, sz / 2
    if count == 1:
        r = sz * 0.36
        return fn(cx, cy, r, fill, color)
    elif count == 2:
        r = sz * 0.24
        return fn(sz * 0.3, cy, r, fill, color) + fn(sz * 0.7, cy, r, fill, color)
    elif count == 3:
        r = sz * 0.18
        return (fn(sz * 0.2, cy, r, fill, color) +
                fn(sz * 0.5, cy, r, fill, color) +
                fn(sz * 0.8, cy, r, fill, color))
    return ''


def make_matrix(cells_9, cell_sz=70):
    """Build a 3×3 matrix SVG from a 9-element list (None → question mark)."""
    gap = 5
    total = cell_sz * 3 + gap * 4
    parts = [f'<svg viewBox="0 0 {total} {total}" xmlns="http://www.w3.org/2000/svg">',
             f'<rect width="{total}" height="{total}" fill="#f0f2ff" rx="10"/>']
    # Grid dividers
    for k in (1, 2):
        x = gap + k * (cell_sz + gap) - gap // 2
        parts.append(f'<line x1="{x}" y1="4" x2="{x}" y2="{total-4}" stroke="#dee2e6" stroke-width="2"/>')
        parts.append(f'<line x1="4" y1="{x}" x2="{total-4}" y2="{x}" stroke="#dee2e6" stroke-width="2"/>')
    for row in range(3):
        for col in range(3):
            idx = row * 3 + col
            ox = gap + col * (cell_sz + gap)
            oy = gap + row * (cell_sz + gap)
            if cells_9[idx] is None:
                parts.append(f'<rect x="{ox}" y="{oy}" width="{cell_sz}" height="{cell_sz}" '
                              f'fill="rgba(124,111,255,0.07)" rx="5" stroke="rgba(124,111,255,0.4)" '
                              f'stroke-width="2" stroke-dasharray="5,3"/>')
                qx, qy = ox + cell_sz // 2, oy + cell_sz // 2 + 10
                parts.append(f'<text x="{qx}" y="{qy}" text-anchor="middle" font-size="26" '
                              f'fill="rgba(124,111,255,0.55)" font-family="Arial,sans-serif" font-weight="bold">?</text>')
            else:
                parts.append(f'<rect x="{ox}" y="{oy}" width="{cell_sz}" height="{cell_sz}" '
                              f'fill="white" rx="5" opacity="0.85"/>')
                parts.append(f'<g transform="translate({ox+int(cell_sz/2-26)},{oy+int(cell_sz/2-26)})">'
                              f'{cells_9[idx]}</g>')
    parts.append('</svg>')
    return ''.join(parts)


def make_opt(content, sz=52):
    """Build a small answer-option SVG."""
    box = sz + 12
    return (f'<svg viewBox="0 0 {box} {box}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="{box}" height="{box}" fill="#f0f2ff" rx="7"/>'
            f'<rect x="3" y="3" width="{box-6}" height="{box-6}" fill="white" rx="5" opacity="0.85"/>'
            f'<g transform="translate(6,6)">{content}</g>'
            f'</svg>')


def make_question(grade, diff, text, cells_9, answer_cells_4, answer_idx, explanation):
    """Build a complete figure-matrices question dict with SVGs."""
    return {
        "battery": "non-verbal",
        "type": "figure-matrices",
        "grade": grade,
        "difficulty": diff,
        "text": text,
        "svg": make_matrix(cells_9),
        "options": [
            {"label": lbl, "text": "", "svg": make_opt(c)}
            for lbl, c in zip(["A", "B", "C", "D"], answer_cells_4)
        ],
        "answer": answer_idx,
        "explanation": explanation,
        "tags": ["figure-matrices", grade, diff],
    }


# ─── QUESTION DEFINITIONS ─────────────────────────────────────────
def build_questions():
    qs = []

    # ── 1. FILL PROGRESSION: solid → outline → dashed ─────────────
    for shape, sname in [('circle', 'circle'), ('square', 'square'), ('triangle', 'triangle'),
                         ('diamond', 'diamond'), ('star', 'star')]:
        for col_color, grade, diff in [('blue', '3', 'easy'), ('teal', '4', 'medium'),
                                       ('orange', '5', 'medium'), ('purple', '6', 'hard')]:
            fills = ['solid', 'outline', 'dashed']
            grid = []
            for row_fill in fills:
                for col_shape in [shape, shape, shape]:
                    grid.append(cell(col_shape, row_fill, col_color))
            grid[-1] = None  # last cell = answer
            opts = [
                cell(shape, 'dashed', col_color),   # correct
                cell(shape, 'solid', col_color),
                cell(shape, 'outline', col_color),
                cell(shape, 'dashed', 'pink'),       # wrong color
            ]
            qs.append(make_question(
                grade, diff,
                f'Each row shows the same {sname} in a different style. What fills the missing cell?',
                grid, opts, 0,
                f'Row 1=filled, Row 2=hollow, Row 3=dashed. Missing cell: dashed {sname}.'
            ))

    # ── 2. SHAPE SEQUENCE (Latin-square): each row & col has all 3 shapes ─
    shapes3 = [('circle', 'square', 'triangle'), ('diamond', 'circle', 'star'),
               ('triangle', 'star', 'square')]
    colors3 = ['blue', 'teal', 'orange']
    for (s1, s2, s3), col_c, grade, diff in [
        (shapes3[0], 'blue',   '2', 'easy'),
        (shapes3[1], 'teal',   '4', 'medium'),
        (shapes3[2], 'orange', '5', 'medium'),
    ]:
        order = [[s1, s2, s3], [s2, s3, s1], [s3, s1, s2]]
        grid = []
        for row_order in order:
            for sh in row_order:
                grid.append(cell(sh, 'solid', col_c))
        grid[-1] = None
        missing_shape = order[2][2]
        other_shapes = [sh for sh in [s1, s2, s3] if sh != missing_shape]
        opts = [
            cell(missing_shape, 'solid', col_c),
            cell(other_shapes[0], 'solid', col_c),
            cell(other_shapes[1], 'solid', col_c),
            cell(missing_shape, 'outline', col_c),
        ]
        qs.append(make_question(
            grade, diff,
            'Every row and every column contains each shape exactly once. What is missing?',
            grid, opts, 0,
            f'Latin-square pattern — each row and column has all three shapes. Missing: {missing_shape}.'
        ))

    # ── 3. COUNT PROGRESSION: 1 → 2 → 3 shapes per row ──────────
    for shape, sname in [('circle', 'circles'), ('square', 'squares'),
                         ('triangle', 'triangles'), ('star', 'stars')]:
        for col_c, grade, diff in [('blue', '2', 'easy'), ('orange', '4', 'medium')]:
            grid = []
            for row_count in [1, 2, 3]:
                for _ in range(3):
                    grid.append(cell(shape, 'solid', col_c, count=row_count))
            grid[-1] = None
            opts = [
                cell(shape, 'solid', col_c, count=3),
                cell(shape, 'solid', col_c, count=1),
                cell(shape, 'solid', col_c, count=2),
                cell(shape, 'outline', col_c, count=3),
            ]
            qs.append(make_question(
                grade, diff,
                f'The number of {sname} increases by 1 each row. What belongs in the last cell?',
                grid, opts, 0,
                f'Row 1=1 {sname}, Row 2=2 {sname}, Row 3=3 {sname}. Last cell: 3 {sname}.'
            ))

    # ── 4. COLOR ROTATION: blue → teal → orange across columns ───
    color_seq = [('blue', 'teal', 'orange'), ('teal', 'orange', 'purple'),
                 ('purple', 'blue', 'teal')]
    for (c1, c2, c3), shape, grade, diff in [
        (color_seq[0], 'circle',   '3', 'easy'),
        (color_seq[1], 'square',   '5', 'medium'),
        (color_seq[2], 'triangle', '6', 'hard'),
    ]:
        grid = []
        for _ in range(3):
            for c in [c1, c2, c3]:
                grid.append(cell(shape, 'solid', c))
        grid[-1] = None
        opts = [
            cell(shape, 'solid', c3),
            cell(shape, 'solid', c1),
            cell(shape, 'solid', c2),
            cell(shape, 'outline', c3),
        ]
        qs.append(make_question(
            grade, diff,
            'Colors follow the same pattern in every row. What is missing?',
            grid, opts, 0,
            f'Each row cycles through the same 3 colors. Last cell uses the 3rd color.'
        ))

    # ── 5. SIZE PROGRESSION: small → medium → large ──────────────
    size_cells = {
        'small':  lambda s, c: SHAPE_FNS[s](26, 26, 10, 'solid', COLORS[c]),
        'medium': lambda s, c: SHAPE_FNS[s](26, 26, 18, 'solid', COLORS[c]),
        'large':  lambda s, c: SHAPE_FNS[s](26, 26, 26, 'solid', COLORS[c]),
    }
    for shape, sname in [('circle', 'circle'), ('square', 'square'), ('diamond', 'diamond')]:
        for col_c, grade, diff in [('teal', '3', 'easy'), ('blue', '5', 'medium')]:
            grid = []
            for _ in range(3):
                for sz_key in ['small', 'medium', 'large']:
                    grid.append(size_cells[sz_key](shape, col_c))
            grid[-1] = None
            opts = [
                size_cells['large'](shape, col_c),
                size_cells['small'](shape, col_c),
                size_cells['medium'](shape, col_c),
                size_cells['large']('circle' if shape != 'circle' else 'square', col_c),
            ]
            qs.append(make_question(
                grade, diff,
                f'Each row shows a {sname} that grows larger. What belongs in the missing cell?',
                grid, opts, 0,
                f'Pattern: small → medium → large {sname}. Missing: large {sname}.'
            ))

    # ── 6. SHAPE + FILL COMBO (rows = shapes, cols = fills) ──────
    for grade, diff, col_c in [('4', 'medium', 'blue'), ('6', 'hard', 'purple'),
                                ('5', 'medium', 'teal')]:
        row_shapes = ['circle', 'square', 'triangle']
        col_fills  = ['solid', 'outline', 'dashed']
        grid = []
        for sh in row_shapes:
            for fi in col_fills:
                grid.append(cell(sh, fi, col_c))
        grid[-1] = None
        # Missing = triangle + dashed
        opts = [
            cell('triangle', 'dashed', col_c),
            cell('triangle', 'solid', col_c),
            cell('square',   'dashed', col_c),
            cell('circle',   'dashed', col_c),
        ]
        qs.append(make_question(
            grade, diff,
            'Each row uses a different shape; each column uses a different style. What fills the missing cell?',
            grid, opts, 0,
            'Row 3 = triangles; Col 3 = dashed style. Missing: dashed triangle.'
        ))

    # ── 7. COUNT + SHAPE CHANGE per column ────────────────────────
    for grade, diff, col_c in [('3', 'medium', 'orange'), ('5', 'hard', 'blue')]:
        # col1 = 1 circle, col2 = 2 squares, col3 = 3 triangles
        grid = []
        combos = [('circle', 1), ('square', 2), ('triangle', 3)]
        for _ in range(3):
            for sh, cnt in combos:
                grid.append(cell(sh, 'solid', col_c, count=cnt))
        grid[-1] = None
        opts = [
            cell('triangle', 'solid', col_c, count=3),
            cell('triangle', 'solid', col_c, count=1),
            cell('circle',   'solid', col_c, count=3),
            cell('square',   'solid', col_c, count=3),
        ]
        qs.append(make_question(
            grade, diff,
            'Col 1 = 1 circle, Col 2 = 2 squares, Col 3 = 3 of what shape?',
            grid, opts, 0,
            'Each column has a consistent shape AND count. Col 3 = 3 triangles.'
        ))

    return qs


# ─── MAIN: APPEND TO questions.json ─────────────────────────────
def main():
    with open(OUT, encoding='utf-8') as f:
        existing = json.load(f)

    # Find the current max numeric ID
    max_id = 0
    for q in existing:
        try:
            num = int(q['id'].lstrip('Q'))
            if num > max_id:
                max_id = num
        except (ValueError, KeyError):
            pass

    new_qs = build_questions()
    for i, q in enumerate(new_qs, max_id + 1):
        q['id'] = f'Q{i:05d}'

    combined = existing + new_qs
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(combined, f, indent=2)

    print(f'✓ Appended {len(new_qs)} SVG figure-matrices questions → {OUT}')
    print(f'  Total questions now: {len(combined)}')
    print(f'  New IDs: Q{max_id+1:05d} – Q{max_id+len(new_qs):05d}')


if __name__ == '__main__':
    main()
