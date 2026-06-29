"""
experiments.py - Запуск экспериментов для исследования RS-метода
"""

import numpy as np
from PIL import Image
from rs_core import rs_analysis
from embedding import (
    embed_lsb_all_pixels, embed_lsb_blue_channel,
    embed_random_pixels, embed_random_bits, embed_fixed_bits,
    embed_random_bits_only, embed_bits_in_one_pixel, embed_bits_in_all_pixels
)
import os


def run_experiment(image_path, method, max_percent=100, step=10, bit_position=0):
    """Эксперимент с разными процентами встройки"""
    results = []
    
    results_dir = os.path.join(os.path.dirname(image_path), "results")
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    img = Image.open(image_path).convert('L')
    pixels_original = np.array(img, dtype=np.uint8)
    original_result = rs_analysis(pixels_original, (0, 1, 0))
    
    results.append({
        'percent': 0,
        'diff_m': original_result['diff_m'],
        'changed_bits': 0
    })
    
    for percent in range(step, max_percent + 1, step):
        temp_path = os.path.join(results_dir, f"temp_exp_{percent}.png")
        
        if method == "LSB все пиксели":
            embed_lsb_all_pixels(image_path, temp_path, percent, bit_position)
        elif method == "LSB синий канал":
            embed_lsb_blue_channel(image_path, temp_path, percent, bit_position)
        elif method == "Случайные пиксели":
            embed_random_pixels(image_path, temp_path, percent, bit_position)
        elif method == "Случайные биты и случайные пиксели":
            embed_random_bits(image_path, temp_path, percent, bit_position)
        elif method == "Только случайные биты":
            embed_random_bits_only(image_path, temp_path, percent, None)
        else:
            continue
        
        img_result = Image.open(temp_path).convert('L')
        pixels_result = np.array(img_result, dtype=np.uint8)
        result = rs_analysis(pixels_result, (0, 1, 0))
        
        results.append({
            'percent': percent,
            'diff_m': result['diff_m'],
            'changed_bits': 0
        })
    
    return results


def run_sensitivity_experiment(image_path, max_bits=20, bit_position=0):
    """Эксперимент с малым количеством битов (1-20) в разных пикселях"""
    results = []
    
    results_dir = os.path.join(os.path.dirname(image_path), "results")
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    img = Image.open(image_path).convert('L')
    pixels_original = np.array(img, dtype=np.uint8)
    original_result = rs_analysis(pixels_original, (0, 1, 0))
    original_diff = original_result['diff_m']
    
    results.append({
        'bits': 0,
        'diff_m': original_diff,
        'change': 0
    })
    
    for num_bits in range(1, max_bits + 1):
        temp_path = os.path.join(results_dir, f"temp_sens_{num_bits}bits.png")
        embed_fixed_bits(image_path, temp_path, num_bits, bit_position)
        
        img_result = Image.open(temp_path).convert('L')
        pixels_result = np.array(img_result, dtype=np.uint8)
        result = rs_analysis(pixels_result, (0, 1, 0))
        
        results.append({
            'bits': num_bits,
            'diff_m': result['diff_m'],
            'change': original_diff - result['diff_m']
        })
    
    return results


def run_pixel_bits_experiment(image_path, max_bits=8):
    """Эксперимент: встраивает от 1 до 8 битов в ОДИН пиксель"""
    results = []
    
    results_dir = os.path.join(os.path.dirname(image_path), "results")
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    img = Image.open(image_path).convert('L')
    pixels_original = np.array(img, dtype=np.uint8)
    original_result = rs_analysis(pixels_original, (0, 1, 0))
    original_diff = original_result['diff_m']
    
    results.append({
        'bits': 0,
        'diff_m': original_diff,
        'change': 0
    })
    
    for num_bits in range(1, max_bits + 1):
        temp_path = os.path.join(results_dir, f"temp_pixel_{num_bits}bits.png")
        embed_bits_in_one_pixel(image_path, temp_path, num_bits)
        
        img_result = Image.open(temp_path).convert('L')
        pixels_result = np.array(img_result, dtype=np.uint8)
        result = rs_analysis(pixels_result, (0, 1, 0))
        
        results.append({
            'bits': num_bits,
            'diff_m': result['diff_m'],
            'change': original_diff - result['diff_m']
        })
    
    return results


def run_all_pixels_bits_experiment(image_path, max_bits=8, progress_callback=None):
    """
    Эксперимент: встраивает от 1 до 8 битов в КАЖДЫЙ пиксель изображения
    """
    results = []
    results_dir = os.path.join(os.path.dirname(image_path), "results")
    os.makedirs(results_dir, exist_ok=True)
    
    img = Image.open(image_path).convert('L')
    pixels_original = np.array(img, dtype=np.uint8)
    original_result = rs_analysis(pixels_original, (0, 1, 0))
    original_diff = original_result['diff_m']
    
    results.append({
        'bits': 0,
        'diff_m': original_diff,
        'change': 0
    })
    
    for num_bits in range(1, max_bits + 1):
        if progress_callback:
            progress = num_bits / max_bits * 100
            progress_callback(progress, num_bits)
        
        temp_path = os.path.join(results_dir, f"temp_all_pixels_{num_bits}bits.png")
        embed_bits_in_all_pixels(image_path, temp_path, num_bits)
        
        img_result = Image.open(temp_path).convert('L')
        pixels_result = np.array(img_result, dtype=np.uint8)
        result = rs_analysis(pixels_result, (0, 1, 0))
        
        results.append({
            'bits': num_bits,
            'diff_m': result['diff_m'],
            'change': original_diff - result['diff_m']
        })
    
    return results


