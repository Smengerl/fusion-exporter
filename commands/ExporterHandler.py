import adsk.core
import adsk.fusion

#from typing import List



class ExporterHandler:

    def export(self, exportSTL:bool, exportPNG:bool, ):
#        app = adsk.core.Application.cast(adsk.core.Application.get())
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Get the "Konstruktion" workspace.
        renderWS = ui.workspaces.itemById('FusionSolidEnvironment')

        