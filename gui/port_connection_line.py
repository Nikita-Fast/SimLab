import typing

from gui.port_widget import PortWidget
from qt import *


class PortConnectionLine(QGraphicsLineItem):

    def __init__(self, source_port: PortWidget, dst_port: PortWidget, parent=None):
        super().__init__(parent=parent)

        if source_port is None or dst_port is None:
            raise Exception('Невозможно создать соединение, если не переданы оба порта')

        p = self.pen()
        p.setWidth(2)
        self.setPen(p)
        self.source_port = source_port
        self.dst_port = dst_port

        self.source_port.connection = self
        self.dst_port.connection = self

        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)

        self.recalculate()
        # TODO Надо подумать над логированием. Возможно принтом пользоваться неправильно.
        # print(f'new connection')

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Delete:
            self.delete()

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.setPen(QPen(QColor('green'), 2))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        if not self.isSelected():
            self.setPen(QPen(QColor('black'), 2))
        super().hoverLeaveEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        self.setPen(QPen(QColor('black'), 2))
        super().focusOutEvent(event)

    def delete(self):
        # удалить ссылку из портов
        self.source_port.disconnect()
        self.dst_port.disconnect()
        # удалить со сцены
        self.scene().removeItem(self)

    def recalculate(self):
        # Перерасчитать начальную и конечную точку соединения

        p1_x = self.source_port.sceneBoundingRect().right()
        p1_y = self.source_port.sceneBoundingRect().center().y()
        p2_x = self.dst_port.sceneBoundingRect().left()
        p2_y = self.dst_port.sceneBoundingRect().center().y()
        self.setLine(p1_x, p1_y, p2_x, p2_y)