'''
Take pictures with a Basler camera over HTTP.

Launch with:

    uv run capycam.py                    # http://127.0.0.1:8000
    PYLON_CAMEMU=1 uv run capycam.py     # emulated camera, no hardware needed
    # be warned: software triggers don't work on an emulated camera, so will cause a timeout

/snap returns a URL rather than image bytes: it is called from Temporal activities, whose
results go into the workflow history and are size limited.

This program uses the headless version of OpenCV, which cannot make pop-up windows. I am sorry,
but I was having trouble with the normal version. Commands such as cv2.destroyAllWindows() or
any command that generates a window with OpenCV do not work and will raise an error.

Camera settings (exposure, gain, ROI, pixel format, auto functions off, ...) are not route
parameters. Can tune them in pylon Viewer, save the features file next to this script as
capycam.pfs, and every grab will use them.
'''
# Utility
import uuid
from pathlib import Path
# Web app
import anyio
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import FileResponse
# Camera
from pypylon import genicam, pylon
import cv2

IMAGES = Path("capycam_images")
SETTINGS = Path(__file__).with_name("capycam.pfs")
app = FastAPI(title="capycam")


def grab(path: Path) -> None:
    """Open the camera, grab one frame, write it to path, close again.

    Saved as TIFF in the sensor's native pixel format: lossless, and it keeps
    the full bit depth of a 12- or 16-bit mono camera. Matt coded this function,
    so it looks a bit different
    """
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    # Open camera to access settings
    camera.Open()
    try:
        # Take settings from file
        if SETTINGS.is_file():
            # validate=True: fail loudly rather than shoot with half the
            # settings applied, which would silently spoil a run.
            pylon.FeaturePersistence.Load(str(SETTINGS), camera.GetNodeMap(), True)
        
        camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

        # Grab frame
        result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        if not result.GrabSucceeded():
            # Throw error
            raise RuntimeError(f"grab failed: {result.ErrorDescription}")
        else:
            # Save image
            image = pylon.PylonImage()
            image.AttachGrabResultBuffer(result)
            image.Save(pylon.ImageFileFormat_Tiff, str(path))
            # Release resources
            image.Release()
        result.Release()
    finally:
        camera.StopGrabbing()
        camera.Close()


