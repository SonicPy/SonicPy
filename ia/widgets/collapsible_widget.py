from PyQt5 import QtCore, QtGui, QtWidgets
import os
from .. import style_path, icons_path


class CollapsibleBox(QtWidgets.QWidget):
    def __init__(self, title="", parent=None):
        super(CollapsibleBox, self).__init__(parent)

        self.setStyleSheet("CollapsibleBox { border: 0px;}")

        self.toggle_button = QtWidgets.QToolButton(
            text=title, checkable=True, checked=False
        )
        button_height = 15
        button_width = 15

        self.right_arrow = QtGui.QIcon(os.path.join(icons_path, 'arrow_right.png'))
        self.down_arrow = QtGui.QIcon(os.path.join(icons_path, 'arrow_down.ico'))

        icon_size = QtCore.QSize(button_height, button_width)
        
        self.toggle_button.setIconSize(icon_size)
        #self.toggle_button.setArrowType(QtCore.Qt.NoArrow)
        self.toggle_button.setFixedWidth(205)
        self.toggle_button.setStyleSheet(''' QToolButton { border-top: 1px solid #ADADAD; 
                                            font: normal 14px;}''')
        self.toggle_button.setToolButtonStyle(
            QtCore.Qt.ToolButtonTextBesideIcon
        )
        #self.toggle_button.setArrowType(QtCore.Qt.RightArrow)
        self.toggle_button.pressed.connect(self.on_pressed)

        self.toggle_animation = QtCore.QParallelAnimationGroup(self)

        self.content_area = QtWidgets.QScrollArea(
            maximumHeight=0, minimumHeight=0
        )
        #self.content_area.setStyleSheet("QScrollArea { border: 1px solid #101112; border-radius: 1px ;font: normal 12px;}")
        self.content_area.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        self.content_area.setFrameShape(QtWidgets.QFrame.NoFrame)

        lay = QtWidgets.QVBoxLayout(self)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.toggle_button)
        lay.addWidget(self.content_area)

        self.toggle_animation.addAnimation(
            QtCore.QPropertyAnimation(self, b"minimumHeight")
        )
        self.toggle_animation.addAnimation(
            QtCore.QPropertyAnimation(self, b"maximumHeight")
        )
        self.toggle_animation.addAnimation(
            QtCore.QPropertyAnimation(self.content_area, b"maximumHeight")
        )

        
        
        

    @QtCore.pyqtSlot()
    def on_pressed(self):
        checked = self.toggle_button.isChecked()
        self.toggle_button.setIcon(
            self.state0_arrow if not checked else self.state1_arrow
        )
        self.toggle_animation.setDirection(
            QtCore.QAbstractAnimation.Forward
            if not checked
            else QtCore.QAbstractAnimation.Backward
        )
        self.toggle_animation.start()

    def setContentLayout(self, layout, state='expanded'):
        if state == 'expanded':
            self.setContentLayoutExapanded(layout)
        elif state == 'collapsed':
            self.setContentLayoutCollapsed(layout)

    def setContentLayoutCollapsed(self, layout):
        self.state0_arrow = self.down_arrow
        self.state1_arrow = self.right_arrow
        self.toggle_button.setIcon(self.right_arrow)
        lay = self.content_area.layout()
        del lay
        self.content_area.setLayout(layout)
        collapsed_height = (
            self.sizeHint().height() - self.content_area.maximumHeight()
        )
        content_height = layout.sizeHint().height()
        for i in range(self.toggle_animation.animationCount()):
            animation = self.toggle_animation.animationAt(i)
            animation.setDuration(150)
            animation.setStartValue(collapsed_height)
            animation.setEndValue(collapsed_height + content_height)

        content_animation = self.toggle_animation.animationAt(
            self.toggle_animation.animationCount() - 1
        )
        content_animation.setDuration(150)
        content_animation.setStartValue(0)
        content_animation.setEndValue(content_height)

    def setContentLayoutExapanded(self, layout):
        self.state1_arrow = self.down_arrow
        self.state0_arrow = self.right_arrow
        self.toggle_button.setIcon(self.down_arrow)
        lay = self.content_area.layout()
        del lay
        self.content_area.setLayout(layout)
        size_hint_height = self.sizeHint().height()
        maximum_height = self.content_area.maximumHeight()
        collapsed_height = (
            size_hint_height - maximum_height
        )
        content_height = layout.sizeHint().height()
        for i in range(self.toggle_animation.animationCount()):
            animation = self.toggle_animation.animationAt(i)
            animation.setDuration(150)
            animation.setStartValue(collapsed_height+ content_height)
            animation.setEndValue(collapsed_height )

        content_animation = self.toggle_animation.animationAt(
            self.toggle_animation.animationCount() - 1
        )
        content_animation.setDuration(150)
        content_animation.setStartValue(content_height)
        content_animation.setEndValue(0)

        self.content_area.setMaximumHeight(content_height)
        self.setFixedHeight(collapsed_height+content_height)


