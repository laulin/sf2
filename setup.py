from setuptools import setup, find_packages
 
setup(name='sf2',
    version='1.0.0',
    url='',
    license='Apachev2',
    author='Laurent MOULIN',
    author_email='gignops@gmail.com',
    description='Encrypt and decrypt your file with Fernet algorithm',
    packages=find_packages(exclude=['tests', "etc", "build", "dist", "sf2.egg-info"]),
    install_requires=["cryptography", "dearpygui"],
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    zip_safe=False,
    classifiers=[
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: Apache Software License",
      "Operating System :: OS Independent",
      "Development Status :: 5 - Production/Stable",
      "Intended Audience :: Information Technology",
      "Topic :: Security :: Cryptography"
    ],
    python_requires='>=3',
      entry_points={
            'console_scripts': [ 
            'sf2 = sf2.sf2:main' 
            ] 
      }
)