from math import log10
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT = Path("outputs/egg_drop_efficiency_trend.png")

SCALE = 2
W, H = 2000 * SCALE, 1280 * SCALE
M_LEFT, M_RIGHT, M_TOP, M_BOTTOM = 170 * SCALE, 510 * SCALE, 150 * SCALE, 330 * SCALE
PLOT_L, PLOT_R = M_LEFT, W - M_RIGHT
PLOT_T, PLOT_B = M_TOP, H - M_BOTTOM
PLOT_W, PLOT_H = PLOT_R - PLOT_L, PLOT_B - PLOT_T

FONT_REG_PATHS = [
    r"C:\Windows\Fonts\Noto Sans SC (TrueType).otf",
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    r"C:\Windows\Fonts\simsun.ttc",
]
FONT_BOLD_PATHS = [
    r"C:\Windows\Fonts\Noto Sans SC Bold (TrueType).otf",
    r"C:\Windows\Fonts\msyhbd.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
]


def pick_font(paths, size):
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size * SCALE)
    return ImageFont.load_default()


FONT_TITLE = pick_font(FONT_BOLD_PATHS, 36)
FONT_SUB = pick_font(FONT_REG_PATHS, 20)
FONT_AXIS = pick_font(FONT_REG_PATHS, 20)
FONT_AXIS_BOLD = pick_font(FONT_BOLD_PATHS, 22)
FONT_LEGEND = pick_font(FONT_REG_PATHS, 21)
FONT_SMALL = pick_font(FONT_REG_PATHS, 17)

labels = [
    "4蛋\n20层",
    "12蛋\n2000层",
    "20蛋\n1万层",
    "40蛋\n20万层",
    "50蛋\n50万层",
    "60蛋\n100万层",
    "5蛋\n10^21层",
    "6蛋\n10^24层",
    "2蛋\n10^30层",
]

series = {
    "蛮力法": {
        "color": (215, 64, 64),
        "points": {0: 742.626},
        "dash_to_top": 1,
        "note": "后续规模递归爆炸，未继续测试",
    },
    "动态规划": {
        "color": (47, 112, 193),
        "points": {0: 0.191, 1: 58.061, 2: 2806.987},
        "dash_to_top": 3,
        "note": "大规模下状态与枚举代价迅速上升",
    },
    "动态规划+二分": {
        "color": (33, 145, 99),
        "points": {0: 0.031, 1: 1.159, 2: 14.265, 3: 707.0, 4: 2364.031},
        "dash_to_top": 5,
        "note": "比普通 DP 更能扩展，但仍受楼层规模影响",
    },
    "动态规划+二分+数学法": {
        "color": (122, 83, 184),
        "points": {
            0: 0.004,
            1: 0.007,
            2: 0.007,
            3: 0.010,
            4: 0.029,
            5: 0.018,
            6: 0.034,
            7: 0.036,
            8: 0.040,
        },
        "dash_to_top": None,
        "note": "超大规模下仍保持极低耗时",
    },
}

Y_MIN, Y_MAX = 0.001, 10000.0
y_ticks = [0.001, 0.01, 0.1, 1, 10, 100, 1000, 10000]


def x_pos(i):
    if len(labels) == 1:
        return PLOT_L + PLOT_W // 2
    return PLOT_L + int(i * PLOT_W / (len(labels) - 1))


def y_pos(value):
    value = min(max(value, Y_MIN), Y_MAX)
    ratio = (log10(value) - log10(Y_MIN)) / (log10(Y_MAX) - log10(Y_MIN))
    return PLOT_B - int(ratio * PLOT_H)


def line_points(points):
    return [(x_pos(i), y_pos(v)) for i, v in sorted(points.items())]


def text_size(draw, text, font):
    box = draw.multiline_textbbox((0, 0), text, font=font, spacing=4 * SCALE)
    return box[2] - box[0], box[3] - box[1]


def draw_centered(draw, xy, text, font, fill, spacing=4 * SCALE):
    x, y = xy
    tw, th = text_size(draw, text, font)
    draw.multiline_text(
        (x - tw / 2, y - th / 2),
        text,
        font=font,
        fill=fill,
        align="center",
        spacing=spacing,
    )


