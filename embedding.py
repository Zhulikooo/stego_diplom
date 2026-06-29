"""
embedding.py - Функции для встраивания информации в LSB изображений
"""

import numpy as np
from PIL import Image
from lcg import LCG


def embed_lsb_all_pixels(image_path, output_path, percent, bit_position=0):
    """
    Встраивание во все пиксели последовательно
    percent: процент изменённых пикселей (битов)
    bit_position: номер бита (0 - LSB, 1 - второй бит, ...)
    """
    img = Image.open(image_path)
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    img = img.convert('L')
    
    pixels = np.array(img, dtype=np.uint8)
    height, width = pixels.shape
    total_pixels = height * width
    
    bits_to_embed = int(total_pixels * percent / 100)
    
    np.random.seed(42)
    message = np.random.randint(0, 2, bits_to_embed)
    
    flat_pixels = pixels.flatten()
    changed_bits = 0
    
    for i in range(bits_to_embed):
        mask_bit = ~(1 << bit_position) & 0xFF
        old_value = flat_pixels[i]
        new_value = (old_value & mask_bit) | (message[i] << bit_position)
        if old_value != new_value:
            changed_bits += 1
        flat_pixels[i] = new_value
    
    result_img = Image.fromarray(flat_pixels.reshape(height, width))
    result_img.save(output_path)
    
    return changed_bits


def embed_lsb_blue_channel(image_path, output_path, percent, bit_position=0):
    """
    Встраивание только в синий канал (B) цветного изображения
    БЕЗ перевода в чёрно-белый!
    """
    img = Image.open(image_path)
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    
    pixels = np.array(img, dtype=np.uint8)
    height, width = pixels.shape[:2]
    total_pixels = height * width
    
    bits_to_embed = int(total_pixels * percent / 100)
    
    np.random.seed(42)
    message = np.random.randint(0, 2, bits_to_embed)
    
    flat_blue = pixels[:, :, 2].flatten()
    changed_bits = 0
    
    for i in range(bits_to_embed):
        mask_bit = ~(1 << bit_position) & 0xFF
        old_value = flat_blue[i]
        new_value = (old_value & mask_bit) | (message[i] << bit_position)
        if old_value != new_value:
            changed_bits += 1
        flat_blue[i] = new_value
    
    pixels[:, :, 2] = flat_blue.reshape(height, width)
    
    result_img = Image.fromarray(pixels)
    result_img.save(output_path)
    
    return changed_bits


def embed_random_pixels(image_path, output_path, percent, bit_position=0):
    """
    Случайный выбор пикселей для встраивания (LCG)
    """
    img = Image.open(image_path)
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    img = img.convert('L')
    
    pixels = np.array(img, dtype=np.uint8)
    total_pixels = pixels.size
    
    bits_to_embed = int(total_pixels * percent / 100)
    
    lcg = LCG(seed=42)
    changed_bits = 0
    
    flat_pixels = pixels.flatten()
    
    for _ in range(bits_to_embed):
        idx = lcg.random_int(0, total_pixels - 1)
        mask_bit = ~(1 << bit_position) & 0xFF
        bit_value = lcg.random_int(0, 1)
        
        old_value = flat_pixels[idx]
        new_value = (old_value & mask_bit) | (bit_value << bit_position)
        if old_value != new_value:
            changed_bits += 1
        flat_pixels[idx] = new_value
    
    result_img = Image.fromarray(flat_pixels.reshape(pixels.shape))
    result_img.save(output_path)
    
    return changed_bits


def embed_random_bits(image_path, output_path, percent, bit_position=0):
    """
    Случайный выбор бита в случайном пикселе
    """
    img = Image.open(image_path)
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    img = img.convert('L')
    
    pixels = np.array(img, dtype=np.uint8)
    total_pixels = pixels.size
    
    flat_pixels = pixels.flatten()
    changed_bits = 0
    
    lcg = LCG(seed=42)
    
    total_changes = int(total_pixels * percent / 100)
    
    changes_made = 0
    while changes_made < total_changes:
        idx = lcg.random_int(0, total_pixels - 1)
        bit_pos = lcg.random_int(0, 7)
        
        mask_bit = ~(1 << bit_pos) & 0xFF
        bit_value = lcg.random_int(0, 1)
        
        old_value = flat_pixels[idx]
        new_value = (old_value & mask_bit) | (bit_value << bit_pos)
        if old_value != new_value:
            changed_bits += 1
        flat_pixels[idx] = new_value
        changes_made += 1
    
    result_img = Image.fromarray(flat_pixels.reshape(pixels.shape))
    result_img.save(output_path)
    
    return changed_bits


