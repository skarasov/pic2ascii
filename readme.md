## PIC2ASCII

Python script to convert pictures to colored ascii!

Required - pillow lib

```
> python .\main.py -h

usage: main.py [-h] [-w W] [-e E] [-t T] [-d D] [-l] [-s] filename

PIC2ASCII

positional arguments:
  filename    picture filename

options:
  -h, --help  show this help message and exit
  -w W        width in chars to fit picture, default = 60
  -e E        height in chars to fit picture, default = 30
  -t T        edge threshold, default = 1.5
  -d D        dim color, default = 1.0
  -l          use lightness instead of value to select char
  -s          output as separate arrays color[r,g,b] and char
```