def draw_dashed_line(draw, xy1, xy2, fill, width, dash=14 * SCALE, gap=9 * SCALE):
    x1, y1 = xy1
    x2, y2 = xy2
    dx, dy = x2 - x1, y2 - y1
    dist = (dx * dx + dy * dy) ** 0.5
    if dist == 0:
        return
    steps = int(dist // (dash + gap)) + 1
    ux, uy = dx / dist, dy / dist
    cur = 0
    for _ in range(steps):
        start = cur
        end = min(cur + dash, dist)
        if start >= dist:
            break
        draw.line(
            (x1 + ux * start, y1 + uy * start, x1 + ux * end, y1 + uy * end),
            fill=fill,
            width=width,
        )
        cur += dash + gap


def wrap_cn(text, max_chars=19):
    lines = []
    current = ""
    for ch in text:
        current += ch
        if len(current) >= max_chars:
            lines.append(current)
            current = ""
    if current:
        lines.append(current)
    return "\n".join(lines)


img = Image.new("RGB", (W, H), (250, 251, 253))
draw = ImageDraw.Draw(img)

# Plot background
draw.rounded_rectangle(
    (PLOT_L - 26 * SCALE, PLOT_T - 24 * SCALE, PLOT_R + 26 * SCALE, PLOT_B + 24 * SCALE),
    radius=18 * SCALE,
    fill=(255, 255, 255),
    outline=(224, 229, 236),
    width=2 * SCALE,
)

# Title
title = "鸡蛋掉落实验：数据规模增大时不同算法耗时走势"
subtitle = "纵轴为运行时间 ms（对数尺度），越低表示效率越高；虚线表示超过实测范围后的不可行趋势示意"
draw_centered(draw, (W // 2, 54 * SCALE), title, FONT_TITLE, (26, 34, 48))
draw_centered(draw, (W // 2, 105 * SCALE), subtitle, FONT_SUB, (88, 98, 112))

# Grid and axes
for tick in y_ticks:
    y = y_pos(tick)
    color = (218, 224, 232) if tick != 1 else (196, 204, 216)
    draw.line((PLOT_L, y, PLOT_R, y), fill=color, width=1 * SCALE)
    label = f"{tick:g}"
    tw, th = text_size(draw, label, FONT_AXIS)
    draw.text((PLOT_L - 18 * SCALE - tw, y - th / 2), label, font=FONT_AXIS, fill=(73, 84, 98))

for i in range(len(labels)):
    x = x_pos(i)
    draw.line((x, PLOT_T, x, PLOT_B), fill=(238, 241, 246), width=1 * SCALE)
    draw.line((x, PLOT_B, x, PLOT_B + 7 * SCALE), fill=(93, 105, 120), width=2 * SCALE)
    draw_centered(draw, (x, PLOT_B + 72 * SCALE), labels[i], FONT_AXIS, (55, 65, 80))

draw.line((PLOT_L, PLOT_B, PLOT_R, PLOT_B), fill=(61, 72, 88), width=3 * SCALE)
draw.line((PLOT_L, PLOT_T, PLOT_L, PLOT_B), fill=(61, 72, 88), width=3 * SCALE)
draw_centered(draw, (PLOT_L + PLOT_W // 2, H - 58 * SCALE), "实验数据规模（从小到大）", FONT_AXIS_BOLD, (34, 44, 58))
draw.text((34 * SCALE, PLOT_T - 48 * SCALE), "运行时间 / ms", font=FONT_AXIS_BOLD, fill=(34, 44, 58))

# Curves
for name, item in series.items():
    color = item["color"]
    pts = line_points(item["points"])
    if len(pts) >= 2:
        draw.line(pts, fill=color, width=5 * SCALE, joint="curve")
    for x, y in pts:
        r = 8 * SCALE
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255), outline=color, width=4 * SCALE)

    dash_to = item.get("dash_to_top")
    if dash_to is not None:
        last_i, last_v = sorted(item["points"].items())[-1]
        start = (x_pos(last_i), y_pos(last_v))
        end = (x_pos(dash_to), y_pos(Y_MAX))
        draw_dashed_line(draw, start, end, color, 4 * SCALE)
        # Small upward arrow head
        ex, ey = end
        draw.polygon(
            [
                (ex, ey - 10 * SCALE),
                (ex - 8 * SCALE, ey + 10 * SCALE),
                (ex + 8 * SCALE, ey + 10 * SCALE),
            ],
            fill=color,
        )

# Key value labels
key_labels = [
    ("742.626", "蛮力法", 0, 742.626, (-45, -36)),
    ("2806.987", "动态规划", 2, 2806.987, (-8, -42)),
    ("2364.031", "动态规划+二分", 4, 2364.031, (-6, -42)),
    ("0.040", "动态规划+二分+数学法", 8, 0.040, (-18, -44)),
]
for text, name, i, v, offset in key_labels:
    color = series[name]["color"]
    x, y = x_pos(i), y_pos(v)
    draw.text((x + offset[0] * SCALE, y + offset[1] * SCALE), text, font=FONT_SMALL, fill=color)

# Legend and notes
legend_x = PLOT_R + 65 * SCALE
legend_y = PLOT_T + 10 * SCALE
draw.text((legend_x, legend_y), "图例", font=FONT_AXIS_BOLD, fill=(34, 44, 58))
legend_y += 48 * SCALE
for name, item in series.items():
    color = item["color"]
    draw.line((legend_x, legend_y + 13 * SCALE, legend_x + 48 * SCALE, legend_y + 13 * SCALE), fill=color, width=5 * SCALE)
    draw.ellipse((legend_x + 20 * SCALE, legend_y + 5 * SCALE, legend_x + 28 * SCALE, legend_y + 21 * SCALE), fill=(255, 255, 255), outline=color, width=3 * SCALE)
    draw.text((legend_x + 64 * SCALE, legend_y), name, font=FONT_LEGEND, fill=(36, 45, 60))
    legend_y += 44 * SCALE
    note = wrap_cn(item["note"], 18)
    draw.multiline_text(
        (legend_x + 64 * SCALE, legend_y),
        note,
        font=FONT_SMALL,
        fill=(91, 103, 118),
        spacing=4 * SCALE,
    )
    legend_y += (46 + 24 * note.count("\n")) * SCALE

# Bottom explanation
note_box = (
    PLOT_L,
    H - 170 * SCALE,
    PLOT_R + 150 * SCALE,
    H - 118 * SCALE,
)
draw.rounded_rectangle(note_box, radius=10 * SCALE, fill=(244, 247, 251), outline=(224, 229, 236), width=1 * SCALE)
draw.text(
    (note_box[0] + 18 * SCALE, note_box[1] + 13 * SCALE),
    "说明：曲线使用报告中的实测耗时绘制；缺失点表示该算法在后续规模下已不适合继续测试或未记录。",
    font=FONT_SMALL,
    fill=(72, 83, 98),
)

OUT.parent.mkdir(parents=True, exist_ok=True)
img = img.resize((W // SCALE, H // SCALE), Image.Resampling.LANCZOS)
img.save(OUT, quality=95)
print(OUT.resolve())
