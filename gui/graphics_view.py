from qt import *


class GraphicsView(QGraphicsView):

    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setMinimumSize(QSize(800, 500))



