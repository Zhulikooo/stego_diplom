import matplotlib.pyplot as plt
import numpy as np

# Данные из ваших экспериментов
methods = [
    'Последовательное\nLSB',
    'LSB в синий\nканал',
    'Случайные\nпиксели (LCG)',
    'Случайные биты +\nслучайные пиксели',
    'Только\nслучайные биты',
    'Многобитовое\n(8 битов)'
]

# R-S разность для каждого метода
rs_diff = [45.15, 85.26, 18.25, 49.23, 59.76, -0.75]

# Цвета для столбцов
colors = ["#6089a7", "#5ba05b", "#c46464", "#dca16d", "#937aac", "#8E3939"]

# Создание фигуры
plt.figure(figsize=(14, 7))

# Построение столбцов
bars = plt.bar(methods, rs_diff, color=colors, edgecolor='black', linewidth=1.2)

# Добавление значений на столбцы
for bar, value in zip(bars, rs_diff):
    # Для отрицательных значений подпись ставим ниже
    if value < 0:
        plt.text(bar.get_x() + bar.get_width()/2, value - 1.5,
                 f'{value:.2f}%', ha='center', va='top', fontsize=11, fontweight='bold', color='red')
    else:
        plt.text(bar.get_x() + bar.get_width()/2, value + 1.5,
                 f'{value:.2f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')

# Добавление пороговых линий
plt.axhline(y=50, color='red', linestyle='--', linewidth=2, label='Порог 50% (чистое)')
plt.axhline(y=20, color='orange', linestyle='--', linewidth=2, label='Порог 20% (встройка)')

# Настройка подписей и заголовка
plt.xlabel('Метод встраивания', fontsize=14, fontweight='bold')
plt.ylabel('R-S разность (%)', fontsize=14, fontweight='bold')
plt.title('Сравнение R-S разности для шести методов LSB-встраивания', fontsize=14, fontweight='bold', pad=15)

# Настройка сетки и легенды
plt.grid(axis='y', linestyle='--', alpha=0.3)
plt.legend(loc='upper right', fontsize=11)

# Установка границ по оси Y
plt.ylim(-10, 100)

# Поворот подписей по оси X
plt.xticks(rotation=0, ha='center', fontsize=10)
plt.yticks(fontsize=11)

# Добавление нулевой линии для наглядности
plt.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)

plt.tight_layout()

# Сохранение в файл
plt.savefig('comparison_6_methods.png', dpi=300, bbox_inches='tight')

# Отображение графика
plt.show()