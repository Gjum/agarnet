try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='agarnet',
      packages=['agarnet'],
      py_modules=['agarnet'],
      version='0.2.1',
      description='agar.io client and connection toolkit',
      install_requires=['websocket-client>=0.32.0'],
      author='Gjum',
      author_email='code.gjum@gmail.com',
      url='https://github.com/Gjum/agarnet',
      license='GPLv3',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Education',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Topic :: Education',
          'Topic :: Games/Entertainment',
      ],
)
