# graphics-editor
### Python приложение с графическим интерфейсом, в котором реализована работа с изображениями. Данное приложение включает в себя ниже перечисленный функционал:
* Просмотр изображений формата PNM
* Поддержка функций чтения из файла и записи через GUI в PNM (P5 и P6)
* Преобразование изображения в разные цветовые пространства (RGB, HSL, HSV, YCbCr.601, YCbCr.709, YCoCg, CMY)
* Гамма-коррекция изображения (задание коэффициента гамма-кореекции и преобразование по заданной гамме)
* Отрисовка растровых линий с применением сглаживания (алогоритм Ву)
* Дизеринг изображений (Ordered 8x8, Random, Floyd-Steinberg, Atkinson)
* Гистограмма изображения (для автоматической коррекции интенсивности)
* Масштабирование изображений (Метод ближайшего соседа, биленейное, Lanczos3, BC-сплайны)
* Алгоритмы фильтрации изображения (Пороговая фильтрация, Пороговая фильтрация методом Оцу, Медианный фильтра, Фильтр Гаусса, Линейный усредняющий фильтр - box blur, unsharp masking через размытие Гаусса с заданным параметром, Contrast Adaptive Sharpening с better diagonals, фильтр Собеля, Canny Edge Detector)

### Пример работы графического редактора - открытие изображение и применение к нему алгоритма фильтрации (Canny Edge Detector):
