import modal

from .images import BASE_IMAGE

app = modal.App("nvidia_smi", image=BASE_IMAGE)


@app.function(gpu="A10G")
def nvidia_smi():
    import subprocess

    output = subprocess.check_output(["nvidia-smi"])
    print(output.decode('utf-8'))
    return output
