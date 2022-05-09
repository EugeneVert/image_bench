import argparse
import csv
import multiprocessing
import multiprocessing.pool
import subprocess
import sys
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Any, Dict

from PIL import Image

from image_metrics_option import ImageMetricsOption


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(dest="input", nargs='?', default='./*')
    parser.add_argument("-o", "--out_dir", type=str, default="./out")
    parser.add_argument("-c", "--cmds", type=str, nargs='+', required=True)
    parser.add_argument("-s", "--save", action="store_true")
    parser.add_argument("--csv_path", type=Path, default="./res.csv", required=False)
    parser.add_argument("-m", "--metrics", action="store_true")
    parser.add_argument("--nproc", type=int)
    args = parser.parse_args()

    imageformats = (".png", ".jpg", ".webp")
    if args.input == "./*":
        args.input = [f for f in Path('.').glob("*") if (f.is_file() and f.name.endswith(imageformats))]

    args_metrics = ImageMetricsOption()
    if args.metrics and args_metrics.check_availability():
        args_metrics.do_metrics = True

    csv_write_header(args, args_metrics)
    if type(args.input) == str:
        args.input = [Path(args.input), ]
    for img in args.input:
        print(img)
        process_image(img, args, args_metrics)


def process_image(img: Path, args, args_metrics: ImageMetricsOption):
    img_filesize = img.stat().st_size
    img_dimensions: tuple[int, int] = Image.open(img).size
    px_count = img_dimensions[0] * img_dimensions[1]

    pool = multiprocessing.Pool(args.nproc)
    enc_img_buffers_with_metrics = pool.starmap(gen_buff, [(img, cmd, args_metrics) for cmd in args.cmds])
    # print(img)

    csv_file = open(args.csv_path, "a", newline='')
    csv_writer = csv.writer(csv_file, delimiter='\t')

    for (i, (buff, metrics)) in enumerate(enc_img_buffers_with_metrics):
        csv_row: list[Any] = []
        buff_filesize = buff.image.getbuffer().nbytes
        buff_bpp = buff_filesize * 8 / px_count
        percentage_of_original = 100 * buff_filesize / img_filesize

        print(
            f"{buff.get_cmd()}\n{byte2size(img_filesize)} \
                --> {byte2size(buff_filesize)}\t{buff_bpp:.2f}\t{percentage_of_original:.1f}%"
        )
        csv_row.append(img.name)
        csv_row.append(buff.get_cmd())
        csv_row.append(img_filesize)
        csv_row.append(px_count)
        csv_row.append(buff_filesize)
        csv_row.append(buff_bpp)
        if args_metrics.do_metrics:
            if args_metrics.butteraugli:
                csv_row.append(metrics[0])
                csv_row.append(metrics[1].split(':')[1])
        csv_writer.writerow(csv_row)
    csv_file.close()


def gen_buff(img, cmd, args_metrics):
    print(img, cmd)
    buff = ImageBuffer(cmd)
    buff.image_generate(img)
    img_distorted = buff.image_decode()
    if args_metrics.butteraugli:
        metrics = args_metrics.butteraugli_run(img, img_distorted.name)
    img_distorted.close()
    return (buff, metrics)


def csv_write_header(args, args_metrics: ImageMetricsOption):
    with open(args.csv_path, "a", newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter='\t')
        # csv header row
        metrics = args_metrics.get_avaible()
        print(f"Metrics: {metrics}")
        csv_row = ["Image", "Method", "Size", "px_count", "Res size", "Res bpp"]
        for metric in metrics:
            csv_row.append(metric)
        csv_writer.writerow(csv_row)


class ImageBuffer:
    def __init__(self, cmd: str):
        self.image: BytesIO = BytesIO()
        # Encoder command (e.g. `cjxl`)
        self.encoder: str = ""
        # Encoder arguments
        self.args: list[str] = []
        # Decoder command (e.g. `djxl`)
        self.decoder: str = ""
        # Decoder arguments
        self.decoder_args: list[str] = []
        # Get image [from stdout | temporary file]
        self.output_from_stdout: bool = False
        # Result image file extension (suffix)
        self.output_extension: str = ""
        # execution time
        self.duration = None

        eprint(cmd)
        split_indexes = [i[0] for i in enumerate(cmd) if i[1] == ':']
        num_of_splits = len(split_indexes)
        if num_of_splits == 1:
            preset = True
        elif num_of_splits == 2:
            preset = False
        else:
            raise Exception("Error parsinig cmd")

        if preset:
            (self.encoder, self.args) = (
                cmd[:split_indexes[0]],
                cmd[split_indexes[0] + 1:].replace("\\.", ":").split(' ')
            )
            self.match_preset(self.encoder)
        else:
            raise NotImplementedError()

    def match_preset(self, preset: str):
        ENC_MAPPING: Dict[str, Dict] = {
            "cjpeg": {
                "output_extension": "jpg",
                "decoder": "djpeg",
                "output_from_stdout": True},
            "png": {
                "output_extension": "png",
                "decoder": "png"},
            "cjxl": {
                "output_extension": "jxl",
                "decoder": "djxl"},
            "avifenc": {
                "output_extension": "avif",
                "decoder": "avifdec",
                "decoder_args": "-d 8"},
            "cavif": {
                "output_extension": "avif",
                "decoder": "avifdec",
                "decoder_args": "-d 8"},
            "cwebp": {
                "output_extension": "webp",
                "decoder": "dwebp",
                "decoder_args": "-o"},
        }
        if setting := ENC_MAPPING.get(preset):
            if output_extension := setting.get("output_extension"):
                self.output_extension = output_extension
            if decoder := setting.get("decoder"):
                self.decoder = decoder
            if decoder_args := setting.get("decoder_args"):
                self.decoder_args = decoder_args.split(' ')
            if output_from_stdout := setting.get("output_from_stdout"):
                self.output_from_stdout = output_from_stdout
        else:
            eprint(f"match error, cmd '{preset}' not supported")
            sys.exit(2)

    def image_generate(self, img: Path):
        if "" in self.args:
            self.args.pop()

        if self.output_from_stdout:
            cmd = (self.encoder, str(img), *self.args)
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.image = BytesIO(process.communicate()[0])
        else:
            buffer = tempfile.NamedTemporaryFile(suffix="." + self.output_extension)
            cmd = (self.encoder, str(img), *self.args, str(buffer.name))
            subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
            self.image = BytesIO(buffer.read())
            self.image.read()
            buffer.close()

    def image_decode(self):
        buffer_image = tempfile.NamedTemporaryFile(suffix="." + self.output_extension)
        buffer_output = tempfile.NamedTemporaryFile(suffix=".png")
        buffer_image.write(self.image.getbuffer())
        buffer_image.seek(0)

        # if len(self.decoder_args):
        cmd = (self.decoder, str(buffer_image.name), *self.decoder_args, str(buffer_output.name))
        # else:
        #     cmd = (self.decoder, str(buffer_image.name), str(buffer_output.name))
        subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()

        buffer_image.close()
        self.image.seek(0)
        return buffer_output

    def get_cmd(self) -> str:
        return self.encoder + " " + " ".join(self.args)


def eprint(*args, **kwargs):
    def eprint(*args, **kwargs):
        print(*args, file=sys.stderr, **kwargs)


def byte2size(num, suffix='iB'):
    for unit in ['', 'K', 'M', 'G']:
        if abs(num) < 1024.0:
            return "%3.1f%s%siB" % (num, unit, suffix)
        num /= 1024.0
    return "%3.1f%s%s" % (num, 'TiB', suffix)


if __name__ == "__main__":
    main()
