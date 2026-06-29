import matplotlib.pyplot as plt
import numpy as np

# =====================================================
# ГРАФИК 1 (к таблице 4.1) - Зависимость R-S разности от процента встраивания
# =====================================================

# Данные для графика 1
percent = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
rs_diff = np.array([68.4, 52.1, 41.3, 34.2, 25.8, 18.6, 12.4, 7.2, 3.1, -1.5, -5.2])

# Создание фигуры и осей для первого графика
fig1, ax1 = plt.subplots(figsize=(10, 6))

# Построение графика
ax1.plot(percent, rs_diff, 'b-o', linewidth=2, markersize=8, label='R-S разность')

# Пороговые линии
ax1.axhline(y=50, color='r', linestyle='--', linewidth=1.5, alpha=0.7, label='Порог 50% (чистое)')
ax1.axhline(y=20, color='orange', linestyle='--', linewidth=1.5, alpha=0.7, label='Порог 20% (встройка)')

# Настройка подписей и заголовка
ax1.set_xlabel('Процент встраивания (%)', fontsize=12)
ax1.set_ylabel('R-S разность (%)', fontsize=12)
ax1.set_title('Зависимость R-S разности от процента встраивания\n(последовательное LSB-встраивание)', fontsize=14)

# Настройка сетки и легенды
ax1.grid(True, alpha=0.3)
ax1.legend(loc='upper right', fontsize=10)

# Установка границ осей
ax1.set_xlim(-5, 105)
ax1.set_ylim(-10, 75)

# Сохранение графика в файл (раскомментируйте при необходимости)
# plt.savefig('graph_4_1.png', dpi=300, bbox_inches='tight')

# Отображение графика
plt.tight_layout()
plt.show()


# =====================================================
# ГРАФИК 2 (к таблице 4.4) - Сравнение встраивания в один пиксель и во все пиксели
# =====================================================

# Данные для графика 2
bits = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8])
rs_one_pixel = np.array([68.4, 65.2, 58.7, 49.3, 38.5, 26.1, 14.8, 6.2, -2.4])
rs_all_pixels = np.array([68.4, 41.3, 28.6, 18.2, 9.4, 2.1, -3.5, -8.4, -12.6])

# Создание фигуры и осей для второго графика
fig2, ax2 = plt.subplots(figsize=(10, 6))

# Построение графиков
ax2.plot(bits, rs_one_pixel, 'g-s', linewidth=2, markersize=8, 
         label='Встраивание в один пиксель')
ax2.plot(bits, rs_all_pixels, 'r-^', linewidth=2, markersize=8, 
         label='Встраивание во все пиксели')

# Пороговая линия 20% (для наглядности)
ax2.axhline(y=20, color='orange', linestyle='--', linewidth=1.5, alpha=0.7, 
            label='Порог 20% (встройка)')

# Настройка подписей и заголовка
ax2.set_xlabel('Количество битов в пикселе', fontsize=12)
ax2.set_ylabel('R-S разность (%)', fontsize=12)
ax2.set_title('Сравнение встраивания в один пиксель и во все пиксели', fontsize=14)

# Настройка сетки и легенды
ax2.grid(True, alpha=0.3)
ax2.legend(loc='upper right', fontsize=10)

# Установка границ осей
ax2.set_xlim(-0.5, 8.5)
ax2.set_ylim(-15, 75)

# Добавление подписей значений на точки (опционально)
for i, (x, y1, y2) in enumerate(zip(bits, rs_one_pixel, rs_all_pixels)):
    ax2.annotate(f'{y1:.1f}', (x, y1), textcoords="offset points", xytext=(0, 10), 
                 ha='center', fontsize=8, alpha=0.7)
    ax2.annotate(f'{y2:.1f}', (x, y2), textcoords="offset points", xytext=(0, -15), 
                 ha='center', fontsize=8, alpha=0.7)

# Сохранение графика в файл (раскомментируйте при необходимости)
# plt.savefig('graph_4_4.png', dpi=300, bbox_inches='tight')

# Отображение графика
plt.tight_layout()
plt.show()