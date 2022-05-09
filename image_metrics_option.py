import shutil
import subprocess
from pathlib import Path


class ImageMetricsOption:
    def __init__(self):
        self.do_metrics = False
        self.butteraugli = False
        self.ssimulacra = False

    def check_availability(self) -> bool:
        if shutil.which("butteraugli_main"):
            self.butteraugli = True
        if shutil.which("ssimulacra"):
            self.ssimulacra = True
        return len(self.get_avaible()) != 0

    def get_avaible(self) -> list[str]:
        res = []
        if self.butteraugli:
            res.append("butteraugli max norm")
            res.append("butteraugli pnorm")
        if self.ssimulacra:
            res.append("ssimulacra")
        return res

    def butteraugli_run(self, original: Path, distorted: Path) -> list[str]:
        cmd = ("butteraugli_main", original, distorted)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # TODO command_print_if_error(& output)?;
        output = process.communicate()
        if output[0]:
            return output[0].decode().split('\n')
        else:
            print(output[1])
            return ['-', ':-']

    def ssimulacra_run(self, original: Path, distorted: Path) -> list[str]:
        pass
    # TODO
    #     let outp = std:: process: : Command: : new("ssimulacra")
    #         .arg(original)
    #         .arg(distorted)
    #         .output()?;
    #     command_print_if_error(& outp)?;
    #     Ok(outp
    #         .stdout
    #         .lines()
    #         .next()
    #         .unwrap_or_else(|| Result:: Ok("-".into()))
    #         .unwrap())
