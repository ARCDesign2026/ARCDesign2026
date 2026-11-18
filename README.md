# ARC Group Hong Kong office plan

This repository holds the measured floor plan of the ARC Group Hong Kong office in three forms.

- `survey/arc-office-survey.html`: the measuring page. It stores each length as typed on site (inches, feet, cm and the floor tile units L and S) and works out the plan.
- `model3d/arc-office-3d.html`: the 3D model with furniture. Live at https://arcdesign2026.github.io/ARCDesign2026/
- `cad/arc-hk-office-plan.pdf`: quick view PDF, page 1 outline with sizes, page 2 with furniture.
- `cad/arc-hk-office.dxf`: the AutoCAD plan in metres, with measured lengths (green) and overall totals (pink). `cad/arc-hk-office-dxf-preview.png` is a picture of it.

## Units

- L is one floor tile long: 4 ft less 1/16 in (1.2176 m).
- S is one floor tile wide: 2 ft less 2/16 in (0.6064 m).
- All lengths run to the white bound at the base of the windows and glass. The window glass (5 in) is drawn outside that line.

## Main sizes

- Office: 14.360 m along the front, 8.267 m from the front to the windows.
- The big boardroom sticks out 1.010 m (39.75 in) past the eating area window line, so the front of the office is 15.370 m there.

## Rebuilding

`tools/build3d.py` builds the 3D page from `tools/snap.json`, `tools/furn.json` and `model3d/template.html`. `tools/mkdxf3.py` writes the DXF from the 3D page data (needs `pip install ezdxf`). Run both from a folder that has the same layout as the scratch folder they came from.
