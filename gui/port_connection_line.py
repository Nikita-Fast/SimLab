import math
import typing

from gui.port_widget import PortWidget
from qt import *


class PortConnectionLine(QGraphicsPathItem):

    def __init__(self, source_port: PortWidget, dst_port: PortWidget, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if source_port is None or dst_port is None:
            raise Exception('Невозможно создать соединение, если не переданы оба порта')

        self._source_port = source_port
        self._dst_port = dst_port
        self._arrow_height = 14
        self._arrow_width = 6

        self._source_port.add_connection(self)
        self._dst_port.add_connection(self)

        self._color = Qt.black

        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)

        self._is_valid = True
        if not self.are_ports_compatible():
            self._is_valid = False

        self._source_port.parentItem().is_setup_properly()
        self._dst_port.parentItem().is_setup_properly()

        # TODO Надо подумать над логированием. Возможно принтом пользоваться неправильно.
        # print(f'new connection')

    @property
    def is_valid(self):
        return self._is_valid

    @property
    def source_port(self):
        return self._source_port

    @property
    def dst_port(self):
        return self._dst_port

    def boundingRect(self) -> QRectF:
        diff = max(self._arrow_width, self._arrow_height)
        return self.path().boundingRect().adjusted(-diff, -diff, diff, diff)

    def get_source_point(self):
        x = self._source_port.sceneBoundingRect().right()
        y = self._source_port.sceneBoundingRect().center().y()
        return QPointF(x, y)

    def get_destination_point(self):
        x = self._dst_port.sceneBoundingRect().left()
        y = self._dst_port.sceneBoundingRect().center().y()
        return QPointF(x, y)

    def bezierPath(self):
        s = self.get_source_point()
        d = self.get_destination_point()
        start_offset = self._source_port.sceneBoundingRect().width() * 1.2
        end_offset = self._dst_port.sceneBoundingRect().width() * 1.2

        path = QPainterPath(s)
        start = QPointF(s.x() + start_offset, s.y())
        end = QPointF(d.x() - end_offset, d.y())
        # line from s to start
        path.lineTo(start)
        # bezier from start to end
        y_diff = math.fabs(start.y() - end.y())
        c1 = QPointF(start.x() + y_diff / 2, start.y())
        c2 = QPointF(end.x() - y_diff / 2, end.y())

        path.cubicTo(c1, c2, end)
        # line from end to d
        path.lineTo(self.get_destination_point())

        return path

    def arrowCalc(self, start_point=None, end_point=None):  # calculates the point where the arrow should be drawn
        try:
            startPoint, endPoint = start_point, end_point

            if start_point is None:
                startPoint = self.get_source_point()

            if endPoint is None:
                endPoint = self.get_destination_point()

            dx, dy = startPoint.x() - endPoint.x(), startPoint.y() - endPoint.y()

            leng = math.sqrt(dx ** 2 + dy ** 2)
            # normalize
            normX, normY = dx / leng, dy / leng

            # perpendicular vector
            perpX = -normY
            perpY = normX

            leftX = endPoint.x() + self._arrow_height * normX + self._arrow_width * perpX
            leftY = endPoint.y() + self._arrow_height * normY + self._arrow_width * perpY

            rightX = endPoint.x() + self._arrow_height * normX - self._arrow_width * perpX
            rightY = endPoint.y() + self._arrow_height * normY - self._arrow_width * perpY

            point2 = QPointF(leftX, leftY)
            point3 = QPointF(rightX, rightY)
            return QPolygonF([point2, endPoint, point3])

        except (ZeroDivisionError, Exception):
            return None

    def paint(self, painter: QPainter, option, widget=None) -> None:
        if not self.isSelected():
            if not self._is_valid:
                self._color = QColor('red')

        painter.setRenderHint(painter.Antialiasing)

        painter.setPen(QPen(self._color, 2))
        painter.setBrush(Qt.NoBrush)

        path = self.bezierPath()

        painter.drawPath(path)
        self.setPath(path)

        # change path.PointAtPercent() value to move arrow on the line
        triangle_source = self.arrowCalc(path.pointAtPercent(0.999), path.pointAtPercent(1))

        if triangle_source is not None:
            painter.drawPolyline(triangle_source)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Delete:
            self.delete()

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self._color = QColor('cyan')
        super().mousePressEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        self._color = QColor('black')
        super().focusOutEvent(event)

    def are_ports_compatible(self):
        src_port_type = self.source_port.get_type_from_descriptor()
        dst_port_type = self.dst_port.get_type_from_descriptor()
        return src_port_type == dst_port_type or dst_port_type == typing.Any

    def delete(self):
        src_module = self.source_port.parentItem()
        dst_module = self.dst_port.parentItem()

        self.dst_port.remove_connection(self)
        self.source_port.remove_connection(self)
        self.scene().removeItem(self)

        src_module.is_setup_properly()
        dst_module.is_setup_properly()

