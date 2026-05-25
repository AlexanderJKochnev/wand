from wang_service import TextImageGenerator

# Инициализируем генератор: размер 800х800, шрифт Arial, цвет красный (255, 0, 0)
# '/System/Library/Fonts/Supplemental/Arial.ttf'
font = '/System/Library/Fonts/Supplemental/Copperplate.ttc'
generator = TextImageGenerator(
    width=300,
    height=800,
    font_name=font,  # 'Arial',
    color_rgb=(255, 0, 0)
)

if __name__ == "__main__":
    # Вариант 1: Обычный горизонтальный текст
    text = " Hennessy Prive "
    generator.generate(
        text="Hennessy Prive", template="horizontal",
        output_path="/Users/kochnev/PycharmProjects/wine/wand/media/main_hor.png"
    )

    # Вариант 2: Текст по кругу
    generator.generate(
        text=text, template="circle", output_path="/Users/kochnev/PycharmProjects/wine/wand/media/main_circle_text.png"
    )
    generator.generate(
        text=text, template="persp",
        output_path="/Users/kochnev/PycharmProjects/wine/wand/media/main_persp_text.png"
    )
    generator.generate(
        text=text, template="wave",
        output_path="/Users/kochnev/PycharmProjects/wine/wand/media/main_wave_text.png"
    )
