import sys
import os
import logging
from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing

# Включаем детальный вывод логов в консоль
logging.basicConfig(
    level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("WandDebug")


def wrap_and_fit_text(img, draw, text, max_width, max_height, initial_font_size=80):
    """
    Разбивает текст на строки по словам и динамически уменьшает размер шрифта,
    чтобы весь текст гарантированно поместился в прямоугольник max_width x max_height.
    Возвращает: (список_строк, итоговый_размер_шрифта, метрики_всего_блока, высота_одной_строки)
    """
    font_size = initial_font_size
    words = text.split()

    if not words:
        return [], font_size, None, 0

    while font_size > 5:
        draw.font_size = font_size
        lines = []
        current_line = []

        # Получаем базовую высоту одной строки для текущего шрифта
        single_line_metrics = draw.get_font_metrics(img, "A")
        line_height = single_line_metrics.text_height

        # 1. Пробуем разбить текст на строки для текущего font_size
        for word in words:
            test_line = ' '.join(current_line + [word]) if current_line else word
            metrics = draw.get_font_metrics(img, test_line)

            # Если одно слово шире, чем холст — текущий font_size велик
            if metrics.text_width > max_width and not current_line:
                lines = None
                break

            if metrics.text_width <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]

        if lines is not None:
            if current_line:
                lines.append(' '.join(current_line))

            # 2. Проверяем, помещается ли получившийся блок строк по высоте
            # Передаем multiline=True для корректного расчета всего блока текста целиком
            full_text_block = '\n'.join(lines)
            block_metrics = draw.get_font_metrics(img, full_text_block, multiline=True)

            # Проверяем, укладывается ли блок в границы
            if block_metrics.text_height <= max_height and block_metrics.text_width <= max_width:
                logger.debug(f"Текст успешно подогнан! Шрифт: {font_size}px. Строк: {len(lines)}")
                return lines, font_size, block_metrics, line_height

        # Если текст не поместился, уменьшаем шрифт и повторяем процесс
        font_size -= 2

    raise ValueError("Текст невозможно уложить в заданные рамки даже минимальным шрифтом.")


def test_contour_generation(text, text_alignment='center'):
    # Настройки размеров холста
    width, height = 800, 800

    # ВНИМАНИЕ: Укажите здесь ваш точный путь к шрифту на Mac!
    font_path = '/System/Library/Fonts/Supplemental/Copperplate.ttc'
    output_path = '/Users/kochnev/PycharmProjects/wine/wand/media/contour_debug_result.png'

    logger.info("=== СТАРТ ОТЛАДКИ ===")

    if not os.path.exists(font_path):
        logger.error(f"КРИТИЧЕСКАЯ ОШИБКА: Шрифт не найден по пути: {font_path}")
        return
    logger.debug("Файл шрифта успешно обнаружен.")

    try:
        logger.debug("Шаг 1: Инициализация прозрачного холста...")
        with Image(width=width, height=height, background=Color('transparent')) as img:
            logger.debug("Шаг 2: Создание объекта векторного рисования Drawing...")
            with Drawing() as draw:
                draw.font = font_path
                draw.text_alignment = text_alignment

                # Настройки контура
                draw.fill_color = Color('transparent')
                draw.stroke_color = Color('rgb(255, 0, 0)')  # Красный контур
                draw.stroke_width = 3
                draw.stroke_antialias = True

                logger.debug("Шаг 3: Запуск умного переноса строк и подгона размера под холст...")
                padding = 10
                max_w = width - (padding * 2)
                max_h = height - (padding * 2)

                lines, final_font_size, block_metrics, line_height = wrap_and_fit_text(
                    img, draw, text, max_width=max_w, max_height=max_h, initial_font_size=80
                )

                # Применяем утвержденный размер шрифта
                draw.font_size = final_font_size

                logger.debug("Шаг 4: Расчет координат для каждой строки...")
                # Суммарная высота рассчитывается как количество строк, помноженное на высоту одной строки
                total_block_height = len(lines) * line_height

                # Центрируем весь блок по вертикали холста
                start_y = (height - total_block_height) / 2 + block_metrics.ascender

                # Вычисляем X-координату в зависимости от выравнивания
                if text_alignment == 'center':
                    x = width / 2
                elif text_alignment == 'right':
                    x = width - padding
                else:  # left
                    x = padding

                # Отрисовываем каждую строку
                for i, line in enumerate(lines):
                    current_y = int(start_y + (i * line_height))
                    logger.debug(f"Рисуем строку '{line}' на позиции X={int(x)}, Y={current_y}")
                    draw.text(int(x), current_y, line)

                logger.debug("Шаг 5: Перенос векторного рисунка на пиксельный холст draw(img)...")
                draw(img)

            logger.debug(f"Шаг 6: Сохранение файла в {output_path}...")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            img.metadata['comment'] = text
            img.metadata['custom:original_text'] = text
            img.save(filename=output_path)

        if os.path.exists(output_path):
            logger.info("=== УСПЕХ! === Файл сохранен")
        else:
            logger.error("Ошибка: файл на диске не появился!")

    except Exception as e:
        logger.critical(f"ПРОИЗОШЕЛ СБОЙ ПРИ ГЕНЕРАЦИИ! {e}", exc_info=True)


if __name__ == "__main__":
    # Параметры выравнивания вынесены в аргумент: 'center', 'left', 'right'
    test_contour_generation("Hennessy, Spirit of Travel Shenzhen XO, Cognac", text_alignment='center')