def embed_fixed_bits(image_path, output_path, num_bits, bit_position=0):
    """
    Встраивает фиксированное количество битов в первые N пикселей
    """
    img = Image.open(image_path)
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    img = img.convert('L')
    
    pixels = np.array(img, dtype=np.uint8)
    flat_pixels = pixels.flatten()
    
    np.random.seed(42)
    message = np.random.randint(0, 2, num_bits)
    changed_bits = 0
    
    for i in range(min(num_bits, len(flat_pixels))):
        mask_bit = ~(1 << bit_position) & 0xFF
        old_value = flat_pixels[i]
        new_value = (old_value & mask_bit) | (message[i] << bit_position)
        if old_value != new_value:
            changed_bits += 1
        flat_pixels[i] = new_value
    
    result_img = Image.fromarray(flat_pixels.reshape(pixels.shape))
    result_img.save(output_path)
    
    return changed_bits


def embed_random_bits_only(image_path, output_path, percent, bit_position=None):
    """
    Только случайный выбор бита, пиксели идут последовательно
    """
    img = Image.open(image_path)
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    img = img.convert('L')
    
    pixels = np.array(img, dtype=np.uint8)
    total_pixels = pixels.size
    
    bits_to_embed = int(total_pixels * percent / 100)
    
    lcg = LCG(seed=42)
    changed_bits = 0
    flat_pixels = pixels.flatten()
    
    for i in range(bits_to_embed):
        if bit_position is None:
            bit_pos = lcg.random_int(0, 7)
        else:
            bit_pos = bit_position
        
        mask_bit = ~(1 << bit_pos) & 0xFF
        bit_value = lcg.random_int(0, 1)
        
        old_value = flat_pixels[i]
        new_value = (old_value & mask_bit) | (bit_value << bit_pos)
        if old_value != new_value:
            changed_bits += 1
        flat_pixels[i] = new_value
    
    result_img = Image.fromarray(flat_pixels.reshape(pixels.shape))
    result_img.save(output_path)
    
    return changed_bits


def embed_bits_in_one_pixel(image_path, output_path, num_bits):
    """
    Встраивает num_bits битов в ОДИН пиксель (первый пиксель изображения)
    num_bits от 1 до 8
    """
    img = Image.open(image_path)
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    img = img.convert('L')
    
    pixels = np.array(img, dtype=np.uint8)
    flat_pixels = pixels.flatten()
    
    np.random.seed(42)
    message_bits = np.random.randint(0, 2, num_bits)
    
    old_value = flat_pixels[0]
    new_value = old_value
    
    for i in range(num_bits):
        if message_bits[i] == 1:
            new_value |= (1 << i)           
        else:
            new_value &= (0xFF ^ (1 << i))  
    
    flat_pixels[0] = new_value
    
    result_img = Image.fromarray(flat_pixels.reshape(pixels.shape))
    result_img.save(output_path)
    
    changed = bin(old_value ^ new_value).count('1')
    return changed


def embed_bits_in_all_pixels(image_path, output_path, num_bits):
    """
    Встраивает num_bits битов в КАЖДЫЙ пиксель изображения
    num_bits от 1 до 8
    """
    img = Image.open(image_path)
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    img = img.convert('L')
    
    pixels = np.array(img, dtype=np.uint8)
    flat_pixels = pixels.flatten()
    
    np.random.seed(42)
    total_pixels = len(flat_pixels)
    
    message_bits = np.random.randint(0, 2, (total_pixels, num_bits))
    
    changed_bits_total = 0
    
    for idx in range(total_pixels):
        old_value = flat_pixels[idx]
        new_value = old_value
        
        for i in range(num_bits):
            if message_bits[idx, i] == 1:
                new_value |= (1 << i)
            else:
                new_value &= (0xFF ^ (1 << i))
        
        if new_value != old_value:
            changed_bits_total += bin(old_value ^ new_value).count('1')
        flat_pixels[idx] = new_value
    
    result_img = Image.fromarray(flat_pixels.reshape(pixels.shape))
    result_img.save(output_path)
    
    return changed_bits_total