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


async def takeTimelapse(path: Path, duration: int, grabInterval: float) -> tuple[int, int]:
    '''Open the camera, grab frames regularly over a time period, save them, close.
    
    The inputted path should be a directory.
    Error catching must stop grabbing and close the camera afterwards.
    '''
    with pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice()) as camera:
        # Open camera to access settings
        camera.Open()
        try:
            # Take settings from file
            if SETTINGS.is_file():
                # validate=True: fail loudly rather than shoot with half the
                # settings applied, which would silently spoil a run.
                pylon.FeaturePersistence.Load(str(SETTINGS), camera.GetNodeMap(), True)

            ''' "Reliable" software triggers for the camera that actually just throw a timeout
            camera.TriggerSelector.Value = "FrameStart"
            camera.TriggerMode.Value = "On"
            camera.TriggerSource.Value = "Software"
            #'''

            camera.StartGrabbing(pylon.GrabStrategy_OneByOne)

            # The function variables are for user convenience and should be translated
            lastGrab = round(-(duration // -grabInterval))
            grabCounter = 0
            failCounter = 0

            # Loop grabbing and saving
            while grabCounter <= lastGrab:
                # "Reliable" trigger
                #camera.ExecuteSoftwareTrigger()

                # Grab frame
                with camera.RetrieveResult(round(2000 * grabInterval), pylon.TimeoutHandling_ThrowException) as result:
                    if result.GrabSucceeded():
                        # Save the image
                        image = pylon.PylonImage()
                        image.AttachGrabResultBuffer(result)
                        image.Save(pylon.ImageFileFormat_Tiff, str(path / f"grab{grabCounter}.tiff"))
                        image.Release()
                    else:
                        # Print the error
                        print(f"Frame {grabCounter}: grab failed: {result.ErrorCode}")
                        print(result.ErrorDescription)
                        failCounter += 1
                # Wait to grab the next image (if necessary)
                if grabCounter != lastGrab:
                    await anyio.sleep(grabInterval)
                grabCounter += 1
        finally:
            camera.StopGrabbing()
    return lastGrab - failCounter + 1, lastGrab + 1


@app.get("/")
async def root() -> dict:
    return {"Capycam": "dormant"}


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


@app.get("/snap")
async def snap(request: Request) -> dict:
    """Take a picture and return its URL"""
    IMAGES.mkdir(exist_ok=True)
    name = f"{uuid.uuid4().hex}.tiff"
    try:
        await anyio.to_thread.run_sync(grab, IMAGES / name)
    except (genicam.GenericException, RuntimeError) as exc:
        raise HTTPException(503, str(exc)) from exc
    return {"name": name, "url": str(request.url_for("image", name=name))}


@app.get("/timelapse/")
async def timelapse(name: str="temp", duration: int=10, grabInterval: float=5.0):
    '''Make a *new* folder, then initiate a timelapse. Queries appreciated'''
    IMAGES.mkdir(exist_ok=True)
    newFolder = IMAGES / name
    try:
        newFolder.mkdir(exist_ok=False)
        status = await takeTimelapse(newFolder, duration, grabInterval)
    except FileExistsError as e:
        raise HTTPException(403, str(e))
    except (genicam.GenericException, RuntimeError) as exc:
        raise HTTPException(503, str(exc)) from exc
    return {
        "name": name,
        "duration": f"{duration} s",
        "grabInterval": f"{grabInterval} s",
        "status": f"{status[0]} out of {status[1]} grabs succeeded"
    }


@app.get("/image/{name}")
async def image(name: str) -> FileResponse:
    #path = IMAGES / Path(name).name
    path = IMAGES / name
    if not path.is_file():
        raise HTTPException(404, f"no such image {name}")
    return FileResponse(path, media_type="image/tiff")


@app.get("/image/{folder}/{name}")
async def imageFromFolder(folder: str, name: str) -> FileResponse:
    path = IMAGES / folder / name
    if not path.is_file():
        raise HTTPException(404, f"no such image {folder}/{name}")
    return FileResponse(path, media_type="image/tiff")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
