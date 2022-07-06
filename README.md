# py-image-resize
Python CLI app for image resizing, format conversion, and compression.

## Try it out

With [Poetry](https://python-poetry.org/) installed:
```sh
poetry install
poetry shell
# scale down to 10%, convert format, add a suffix to the filename
python resize.py -v -s 10 -f JPEG -u '.thumbnail' test/sample.png
```
