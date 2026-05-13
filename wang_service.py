import math
from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing


class TextImageGenerator:
    def __init__(self, width: int, height: int, font_name: str, color_rgb: tuple):
        self.width = width
        self.height = height
        self.font_name = font_name
        # Преобразуем кортеж (R, G, B) в строку для Wand
        self.color_string = f"rgb({color_rgb[0]},{color_rgb[1]},{color_rgb[2]})"
    
    def generate(self, text: str, template: str, output_path: str):
        """
        Основной метод генерации.
        template: 'horizontal' или 'circle'
        """
        # Создаем пустое прозрачное изображение
        print(33)
        with Image(width = self.width, height = self.height, background = Color('transparent')) as img:
            print('=============111111111111111=======================')
            with Drawing() as draw:
                # Настраиваем общие параметры шрифта
                print('=============211111111111111=======================')
                if self.stroke_mode:
                    draw.font = self.font_name
                    draw.fill_color = Color('blue')
                    draw.stroke_color = Color(self.color_string)
                    draw.stroke_width = self.stroke_width
                else:
                    draw.fill_color = Color(self.color_string)
                    if template == 'horizontal':
                        self._draw_horizontal(draw, img, text)
                    elif template == 'circle':
                        self._draw_circle(draw, img, text)
                    elif template == 'wave':
                        self._draw_wave(draw, img, text)
                    elif template == 'persp':
                        self._draw_perspective(draw, img, text)
                    else:
                        raise ValueError(f"Неизвестный шаблон: {template}")
            print('=============311111111111111=======================')
            if self.stroke_mode:
                # Принудительно заменяем наш технический «синий» цвет внутри букв
                # на абсолютную прозрачность (alpha=0.0)
                img.transparent_color(Color('blue'), alpha = 0.0, fuzz = 0.0)
            print('===================================================')
            # Сохраняем результат в файл
            img.save(filename = output_path)
    
    def _draw_horizontal(self, draw, img, text):
        """Шаблон 1: Текст в одну горизонтальную строку ровно по центру"""
        # Автоматически подбираем размер шрифта под ширину картинки (минус отступы)
        draw.font_size = self._calculate_font_size(text, self.width * 0.9)
        draw.text_alignment = 'center'
        
        # Метрики шрифта для точного вертикального центрирования
        metrics = draw.get_font_metrics(img, text)
        y = int((self.height / 2) + (metrics.text_height / 3))
        x = int(self.width / 2)
        
        draw.text(x, y, text)
        draw(img)
    
    def _draw_circle(self, draw, img, text):
        """Шаблон 2: Текст, изогнутый по окружности (через дисторсию)"""
        # Сначала настраиваем размер шрифта
        # Для дисторсии лучше использовать крупный шрифт, чтобы при изгибе не терялось качество
        draw.font_size = self._calculate_font_size(text, self.width * 1.2)
        draw.text_alignment = 'center'
        
        # Получаем метрики для точного позиционирования до деформации
        metrics = draw.get_font_metrics(img, text)
        
        # Шаг 1: Рисуем плоский текст в верхней части холста
        # Смещение y определяет, насколько большим будет радиус круга при изгибе
        x = int(self.width / 2)
        y = int(metrics.text_height * 1.5)
        
        draw.text(x, y, text)
        draw(img)
        
        # Шаг 2: Применяем дисторсию 'arc' (изгиб в кольцо)
        # Аргумент (угол_дуги, ) определяет градус развертки текста.
        # 360 градусов — полный круг. Для 1-5 слов лучше использовать 180-270,
        # чтобы текст не накладывался сам на себя. Используем 240 для баланса.
        img.distort('arc', (90.0,))
    
    def _calculate_font_size(self, text, max_available_width):
        """Вспомогательный метод для динамического подбора размера шрифта"""
        # Базовая формула: делим доступную ширину на количество символов с коэффициентом
        estimated_size = max_available_width / (len(text) * 0.6)
        # Ограничиваем снизу и сверху, чтобы текст не ломал верстку
        return max(12, min(estimated_size, self.height * 0.5))
    
    def _draw_wave(self, draw, img, text):
        """Шаблон 3: Текст волной"""
        draw.font_size = self._calculate_font_size(text, self.width * 0.9)
        draw.text_alignment = 'center'
        
        # Рисуем строго по центру
        metrics = draw.get_font_metrics(img, text)
        x = int(self.width / 2)
        y = int((self.height / 2) + (metrics.text_height / 3))
        
        draw.text(x, y, text)
        draw(img)
        
        # Применяем волну: амплитуда 25 пикселей, длина волны 150 пикселей
        img.wave(amplitude = 25, wave_length = 150)
    
    def _draw_perspective(self, draw, img, text):
        """Шаблон 4: 3D Перспектива (уходящий вдаль текст)"""
        draw.font_size = self._calculate_font_size(text, self.width * 0.8)
        draw.text_alignment = 'center'
        
        # Рисуем текст в центре
        metrics = draw.get_font_metrics(img, text)
        x = int(self.width / 2)
        y = int((self.height / 2) + (metrics.text_height / 3))
        draw.text(x, y, text)
        draw(img)
        
        # Координаты искажения: [x_исходная, y_исходная, x_целевая, y_целевая, ...]
        # Сжимаем правые углы изображения к центру по вертикали
        w, h = self.width, self.height
        points = [0, 0, 0, 0,  # Верхний левый угол на месте
                0, h, 0, h,  # Нижний левый угол на месте
                w, 0, w, h * 0.2,  # Верхний правый смещаем вниз
                w, h, w, h * 0.8  # Нижний правый смещаем вверх
                ]
        img.distort('perspective', points)
    