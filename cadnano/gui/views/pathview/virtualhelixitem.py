#!/usr/bin/env python
# encoding: utf-8

from math import floor
from cadnano import util
from cadnano.enum import StrandType
from cadnano.gui.controllers.itemcontrollers.virtualhelixitemcontroller import VirtualHelixItemController
from cadnano.gui.palette import newPenObj, getNoPen, getPenObj, getBrushObj, getNoBrush
from cadnano.gui.views.abstractitems.abstractvirtualhelixitem import AbstractVirtualHelixItem
from .strand.stranditem import StrandItem
from .virtualhelixhandleitem import VirtualHelixHandleItem
from . import pathstyles as styles

from PyQt5.QtCore import QRectF, Qt, QObject, QPointF, pyqtSignal
from PyQt5.QtGui import QBrush, QPen, QColor, QPainterPath, QPolygonF
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsPathItem, QGraphicsRectItem
from PyQt5.QtWidgets import QGraphicsEllipseItem

_BASE_WIDTH = styles.PATH_BASE_WIDTH


PHOS_ITEM_WIDTH = 6
PHOS = QPainterPath()  # Left 5', Right 3' PainterPath
P_POLY = QPolygonF()
P_POLY.append(QPointF(0, 0))
P_POLY.append(QPointF(0.75 * PHOS_ITEM_WIDTH, 0.5 * PHOS_ITEM_WIDTH))
P_POLY.append(QPointF(0, PHOS_ITEM_WIDTH))
P_POLY.append(QPointF(0, 0))
BOX = QPolygonF()
BOX.append(QPointF(0, 0))
BOX.append(QPointF(0, PHOS_ITEM_WIDTH))
BOX.append(QPointF(PHOS_ITEM_WIDTH, PHOS_ITEM_WIDTH))
BOX.append(QPointF(PHOS_ITEM_WIDTH, 0))
BOX.append(QPointF(0, 0))
# PHOS.addPolygon(BOX)
PHOS.addPolygon(P_POLY)


class PreXoverItem(QGraphicsPathItem):
    def __init__(self, parent=None):
        super(QGraphicsPathItem, self).__init__(parent)
    # end def

    def hoverEnterEvent(self, event):
        pass
    # end def

    def hoverMoveEvent(self, event):
        pass
    # end def

    def hoverLeaveEvent(self, event):
        pass
    # end def

# end class


class PreXoverItemGroup(QGraphicsRectItem):
    def __init__(self, parent=None):
        super(QGraphicsRectItem, self).__init__(parent)
        self._parent = parent
        self.setPen(getNoPen())
        iw = _ITEM_WIDTH = 6
        bw = _BASE_WIDTH
        bw2 = 2 * bw
        part = parent.part()
        path = QPainterPath()
        step_size = part.stepSize()
        sub_step_size = part.subStepSize()
        canvas_size = part.maxBaseIdx() + 1
        self.setRect(0, 0, bw * canvas_size, 2 * bw)

        fwd_bases = range(step_size)
        rev_bases = range(step_size)
        fwd_colors = [QColor() for i in range(step_size)]
        for i in range(len(fwd_colors)):
            fwd_colors[i].setHsvF(i/(step_size*1.6), 0.75, 0.8)
        rev_colors = [QColor() for i in range(step_size)]
        for i in range(len(rev_colors)):
            rev_colors[i].setHsvF(i/(step_size*1.6), 0.75, 0.8)
        rev_colors = rev_colors[::-1]

        self._fwd_pxo_items = {}
        self._rev_pxo_items = {}

        for i in range(0,part.maxBaseIdx(),part.stepSize()):
            for j in range(len(fwd_bases)):
                idx = fwd_bases[j]
                item = QGraphicsPathItem(PHOS, self)
                item.setPen(QPen(Qt.NoPen))
                item.setBrush(getBrushObj(fwd_colors[j].name()))
                self._fwd_pxo_items[i+idx] = item
                fx = bw*(i+idx) + bw/2 - 2  # base_index + base_middle - my_width
                fy = -iw/2
                item.setPos(fx,fy)
            for j in range(len(rev_bases)):
                idx = rev_bases[j]
                ritem = QGraphicsPathItem(PHOS, self)
                ritem.setPen(getPenObj(rev_colors[j].name(),1))
                ritem.setBrush(getNoBrush())
                ritem.setTransformOriginPoint(ritem.boundingRect().center())
                ritem.setRotation(180)
                self._rev_pxo_items[i+idx] = ritem
                rx = bw*(i+idx) + bw/2 - 2  # base_index + base_middle - my_width
                ry = bw2 - iw/2
                ritem.setPos(rx,ry)

        # for i in range(0,part.maxBaseIdx(),7):
        #     item = QGraphicsEllipseItem(0, 0, iw, iw, self)
        #     item.setPen(QPen(Qt.NoPen))
        #     item.setBrush(getBrushObj(fwd_colors[int(i/7%3)]))
        #     self._prexo_items[i] = item
        #     fx = bw*i + bw/2 - 2  # base_index + base_middle - my_width
        #     fy = -iw/2
        #     item.setPos(fx,fy)
        #     rx = bw*(i+5) + bw/2 - 2  # base_index + base_middle - my_width
        #     ry = bw2 - iw/2
        #     ritem = QGraphicsEllipseItem(0, 0, iw, iw, self)
        #     ritem.setPen(getPenObj(rev_colors[int((i+5)/7%3)],1))
        #     ritem.setBrush(getNoBrush())
        #     ritem.setPos(rx,ry)
        #     self._prexo_items[i+5] = ritem
    # end def

    def updatePositionsAfterRotation(self, angle):
        bw = _BASE_WIDTH
        part = self._parent.part()
        canvas_size = part.maxBaseIdx() + 1
        step_size = part.stepSize()
        xdelta = angle/360. * bw*step_size
        for i, item in self._fwd_pxo_items.items():
            x = ((bw*i + bw/2 - 2) + xdelta) % (bw*canvas_size)
            item.setX(x)
        for i, item in self._rev_pxo_items.items():
            x = ((bw*i + bw/2 - 2) + xdelta) % (bw*canvas_size)
            item.setX(x)
    # end def


