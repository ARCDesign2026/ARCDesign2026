import ezdxf,matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, ColorPolicy, BackgroundPolicy
doc=ezdxf.readfile('/mnt/project-files/office-dimensions/arc-hk-office.dxf'); msp=doc.modelspace()
cfg=Configuration(color_policy=ColorPolicy.BLACK, background_policy=BackgroundPolicy.WHITE, min_lineweight=0.35)
ALL={'WALL','GLASS','WINDOW','DOOR','PILLAR','CUPBOARD','ROOM_NAMES','FURNITURE','CHAIRS','DIM_TOTAL','DIM_MEASURED'}
pages=[('Full plan: walls, doors, pillars, cupboards, desks, tables, chairs and sizes',ALL),
       ('Outline only: walls, glass, doors, pillars, cupboards and sizes',ALL-{'FURNITURE','CHAIRS'})]
out='/mnt/project-files/office-dimensions/arc-hk-office-plan.pdf'
with PdfPages(out) as pdf:
    for title,keep in pages:
        fig=plt.figure(figsize=(16.54,11.69)); ax=fig.add_axes([0.03,0.05,0.94,0.85])
        ctx=RenderContext(doc)
        Frontend(ctx,MatplotlibBackend(ax),config=cfg).draw_entities(e for e in msp if e.dxf.layer in keep)
        ax.set_xlim(-1.2,16.2); ax.set_ylim(-2.4,9.7); ax.set_aspect('equal',adjustable='datalim'); ax.axis('off')
        fig.text(0.03,0.95,'ARC Group Hong Kong office, 5/F',fontsize=18,weight='bold')
        fig.text(0.03,0.925,title+'. Units: metres. Windows at top, lift lobby at bottom. 18 Nov 2026.',fontsize=11)
        pdf.savefig(fig); plt.close(fig)
print('ok')
