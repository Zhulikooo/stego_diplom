"""
rs_core.py - Ядро RS-метода стегоанализа (Фридрих, 2001)
"""

import numpy as np
from PIL import Image


def flipper_f1(x):
    """Функция флиппинга F1 (переворот LSB)"""
    if x % 2 == 0:
        return x + 1
    else:
        return x - 1


def flipper_f_minus1(x):
    """Функция флиппинга F-1 (сдвинутый переворот LSB)"""
    if x == 0:
        return 255
    elif x == 255:
        return 0
    elif x % 2 == 1:
        return x + 1
    else:
        return x - 1


def discrimination_function(group):
    """Дискриминантная функция (гладкость группы пикселей)"""
    total = 0
    for i in range(len(group) - 1):
        diff = abs(int(group[i]) - int(group[i + 1]))
        total += diff
    return total


def rs_analysis(pixels, mask=(0, 1, 0), group_size=None):
    """
    Выполняет RS-анализ массива пикселей
    
    Возвращает:
    - R_m, S_m, U_m: проценты для маски M
    - R_minus_m, S_minus_m, U_minus_m: проценты для маски -M
    - diff_m, diff_minus_m: разности R-S
    """
    if group_size is None:
        group_size = len(mask)
    
    height, width = pixels.shape
    
    groups = []
    for y in range(height):
        for x in range(0, width - group_size + 1, group_size):
            group = [pixels[y, x + i] for i in range(group_size)]
            groups.append(group)
    
    total_groups = len(groups)
    
    R_m = S_m = U_m = 0
    R_minus_m = S_minus_m = U_minus_m = 0
    
    for group in groups:
        flipped_group_m = []
        for i, pixel in enumerate(group):
            if mask[i] == 1:
                flipped_group_m.append(flipper_f1(pixel))
            elif mask[i] == -1:
                flipped_group_m.append(flipper_f_minus1(pixel))
            else:
                flipped_group_m.append(pixel)
        

        flipped_group_minus_m = []
        for i, pixel in enumerate(group):
            if mask[i] == 1:
                flipped_group_minus_m.append(flipper_f_minus1(pixel))
            elif mask[i] == -1:
                flipped_group_minus_m.append(flipper_f1(pixel))
            else:
                flipped_group_minus_m.append(pixel)
        
        f_original = discrimination_function(group)
        f_m = discrimination_function(flipped_group_m)
        f_minus_m = discrimination_function(flipped_group_minus_m)
        
        if f_m > f_original:
            R_m += 1
        elif f_m < f_original:
            S_m += 1
        else:
            U_m += 1
        
        if f_minus_m > f_original:
            R_minus_m += 1
        elif f_minus_m < f_original:
            S_minus_m += 1
        else:
            U_minus_m += 1
    
    return {
        'R_m': 100 * R_m / total_groups,
        'S_m': 100 * S_m / total_groups,
        'U_m': 100 * U_m / total_groups,
        'R_minus_m': 100 * R_minus_m / total_groups,
        'S_minus_m': 100 * S_minus_m / total_groups,
        'U_minus_m': 100 * U_minus_m / total_groups,
        'diff_m': 100 * (R_m - S_m) / total_groups,
        'diff_minus_m': 100 * (R_minus_m - S_minus_m) / total_groups
    }


def analyze_image(image_path, mask=(0, 1, 0)):
    """Загружает изображение и выполняет RS-анализ"""
    img = Image.open(image_path)
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    img = img.convert('L')
    pixels = np.array(img, dtype=np.uint8)
    return rs_analysis(pixels, mask)


def analyze_blue_channel(image_path, mask=(0, 1, 0)):
    """Анализирует только синий канал цветного изображения"""
    img = Image.open(image_path)
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    pixels = np.array(img, dtype=np.uint8)
    blue_channel = pixels[:, :, 2]
    return rs_analysis(blue_channel, mask)