from PIL import Image
import numpy as np

# Создаём изображение 32×32
img = Image.fromarray(np.random.randint(0, 256, (32, 32), dtype=np.uint8))
img.save("small_32x32.png")

print("✅ Создано: small_32x32.png (32×32 пикселя)")

# Создаём изображение 50×50
img2 = Image.fromarray(np.random.randint(0, 256, (50, 50), dtype=np.uint8))
img2.save("small_50x50.png")

print("✅ Создано: small_50x50.png (50×50 пикселей)")

# Создаём изображение 100×100
img3 = Image.fromarray(np.random.randint(0, 256, (100, 100), dtype=np.uint8))
img3.save("small_100x100.png")

print("✅ Создано: small_100x100.png (100×100 пикселей)")