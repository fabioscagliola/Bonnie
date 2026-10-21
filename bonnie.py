import atexit
import fastapi
import pydantic
import subprocess
import threading


PATH = "/home/fabio/Documents/GitHub/hzeller/rpi-rgb-led-matrix"


bonnie = fastapi.FastAPI()
lock = threading.Lock()
proc = None


class Incoming(pydantic.BaseModel):
    text: str
    disable_scrolling: bool = False
    color: str = "255,255,255"


def stop():
    global proc
    if proc is not None and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
    proc = None


atexit.register(stop)


@bonnie.post("/text-scroller")
def text_scroller(incoming: Incoming) -> fastapi.Response:
    global proc

    if not incoming.text.strip():
        raise fastapi.HTTPException(status_code=400, detail="What text?!")

    try:
        rgb = [int(x) for x in incoming.color.split(",")]
        if len(rgb) != 3 or any(x < 0 or x > 255 for x in rgb):
            raise ValueError
    except ValueError:
        raise fastapi.HTTPException(status_code=400, detail="What color?!")

    command = [
        "./utils/text-scroller",
        "--led-chain=4",
        "--led-cols=64",
        "--led-gpio-mapping=adafruit-hat",
        "--led-rows=32",
        "-f", "fonts/10x20.bdf",
        "-y", "6",
        "-C", ",".join(map(str, rgb)),
    ]

    if incoming.disable_scrolling:
        x = (256 - len(incoming.text) * 10) // 2
        command.extend(["-s", "0", "-x", str(x)])

    command.append(incoming.text)

    with lock:
        stop()
        try:
            proc = subprocess.Popen(command, cwd=PATH)
        except OSError as e:
            raise fastapi.HTTPException(status_code=500, detail=str(e))

    return fastapi.Response(status_code=200)


@bonnie.post("/clear")
def clear() -> fastapi.Response:
    global proc

    with lock:
        stop()

    return fastapi.Response(status_code=200)

