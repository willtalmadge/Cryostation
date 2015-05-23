from setuptools import setup

setup(name='cryostation',
      version='0.1',
      description='A library for communicating with a Montana Instruments Cryostation',
      url='https://github.com/willtalmadge/Cryostation',
      author='William Talmadge',
      author_email='willtalmadge@gmail.com',
      license='MIT',
      packages=[
          'cryostation',
          'cryostation.rx'
      ],
      install_requires=[
            'rx',
            'numpy'
      ],
      zip_safe=False)