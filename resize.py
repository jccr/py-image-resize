"""Image Resize

Usage:
  resize.py [options] (<glob> | <file>...)

Options:
  -h --help               print this screen
  --version               print version
  -s, --scale PERCENT     scale proportionally [default: 100]
  -f, --format FORMAT     output format (jpeg, png)
                          if not specified, the format matches the input
  -d, --directory DIR     output directory for processed input files
                          if not specified, output files are overwritten
  -p, --prefix PREFIX     prefix for output file names
  -u, --suffix SUFFIX     suffix for output file names
  -v, --verbose           verbose mode
  -q, --quality QUALITY   jpeg compression level; 0 (worst) to 95 (best) [default: 75]
  -c, --compression C     png compression level; 0 (none) to 9 (best) [default: 6]
  -r, --dry-run           dry run mode, no operations performed
  -m, --subsampling M     jpeg subsampling; 0 (4:4:4), 1 (4:2:2), 2 (4:2:0),
                          keep (retain original) or auto (determined by library)
                          [default: keep]
                          if the input format is not jpeg, keep is used as auto
  -x, --exclude-icc       exclude ICC profile
  --debug                 debug mode
"""
from distutils import extension
from itertools import chain
import glob
from pathlib import Path
from docopt import docopt
from PIL import Image, JpegImagePlugin


def iterate_glob(glob_pattern):
    if glob_pattern is not None:
        for filename in glob.iglob(glob_pattern, recursive=True):
            yield filename


def scale_image(image, scale):
    (width, height) = (int(image.width * scale), int(image.height * scale))
    return image.resize((width, height))


def parse_subsampling(image, subsampling):
    if subsampling == "auto":
        return None
    if subsampling == "keep" and image.format != "JPEG":
        return None
    if subsampling == "keep":
        return JpegImagePlugin.get_sampling(image)
    return int(subsampling)


def main():
    args = docopt(__doc__, version="Image Resize 1.0")
    if args["--debug"]:
        print(args)

    for filename in chain(iterate_glob(args["<glob>"]), args["<file>"]):
        with Image.open(filename) as image:
            path = Path(filename)

            if args["--scale"]:
                new_image = scale_image(image, int(args["--scale"]) / 100)

            if args["--format"]:
                format = args["--format"].upper()
            else:
                format = image.format

            if format == "JPEG" and image.mode in ("RGBA", "P"):
                new_image = new_image.convert("RGB")

            extension = path.suffix
            if format == "JPEG":
                extension = ".jpg"
            if format == "PNG":
                extension = ".png"

            if args["--directory"]:
                output_filename = Path(args["--directory"]) / (
                    (args["--prefix"] or "")
                    + path.stem
                    + (args["--suffix"] or "")
                    + extension
                )
            else:
                output_filename = path.parent / (
                    (args["--prefix"] or "")
                    + path.stem
                    + (args["--suffix"] or "")
                    + extension
                )

            if args["--verbose"]:
                print("{} -> {}".format(filename, output_filename))

            params = dict(
                fp=output_filename,
                format=format,
                quality=int(args["--quality"]),
                compress_level=int(args["--compression"]),
            )

            if not args["--exclude-icc"]:
                params["icc_profile"] = image.info.get("icc_profile")

            subsampling = parse_subsampling(image, args["--subsampling"])
            if subsampling:
                params["subsampling"] = subsampling

            if args["--debug"]:
                print(params)

            if not args["--dry-run"]:
                new_image.save(**params)


if __name__ == "__main__":
    main()
