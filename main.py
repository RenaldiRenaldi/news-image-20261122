"""Copy THE WIRE's finished image to the competition output directory."""
import os
from pathlib import Path
import shutil

root = Path(__file__).resolve().parent
output = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
output.mkdir(parents=True, exist_ok=True)
shutil.copyfile(root / "entry.png", output / "entry.png")
