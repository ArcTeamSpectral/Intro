import modal

BASE_IMAGE = (
    modal.Image.from_registry("nvidia/cuda:12.1.0-base-ubuntu22.04", add_python="3.10")
    .apt_install("tree")
    .pip_install("lightning", "torchvision")
    .pip_install("transformers", "pillow")
    .pip_install("bing-image-downloader", "jupyter")
    .pip_install("diffusers", "sentencepiece", "accelerate")
)
