import adsk.core
import adsk.fusion

from ..apper import apper
from .. import config


class ExportWorkspaceActivatedEventHandler(apper.Fusion360WorkspaceEvent):

    def workspace_event_received(self, event_args, workspace):
        app = adsk.core.Application.cast(adsk.core.Application.get())
        msg = "You just ACTIVATED a workspace called: name:{}, id:{}".format(workspace.name, workspace.id)
        app.userInterface.messageBox(msg)

