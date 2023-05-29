import typing
from qt import *


class PortWidget(QGraphicsRectItem):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setBrush(QBrush(QColor('orange')))
        self.setAcceptHoverEvents(True)
        self._is_selected = False
        # self._connection = None
        self._connections: typing.List = []
        self.setFlags(QGraphicsItem.ItemSendsGeometryChanges | QGraphicsItem.ItemSendsScenePositionChanges)

    def disconnect(self):
        if self.is_connected:
            self._connections = None

    def remove_connection(self, connection):
        # НЕ ИСПОЛЬЗОВАТЬ ДЛЯ УДАЛЕНИЯ СОЕДИНЕНИЯ
        # raises ValueError if connection not in self._connections
        self._connections.remove(connection)

    # @property
    # def is_connected(self):
    #     return self._connections is not None

    @property
    def is_connected(self):
        return len(self._connections) > 0

    # @property
    # def connection(self):
    #     return self._connections

    @property
    def connections(self) -> typing.List:
        return self._connections

    # @connections.setter
    # def connections(self, value):
    #     raise ValueError('do not use this method')
    #     if self._connections is not None and self.is_input_port():
    #         raise Exception(f'К входному порту {self} нельзя сделать соединение т.к. он уже соединен с кем-то')
    #     self._connections = value

    def add_connection(self, connection) -> None:
        if len(self._connections) > 0 and self.is_input_port():
            raise Exception(f'К входному порту {self} нельзя добавить соединение т.к. он уже соединен с кем-то')
        self._connections.append(connection)

    @property
    def is_selected(self):
        return self._is_selected

    @is_selected.setter
    def is_selected(self, value):
        self._is_selected = value

    def get_type_from_descriptor(self):
        if self.is_input_port():
            ports = self.parentItem().module.__dict__.get("input_ports")
        if self.is_output_port():
            ports = self.parentItem().module.__dict__.get("output_ports")
        port_number = self.get_descriptor_based_serial_number()
        port_info = ports[port_number]
        return port_info.get("type", typing.Any)

    def is_input_port(self):
        inputs = [port for port, _ in self.parentItem().inputs]
        return self in inputs

    def is_output_port(self):
        outputs = [port for port, _ in self.parentItem().outputs]
        return self in outputs

    def get_descriptor_based_serial_number(self):
        # Получить номер этого порта в соответствии с дескриптором модуля

        inputs = [port for port, _ in self.parentItem().inputs]
        if self in inputs:
            return inputs.index(self)
        outputs = [port for port, _ in self.parentItem().outputs]
        if self in outputs:
            return outputs.index(self)
        raise ValueError('порт не добавлен во входы или выходы модуля')

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
