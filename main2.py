from image_generator import ModularTextGenerator, TextLayerConfig

# Путь к шрифту на Mac (измените для Linux, если нужно)
FONT = '/System/Library/Fonts/Supplemental/Copperplate.ttc'

generator = ModularTextGenerator(width=800, height=800)

# Описываем слои нашей будущей картинки
layers = [
    # Слои накладываются по очереди (первый — самый нижний)
    TextLayerConfig(
        text="НИЖНИЙ КРУГЛЫЙ ТЕКСТ",
        font_path=FONT,
        color_rgb=(255, 0, 0), # Красный
        stroke_mode=False,     # Сплошной
        transformations=["circle"]
    ),
    TextLayerConfig(
        text="ВЕРХНИЙ КОНТУР ВОЛНОЙ",
        font_path=FONT,
        color_rgb=(0, 0, 255), # Синий
        stroke_mode=True,      # ТОЛЬКО КОНТУР
        stroke_width=3.0,
        transformations=["wave"] # Волна
    )
]
if __name__ == "__main__":
# Генерируем сложный «пирог» в один файл
    generator.generate_complex_image(layers, "/Users/kochnev/PycharmProjects/wine/wand/media/complex_result.png")
    print("Файл complex_result.png успешно создан!")
