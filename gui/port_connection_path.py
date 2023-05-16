import math

from gui.port_widget import PortWidget
from qt import *


class Path(QGraphicsPathItem):
    def __init__(self, source_port: PortWidget, dst_port: PortWidget, *args, **kwargs):
        super(Path, self).__init__(*args, **kwargs)

        self._source_port = source_port
        self._dst_port = dst_port

        self._arrow_height = 10
        self._arrow_width = 8

    def get_source_point(self):
        x = self._source_port.sceneBoundingRect().right()
        y = self._source_port.sceneBoundingRect().center().y()
        return QPointF(x, y)

    def get_destination_point(self):
        x = self._dst_port.sceneBoundingRect().left()
        y = self._dst_port.sceneBoundingRect().center().y()
        return QPointF(x, y)

    def directPath(self):
        path = QPainterPath(self.get_source_point())
        path.lineTo(self.get_destination_point())
        return path

    def squarePath(self):
        s = self.get_source_point()
        d = self.get_destination_point()

        mid_x = s.x() + ((d.x() - s.x()) * 0.5)

        path = QPainterPath(QPointF(s.x(), s.y()))
        path.lineTo(mid_x, s.y())
        path.lineTo(mid_x, d.y())
        path.lineTo(d.x(), d.y())

        return path

    def bezierPath(self):
        s = self.get_source_point()
        d = self.get_destination_point()

        source_x, source_y = s.x(), s.y()
        destination_x, destination_y = d.x(), d.y()

        dist = (d.x() - s.x()) * 0.5

        cpx_s = +dist
        cpx_d = -dist
        cpy_s = 0
        cpy_d = 0

        if (s.x() > d.x()) or (s.x() < d.x()):
            cpx_d *= -1
            cpx_s *= -1

            cpy_d = (
                (source_y - destination_y) /
                math.fabs((source_y - destination_y) if (source_y - destination_y) != 0 else 0.00001)
            ) * 150

            cpy_s = (
                (destination_y - source_y) /
                math.fabs((destination_y - source_y) if (destination_y - source_y) != 0 else 0.00001)
            ) * 150

        path = QPainterPath(self.get_source_point())

        path.cubicTo(destination_x + cpx_d, destination_y + cpy_d, source_x + cpx_s, source_y + cpy_s,
                     destination_x, destination_y)

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
            normX, normY = dx / leng, dy / leng  # normalize

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
        painter.setRenderHint(painter.Antialiasing)

        painter.pen().setWidth(2)
        painter.setBrush(Qt.NoBrush)

        # path = self.directPath()
        path = self.squarePath()
        # path = self.bezierPath()
        painter.drawPath(path)
        self.setPath(path)

        # change path.PointAtPercent() value to move arrow on the line
        triangle_source = self.arrowCalc(path.pointAtPercent(0.999), path.pointAtPercent(1))

        if triangle_source is not None:
            painter.drawPolyline(triangle_source)
