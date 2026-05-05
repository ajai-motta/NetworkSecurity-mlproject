from setuptools import find_packages,setup
from typing import List
def get_requirements(file_path: str) -> List[str]:
    """
    This function returns a list of requirements
    from requirements.txt file.
    """
    requirements = []

    try:
        with open(file_path, "r") as file:
            lines = file.readlines()

            for line in lines:
                req = line.strip()

                # Ignore empty lines and comments
                if req and not req.startswith("#"):
                    # Remove editable installs (-e .)
                    if req == "-e .":
                        continue

                    requirements.append(req)

    except FileNotFoundError:
        raise FileNotFoundError(f"{file_path} not found")

    return requirements

setup(
    name='networksecurity',
    version='0.0.1',
    author='Ajai',
    author_email='ajayjoseo8@gmail.com',
    packages=find_packages(),
    install_requires=get_requirements('requirements.txt'),

)