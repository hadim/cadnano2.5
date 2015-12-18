from cadnano.cnproxy import UndoCommand
from cadnano.virtualhelix import VirtualHelix

class CreateVirtualHelixCommand(UndoCommand):
    def __init__(self, part, x, y):
        super(CreateVirtualHelixCommand, self).__init__("create virtual helix")
        self._part = part
        id_num = part._reserveHelixIDNumber(requested_id_num=None)
        self._vhelix = VirtualHelix(part, x, y, id_num)
        self._id_num = id_num
        # self._batch = batch
    # end def

    def redo(self):
        vh = self._vhelix
        part = self._part
        id_num = self._id_num
        vh.setPart(part)
        part._addVirtualHelix(vh)
        vh.setNumber(id_num)
        # need to always reserve an id
        part._reserveHelixIDNumber(requested_id_num=id_num)
        # end if
        part.partVirtualHelixAddedSignal.emit(part, vh)
        part.partActiveSliceResizeSignal.emit(part)
    # end def

    def undo(self):
        vh = self._vhelix
        part = self._part
        id_num = self._id_num

        # since we're hashing on the object in the views do this first
        vh.virtualHelixRemovedSignal.emit(part, vh)

        part._removeVirtualHelix(vh)
        part._recycleHelixIDNumber(id_num)
        # clear out part references
        vh.setNumber(None)  # must come before setPart(None)
        vh.setPart(None)
        part.partActiveSliceResizeSignal.emit(part)
    # end def
# end class
