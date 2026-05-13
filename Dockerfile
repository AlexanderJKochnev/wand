FROM python:3.11-slim

# 1. Устанавливаем зависимости для сборки и библиотеки поддержки шрифтов
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    build-essential \
    pkg-config \
    # Обязательные библиотеки для текста и шрифтов:
    libfreetype6-dev \
    libfontconfig1-dev \
    libraqm-dev \
    # Дополнительные библиотеки для картинок (PNG, JPEG):
    libpng-dev \
    libjpeg-dev \
    libtiff-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Скачиваем, компилируем и устанавливаем ImageMagick 7
RUN wget imagemagick.org && \
    tar xzf ImageMagick.tar.gz && \
    cd ImageMagick-* && \
    ./configure --with-freetype=yes --with-fontconfig=yes --with-raqm=yes && \
    make && \
    make install && \
    ldconfig /usr/local/lib && \
    cd .. && rm -rf ImageMagick*

# 3. Устанавливаем Python-библиотеку Wand
RUN pip install --no-cache-dir wand

# Проверить сборку в контейнере можно командой: magick -version
