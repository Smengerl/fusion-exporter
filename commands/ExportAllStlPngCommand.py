import adsk.core
import adsk.fusion
from .AbstractExportStlPngCommand import AbstractExportStlPngCommand

class ExportAllPngStlCommand(AbstractExportStlPngCommand):
    """Export all top-level occurrences in the active design."""

    def selectComponents(self, selection_input: adsk.core.SelectionCommandInput):
        # Pre-select all occurrences
        try:
            app = ao.app
            product = app.activeProduct
            design = adsk.fusion.Design.cast(product)
            root = design.rootComponent
            occs = root.occurrences
            for i in range(occs.count):
                occ = occs.item(i)
                selection_input.addSelection(occ)
        except Exception:
            # Best-effort: if anything fails, leave selection empty and continue
            pass