class EliderLabel(QtWidgets.QLabel):

    '''
    downloaded from https://stackoverflow.com/questions/11446478/pyside-pyqt-truncate-text-in-qlabel-based-on-minimumsize
    '''

    elision_changed = QtCore.pyqtSignal(bool)

    def __init__(self, text='', mode=QtCore.Qt.ElideRight, **kwargs):
        super().__init__(**kwargs)

        self._mode = mode
        self.elided = False

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setText(text)

    def setText(self, text):
        self._contents = text
        # Changing the content require a repaint of the widget (or so
        # says the overview)
        self.update()

    def text(self):
        return self._contents

    def minimumSizeHint(self):
        metrics = QtGui.QFontMetrics(self.font())
        return QtCore.QSize(0, metrics.height())

    def paintEvent(self, event):

        super().paintEvent(event)

        did_elide = False

        painter = QtGui.QPainter(self)
        font_metrics = painter.fontMetrics()
        # if fontMetrics.width() is deprecated; use horizontalAdvance
        text_width = font_metrics.width(self.text())

        # Layout phase, per the docs
        text_layout = QtGui.QTextLayout(self._contents, painter.font())
        text_layout.beginLayout()

        while True:

            line = text_layout.createLine()

            if not line.isValid():
                break

            line.setLineWidth(self.width())

            if text_width >= self.width():
                elided_line = font_metrics.elidedText(self._contents, self._mode, self.width())
                painter.drawText(QtCore.QPoint(0, font_metrics.ascent()), elided_line)
                did_elide = line.isValid()
                break
            else:
                line.draw(painter, QtCore.QPoint(0, 0))

        text_layout.endLayout()

        self.elision_changed.emit(did_elide)

        if did_elide != self.elided:
            self.elided = did_elide
            self.elision_changed.emit(did_elide)


'''if __name__ == "__main__":
    import sys
    import random

    app = QtWidgets.QApplication(sys.argv)

    w = QtWidgets.QMainWindow()
    
    
    scroll = QtWidgets.QScrollArea()
    w.setCentralWidget(scroll)
    content = QtWidgets.QWidget()
    scroll.setWidget(content)
    scroll.setWidgetResizable(True)
    vlay = QtWidgets.QVBoxLayout(content)
    for i in range(10):
        box = CollapsibleBox("Collapsible Box Header-{}".format(i))
        vlay.addWidget(box)
        lay = QtWidgets.QVBoxLayout()
        for j in range(8):
            label = QtWidgets.QLabel("{}".format(j))
            color = QtGui.QColor(*[random.randint(0, 255) for _ in range(3)])
            label.setStyleSheet(
                "background-color: {}; color : white;".format(color.name())
            )
            label.setAlignment(QtCore.Qt.AlignCenter)
            lay.addWidget(label)

        box.setContentLayout(lay)
    vlay.addStretch()
    w.resize(640, 480)
    w.show()
    sys.exit(app.exec_())'''