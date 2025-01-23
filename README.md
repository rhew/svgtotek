# SVG to Tektronix 4010

## Quick Start

```
inkscape input.svg --batch-process --actions='EditSelectAll;SelectionSimplify;FileSave;FileClose'

python svgtotek.py input.svg input.tek
```

## Resolution

From RETRO-GRAPHIX Users Manual:

"The RG-512 graphics grid is automatically scaled to the graphics grid used by Tektronix Plot 10 software"

  - Tektronix Plot 10: 1024 x 780
  - RG-512: 512 x 250

From example, 0 based. 0-1023; 0-779

## Encoding

- https://vt100.net/docs/vt3xx-gp/chapter13.html
- https://bitsavers.org/pdf/tektronix/401x/070-1225-00_4010um_Jul81.pdf
  - page 3-2

