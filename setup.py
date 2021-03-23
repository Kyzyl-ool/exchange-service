from distutils.core import setup

setup(
    # Application name:
    name="exchange-service",

    # Version number (initial):
    version="0.1.0",

    # Application author details:
    author="Kyzyl-ool Kezhik",
    author_email="kyzyloolk@mail.ru",

    # Packages
    packages=[
        "src.exchange.abstract",
        "src.exchange.finam_test",
        "src.exchange.tinkoff",
        "src.exchange.types",
        "src.utils.D",
        "src.utils.trade_toolkit",
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
    ],
)