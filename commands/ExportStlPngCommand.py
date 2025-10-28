import adsk.core
from .AbstractExportStlPngCommand import AbstractExportStlPngCommand

class ExportStlPngCommand(AbstractExportStlPngCommand):
    """Export all currently selected occurrences in the active design."""

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
                # Only add occurrences that are visible (light bulb on)
                if getattr(occ, 'isLightBulbOn', True):
                    selection_input.addSelection(occ)
        except Exception:
            # Best-effort: if anything fails, leave selection empty and continue
            pass
