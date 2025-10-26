import adsk.core
import adsk.fusion

from ..apper import apper
from .. import config



class ExportDocumentSavedEvent(apper.Fusion360DocumentEvent):

    def document_event_received(self, event_args, document):
        app = adsk.core.Application.cast(adsk.core.Application.get())
        msg = "You just SAVED a document called: {}".format(document.name)
        app.userInterface.messageBox(msg)