class VirtualHelixItem(QGraphicsPathItem, AbstractVirtualHelixItem):
    """VirtualHelixItem for PathView"""
    findChild = util.findChild  # for debug

    def __init__(self, part_item, model_virtual_helix, viewroot):
        super(VirtualHelixItem, self).__init__(part_item.proxy())
        self._part_item = part_item
        self._model_virtual_helix = model_virtual_helix
        self._viewroot = viewroot
        self._getActiveTool = part_item._getActiveTool
        self._controller = VirtualHelixItemController(self, model_virtual_helix)

        self._handle = VirtualHelixHandleItem(model_virtual_helix, part_item, viewroot)
        self._last_strand_set = None
        self._last_idx = None
        self._scaffold_background = None
        self.setFlag(QGraphicsItem.ItemUsesExtendedStyleOption)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.setBrush(getNoBrush())

        view = viewroot.scene().views()[0]
        view.levelOfDetailChangedSignal.connect(self.levelOfDetailChangedSlot)
        should_show_details = view.shouldShowDetails()

        pen = newPenObj(styles.MINOR_GRID_STROKE, styles.MINOR_GRID_STROKE_WIDTH)
        pen.setCosmetic(should_show_details)
        self.setPen(pen)

        self.refreshPath()
        self.setAcceptHoverEvents(True)  # for pathtools
        self.setZValue(styles.ZPATHHELIX)

        self._prexoveritemgroup = _pxig = PreXoverItemGroup(self)
    # end def

    ### SIGNALS ###

    ### SLOTS ###

    def levelOfDetailChangedSlot(self, boolval):
        """Not connected to the model, only the QGraphicsView"""
        pen = self.pen()
        pen.setCosmetic(boolval)
        self.setPen(pen)
    # end def

    def strandAddedSlot(self, sender, strand):
        """
        Instantiates a StrandItem upon notification that the model has a
        new Strand.  The StrandItem is responsible for creating its own
        controller for communication with the model, and for adding itself to
        its parent (which is *this* VirtualHelixItem, i.e. 'self').
        """
        StrandItem(strand, self, self._viewroot)
    # end def

    def decoratorAddedSlot(self, decorator):
        """
        Instantiates a DecoratorItem upon notification that the model has a
        new Decorator.  The Decorator is responsible for creating its own
        controller for communication with the model, and for adding itself to
        its parent (which is *this* VirtualHelixItem, i.e. 'self').
        """
        pass

    def virtualHelixNumberChangedSlot(self, virtual_helix, number):
        self._handle.setNumber()
    # end def

    def virtualHelixPropertyChangedSlot(self, virtual_helix, property_key, new_value):
        if property_key == 'eulerZ':
            self._handle.rotateWithCenterOrigin(new_value)
            self._prexoveritemgroup.updatePositionsAfterRotation(new_value)
    # end def

    def partPropertyChangedSlot(self, model_part, property_key, new_value):
        if property_key == 'color':
            self._handle.refreshColor()
    # end def

    def virtualHelixRemovedSlot(self, virtual_helix):
        self._controller.disconnectSignals()
        self._controller = None

        scene = self.scene()
        self._handle.remove()
        scene.removeItem(self)
        self._part_item.removeVirtualHelixItem(self)
        self._part_item = None
        self._model_virtual_helix = None
        self._getActiveTool = None
        self._handle = None
    # end def

    ### ACCESSORS ###

    def coord(self):
        return self._model_virtual_helix.coord()
    # end def

    def viewroot(self):
        return self._viewroot
    # end def

    def handle(self):
        return self._handle
    # end def

    def part(self):
        return self._part_item.part()
    # end def

    def partItem(self):
        return self._part_item
    # end def

    def number(self):
        return self._model_virtual_helix.number()
    # end def

    def virtualHelix(self):
        return self._model_virtual_helix
    # end def

    def window(self):
        return self._part_item.window()
    # end def

    ### DRAWING METHODS ###
    def isStrandOnTop(self, strand):
        return strand.strandSet().isScaffold()
        # sS = strand.strandSet()
        # isEvenParity = self._model_virtual_helix.isEvenParity()
        # return isEvenParity and sS.isScaffold() or\
        #        not isEvenParity and sS.isStaple()
    # end def

    def isStrandTypeOnTop(self, strand_type):
        return strand_type is StrandType.SCAFFOLD
        # isEvenParity = self._model_virtual_helix.isEvenParity()
        # return isEvenParity and strand_type is StrandType.SCAFFOLD or \
        #        not isEvenParity and strand_type is StrandType.STAPLE
    # end def

    def upperLeftCornerOfBase(self, idx, strand):
        x = idx * _BASE_WIDTH
        y = 0 if self.isStrandOnTop(strand) else _BASE_WIDTH
        return x, y
    # end def

    def upperLeftCornerOfBaseType(self, idx, strand_type):
        x = idx * _BASE_WIDTH
        y = 0 if self.isStrandTypeOnTop(strand_type) else _BASE_WIDTH
        return x, y
    # end def

    def refreshPath(self):
        """
        Returns a QPainterPath object for the minor grid lines.
        The path also includes a border outline and a midline for
        dividing scaffold and staple bases.
        """
        bw = _BASE_WIDTH
        bw2 = 2 * bw
        part = self.part()
        path = QPainterPath()
        sub_step_size = part.subStepSize()
        canvas_size = part.maxBaseIdx() + 1
        # border
        path.addRect(0, 0, bw * canvas_size, 2 * bw)
        # minor tick marks
        for i in range(canvas_size):
            x = round(bw * i) + .5
            if i % sub_step_size == 0:
                path.moveTo(x - .5,  0)
                path.lineTo(x - .5,  bw2)
                path.lineTo(x - .25, bw2)
                path.lineTo(x - .25, 0)
                path.lineTo(x,       0)
                path.lineTo(x,       bw2)
                path.lineTo(x + .25, bw2)
                path.lineTo(x + .25, 0)
                path.lineTo(x + .5,  0)
                path.lineTo(x + .5,  bw2)

                # path.moveTo(x-.5, 0)
                # path.lineTo(x-.5, 2 * bw)
                # path.lineTo(x+.5, 2 * bw)
                # path.lineTo(x+.5, 0)

            else:
                path.moveTo(x, 0)
                path.lineTo(x, 2 * bw)

        # staple-scaffold divider
        path.moveTo(0, bw)
        path.lineTo(bw * canvas_size, bw)

        self.setPath(path)

        if self._model_virtual_helix.scaffoldIsOnTop():
            scaffoldY = 0
        else:
            scaffoldY = bw
    # end def

    def resize(self):
        """Called by part on resize."""
        self.refreshPath()

    ### PUBLIC SUPPORT METHODS ###
    def setActive(self, idx):
        """Makes active the virtual helix associated with this item."""
        self.part().setActiveVirtualHelix(self._model_virtual_helix, idx)
    # end def

    ### EVENT HANDLERS ###
    def mousePressEvent(self, event):
        """
        Parses a mousePressEvent to extract strand_set and base index,
        forwarding them to approproate tool method as necessary.
        """
        self.scene().views()[0].addToPressList(self)
        strand_set, idx = self.baseAtPoint(event.pos())
        self.setActive(idx)
        tool_method_name = self._getActiveTool().methodPrefix() + "MousePress"

        ### uncomment for debugging modifier selection
        # strand_set, idx = self.baseAtPoint(event.pos())
        # row, col = strand_set.virtualHelix().coord()
        # self._part_item.part().selectPreDecorator([(row,col,idx)])

        if hasattr(self, tool_method_name):
            self._last_strand_set, self._last_idx = strand_set, idx
            getattr(self, tool_method_name)(strand_set, idx)
        else:
            event.setAccepted(False)
    # end def

    def mouseMoveEvent(self, event):
        """
        Parses a mouseMoveEvent to extract strand_set and base index,
        forwarding them to approproate tool method as necessary.
        """
        tool_method_name = self._getActiveTool().methodPrefix() + "MouseMove"
        if hasattr(self, tool_method_name):
            strand_set, idx = self.baseAtPoint(event.pos())
            if self._last_strand_set != strand_set or self._last_idx != idx:
                self._last_strand_set, self._last_idx = strand_set, idx
                getattr(self, tool_method_name)(strand_set, idx)
        else:
            event.setAccepted(False)
    # end def

    def customMouseRelease(self, event):
        """
        Parses a mouseReleaseEvent to extract strand_set and base index,
        forwarding them to approproate tool method as necessary.
        """
        tool_method_name = self._getActiveTool().methodPrefix() + "MouseRelease"
        if hasattr(self, tool_method_name):
            getattr(self, tool_method_name)(self._last_strand_set, self._last_idx)
        else:
            event.setAccepted(False)
    # end def

    ### COORDINATE UTILITIES ###
    def baseAtPoint(self, pos):
        """
        Returns the (strand_type, index) under the location x,y or None.

        It shouldn't be possible to click outside a pathhelix and still call
        this function. However, this sometimes happens if you click exactly
        on the top or bottom edge, resulting in a negative y value.
        """
        x, y = pos.x(), pos.y()
        mVH = self._model_virtual_helix
        base_idx = int(floor(x / _BASE_WIDTH))
        min_base, max_base = 0, mVH.part().maxBaseIdx()
        if base_idx < min_base or base_idx >= max_base:
            base_idx = util.clamp(base_idx, min_base, max_base)
        if y < 0:
            y = 0  # HACK: zero out y due to erroneous click
        strandIdx = floor(y * 1. / _BASE_WIDTH)
        if strandIdx < 0 or strandIdx > 1:
            strandIdx = int(util.clamp(strandIdx, 0, 1))
        strand_set = mVH.getStrandSetByIdx(strandIdx)
        return (strand_set, base_idx)
    # end def

    def keyPanDeltaX(self):
        """How far a single press of the left or right arrow key should move
        the scene (in scene space)"""
        dx = self._part_item.part().stepSize() * _BASE_WIDTH
        return self.mapToScene(QRectF(0, 0, dx, 1)).boundingRect().width()
    # end def

    def hoverLeaveEvent(self, event):
        self._part_item.updateStatusBar("")
    # end def

    def hoverMoveEvent(self, event):
        """
        Parses a mouseMoveEvent to extract strand_set and base index,
        forwarding them to approproate tool method as necessary.
        """
        base_idx = int(floor(event.pos().x() / _BASE_WIDTH))
        loc = "%d[%d]" % (self.number(), base_idx)
        self._part_item.updateStatusBar(loc)

        active_tool = self._getActiveTool()
        tool_method_name = self._getActiveTool().methodPrefix() + "HoverMove"
        if hasattr(self, tool_method_name):
            strand_type, idx_x, idx_y = active_tool.baseAtPoint(self, event.pos())
            getattr(self, tool_method_name)(strand_type, idx_x, idx_y)
    # end def

    ### TOOL METHODS ###
    def pencilToolMousePress(self, strand_set, idx):
        """strand.getDragBounds"""
        # print "%s: %s[%s]" % (util.methodName(), strand_set, idx)
        active_tool = self._getActiveTool()
        if not active_tool.isDrawingStrand():
            active_tool.initStrandItemFromVHI(self, strand_set, idx)
            active_tool.setIsDrawingStrand(True)
    # end def

    def pencilToolMouseMove(self, strand_set, idx):
        """strand.getDragBounds"""
        # print "%s: %s[%s]" % (util.methodName(), strand_set, idx)
        active_tool = self._getActiveTool()
        if active_tool.isDrawingStrand():
            active_tool.updateStrandItemFromVHI(self, strand_set, idx)
    # end def

    def pencilToolMouseRelease(self, strand_set, idx):
        """strand.getDragBounds"""
        # print "%s: %s[%s]" % (util.methodName(), strand_set, idx)
        active_tool = self._getActiveTool()
        if active_tool.isDrawingStrand():
            active_tool.setIsDrawingStrand(False)
            active_tool.attemptToCreateStrand(self, strand_set, idx)
    # end def

    def pencilToolHoverMove(self, strand_type, idx_x, idx_y):
        """Pencil the strand is possible."""
        part_item = self.partItem()
        active_tool = self._getActiveTool()
        if not active_tool.isFloatingXoverBegin():
            temp_xover = active_tool.floatingXover()
            temp_xover.updateFloatingFromVHI(self, strand_type, idx_x, idx_y)
    # end def
