import pandas as pd

def load_schema(path):
    df = pd.read_excel(path)

    schema = {}
    fks = {}

    for _, r in df.iterrows():
        t = r["Table Name"]
        c = r["Column Name"]
        k = str(r.get("Key", "")).lower()

        if t not in schema:
            schema[t] = {"columns": [], "pk": None, "fks": {}}

        schema[t]["columns"].append(c)

        if "pk" in k:
            schema[t]["pk"] = c
        if "fk" in k:
            ref = r["References"]     # e.g patient.id
            parent, col = ref.split(".")
            schema[t]["fks"][c] = parent

    return schema
