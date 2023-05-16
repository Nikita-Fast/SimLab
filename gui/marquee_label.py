from qt import *


class MarqueeLabelProxyWidget(QGraphicsProxyWidget):
    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        label = MarqueeLabel()
        short_msg = 'Ккккк'
        label.setText(short_msg)
        self.setWidget(label)
        self.setTransformOriginPoint(self.boundingRect().center())
        self.widget().setText(text)
        self.widget().update_coordinates()


class MarqueeLabel(QLabel):
    def __init__(self, parent=None):
        super(MarqueeLabel, self).__init__(parent)
        self.px = 0
        self.py = 15
        self._direction = Qt.RightToLeft
        self.setWordWrap(True)
        self.timer = QTimer(self)
        self.timer.setInterval(33)
        self.timer.timeout.connect(self.timer_slot)
        self.timer.start()
        self._speed = 1
        self.textLength = 0
        self.fontPointSize = 0
        self.setAlignment(Qt.AlignVCenter)
        self.setFixedHeight(self.fontMetrics().height())
        self.set_background_color()

    def set_background_color(self):
        self.setPalette(Qt.transparent)

    def setFont(self, arg__1: QFont) -> None:
        super(MarqueeLabel, self).setFont(arg__1)
        self.setFixedHeight(self.fontMetrics().height())

    def update_coordinates(self):
        align = self.alignment()
        if align == Qt.AlignTop:
            self.py = 10
        elif align == Qt.AlignBottom:
            self.py = self.height() - 10
        elif align == Qt.AlignVCenter:
            self.py = self.height() / 2
        self.fontPointSize = self.font().pointSize() / 2
        self.textLength = self.fontMetrics().size(Qt.TextSingleLine, self.text()).width()

    def setAlignment(self, alignment):
        self.update_coordinates()
        QLabel.setAlignment(self, alignment)

    def resizeEvent(self, event):
        self.update_coordinates()
        super(MarqueeLabel, self).resizeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.black))
        if self.textLength <= self.width():
            # помещающееся сообщение не будет двигаться
            pass
        else:
            if self._direction == Qt.RightToLeft:
                if self.px <= -self.textLength:
                    self.px = self.width()
            else:
                if self.px >= self.width():
                    self.px = -self.textLength
        painter.drawText(self.px, self.py + self.fontPointSize, self.text())
        painter.translate(self.px, 0)

    def speed(self):
        return self._speed

    def timer_slot(self):
        if self._direction == Qt.RightToLeft:
            self.px -= self.speed()
        else:
            self.px += self.speed()
        self.update()

    def set_speed(self, speed):
        self._speed = speed

    def set_direction(self, direction):
        self._direction = direction
        if self._direction == Qt.RightToLeft:
            self.px = self.width() - self.textLength
        else:
            self.px = 0
        self.update()

    def pause(self):
        self.timer.stop()

    def unpause(self):
        self.timer.start()