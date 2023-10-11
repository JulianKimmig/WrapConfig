from setuptools import setup
import config_manager

# Read the requirements from requirements.txt
with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setup(
    name="conf_manager",
    version=config_manager.__version__,
    description="Wraper to manage configurations",
    author="Julian Kimmig",
    author_email="julian.kimmig@linkdlab.de",
    packages=["config_manager"],  # Update with your package name
    install_requires=requirements,
)
