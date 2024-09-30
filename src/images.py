import modal

BASE_IMAGE = (
    modal.Image.from_registry("nvidia/cuda:12.1.0-base-ubuntu22.04", add_python="3.10")
    .apt_install("tree")
    .pip_install("lightning", "torchvision")
    .pip_install("transformers", "pillow")
    .pip_install("bing-image-downloader", "jupyter")
)

NOTEBOOK_IMAGE = (
    BASE_IMAGE.apt_install(
        "git", "wget", "curl", "htop", "vim", "tmux", "unzip", "tar", "gzip", "bzip2"
    )
    .pip_install(
        "numpy",
        "pandas",
        "matplotlib",
        "scikit-learn",
        "tensorflow",
        "keras",
        "opencv-python",
        "scipy",
        "seaborn",
        "openai",
        "tiktoken",
        "datasets",
        "transformers",
        "diffusers",
        "sentencepiece",
        "accelerate",
    )
    .pip_install("peft", "bitsandbytes", "trl")
)

setup_commands = [
    "git clone https://github.com/fchollet/ARC-AGI.git",
    "echo 'ready to go!'",
]
ARC_IMAGE = NOTEBOOK_IMAGE.run_commands(setup_commands)
