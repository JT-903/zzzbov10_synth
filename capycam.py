# /// script
# requires-python = ">=3.12"
# dependencies = ["fastapi", "uvicorn", "pypylon"]
# ///
"""Take pictures with a Basler camera over HTTP.

Launch with:

    uv run capycam.py                    # http://127.0.0.1:8000
    PYLON_CAMEMU=1 uv run capycam.py     # emulated camera, no hardware needed

/snap returns a URL rather than image bytes: it is called from Temporal
activities, whose results go into the workflow history and are size limited.

Camera settings (exposure, gain, ROI, pixel format, auto functions off, ...)
are not route parameters. Can tune them in pylon Viewer, save the features file
next to this script as capycam.pfs, and every grab will use them.
"""

import uuid
from pathlib import Path

import anyio
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from pypylon import genicam, pylon

IMAGES = Path("capycam_images")
SETTINGS = Path(__file__).with_name("capycam.pfs")
app = FastAPI(title="capycam")


def grab(path: Path) -> None:
    """Open the camera, grab one frame, write it to path, close again.

    Saved as TIFF in the sensor's native pixel format: lossless, and it keeps
    the full bit depth of a 12- or 16-bit mono camera.
    """
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    camera.Open()
    try:
        if SETTINGS.is_file():
            # validate=True: fail loudly rather than shoot with half the
            # settings applied, which would silently spoil a run.
            pylon.FeaturePersistence.Load(str(SETTINGS), camera.GetNodeMap(), True)
        camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        if not result.GrabSucceeded():
            raise RuntimeError(f"grab failed: {result.ErrorDescription}")
        image = pylon.PylonImage()
        image.AttachGrabResultBuffer(result)
        image.Save(pylon.ImageFileFormat_Tiff, str(path))
        image.Release()
        result.Release()
    finally:
        camera.StopGrabbing()
        camera.Close()


@app.get("/ready")
async def ready() -> dict:
    """Grab and discard a frame: a camera that opens may still not grab."""
    IMAGES.mkdir(exist_ok=True)
    try:
        await anyio.to_thread.run_sync(grab, IMAGES / "ready.tiff")
    except (genicam.GenericException, RuntimeError) as exc:
        return {"ready": False, "detail": str(exc), "settings": None}
    return {
        "ready": True,
        "detail": "camera open and grabbing",
        "settings": str(SETTINGS) if SETTINGS.is_file() else None,
    }


@app.post("/snap")
async def snap(request: Request) -> dict:
    IMAGES.mkdir(exist_ok=True)
    name = f"{uuid.uuid4().hex}.tiff"
    try:
        await anyio.to_thread.run_sync(grab, IMAGES / name)
    except (genicam.GenericException, RuntimeError) as exc:
        raise HTTPException(503, str(exc)) from exc
    return {"name": name, "url": str(request.url_for("image", name=name))}


@app.get("/image/{name}")
async def image(name: str) -> FileResponse:
    path = IMAGES / Path(name).name
    if not path.is_file():
        raise HTTPException(404, f"no such image {name}")
    return FileResponse(path, media_type="image/tiff")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
