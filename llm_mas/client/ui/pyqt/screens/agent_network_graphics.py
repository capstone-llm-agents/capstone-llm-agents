from PyQt6.QtWidgets import QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem
from PyQt6.QtGui import QBrush, QPen, QColor, QFontMetrics
from PyQt6.QtCore import QPointF, Qt

# Documentation below
# https://doc.qt.io/qt-6/qtwidgets-module.html
# QFontMetrics is a thing to make the box actually fit the text
# 


# ideally these would be an auto thing according to the screen size or other things but just hardcoded right now
MIN_NODE_WIDTH = 80
MIN_NODE_HEIGHT = 40
MIN_ACTION_WIDTH = 60
MIN_ACTION_HEIGHT = 30

class Rectangle(QGraphicsRectItem):
    def __init__(self, text: str, color: str = "#dedede"): # make not grey later
        # use the font metrics to determine rectangle size
        font_metrics = QFontMetrics(QGraphicsTextItem().font())
        width = max(MIN_NODE_WIDTH, font_metrics.horizontalAdvance(text) + 20)
        height = max(MIN_NODE_HEIGHT, font_metrics.height() + 20)

        super().__init__(-width/2, -height/2, width, height) # center

        # border
        self.setBrush(QBrush(QColor(color)))
        self.setPen(QPen(Qt.GlobalColor.black, 2))

        # qt flags for making the things movable
        # https://doc.qt.io/qt-6/qgraphicsitem.html
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)

        # label
        self.text = QGraphicsTextItem(text, self)
        self.text.setDefaultTextColor(QColor("black"))
        t_rect = self.text.boundingRect()
        self.text.setPos(-t_rect.width()/2, -t_rect.height()/2)

        self.edges: list[QGraphicsLineItem] = []

    def add_edge(self, edge: QGraphicsLineItem):
        # connected lines
        self.edges.append(edge)

    def itemChange(self, change, value):
        # as thing moves about keep the same connections/lines without breaking
        if change == QGraphicsRectItem.GraphicsItemChange.ItemPositionChange:
            for edge in self.edges:
                line = edge
                p1 = QPointF(line.line().p1())
                p2 = QPointF(line.line().p2())
                if line.data(0) == self:  # source
                    line.setLine(value.x(), value.y(), p2.x(), p2.y())
                elif line.data(1) == self:  # dest
                    line.setLine(p1.x(), p1.y(), value.x(), value.y())
        return super().itemChange(change, value)

def draw_line(scene: QGraphicsScene, src: Rectangle, dest: Rectangle, color=Qt.GlobalColor.black, width=2, style=Qt.PenStyle.SolidLine) -> QGraphicsLineItem:
    #lines between rects, add styles to qss later
    line = QGraphicsLineItem(src.x(), src.y(), dest.x(), dest.y())
    pen = QPen(color, width, style)
    line.setPen(pen)
    line.setZValue(-1) # lowest z layer cos they were showing above the rects
    line.setData(0, src)
    line.setData(1, dest)
    scene.addItem(line)
    src.add_edge(line)
    dest.add_edge(line)
    return line
