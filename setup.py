from setuptools import setup, find_packages

setup(
    name='gym_pikachu_volleyball',
    version='0.1.0',
    author="Hoseong Lee",
    author_email="leehs.git@gmail.com",
    install_requires=[
        "gym >= 0.25.0",
        "pygame >= 2.1.2",
    ],
    description="An openai-gym wrapper for pikachu-volleyball",
    url="https://github.com/HoseongLee/gym-pikachu-volleyball",
    packages=find_packages(),
    include_package_data=True,
    zip_safe = False
)
