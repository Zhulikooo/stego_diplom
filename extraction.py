"""
extraction.py - Функции для извлечения скрытого текста из LSB изображений
"""

import numpy as np
from PIL import Image


def text_to_bits(text):
    """Превращает текст в последовательность битов с маркером"""
    marker = bytes([0xAA, 0xBB, 0xCC, 0xDD])
    data = marker + text.encode('utf-8') + b'\x00'
    bits = []
    for byte in data:
        for i in range(8):
            bits.append((byte >> i) & 1)
    return bits


def bits_to_text(bits):
    """Превращает биты обратно в текст"""
    bytes_list = []
    for i in range(0, len(bits), 8):
        if i + 8 > len(bits):
            break
        byte = 0
        for j in range(8):
            if bits[i + j]:
                byte |= (1 << j)
        bytes_list.append(byte)
    
    data = bytes(bytes_list)
    marker = bytes([0xAA, 0xBB, 0xCC, 0xDD])
    marker_pos = data.find(marker)
    
    if marker_pos == -1:
        return None
    
    text_bytes = data[marker_pos + len(marker):]
    end_pos = text_bytes.find(b'\x00')
    if end_pos != -1:
        text_bytes = text_bytes[:end_pos]
    
    try:
        return text_bytes.decode('utf-8')
    except:
        return None


def extract_text_from_image(image_path):
    """Извлекает текст из LSB изображения"""
    img = Image.open(image_path)
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    img = img.convert('L')
    
    pixels = np.array(img, dtype=np.uint8)
    flat_pixels = pixels.flatten()
    
    max_bits = min(len(flat_pixels), 100000)
    bits = [flat_pixels[i] & 1 for i in range(max_bits)]
    
    return bits_to_text(bits)


def embed_text_only(image_path, output_path, text):
    """Встраивает только текст (мало битов)"""
    img = Image.open(image_path)
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    img = img.convert('L')
    
    pixels = np.array(img, dtype=np.uint8)
    total_pixels = pixels.size
    bits = text_to_bits(text)
    
    if len(bits) > total_pixels:
        raise ValueError(f"Сообщение слишком длинное!")
    
    flat_pixels = pixels.flatten()
    for i in range(len(bits)):
        flat_pixels[i] = (flat_pixels[i] & 0xFE) | bits[i]
    
    result_img = Image.fromarray(flat_pixels.reshape(pixels.shape))
    result_img.save(output_path)
    return len(bits)


def embed_text_with_fill(image_path, output_path, text, fill_percent=50):
    """Встраивает текст + случайные биты до fill_percent%"""
    img = Image.open(image_path)
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    img = img.convert('L')
    
    pixels = np.array(img, dtype=np.uint8)
    total_pixels = pixels.size
    
    text_bits = text_to_bits(text)
    flat_pixels = pixels.flatten()
    
    for i in range(min(len(text_bits), total_pixels)):
        flat_pixels[i] = (flat_pixels[i] & 0xFE) | text_bits[i]
    
    bits_to_fill = int(total_pixels * fill_percent / 100) - len(text_bits)
    
    if bits_to_fill > 0:
        np.random.seed(42)
        random_bits = np.random.randint(0, 2, bits_to_fill)
        start_pos = len(text_bits)
        for i in range(bits_to_fill):
            if start_pos + i < total_pixels:
                flat_pixels[start_pos + i] = (flat_pixels[start_pos + i] & 0xFE) | random_bits[i]
    
    result_img = Image.fromarray(flat_pixels.reshape(pixels.shape))
    result_img.save(output_path)
    return len(text_bits) + bits_to_fill