import modal
from .notebook import notebook_registry

app = modal.App("notebook")


@app.function()
@modal.web_endpoint()
def get_notebooks():
    for t in notebook_registry.items():
        print(t)
    return {"notebooks": dict(notebook_registry)}
