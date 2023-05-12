from setuptools import setup, find_packages
 
setup(name='sf2',
    version='2.0.0',
    url='https://github.com/laulin/sf2',
    license='MIT',
    author='Laurent MOULIN',
    author_email='gignops@gmail.com',
    description='Share and work in team your files in full safety thanks to SSH keys.',
    packages=find_packages(exclude=['test', "etc", "build", "dist", "sf2.egg-info", "bin"]),
    install_requires=["cryptography", "inotify", "msgpack", "flufl.lock", "password-validator", "pyyaml", "pywebio", "pywebview"],
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    zip_safe=False,
    classifiers=[
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: MIT License",
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