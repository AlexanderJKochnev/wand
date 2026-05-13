import os
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass, field
from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing


@dataclass(slots = True)  # slots=True экономит память и ускоряет доступ к атрибутам
class TextLayerConfig:
    """Легковесная конфигурация для одного слоя текста"""
    text: str
    font_path: str
    font_size: Optional[int] = None
    color_rgb: Tuple[int, int, int] = (255, 0, 0)
    stroke_mode: bool = False
    stroke_width: float = 2.0
    transformations: List[str] = field(default_factory = lambda: ["horizontal"])


class ModularTextGenerator:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
    
    def generate_complex_image(self, layers_config: List[TextLayerConfig], output_path: str):
        """Собирает пирог из независимо трансформированных слоев"""
        with Image(width = self.width, height = self.height, background = Color('transparent')) as base_canvas:
            for config in layers_config:
                with Image(width = self.width, height = self.height, background = Color('transparent')) as text_layer:
                    self._render_text_style(text_layer, config)
                    self._apply_transformations(text_layer, config)
                    base_canvas.composite(text_layer, left = 0, top = 0)
            
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok = True)
            base_canvas.save(filename = output_path)
    
    def _render_text_style(self, img: Image, config: TextLayerConfig):
        with Drawing() as draw:
            draw.font = config.font_path
            draw.text_alignment = 'center'
            
            if config.font_size:
                draw.font_size = config.font_size
            else:
                draw.font_size = self._calculate_font_size(config.text, self.width * 0.9)
            
            color_str = f"rgb({config.color_rgb[0]},{config.color_rgb[1]},{config.color_rgb[2]})"
            
            if config.stroke_mode:
                draw.fill_color = Color('transparent')
                draw.stroke_color = Color(color_str)
                draw.stroke_width = config.stroke_width
                draw.stroke_antialias = True
            else:
                draw.fill_color = Color(color_str)
                draw.stroke_color = Color('transparent')
            
            metrics = draw.get_font_metrics(img, config.text)
            x = int(self.width / 2)
            
            if "circle" in config.transformations:
                y = int(metrics.text_height * 1.5)
            else:
                y = int((self.height / 2) + (metrics.text_height / 3))
            
            draw.text(x, y, config.text)
            draw(img)
    
    def _apply_transformations(self, img: Image, config: TextLayerConfig):
        for transform in config.transformations:
            if transform == 'horizontal':
                continue
            elif transform == 'circle':
                img.distort('arc', (240.0,))
            elif transform == 'wave':
                img.wave(amplitude = 20, wave_length = 160)
            elif transform == 'perspective':
                w, h = self.width, self.height
                points = [0, 0, 0, 0, 0, h, 0, h, w, 0, w, h * 0.25, w, h, w, h * 0.75]
                img.distort('perspective', points)
            elif transform == 'rotate_45':
                img.rotate(45)
            elif transform == 'rotate_90':
                img.rotate(90)
    
    def _calculate_font_size(self, text: str, max_width: float) -> float:
        estimated_size = max_width / (len(text) * 0.6)
        return max(14, min(estimated_size, self.height * 0.4))
