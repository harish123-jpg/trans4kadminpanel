import os
from setuptools import setup
from Cython.Build import cythonize

SKIP_DIRS = {
    "migrations",
    "__pycache__",
    "venv",
    "ENV",
    "dist",
    "build",
    ".git",
}

SKIP_FILES = {
    "manage.py",
    "setup.py",
    "settings.py",
}

def collect_py_files():
    all_files = []

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for file in files:
            if not file.endswith(".py"):
                continue

            if file in SKIP_FILES:
                continue

            if file == "__init__.py":
                continue

            filepath = os.path.join(root, file)

            if filepath.startswith("./"):
                filepath = filepath[2:]

            filepath = filepath.replace("\\", "/")
            all_files.append(filepath)

    return sorted(all_files)

py_files = collect_py_files()

print(f"\nTotal files to compile: {len(py_files)}\n")
for f in py_files:
    print(f)

setup(
    ext_modules=cythonize(
        py_files,
        compiler_directives={
            "language_level": "3"
        },
        nthreads=4,
        quiet=False,
    )
)