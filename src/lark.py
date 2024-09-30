import modal

app = modal.App("lark")


# Create a persisted dict - the data gets retained between app runs
my_dict = modal.Dict.from_name("my-persisted-dict", create_if_missing=True)


@app.function()
def hello():
    print(my_dict["A"])
    my_dict["A"] = 20
    print(my_dict["A"])
    return "Hello, World!"


@app.local_entrypoint()
def main():
    my_dict["A"] = 10
    hello.remote()
    print("After calling hello:", my_dict["A"])
