"""
generate_ledmaps.py — финальная версия под ledmap.json (по документации WLED)
Создаёт папки ledmaps/FL/, ledmaps/P/ и т.д. с файлом строго ledmap.json внутри
"""

import json
import os
from collections import defaultdict

# ==================== ТВОИ ОРИЕНТАЦИИ ====================
ORIENTATIONS = {
    'FL': "Top Left, Vertical, Serpentine",
    'FR': "Top Left, Vertical, Serpentine",
    'ML': "Top Left, Vertical, Serpentine",
    'MR': "Bottom Right, Vertical, Serpentine",
    'P':  "Bottom Left, Vertical, Serpentine",
    'I':  "Top Left, Vertical, Serpentine"
}

# Загружаем mapping.json
with open("mapping.json", encoding="utf-8") as f:
    mapping = json.load(f)

# Создаём корневую папку
os.makedirs("ledmaps", exist_ok=True)

# Группируем светодиоды по буквам
groups = defaultdict(list)
for led_name, (row, col) in mapping.items():
    letter = led_name.split('_')[0]
    phys_index = int(led_name.split('_')[1]) - 1   # 0-based
    groups[letter].append((phys_index, row, col))

print("Генерация ledmap.json для каждой буквы...\n")

for letter in sorted(groups.keys()):
    leds = groups[letter]
    if not leds:
        continue

    # Tight bounding box (убираем лишние пустые края — это часто решает проблемы с П)
    rows = [r for _, r, _ in leds]
    cols = [c for _, _, c in leds]
    min_row, max_row = min(rows), max(rows)
    min_col, max_col = min(cols), max(cols)

    height = max_row - min_row + 1
    width  = max_col - min_col + 1

    # Создаём сетку
    grid = [[-1 for _ in range(width)] for _ in range(height)]

    for phys_index, row, col in leds:
        local_y = row - min_row
        local_x = col - min_col
        grid[local_y][local_x] = phys_index

    # Плоский массив (row-major) — именно так требует WLED
    flat_map = [grid[y][x] for y in range(height) for x in range(width)]

    ledmap = {
        "width": width,
        "height": height,
        "map": flat_map
    }

    # Создаём папку для буквы и сохраняем файл
    folder = f"ledmaps/{letter}"
    os.makedirs(folder, exist_ok=True)
    filename = f"{folder}/ledmap.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(ledmap, f, separators=(',', ':'), ensure_ascii=False)

    real_leds = sum(1 for v in flat_map if v != -1)
    fill = real_leds / len(flat_map) * 100

    print(f"✓ {letter:3} → {filename}")
    print(f"   Размер матрицы: {width}×{height} | LED: {real_leds} ({fill:.1f}%)")
    print(f"   Рекомендация 2D Configuration:")
    print(f"   → Start corner: {ORIENTATIONS[letter]}")
    print(f"   → Width: {width}   Height: {height}")
    print(f"   → Type: 2D Matrix   Serpentine: включено")
    print("-" * 70)

print("\n✅ Готово! Все ledmap.json созданы в папках ledmaps/...")
