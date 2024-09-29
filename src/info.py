import modal
from .volumes import TRAINING_CHECKPOINTS_VOLUME
from .images import BASE_IMAGE

app = modal.App("info")


@app.function(
    image=BASE_IMAGE.env({"HF_HOME": "/zenith/huggingface"}),
    volumes={"/zenith": TRAINING_CHECKPOINTS_VOLUME},
)
def info():
    import os
    import subprocess

    print("Operating System:", os.name)
    print("\nContents of PATH:")
    for path in os.environ["PATH"].split(os.pathsep):
        print(path)

    print("Contents of /zenith:")
    result = subprocess.run(["tree", "/zenith"], capture_output=True, text=True)
    print(result.stdout)


def download_puppy_image():
    import requests
    import os

    # URL of the image
    image_url = "https://hgtvhome.sndimg.com/content/dam/images/hgtv/fullset/2018/3/22/0/shutterstock_national-puppy-day-224423782.jpg.rend.hgtvcom.616.462.suffix/1521744674350.jpeg"

    # Define the path where the image will be saved
    save_path = "/zenith/puppy.jpg"

    # Download the image
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(save_path, "wb") as file:
            file.write(response.content)
        print(f"Image downloaded and saved to {save_path}")
    else:
        print("Failed to download the image")

    # Verify the file exists
    if os.path.exists(save_path):
        print(f"File size: {os.path.getsize(save_path)} bytes")
    else:
        print("File does not exist")


@app.function(
    image=BASE_IMAGE.env({"HF_HOME": "/zenith/huggingface"}),
    volumes={"/zenith": TRAINING_CHECKPOINTS_VOLUME},
)
def download_clip():
    print("Downloading CLIP model...")
    import torch
    from PIL import Image
    from transformers import CLIPProcessor, CLIPModel

    class CLIP:
        def __init__(self):
            # Load the CLIP model and processor
            self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.processor = CLIPProcessor.from_pretrained(
                "openai/clip-vit-base-patch32"
            )

        def encode_image(self, image_path):
            # Load and preprocess the image
            image = Image.open(image_path)
            inputs = self.processor(images=image, return_tensors="pt")

            # Generate the image features
            with torch.no_grad():
                image_features = self.model.get_image_features(**inputs)

            return image_features

        def encode_text(self, text):
            inputs = self.processor(text=text, return_tensors="pt")
            with torch.no_grad():
                text_features = self.model.get_text_features(**inputs)
            return text_features

    download_puppy_image()
    myclip = CLIP()
    print("CLIP model downloaded.")
    image_path = "/zenith/puppy.jpg"
    features = myclip.encode_image(image_path)
    print(features.shape)  # Should be [1, 512] for the base model
