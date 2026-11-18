"""
Visual Runner Service.
Handles accurate automatic visual rendering for graphics tasks when no screenshots are uploaded:
1. 3D Wireframe Cuboid/Cube OpenGL tasks -> 4 perspective rotation renders (0, 35, 70, 120 deg).
2. 2D Rasterization (DDA Line, Bresenham Line, Midpoint Circle) -> crisp 2D coordinate grid plots.
3. All other tasks -> returns [] (never fakes an unrelated graphic).
"""

import io
import re
import math
import base64
from PIL import Image, ImageDraw


def _detect_visual_kind(task_title: str, task_description: str, code: str) -> str | None:
    """Return 'cuboid_3d', 'dda_2d', 'circle_2d', or None."""
    combined = f"{task_title} {task_description} {code}".lower()

    if any(k in combined for k in ("cuboid", "wireframe", "glrotatef", "gluperspective", "3d cube", "rotating cube")):
        return "cuboid_3d"
    if any(k in combined for k in ("dda", "bresenham", "line drawing")):
        if "circle" in combined and "line" not in combined:
            return "circle_2d"
        return "dda_2d"
    if "midpoint circle" in combined or "bresenham circle" in combined:
        return "circle_2d"
    return None


def is_visual_task(task_title: str, task_description: str, code: str) -> bool:
    """Detect if task can be auto-rendered visually."""
    return _detect_visual_kind(task_title, task_description, code) is not None


def _img_to_b64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")


def render_3d_wireframe(
    vertices: list[list[float]],
    edges: list[tuple[int, int]],
    angle_y_deg: float,
    tilt_x_deg: float = 20.0,
    width: int = 800,
    height: int = 600,
    color: tuple[int, int, int] = (255, 0, 0),
    bg_color: tuple[int, int, int] = (0, 0, 0),
    line_width: int = 3,
) -> str:
    """Render 3D wireframe perspective projection and return as Base64 data URL."""
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    rad_y = math.radians(angle_y_deg)
    rad_x = math.radians(tilt_x_deg)

    projected = []
    for x, y, z in vertices:
        x1 = x * math.cos(rad_y) + z * math.sin(rad_y)
        y1 = y
        z1 = -x * math.sin(rad_y) + z * math.cos(rad_y)

        x2 = x1
        y2 = y1 * math.cos(rad_x) - z1 * math.sin(rad_x)
        z2 = y1 * math.sin(rad_x) + z1 * math.cos(rad_x)

        z_cam = z2 + 8.0
        if z_cam <= 0.1:
            z_cam = 0.1
        fov_scale = 650.0 / z_cam
        px = width / 2.0 + x2 * fov_scale
        py = height / 2.0 - y2 * fov_scale
        projected.append((px, py))

    for u, v in edges:
        if u < len(projected) and v < len(projected):
            draw.line([projected[u], projected[v]], fill=color, width=line_width)

    return _img_to_b64(img)


def _render_dda_grid(x0: int, y0: int, x1: int, y1: int, accent=(16, 185, 129)) -> str:
    """Render a clean 2D rasterized pixel grid for DDA/Bresenham line drawing."""
    w, h = 800, 600
    img = Image.new("RGB", (w, h), (15, 23, 28))
    draw = ImageDraw.Draw(img)

    margin = 60
    grid_n = 20
    cell_w = (w - 2 * margin) / grid_n
    cell_h = (h - 2 * margin) / grid_n

    # Draw subtle grid
    for i in range(grid_n + 1):
        gx = margin + i * cell_w
        gy = margin + i * cell_h
        draw.line([(gx, margin), (gx, h - margin)], fill=(34, 52, 60), width=1)
        draw.line([(margin, gy), (w - margin, gy)], fill=(34, 52, 60), width=1)

    # Axes
    draw.line([(margin, h - margin), (w - margin, h - margin)], fill=(148, 163, 184), width=2)
    draw.line([(margin, margin), (margin, h - margin)], fill=(148, 163, 184), width=2)

    # DDA rasterization
    dx = x1 - x0
    dy = y1 - y0
    steps = max(abs(dx), abs(dy), 1)
    x_inc = dx / steps
    y_inc = dy / steps
    cx, cy = float(x0), float(y0)
    pts = []
    for _ in range(steps + 1):
        rx, ry = round(cx), round(cy)
        pts.append((rx, ry))
        px0 = margin + rx * cell_w + 2
        py0 = h - margin - (ry + 1) * cell_h + 2
        px1 = px0 + cell_w - 4
        py1 = py0 + cell_h - 4
        draw.rectangle([px0, py0, px1, py1], fill=accent, outline=(255, 255, 255))
        cx += x_inc
        cy += y_inc

    # Ideal mathematical line overlay
    sx = margin + (x0 + 0.5) * cell_w
    sy = h - margin - (y0 + 0.5) * cell_h
    ex = margin + (x1 + 0.5) * cell_w
    ey = h - margin - (y1 + 0.5) * cell_h
    draw.line([(sx, sy), (ex, ey)], fill=(250, 204, 21), width=3)

    return _img_to_b64(img)