async def takeTimelapse(path: Path, duration: int, grabInterval: float) -> None:
    """Open the camera, grab frames regularly over a time period, save them, close.
    
    The inputted path should be a directory.
    Error catching must stop grabbing and close the camera afterwards.
    """
    with pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice()) as camera:
        # Open camera to access settings
        camera.Open()
        try:
            # Take settings from file
            if SETTINGS.is_file():
                # validate=True: fail loudly rather than shoot with half the
                # settings applied, which would silently spoil a run.
                pylon.FeaturePersistence.Load(str(SETTINGS), camera.GetNodeMap(), True)

            #''' Reliable software triggers for the camera - throws timeout on emulation
            camera.TriggerSelector.Value = "FrameStart"
            camera.TriggerMode.Value = "On"
            camera.TriggerSource.Value = "Software"
            #'''

            camera.StartGrabbing(pylon.GrabStrategy_OneByOne)

            # Create some new variables for frame tracking
            lastGrab = round(-(duration // -grabInterval))
            grabCounter = 0
            failCounter = 0

            # Loop grabbing and saving
            while grabCounter <= lastGrab:
                # Reliable trigger
                camera.ExecuteSoftwareTrigger()

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
            print(f"Timelapse finished with {'no' if failCounter == 0 else failCounter} errors.")


async def takeVideo(path: Path, duration: int, grabInterval: float, playbackFPS: int) -> None:
    """Open the camera, grab frames at the specified interval, save them to video, close
    
    path is the name of the video file"""

    with pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice()) as camera:
        # Open camera to access settings
        camera.Open()

        # OpenCV uses BGR images
        converter = pylon.ImageFormatConverter()
        converter.OutputPixelFormat = pylon.PixelType_BGR8packed

        try:
            # Take settings from file
            if SETTINGS.is_file():
                # validate=True: fail loudly rather than shoot with half the
                # settings applied, which would silently spoil a run.
                pylon.FeaturePersistence.Load(str(SETTINGS), camera.GetNodeMap(), True)

            # Get camera frame dimensions - could be changed by settings
            frame_width = camera.Width.Value
            frame_height = camera.Height.Value
            # Create a video writer
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(str(path), fourcc, playbackFPS, (frame_width, frame_height))
            if not out.isOpened():
                raise RuntimeError(f"Could not open video writer: {path}")

            #''' Reliable software triggers for the camera - throws timeout on emulation
            camera.TriggerSelector.Value = "FrameStart"
            camera.TriggerMode.Value = "On"
            camera.TriggerSource.Value = "Software"
            #'''

            camera.StartGrabbing(pylon.GrabStrategy_OneByOne)

            # Create some new variables for frame tracking
            lastGrab = round(-(duration // -grabInterval))
            grabCounter = 0
            failCounter = 0

            # Loop grabbing and saving
            while grabCounter <= lastGrab:
                # Reliable trigger
                camera.ExecuteSoftwareTrigger()

                # Grab frame
                with camera.RetrieveResult(round(2000 * grabInterval), pylon.TimeoutHandling_ThrowException) as result:
                    if result.GrabSucceeded():
                        # Convert the image and write it to the video
                        image = converter.ConvertToArray(result.GetFirstImageDataComponent())
                        out.write(image)
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
            # Necessary clean-up
            camera.StopGrabbing()
            out.release()
            print(f"Video capture finished with {'no' if failCounter == 0 else failCounter} errors.")


@app.get("/")
async def root() -> dict:
    """Check the app is running"""
    return {"Capycam": "dormant"}


@app.get("/ready")
async def ready() -> dict:
    """Grab and discard a frame: a camera that opens may still not grab"""
    IMAGES.mkdir(exist_ok=True)
    try:
        await anyio.to_thread.run_sync(grab, IMAGES / "ready.tiff")
    except (genicam.GenericException, RuntimeError) as exc:
        return {"ready": False, "detail": str(exc)}
    return {
        "ready": True,
        "detail": "camera open and grabbing",
        "settings": str(SETTINGS) if SETTINGS.is_file() else None
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
async def timelapse(background_tasks: BackgroundTasks, name: str="temp", duration: int=60, grabInterval: float=5.0):
    """Make a *new* folder, then initiate a timelapse. Queries appreciated"""
    IMAGES.mkdir(exist_ok=True)
    newFolder = IMAGES / name
    # error checking
    if duration < 0:
        return {"name": name, "status": f"failed to start: duration must be non-negative (got {duration})"}
    if grabInterval <= 0:
        return {"name": name, "status": f"failed to start: grabInterval must be positive (got {grabInterval})"}

    try:
        newFolder.mkdir(exist_ok=False)
    except FileExistsError as e:
        raise HTTPException(403, str(e))

    # This prevents browser time-outs
    background_tasks.add_task(takeTimelapse, newFolder, duration, grabInterval)

    return {"name": name, "duration": f"{duration} s", "grabInterval": f"{grabInterval} s", "status": "started successfully"}


@app.get("/video/")
async def video(background_tasks: BackgroundTasks, path: str="temp.mp4",
                duration: int=60, grabInterval: float=5.0, playbackFPS: int=6) -> dict:
    """Initiate a video recording. Queries appreciated"""
    IMAGES.mkdir(exist_ok=True)

    path = Path(path)
    # error checking on path: needs to be .mp4 - two options available
    if path.suffix != ".mp4":
        path = path.with_suffix(".mp4")
        #return {"name": path, "status": "failed to start: invalid file extension"}
    # error checking
    if duration < 0:
        return {"name": path, "status": f"failed to start: duration must be non-negative (got {duration})"}
    if grabInterval <= 0:
        return {"name": path, "status": f"failed to start: grabInterval must be positive (got {grabInterval})"}
    if playbackFPS <= 0:
        return {"name": path, "status": f"failed to start: playbackFPS must be positive (got {playbackFPS})"}

    background_tasks.add_task(takeVideo, IMAGES / path, duration, grabInterval, playbackFPS)

    return {"name": path, "duration": f"{duration} s", "grabInterval": f"{grabInterval} s",
            "playbackFPS": f"{playbackFPS} fps", "status": "started successfully"}


@app.get("/image/{name}")
async def image(name: str) -> FileResponse:
    """Return a download prompt for an image"""
    path = IMAGES / name
    if not path.is_file():
        raise HTTPException(404, f"no such image {name}")
    return FileResponse(path, media_type="image/tiff")


@app.get("/image/{folder}/{name}")
async def imageFromFolder(folder: str, name: str) -> FileResponse:
    """Return a download prompt for an image in a folder"""
    path = IMAGES / folder / name
    if not path.is_file():
        raise HTTPException(404, f"no such image {folder}/{name}")
    return FileResponse(path, media_type="image/tiff")


# Run the app - DO NOT TOUCH
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)