import qt
import sys

from gui.main_window import MainWindow

# TODO ВОПРОСЫ ДЛЯ ОБСУЖДЕНИЯ И РЕКОМЕНДАЦИИ:
#  1. + Мне кажется соединения надо делать выделяемыми и удаляемыми по Del.
#  2. Меньше кода - меньше багов. Должны быть 100% аргументы для каждого написанного тобою символа в коде.
#  3. НЕЛЬЗЯ делать доступ к полям класса напрямую. Обращайся всегда через метод (почему - обсудим при встрече).
#  Посмотри properties.
#  4. + Использование комментариев в коде требует обсуждения.
#  5. + Надо стартовые параметры виджета подобрать (размеры) для двух портов, чтобы выглядел нормально. Сейчас непонято.
#  6. НЕ ДОЛЖНО БЫТЬ ИМПОРТОВ QT ВНЕ ФАЙЛА qt.py!!!

# TODO РЕЗЮМЕ:
#  1. Устрани туду.
#  2. Приведи код в порядок - ни одной лишней сущности.
#  3. Чем раньше скинешь - тем лучше. Мне после этого понадобится дня двы и надо будет встретится - обсудить код и
#  дальнейшие шаги.

# Проблемы:
# 1. Отрисовка блока посредника при соединении портов одного модуля.


app = qt.QApplication([])
window = MainWindow()
sys.exit(app.exec_())