def run_experiment_with_progress(image_path, method, max_percent=100, step=10, bit_position=0, progress_callback=None):
    """Эксперимент с процентами и обновлением прогресса"""
    results = []
    results_dir = os.path.join(os.path.dirname(image_path), "results")
    os.makedirs(results_dir, exist_ok=True)
    
    img = Image.open(image_path).convert('L')
    pixels_original = np.array(img, dtype=np.uint8)
    original_result = rs_analysis(pixels_original, (0, 1, 0))
    
    results.append({
        'percent': 0,
        'diff_m': original_result['diff_m'],
        'changed_bits': 0
    })
    
    steps = list(range(step, max_percent + 1, step))
    total_steps = len(steps)
    
    for idx, percent in enumerate(steps):
        if progress_callback:
            progress = (idx + 1) / total_steps * 100
            progress_callback(progress, percent)
        
        temp_path = os.path.join(results_dir, f"temp_exp_{percent}.png")
        
        if method == "LSB все пиксели":
            embed_lsb_all_pixels(image_path, temp_path, percent, bit_position)
        elif method == "LSB синий канал":
            embed_lsb_blue_channel(image_path, temp_path, percent, bit_position)
        elif method == "Случайные пиксели":
            embed_random_pixels(image_path, temp_path, percent, bit_position)
        elif method == "Случайные биты и случайные пиксели":
            embed_random_bits(image_path, temp_path, percent, bit_position)
        elif method == "Только случайные биты":
            embed_random_bits_only(image_path, temp_path, percent, None)
        else:
            continue
        
        img_result = Image.open(temp_path).convert('L')
        pixels_result = np.array(img_result, dtype=np.uint8)
        result = rs_analysis(pixels_result, (0, 1, 0))
        
        results.append({
            'percent': percent,
            'diff_m': result['diff_m'],
            'changed_bits': 0
        })
    
    return results


def run_sensitivity_experiment_with_progress(image_path, max_bits=20, bit_position=0, progress_callback=None):
    """Эксперимент с порогом и обновлением прогресса"""
    results = []
    results_dir = os.path.join(os.path.dirname(image_path), "results")
    os.makedirs(results_dir, exist_ok=True)
    
    img = Image.open(image_path).convert('L')
    pixels_original = np.array(img, dtype=np.uint8)
    original_result = rs_analysis(pixels_original, (0, 1, 0))
    original_diff = original_result['diff_m']
    
    results.append({
        'bits': 0,
        'diff_m': original_diff,
        'change': 0
    })
    
    for num_bits in range(1, max_bits + 1):
        if progress_callback:
            progress = num_bits / max_bits * 100
            progress_callback(progress, num_bits)
        
        temp_path = os.path.join(results_dir, f"temp_sens_{num_bits}bits.png")
        embed_fixed_bits(image_path, temp_path, num_bits, bit_position)
        
        img_result = Image.open(temp_path).convert('L')
        pixels_result = np.array(img_result, dtype=np.uint8)
        result = rs_analysis(pixels_result, (0, 1, 0))
        
        results.append({
            'bits': num_bits,
            'diff_m': result['diff_m'],
            'change': original_diff - result['diff_m']
        })
    
    return results


def run_pixel_bits_experiment_with_progress(image_path, max_bits=8, progress_callback=None):
    """Эксперимент с битами в пикселе и обновлением прогресса"""
    results = []
    results_dir = os.path.join(os.path.dirname(image_path), "results")
    os.makedirs(results_dir, exist_ok=True)
    
    img = Image.open(image_path).convert('L')
    pixels_original = np.array(img, dtype=np.uint8)
    original_result = rs_analysis(pixels_original, (0, 1, 0))
    original_diff = original_result['diff_m']
    
    results.append({
        'bits': 0,
        'diff_m': original_diff,
        'change': 0
    })
    
    for num_bits in range(1, max_bits + 1):
        if progress_callback:
            progress = num_bits / max_bits * 100
            progress_callback(progress, num_bits)
        
        temp_path = os.path.join(results_dir, f"temp_pixel_{num_bits}bits.png")
        embed_bits_in_one_pixel(image_path, temp_path, num_bits)
        
        img_result = Image.open(temp_path).convert('L')
        pixels_result = np.array(img_result, dtype=np.uint8)
        result = rs_analysis(pixels_result, (0, 1, 0))
        
        results.append({
            'bits': num_bits,
            'diff_m': result['diff_m'],
            'change': original_diff - result['diff_m']
        })
    
    return results