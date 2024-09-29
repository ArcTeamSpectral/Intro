import modal

TRAINING_CHECKPOINTS_VOLUME = modal.Volume.from_name("training-checkpoints", create_if_missing=True)
