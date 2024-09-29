import os

import modal

app = modal.App("interrupt-resume-lightning")
image = modal.Image.from_registry(
    "nvidia/cuda:12.1.0-base-ubuntu22.04", add_python="3.10"
).pip_install("lightning", "torchvision")

volume = modal.Volume.from_name("training-checkpoints", create_if_missing=True)

VOLUME_PATH = "/vol"
DATA_PATH = f"{VOLUME_PATH}/data"
CHECKPOINTS_PATH = f"{VOLUME_PATH}/checkpoints"

def get_checkpoint(checkpoint_dir):
    from lightning.pytorch.callbacks import ModelCheckpoint

    return ModelCheckpoint(
        dirpath=checkpoint_dir,
        save_last=True,
        every_n_epochs=10,
        filename="epoch{epoch:02d}",
    )


def train_model(data_dir, checkpoint_dir, resume_from_checkpoint=None):
    import lightning as L

    from .train import get_autoencoder, get_train_loader

    # train the model (hint: here are some helpful Trainer arguments for rapid idea iteration)
    autoencoder = get_autoencoder()
    train_loader = get_train_loader(data_dir=data_dir)
    checkpoint_callback = get_checkpoint(checkpoint_dir)
    trainer = L.Trainer(
        limit_train_batches=100, max_epochs=100, callbacks=[checkpoint_callback]
    )
    if resume_from_checkpoint:
        print(f"Resuming from checkpoint: {resume_from_checkpoint}")
        trainer.fit(
            model=autoencoder,
            train_dataloaders=train_loader,
            ckpt_path=resume_from_checkpoint,
        )
    else:
        print("Starting training from scratch")
        trainer.fit(autoencoder, train_loader)
    print("Done training")
    return

@app.function(
    image=image,
    volumes={VOLUME_PATH: volume},
    gpu="any",
    timeout=30,
)
def train():
    last_checkpoint = os.path.join(CHECKPOINTS_PATH, "last.ckpt")

    try:
        if os.path.exists(last_checkpoint):
            # Resume from the latest checkpoint
            print(
                f"Resuming training from the latest checkpoint: {last_checkpoint}"
            )
            train_model(
                DATA_PATH,
                CHECKPOINTS_PATH,
                resume_from_checkpoint=last_checkpoint,
            )
            print("Training resumed successfully")
        else:
            print("Starting training from scratch")
            train_model(DATA_PATH, CHECKPOINTS_PATH)
    except Exception as e:
        raise e

    return

@app.local_entrypoint()
def main():
    while True:
        try:
            print("Starting new training run")
            train.remote()

            print("Finished training")
            break  # Exit the loop if training completes successfully
        except KeyboardInterrupt:
            print("Job was preempted")
            print("Will attempt to resume in the next iteration.")
            continue
        except modal.exception.FunctionTimeoutError:
            print("Function timed out")
            print("Will attempt to resume in the next iteration.")
            continue
        except Exception as e:
            print(f"Error: {str(e)}")
            break