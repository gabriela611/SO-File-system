from setuptools import setup, find_packages

setup(
    name="so-file-system",
    version="26.3.5",
    author="TuNombre",
    author_email="tunombre@correo.com",
    description="Un sistema de archivos versionado con Copy-on-Write en Python.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/TuUsuario/so-file-system",  # Opcional, tu repo
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "tqdm",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)