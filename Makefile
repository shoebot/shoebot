PYTHON=`which python`
DESTDIR=/
BUILDIR=$(CURDIR)/debian/shoebot
PROJECT=shoebot
VERSION=1.3.1

all:
	@echo "make source - Create source package"
	@echo "make install - Install on local system"
	@echo "make buildrpm - Generate a rpm package"
	@echo "make builddeb - Generate a deb package"
	@echo "make clean - Get rid of scratch and byte files"

source:
	$(PYTHON) setup.py sdist $(COMPILE)

install:
	$(PYTHON) setup.py install --root $(DESTDIR) $(COMPILE)

install-gedit:
	cd extensions/gedit-plugin && $(SHELL) ./install.sh && cd ../..

buildrpm:
	$(PYTHON) setup.py bdist_rpm --post-install=rpm/postinstall --pre-uninstall=rpm/preuninstall

builddeb:
	# build the source package in the parent directory
	# then rename it to project_version.orig.tar.gz
	$(PYTHON) setup.py sdist $(COMPILE) --dist-dir=../
	rename -f 's/$(PROJECT)-(.*)\.tar\.gz/$(PROJECT)_$$1\.orig\.tar\.gz/' ../*
	# build the package
	dpkg-buildpackage -i -I -rfakeroot -S

clean:
	$(PYTHON) setup.py clean
	fakeroot $(MAKE) -f $(CURDIR)/debian/rules clean
	rm -rf build/ dist/ MANIFEST
	find . -name '*.pyc' -delete

deploy: clean html
	rsync --compress --checksum --progress --recursive --update build/html/ manufactura:~/apps/shoebot-docs/ --exclude="__pycache__" --exclude=".*"
dry-deploy: clean html
	rsync --compress --checksum --progress --recursive --update build/html/ manufactura:~/apps/shoebot-docs/ --exclude="__pycache__" --exclude=".*" --dry-run
