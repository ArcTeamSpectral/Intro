import modal
from .images import BASE_IMAGE
from .volumes import TRAINING_CHECKPOINTS_VOLUME

app = modal.App("notebook", image=BASE_IMAGE.env({"HF_HOME": "/zenith/huggingface"}))

# a password for the jupyter server
JUPYTER_TOKEN = "friend"


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


def start_monitoring_disk_space(interval: int = 30) -> None:
    """Start monitoring the disk space in a separate thread."""
    import os
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


@app.function(
    concurrency_limit=1, volumes={"/zenith": TRAINING_CHECKPOINTS_VOLUME}, timeout=1_500, gpu="A10G"
)
def run_jupyter(timeout: int):
    import os
    import subprocess
    import time

    start_monitoring_disk_space()

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
            env={**os.environ, "JUPYTER_TOKEN": JUPYTER_TOKEN},
        )

        print(f"Jupyter available at => {tunnel.url}")

        try:
            end_time = time.time() + timeout
            while time.time() < end_time:
                time.sleep(5)
            print(f"Reached end of {timeout} second timeout period. Exiting...")
        except KeyboardInterrupt:
            print("Exiting...")
        finally:
            jupyter_process.kill()


@app.local_entrypoint()
def main(timeout: int = 10_000):
    # Write some images to a volume, for demonstration purposes.
    seed_volume.remote()
    # Run the Jupyter Notebook server
    run_jupyter.remote(timeout=timeout)
