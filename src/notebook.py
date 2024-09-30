import modal
from .images import NOTEBOOK_IMAGE
from .volumes import TRAINING_CHECKPOINTS_VOLUME

app = modal.App(
    "notebook", image=NOTEBOOK_IMAGE.env({"HF_HOME": "/zenith/huggingface"})
)

# Create a persisted queue - the data gets retained between app runs
notebook_registry = modal.Dict.from_name("notebook-registry", create_if_missing=True)

CPU = 4.0
GPU = None
TIMEOUT_HOURS = 2  # max timeout is 24 hours
TIMEOUT = TIMEOUT_HOURS * 60 * 60


@app.function(volumes={"/zenith": TRAINING_CHECKPOINTS_VOLUME})
def seed_volume():
    # Bing it!
    from bing_image_downloader import downloader

    import os

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


def start_monitoring_cpu_utilization(interval: int = 30) -> None:
    """Start monitoring the CPU utilization in a separate thread."""
    import os
    import sys
    import threading
    import time
    import psutil

    task_id = os.environ["MODAL_TASK_ID"]

    def log_cpu_utilization(interval: int) -> None:
        while True:
            cpu_percent = psutil.cpu_percent(interval=1)
            print(
                f"{task_id} CPU utilization: {cpu_percent:.2f}%",
                file=sys.stderr,
            )
            time.sleep(interval)

    monitoring_thread = threading.Thread(target=log_cpu_utilization, args=(interval,))
    monitoring_thread.daemon = True
    monitoring_thread.start()


# This is all that's needed to create a long-lived Jupyter server process in Modal
# that you can access in your Browser through a secure network tunnel.
# This can be useful when you want to interactively engage with Volume contents
# without having to download it to your host computer.


@app.function(
    concurrency_limit=1,
    volumes={"/zenith": TRAINING_CHECKPOINTS_VOLUME},
    cpu=CPU,
    gpu=GPU,
    timeout=TIMEOUT,
)
def run_jupyter():
    import os
    import subprocess
    import time
    import secrets
    from datetime import datetime

    start_monitoring_cpu_utilization()

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

        print(f"Jupyter available at => {url}")
        notebook_registry[url] = {
            "created_at": datetime.now().isoformat(),
        }

        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            print("Exiting...")
        finally:
            jupyter_process.kill()
            del notebook_registry[url]


@app.local_entrypoint()
def main():
    # Write some images to a volume, for demonstration purposes.
    seed_volume.remote()
    # Run the Jupyter Notebook server
    run_jupyter.remote()
