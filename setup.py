from distutils.core import setup
import os

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)


for dirpath, dirnames, filenames in os.walk('imageservice'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)

setup(name='django-imagemagick',
      version='0.1.1',
      description='Adds the possibility to scale images on server side using imagemagick',
      author='Tobias Hasselrot',
      author_email='tobias.hasselrot@gmail.com',
      url='',
      download_url='http://github.com/mewantit/django-imagemagick/',
      package_dir={'django-imagemagick': 'django-imagemagick'},
      packages=packages,
      package_data={'django-imagemagick': data_files},
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
      )
