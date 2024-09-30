# Zenith Dev environment

This repo contains the code for the Zenith development environment.

## Quick Start (using my modal resources)

To get started, set the `TOKEN` environment variable to your Modal token:

```bash
export TOKEN=<your-modal-token>
```

Then, we can create a notebook with the appropriate GPU type with:

```bash
make cpu
make t4
make a100
make a10g
```

### Cleanup

To stop the notebook and clean up the resources, run:

```bash
modal container list
modal container stop <container-id>
```



## Self Deploy

If you want to use your own Modal resources, you can deploy the app with:

```bash
modal deploy src.notebook
```

This will deploy the service to start Jupyter notebook kernels. It's intended to be consumed by the VSCode extension -- right now, we simulate this by having the Makefile to make PUT requests to the endpoint.

Make sure you do the following:
1. You have a volume set up at `training-checkpoints`
2. You have a secret set up at `my-custom-secret` with the `SECRET_PASSPHRASE_AUTH_TOKEN` environment variable set to your desired auth token.

Happy coding!