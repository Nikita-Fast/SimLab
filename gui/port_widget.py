import typing
from qt import *


class PortWidget(QGraphicsRectItem):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setBrush(QBrush(QColor('orange')))
        self.setAcceptHoverEvents(True)
        self._is_selected = False
        self._connection = None
        self.setFlags(QGraphicsItem.ItemSendsGeometryChanges | QGraphicsItem.ItemSendsScenePositionChanges)

    def disconnect(self):
        if self.is_connected:
            self._connection = None

    @property
    def is_connected(self):
        return self._connection is not None

    @property
    def connection(self):
        return self._connection

    @connection.setter
    def connection(self, value):
        if self._connection is not None:
            raise Exception(f'К порту {self} нельзя сделать соединение т.к. он уже соединен с кем-то')
        self._connection = value

    @property
    def is_selected(self):
        return self._is_selected

    @is_selected.setter
    def is_selected(self, value):
        self._is_selected = value

    # def get_descriptor_based_serial_number(self):
    #     # Получить номер этого порта в соответствии с дескриптором модуля
    #
    #     inputs = [port for port, _ in self.parentItem().inputs]
    #     if self in inputs:
    #         return inputs.index(self)
    #     outputs = [port for port, _ in self.parentItem().outputs]
    #     if self in outputs:
    #         return outputs.index(self)
    #     raise ValueError('порт не добавлен во входы или выходы модуля')

    # def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: typing.Any) -> typing.Any:
    #     if change == QGraphicsItem.ItemScenePositionHasChanged:
    #         if self.is_connected:
    #             self.connection.recalculate()
    #     return super().itemChange(change, value)

    def enable_highlight(self):
        self.setBrush(QBrush(QColor('green')))

    def disable_highlight(self):
        self.setBrush(QBrush(QColor('orange')))

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.enable_highlight()
        super(PortWidget, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        if not self.is_selected:
            self.disable_highlight()
        super(PortWidget, self).hoverLeaveEvent(event)
