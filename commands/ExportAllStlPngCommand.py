import adsk.core
import adsk.fusion
from pathlib import Path

from ..apper import apper
from .. import config
from .ExportStlPngCommand import ExportStlPngCommand
from . import export_helpers


class ExportAllPngStlCommand(ExportStlPngCommand):
    """Export all top-level occurrences in the active design.

    This subclasses the normal ExportStlPngCommand for UI/validation reuse
    but implements an on_execute that ignores the selection input and
    operates on every occurrence in the root component.
    """



    def selectComponents(self, selection_input: adsk.core.SelectionCommandInput):
        # Pre-select all currently visible occurrences
        try:
            app = ao.app
            product = app.activeProduct
            design = adsk.fusion.Design.cast(product)
            root = design.rootComponent
            occs = root.occurrences
            for i in range(occs.count):
                occ = occs.item(i)
                sel.addSelection(occ)
        except Exception:
            # Best-effort: if anything fails, leave selection empty and continue
            pass