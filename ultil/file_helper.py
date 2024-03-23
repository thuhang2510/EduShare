import os

def save(files, path):
    for f in files:
        f.save(os.path.join(path))
        f.close()

    return os.path.join(path)