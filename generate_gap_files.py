"""
generate_gap_files.py — ИСПРАВЛЕННАЯ версия
Создаёт gap_XX.json, где список идёт СТРОГО по физическому ходу светодиодов
(по serpentine-пути с нужного угла, как реально проложена лента).
"""

import json
from collections import defaultdict

# ==================== НАСТРОЙКИ (как раньше) ====================
ORIENTATIONS = {
    'FL': "Top Left, Vertical, Serpentine",
    'FR': "Top Left, Vertical, Serpentine",
    'ML': "Top Left, Vertical, Serpentine",
    'MR': "Bottom Right, Vertical, Serpentine",
    'P':  "Bottom Left, Vertical, Serpentine",
    'I':  "Top Left, Vertical, Serpentine"
}

# Загружаем mapping
with open("mapping.json", encoding="utf-8") as f:
    mapping = json.load(f)

groups = defaultdict(set)
for led_name, (row, col) in mapping.items():
    letter = led_name.split('_')[0]
    groups[letter].add((row, col))   # (row, col) — оригинальные координаты из таблицы

print("Генерация корректных gap-файлов (по физическому ходу ленты)...\n")

def get_traversal_order(width: int, height: int, corner: str, serpentine: bool = True) -> list[tuple[int, int]]:
    """Возвращает порядок обхода всех ячеек (local_x, local_y) по физическому serpentine-пути"""
    order = []
    x_step = 1 if corner in ("Top Left", "Bottom Left") else -1
    y_step = 1 if corner in ("Top Left", "Top Right") else -1
    x = 0 if x_step > 0 else width - 1
    y = 0 if y_step > 0 else height - 1

    for col_idx in range(width):
        # Определяем направление по Y для текущего столбца
        current_y_step = y_step
        if serpentine and (col_idx % 2 == 1):
            current_y_step = -y_step

        # Начальная Y для столбца
        cur_y = 0 if current_y_step > 0 else height - 1

        for _ in range(height):
            order.append((x, cur_y))
            cur_y += current_y_step

        x += x_step

    return order


for letter in sorted(groups.keys()):
    positions = groups[letter]
    if not positions:
        continue

    rows = [r for r, _ in positions]
    cols = [c for _, c in positions]
    min_r, max_r = min(rows), max(rows)
    min_c, max_c = min(cols), max(cols)

    height = max_r - min_r + 1
    width  = max_c - min_c + 1

    # Парсим настройки для этой буквы
    corner_str, _, _ = ORIENTATIONS[letter].partition(", ")
    traversal = get_traversal_order(width, height, corner_str)

    # Формируем gap_map ПО ФИЗИЧЕСКОМУ ПОРЯДКУ (индекс = шаг по ленте)
    gap_map = []
    real_positions = {(r - min_r, c - min_c) for r, c in positions}  # локальные (y, x)

    for local_x, local_y in traversal:
        if (local_y, local_x) in real_positions:   # (y, x) — как в матрице
            gap_map.append(1)
        else:
            gap_map.append(-1)

    filename = f"gap_{letter}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(gap_map, f, separators=(',', ':'), ensure_ascii=False)

    real_leds = sum(1 for v in gap_map if v == 1)
    fill = real_leds / len(gap_map) * 100

    print(f"✓ {letter:3} → {filename:15} | {width:3}×{height:<3} | "
          f"LED: {real_leds:4} ({fill:.1f}%)")
    print(f"   Рекомендуемые настройки 2D Configuration:")
    print(f"   → Start corner: {ORIENTATIONS[letter]}")
    print(f"   → Width: {width}   Height: {height}")
    print(f"   → Orientation: Vertical   Serpentine: включено")
    print("-" * 70)

print("\n✅ Все gap-файлы готовы!")
print("Теперь для каждого контроллера:")
print("1. Загрузи gap_XX.json через /edit")
print("2. В Config → 2D Configuration поставь ТОЧНО те значения, которые выше")
print("3. LED Preferences → LED count оставь как есть (реальное количество)")
print("4. Сохрани + Reset")
print("\nТеперь WLED будет правильно обрабатывать пропуски даже без ledmap.json!")