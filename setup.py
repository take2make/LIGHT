import setuptools

setuptools.setup(
    name="light", # Replace with your own username
    version="0.0.1",
    author="take2make",
    author_email="lutixalex1998@gmail.com",
    description="package for find times of lbol",
    long_description_content_type="text/markdown",
    packages=['light_curve','light_curve/calculate'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    entry_points={
    'console_scripts': [
        'light=light_curve:parsing',
        ],
    },
    install_requires=[
        'matplotlib',
        'numpy'
    ]
)
