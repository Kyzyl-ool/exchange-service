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
        "victor.algorithm.filter",
        "victor.algorithm.momentum",
        "victor.algorithm.momentum.bar_rotation",
        "victor.algorithm.momentum.breakout",
        "victor.algorithm.momentum.complex",
        "victor.algorithm.momentum.RSI",
        "victor.generators.generator",
        "victor.backtest",
        "victor.backtest.configs",
        "victor.config",
        "victor.exchange",
        "victor.exchange.abstract",
        "victor.exchange.finam_test",
        "victor.exchange.tinkoff",
        "victor.exchange.types",
        "victor.generators",
        "victor.generators.generator",
        "victor.generators.generator.candle",
        "victor.generators.generator.filters",
        "victor.generators.generator.patterns",
        "victor.generators.generator.technical_indicators",
        "victor.risk_management",
        "victor.risk_management.classic",
        "victor.risk_management.momentum",
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
        "tqdm"
    ],
)