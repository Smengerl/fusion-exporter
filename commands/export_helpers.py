import adsk.core
import adsk.fusion
from pathlib import Path
from typing import Callable, Optional, List

from ..apper import apper


def check_folder_validity(path: Path) -> Optional[str]:
    """Ensure path exists (or can be created) and is writable.

    Returns None on success, otherwise an error message string.
    """
    try:
        path.resolve(strict=False)
    except Exception as e:
        return f"Invalid path: {e}"

    if path.exists():
        if path.is_file():
            return "A file with this name already exists."
        if not path.is_dir():
            return "Path exists but is not a directory."
    else:
        try:
            path.mkdir(parents=True)
        except Exception as e:
            return f"Could not create directory: {e}"

    try:
        testfile = path / ".deleteme.tmp"
        with open(testfile, "w") as f:
            f.write("test")
        testfile.unlink()
    except Exception as e:
        return f"Directory is not writable: {e}"

    return None


def set_occurrence_recursive(occurrence: adsk.fusion.Occurrence, predicate: Callable[[adsk.fusion.Occurrence], bool]):
    """Set visibility for an occurrence and all children based on predicate."""
    occurrence.isLightBulbOn = bool(predicate(occurrence))
    children = occurrence.childOccurrences
    for i in range(children.count):
        child = children.item(i)
        set_occurrence_recursive(child, predicate)


def sanitize_filename(name: str, replacement: str = '_') -> str:
    """Return a filesystem-safe filename by replacing unsafe characters.

    This is a conservative sanitizer: it replaces characters that are invalid
    in common filesystems and strips control characters. It also trims
    whitespace from ends. Keeps file extensions if present (caller should
    include extension separately).
    """
    # Keep only a whitelist of safe characters plus dot and dash
    import re
    name = name.strip()
    # Replace path separators and control characters
    name = re.sub(r'[\\/\x00-\x1f]', replacement, name)
    # Replace other unsafe chars
    name = re.sub(r'[:\*\?"<>\|]', replacement, name)
    # Collapse multiple replacements
    name = re.sub(re.escape(replacement) + r'+', replacement, name)
    # Trim leading/trailing dots or spaces
    name = name.strip(' .')
    if len(name) == 0:
        return 'unnamed'
    return name


def export_stl_to_file(file_name: str, occ: adsk.fusion.Occurrence):
    """Export the given occurrence to an STL file.
    """
    ao = apper.AppObjects()
    app: adsk.core.Application = ao.app
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    export_mgr = design.exportManager

    root = design.rootComponent
    occs = root.occurrences
    for i in range(occs.count):
        other = occs.item(i)
        #other.isIsolated = True
        set_occurrence_recursive(other, lambda o: o == occ)

    opts = export_mgr.createSTLExportOptions(occ, file_name)
    export_mgr.execute(opts)


def export_png_to_file(file_name: str, occ: adsk.fusion.Occurrence, width: int, height: int):
    """Export a viewport snapshot of the given occurrence to an PNG file.
    """
    ao = apper.AppObjects()
    app = ao.app
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)

    root = design.rootComponent
    occs = root.occurrences
    for i in range(occs.count):
        other = occs.item(i)
        set_occurrence_recursive(other, lambda o: o == occ)

    view = app.activeViewport
    view.fit()
    view.saveAsImageFile(file_name, width, height)

#    export_options = adsk.fusion.ImageExportOptions.create(file_name)
#    export_options.width = width
#    export_options.height = height
#    export_options.isBackgroundTransparent = transparency
#    export_options.imageType = adsk.core.ImageFileTypes.PNGImageFileType
#    view.saveAsImageFileWithOptions(export_options)



def export_components(components: List[adsk.fusion.Occurrence], 
                      include_referenced_components: bool,
                      include_flagged_components: bool,
                      export_stl: bool, stl_path: Path,
                      export_png: bool, png_path: Path, 
                      width: int, height: int):
    ao = apper.AppObjects()

    dlg = ao.ui.createProgressDialog()
    dlg.cancelButtonText = 'Cancel'
    dlg.isBackgroundTranslucent = False
    dlg.isCancelButtonShown = True
    dlg.show('Exporting', '%p%% (%v of %m components exported)', 0, len(components), 1)
    
    exported_components = set()

    skippedItems = 0
    for occ in components:
        dlg.progressValue += 1
        if occ.isReferencedComponent and not include_referenced_components:
            skippedItems += 1
            continue
        if occ.name.startswith('_') and not include_flagged_components:
            skippedItems += 1
            continue

        if occ.component.id in exported_components:
            skippedItems += 1
            continue
        else:
            exported_components.add(occ.component.id)

        if dlg.wasCancelled:
            break
        if export_stl:
            safe = sanitize_filename(occ.component.name)
            out_stl = str((stl_path / f"{safe}.stl").resolve())
            export_stl_to_file(out_stl, occ)
        if export_png:
            safe = sanitize_filename(occ.component.name)
            out_png = str((png_path / f"{safe}.png").resolve())
            export_png_to_file(out_png, occ, width, height)


    dlg.hide()
    ao.ui.messageBox(f"Export finished.\n{len(components)} items processed.\n{skippedItems} skipped.\nPNG exported: {export_png}\nSTL exported: {export_stl}")  # type: ignore
