# Pillow 兼容性补丁
import PIL.Image
# 为新版本Pillow添加ANTIALIAS别名
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
