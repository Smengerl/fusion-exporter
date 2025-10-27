# Auto GitHub Exporter

Automatic exporter for Autodesk Fusion 360 files into the common formats used in the author's GitHub projects.

This add-in automates the process of exporting Fusion 360 designs into common file formats (STL, PNG, F3D, etc.) and packages them in a layout suitable for publishing alongside project source on GitHub.

## Features

- Export parts and assemblies to commonly used formats (STL, STEP, PNG previews, Fusion archive files)
- Place exported files into a consistent folder structure for GitHub repositories
- Lightweight script suitable for use as a Fusion 360 Add-In

## Installation

1. Copy the `Auto-GitHub-Exporter` add-in folder into Fusion 360's AddIns directory. For example:

   - macOS: `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/`

2. Start Fusion 360 and enable the add-in from the Add-Ins menu.

3. Configure any output paths or options inside the add-in UI (if applicable) or edit the provided configuration files in the add-in folder.

## Usage

1. Open the design you want to export in Fusion 360.
2. Run the Auto GitHub Exporter add-in from the Add-Ins menu.
3. Follow the prompts to choose export targets and output folder.

The exporter will create a folder structure with exported binaries and preview images that can be copied directly into a GitHub repository.

## Requirements

- Autodesk Fusion 360 (tested with Fusion 360 versions current at the time of development)
- Python (shipped with Fusion 360's scripting environment)

## Compatibility

This add-in uses Fusion 360's Python API and should work across platforms where Fusion 360 runs (macOS and Windows). Behavior depends on Fusion's API stability across versions.

## Development

If you'd like to develop or extend this add-in:

1. Clone the repository into your Fusion 360 AddIns folder.
2. Edit the Python scripts in-place using your editor of choice.
3. Restart Fusion 360 or reload the add-in to pick up changes.

Contributions are welcome — see `CONTRIBUTING.md` for details.

## License

This project is licensed under the MIT License — see `LICENSE.txt` for details.

## Authors

- Simon Gerlach <https://github.com/Smenger>

---

If something in this README is missing or unclear, please open an issue in the repository so the instructions can be improved.
