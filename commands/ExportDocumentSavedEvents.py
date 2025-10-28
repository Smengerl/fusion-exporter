import adsk.core

from ..apper import apper



class ExportDocumentSavedEvent(apper.Fusion360DocumentEvent):

    def document_event_received(self, event_args, document):
        app = adsk.core.Application.cast(adsk.core.Application.get())
        ui = app.userInterface

        # Prompt the user whether to export components after save
        prompt = f"Document '{document.name}' was saved. Export all components? (No=visible ones only)?"

        # Use Yes/No/Cancel style: we'll map Yes = Export visible, No = Export all, Cancel = Skip
        # Create a custom set of buttons by using messageBox with YesNoCancelButtonType
        res = ui.messageBox(prompt,
                            'Export on save',
                            adsk.core.MessageBoxButtonTypes.YesNoCancelButtonType,
                            adsk.core.MessageBoxIconTypes.QuestionIconType)

        # DialogResults: DialogYes, DialogNo, DialogCancel
        if res == adsk.core.DialogResults.DialogCancel:
            # User chose Skip
            return
        try:
            # The addin registered the commands with base ids 'sample_cmd_1' and 'sample_cmd_2'.
            # Use fusion_app.command_id_from_name to get the full id and execute the command to show its dialog.
            if not hasattr(self, 'fusion_app') or self.fusion_app is None:
                # Try to retrieve from the global app registration as a fallback
                # (in normal startup fusion_app is set by FusionApp.add_document_event)
                from ..AutoExporter import my_addin
                fusion_app = my_addin
            else:
                fusion_app = self.fusion_app

            if res == adsk.core.DialogResults.DialogYes:
                cmd_id = fusion_app.command_id_from_name(AutoExporter.EXPORT_ALL_STL_PMG_COMMAND_ID)
            else:
                cmd_id = fusion_app.command_id_from_name(AutoExporter.EXPORT_STL_PMG_COMMAND_ID)

            if cmd_id:
                cmd_def = ui.commandDefinitions.itemById(cmd_id)
                if cmd_def:
                    cmd_def.execute()
                else:
                    ui.messageBox(f'Command definition not found: {cmd_id}')
            else:
                ui.messageBox('Export command id not found')
        except Exception:
            ui.messageBox('Export on save failed: {}'.format(__import__('traceback').format_exc()))