def _render_circle_grid(radius: int, accent=(56, 189, 248)) -> str:
    """Render a clean 2D rasterized midpoint circle grid."""
    w, h = 800, 600
    img = Image.new("RGB", (w, h), (15, 23, 28))
    draw = ImageDraw.Draw(img)

    margin = 50
    grid_n = 24
    cell = min((w - 2 * margin), (h - 2 * margin)) / grid_n
    ox = (w - grid_n * cell) / 2
    oy = (h - grid_n * cell) / 2
    cx_idx = grid_n // 2
    cy_idx = grid_n // 2

    for i in range(grid_n + 1):
        draw.line([(ox + i * cell, oy), (ox + i * cell, oy + grid_n * cell)], fill=(34, 52, 60), width=1)
        draw.line([(ox, oy + i * cell), (ox + grid_n * cell, oy + i * cell)], fill=(34, 52, 60), width=1)

    # Midpoint circle points
    x, y = 0, radius
    p = 1 - radius
    pixels = set()
    while x <= y:
        for px, py in (
            (x, y), (-x, y), (x, -y), (-x, -y),
            (y, x), (-y, x), (y, -x), (-y, -x),
        ):
            pixels.add((cx_idx + px, cy_idx + py))
        x += 1
        if p < 0:
            p += 2 * x + 1
        else:
            y -= 1
            p += 2 * (x - y) + 1

    for gx, gy in pixels:
        if 0 <= gx < grid_n and 0 <= gy < grid_n:
            x0 = ox + gx * cell + 2
            y0 = oy + (grid_n - 1 - gy) * cell + 2
            draw.rectangle([x0, y0, x0 + cell - 4, y0 + cell - 4], fill=accent, outline=(255, 255, 255))

    return _img_to_b64(img)


def generate_auto_visualizations(task_title: str, task_description: str, code: str) -> list[dict]:
    """
    Generate accurate automatic visualizations when no screenshots are provided.
    Returns [] if the task is not a supported auto-render visual type.
    """
    kind = _detect_visual_kind(task_title, task_description, code)
    if not kind:
        return []

    combined = f"{task_title} {task_description} {code}".lower()

    if kind == "dda_2d":
        cases = [
            (2, 2, 17, 11, (16, 185, 129), "Gentle positive slope ($0 < m < 1$)"),
            (3, 2, 11, 17, (56, 189, 248), "Steep positive slope ($m > 1$)"),
            (2, 15, 17, 4, (244, 114, 182), "Negative slope ($m < 0$)"),
            (2, 10, 17, 10, (250, 204, 21), "Horizontal line ($m = 0$)"),
        ]
        return [{"data": _render_dda_grid(x0, y0, x1, y1, col), "caption": cap} for x0, y0, x1, y1, col, cap in cases]

    if kind == "circle_2d":
        cases = [
            (5, (16, 185, 129), "Midpoint circle ($r = 5$)"),
            (8, (56, 189, 248), "Midpoint circle ($r = 8$)"),
        ]
        return [{"data": _render_circle_grid(r, col), "caption": cap} for r, col, cap in cases]

    # Default cuboid_3d
    vertices = [
        [2.0, -1.0, -1.5], [2.0, 1.0, -1.5], [-2.0, 1.0, -1.5], [-2.0, -1.0, -1.5],
        [2.0, -1.0, 1.5], [2.0, 1.0, 1.5], [-2.0, -1.0, 1.5], [-2.0, 1.0, 1.5],
    ]
    edges = [
        (0, 1), (0, 3), (0, 4), (2, 1), (2, 3), (2, 7),
        (6, 3), (6, 4), (6, 7), (5, 1), (5, 4), (5, 7),
    ]

    try:
        v_matches = re.findall(r"\(\s*(-?[\d\.]+)\s*,\s*(-?[\d\.]+)\s*,\s*(-?[\d\.]+)\s*\)", code)
        if len(v_matches) >= 8:
            vertices = [[float(x), float(y), float(z)] for x, y, z in v_matches[:8]]
    except Exception:
        pass

    color = (255, 0, 0)
    if "green" in combined:
        color = (0, 255, 0)
    elif "blue" in combined:
        color = (0, 100, 255)
    elif "white" in combined:
        color = (255, 255, 255)

    line_width = 3
    if "gllinewidth(2" in combined:
        line_width = 2
    elif "gllinewidth(4" in combined:
        line_width = 4

    angles = [
        (0, "Front view ($\\theta = 0^\\circ$)"),
        (35, "Rotating view ($\\theta = 35^\\circ$)"),
        (70, "Side-angled view ($\\theta = 70^\\circ$)"),
        (120, "Side view ($\\theta = 120^\\circ$)"),
    ]

    return [
        {
            "data": render_3d_wireframe(
                vertices=vertices,
                edges=edges,
                angle_y_deg=deg,
                tilt_x_deg=20.0,
                width=800,
                height=600,
                color=color,
                line_width=line_width,
            ),
            "caption": caption,
        }
        for deg, caption in angles
    ]
