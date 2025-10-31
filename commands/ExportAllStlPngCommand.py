import adsk.core
import adsk.fusion
import traceback
from .AbstractExportStlPngCommand import AbstractExportStlPngCommand

from ..apper import apper

class ExportAllStlPngCommand(AbstractExportStlPngCommand):
    """Export all top-level occurrences in the active design."""

    CMD_ID = 'export_all_stl_png_cmd_id'
            


    def add_occurrence_recursive(self, occurrence: adsk.fusion.Occurrence, selection_input: adsk.core.SelectionCommandInput):
        """Adds a child occurences to selection"""
        selection_input.addSelection(occurrence)
        children = occurrence.childOccurrences
        for i in range(children.count):
            child = children.item(i)
            self.add_occurrence_recursive(child, selection_input)



    def selectComponents(self, selection_input: adsk.core.SelectionCommandInput):
        # Pre-select all occurrences
        try:
            ao = apper.AppObjects()
            app = ao.app
            product = app.activeProduct
            design = adsk.fusion.Design.cast(product)
            root = design.rootComponent
            occs = root.occurrences
            for i in range(occs.count):
                occ = occs.item(i)
                self.add_occurrence_recursive(occ, selection_input)
        except Exception:
            app = adsk.core.Application.get()
            ui = app.userInterface
            if ui:
                ui.messageBox('Initialization Failed: {}'.format(traceback.format_exc()))
