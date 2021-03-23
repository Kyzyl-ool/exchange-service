from distutils.core import setup, Extension

setup(
    # Application name:
    name="victor",

    # Version number (initial):
    version="0.1.0",

    # Application author details:
    author="Kyzyl-ool Kezhik",
    author_email="kyzyloolk@mail.ru",

    # Packages
    packages=[
        "victor.exchange.abstract",
        "victor.exchange.finam_test",
        "victor.exchange.tinkoff",
        "victor.exchange.types",
        "victor.utils.D",
        "victor.utils.trade_toolkit",
        "victor.generators",
        "victor.generators.generator",
        "victor.generators.generator.technical_indicators",
        "victor.generators.generator_family",
        "victor.generators.generator_set",
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
        "tqdm"
    ],
)