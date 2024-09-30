import os
import modal
import signal
import subprocess
from .images import NOTEBOOK_IMAGE
from .volumes import TRAINING_CHECKPOINTS_VOLUME

app = modal.App(
    "notebook", image=NOTEBOOK_IMAGE.env({"HF_HOME": "/zenith/huggingface"})
)

# a password for the jupyter server
JUPYTER_TOKEN = "friend"


@app.function(volumes={"/zenith": TRAINING_CHECKPOINTS_VOLUME})
def seed_volume():
    # Bing it!
    from bing_image_downloader import downloader

    # Check if the sample_images directory exists and has more than 5 files
    sample_images_dir = "/zenith/sample_images/modal labs"
    if os.path.exists(sample_images_dir) and len(os.listdir(sample_images_dir)) > 5:
        print("Sample images already exist. Skipping download.")
        return

    # This will save into the Modal volume and allow you view the images
    # from within Jupyter at a path like `/root/cache/modal labs/Image_1.png`.
    downloader.download(
        query="modal labs",
        limit=10,
        output_dir="/zenith/sample_images",
        force_replace=False,
        timeout=60,
        verbose=True,
    )
    TRAINING_CHECKPOINTS_VOLUME.commit()


from modal import Dict
from datetime import datetime

notebook_registry = Dict.from_name("notebook-registry", create_if_missing=True)


def register_notebook(notebook_id: str) -> None:
    notebook_registry[notebook_id] = {
        "created_at": datetime.now(),
    }


def need_to_delete_notebook(notebook_id: str) -> bool:
    return notebook_id not in notebook_registry


def delete_notebook(notebook_id: str) -> bool:
    if notebook_id in notebook_registry:
        del notebook_registry[notebook_id]
        return True
    return False


def start_monitoring_disk_space(interval: int = 30) -> None:
    """Start monitoring the disk space in a separate thread."""
    import sys
    import threading
    import time

    task_id = os.environ["MODAL_TASK_ID"]

    def log_disk_space(interval: int) -> None:
        while True:
            statvfs = os.statvfs("/")
            free_space = statvfs.f_frsize * statvfs.f_bavail
            print(
                f"{task_id} free disk space: {free_space / (1024 ** 3):.2f} GB",
                file=sys.stderr,
            )
            time.sleep(interval)

    monitoring_thread = threading.Thread(target=log_disk_space, args=(interval,))
    monitoring_thread.daemon = True
    monitoring_thread.start()


# This is all that's needed to create a long-lived Jupyter server process in Modal
# that you can access in your Browser through a secure network tunnel.
# This can be useful when you want to interactively engage with Volume contents
# without having to download it to your host computer.


def run_jupyter_actually(q: modal.Queue):
    import os
    import subprocess
    import secrets

    # Print the value of HF_HOME environment variable
    print("HF_HOME:", os.environ.get("HF_HOME", "Not set"))

    # Create /zenith/notebooks directory if it doesn't exist
    notebooks_dir = "/zenith/notebooks"
    if not os.path.exists(notebooks_dir):
        os.makedirs(notebooks_dir)
        print(f"Created directory: {notebooks_dir}")
    else:
        print(f"Directory already exists: {notebooks_dir}")

    jupyter_port = 8888
    with modal.forward(jupyter_port) as tunnel:
        token = secrets.token_urlsafe(13)
        url = tunnel.url + "/?token=" + token
        print(f"Starting Jupyter at {url}")
        q.put(url)

        register_notebook(url)

        jupyter_process = subprocess.Popen(
            [
                "jupyter",
                "notebook",
                "--no-browser",
                "--allow-root",
                "--ip=0.0.0.0",
                "--notebook-dir=/zenith/notebooks",
                f"--port={jupyter_port}",
                "--NotebookApp.allow_origin='*'",
                "--NotebookApp.allow_remote_access=1",
            ],
            env={**os.environ, "JUPYTER_TOKEN": token},
        )

        import time

        while True:
            time.sleep(1)
            print("Checking if need to delete notebook at", url)
            if need_to_delete_notebook(url):
                print(f"Deleting Jupyter process at {url}...")
                jupyter_process.terminate()  # Terminate the process
                jupyter_process.wait()  # Wait for the process to finish
                print(f"Jupyter process at {url} has been terminated.")
                return  # Exit the function to prevent restart


@app.function(
    concurrency_limit=1,
    volumes={"/zenith": TRAINING_CHECKPOINTS_VOLUME},
    timeout=900,
)
def cpu_notebook(q: modal.Queue):
    return run_jupyter_actually(q)


@app.function(
    concurrency_limit=1,
    volumes={"/zenith": TRAINING_CHECKPOINTS_VOLUME},
    timeout=900,
    gpu="t4",
)
def gpu_notebook(q: modal.Queue):
    return run_jupyter_actually(q)


@app.function(
    concurrency_limit=1,
    volumes={"/zenith": TRAINING_CHECKPOINTS_VOLUME},
    timeout=900,
    gpu="a10g",
)
def a10g_notebook(q: modal.Queue):
    return run_jupyter_actually(q)


@app.function(
    concurrency_limit=1,
    volumes={"/zenith": TRAINING_CHECKPOINTS_VOLUME},
    timeout=900,
    gpu="a100",
)
def a100_notebook(q: modal.Queue):
    return run_jupyter_actually(q)


from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

auth_scheme = HTTPBearer()


@app.function(secrets=[modal.Secret.from_name("my-custom-secret")])
@modal.web_endpoint(method="POST")
async def stop(
    request: Request, token: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    print(os.environ["SECRET_PASSPHRASE_AUTH_TOKEN"])
    print(token.credentials)
    is_valid = token.credentials == os.environ["SECRET_PASSPHRASE_AUTH_TOKEN"]

    if is_valid:
        # Read the notebook_url from the request body
        request_data = await request.json()
        notebook_url = request_data.get("notebook_url")

        if not notebook_url:
            raise HTTPException(400, "notebook_url is required")

        print(f"Attempting to delete notebook at URL: {notebook_url}")

        # Call the function to delete the notebook
        deleted = delete_notebook(notebook_url)

        if deleted:
            return {
                "message": f"Notebook at {notebook_url} is marked for deletion",
                "code": 0,
            }
        else:
            raise {"message": f"No active notebook found at {notebook_url}", "code": 1}
    else:
        raise HTTPException(401, "Not authenticated")


@app.function(secrets=[modal.Secret.from_name("my-custom-secret")])
@modal.web_endpoint(method="POST")
async def start(
    request: Request, token: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    print(os.environ["SECRET_PASSPHRASE_AUTH_TOKEN"])
    print(token.credentials)
    is_valid = token.credentials == os.environ["SECRET_PASSPHRASE_AUTH_TOKEN"]

    if is_valid:
        # Read the gpu_type from the request body
        request_data = await request.json()
        gpu_type = request_data.get("gpu_type")
        print("Starting notebook with gpu_type:", gpu_type)

        with modal.Queue.ephemeral() as q:
            if gpu_type is None:
                cpu_notebook.spawn(q)
            elif gpu_type == "t4":
                gpu_notebook.spawn(q)
            elif gpu_type == "a100":
                a100_notebook.spawn(q)
            elif gpu_type == "a10g":
                a10g_notebook.spawn(q)

            url = q.get()
            print("Got URL:", url)
            return {"url": url, "gpu_type": gpu_type}

    else:
        raise HTTPException(401, "Not authenticated")


@app.function()
@modal.web_endpoint(method="GET")
def index():
    return {"message": "To start a notebook, make a POST request to this endpoint."}
