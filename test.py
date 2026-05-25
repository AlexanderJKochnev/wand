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


def test_contour_generation(text):
    # Настройки
    width, height = 150, 800

    # ВНИМАНИЕ: Укажите здесь ваш точный путь к шрифту на Mac!
    font_path = '/System/Library/Fonts/Supplemental/Copperplate.ttc'
    output_path = '/Users/kochnev/PycharmProjects/wine/wand/media/contour_debug_result.png'

    logger.info("=== СТАРТ ОТЛАДКИ ===")

    # Проверка файла шрифта
    if not os.path.exists(font_path):
        logger.error(f"КРИТИЧЕСКАЯ ОШИБКА: Шрифт не найден по пути: {font_path}")
        return
    logger.debug(f"Файл шрифта успешно обнаружен. Размер: {os.path.getsize(font_path)} байт")

    try:
        logger.debug("Шаг 1: Инициализация прозрачного холста...")
        with Image(width=width, height=height, background=Color('transparent')) as img:
            logger.debug(f"Холст создан. Размер: {img.width}x{img.height}, Формат: {img.format}")

            logger.debug("Шаг 2: Создание объекта векторного рисования Drawing...")
            with Drawing() as draw:
                # Явная конфигурация параметров
                draw.font = font_path
                draw.font_size = 80
                draw.text_alignment = 'center'

                # СТАБИЛЬНЫЙ ВАРИАНТ ДЛЯ КОНТУРА:
                # Напрямую передаем строку 'transparent' в объект Color.
                # Так ImageMagick понимает, что заливка есть, но она невидима.
                draw.fill_color = Color('transparent')
                draw.stroke_color = Color('rgb(255, 0, 0)')  # Красный контур
                draw.stroke_width = 3
                draw.stroke_antialias = True

                logger.debug(
                    f"Стили применены. Fill: {draw.fill_color}, Stroke: {draw.stroke_color}, Width: {draw.stroke_width}"
                )

                logger.debug("Шаг 3: Запрос метрик шрифта у ImageMagick...")
                metrics = draw.get_font_metrics(img, text)
                logger.debug(
                    f"Метрики получены успешно: Ширина текста={metrics.text_width}, Высота={metrics.text_height}"
                )

                # Расчет координат
                x = int(width / 2)
                y = int((height / 2) + (metrics.text_height / 3))
                logger.debug(f"Рассчитаны координаты центра текста: X={x}, Y={y}")

                # Проверка выхода за границы холста
                if x > width or y > height or x < 0 or y < 0:
                    logger.warning(
                        f"Внимание: Координаты рендеринга ({x}, {y}) выходят за рамки холста ({width}x{height})"
                    )

                logger.debug("Шаг 4: Вызов метода рисования текста draw.text()...")
                draw.text(x, y, text)

                logger.debug("Шаг 5: Перенос векторного рисунка на пиксельный холст draw(img)...")
                draw(img)
                logger.debug("Отрисовка в буфер ImageMagick завершена без сбоев.")

            logger.debug(f"Шаг 6: Сохранение файла в {output_path}...")
            img.save(filename=output_path)

        if os.path.exists(output_path):
            logger.info(f"=== УСПЕХ! === Файл сохранен, размер: {os.path.getsize(output_path)} байт")
        else:
            logger.error("Ошибка: Блок завершился, но файл на диске не появился!")

    except Exception as e:
        logger.critical(f"ПРОИЗОШЕЛ СБОЙ ПРИ ГЕНЕРАЦИИ! {e}", exc_info=True)


if __name__ == "__main__":
    test_contour_generation("Hennessy Prive")
