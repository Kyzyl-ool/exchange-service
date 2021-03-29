from distutils.core import setup

setup(
    # Application name:
    name="victor",

    # Version number (initial):
    version="0.1.1",

    # Application author details:
    author="Kyzyl-ool Kezhik",
    author_email="kyzyloolk@mail.ru",

    # Packages
    packages=[
        "victor.algorithm",
        "victor.backtest",
        "victor.config",
        "victor.exchange",
        "victor.generators",
        "victor.risk_management",
        "victor.trader",
    ],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="https://github.com/Kyzyl-ool/exchange-service",

    #
    # license="LICENSE.txt",
    description="Useful towel-related stuff.",

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[
        "flask",
        "pandas",
        "matplotlib",
        "numpy",
        "tqdm",
        "wheel"
    ],
)