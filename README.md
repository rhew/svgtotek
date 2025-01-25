# SVG to Tektronix 4010

## Draw on an ADM-3A with an RG-512

Prepare a Linux host for attachment
```
stty -F /dev/ttyUSB0 9600 cs8 -cstopb -parenb -ixon
sudo agetty -L ttyUSB0 9600 adm3a
```

And Run from the ADM-3A
```
./svgtotek.py input.svg -d -t 30
```

## Convert SVG to Tektronix 4010 characters
```
source venv/bin/activate
./svgtotek.py input.svg -o output.tek
```

---

## Simplify SVG Files if necessary

inkscape input.svg --batch-process --actions='EditSelectAll;SelectionSimplify;FileSave;FileClose'

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

