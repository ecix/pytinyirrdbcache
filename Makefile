#
# Ecix Whoiscache API Server
#
# This makefile provides scripts for building
# the distribution and creating a .rpm file
#

# The project to build
# When changing this, remember to update your startup scripts
# and other dependent config files.
APP=whoiscache

# Remote RPM building server
BUILD_SERVER=build-srpm.ecix.net

# Testing server
STAGING_SERVER=epix.dev.ecix.net

# Remote RPM building server
RPM_BUILD_SERVER=build.ecix.net

### END CONFIGURATION ###
#
# Do not change anything below this line, unless you
# really know what you are doing.
#

APP_VERSION=$(shell cat VERSION)
VERSION=$(APP_VERSION)
# _$(shell git rev-parse --short HEAD)

# Distribution directory
DIST=BUILD-RPM
REMOTE_DIST=$(APP)-$(DIST)
BUILD_ARCHIVE=.$(APP)-BUILD.tar.gz

APP_DIST=$(DIST)/opt/ecix/$(APP)

LOCAL_RPMS=RPMS

RPM=$(APP)-$(VERSION)-1.x86_64.rpm

all:
	echo "Nothing to do"

rpm: $(LOCAL_RPMS)/$(RPM)


dist: clean

	# Create dist filesystem
	mkdir -p $(DIST)/etc

	# Copy configuration and startup
	cp -r etc/* $(DIST)/etc/.

	# Create app install target
	mkdir -p $(APP_DIST)

	# Copy app
	rsync -av \
		--exclude Makefile \
		--exclude $(DIST) \
		--exclude $(LOCAL_RPMS) \
		--exclude venv \
		--exclude *local* \
		--exclude *.pid \
		--exclude *.swp \
		--exclude *.swo \
		--exclude *.pyc \
		--exclude *.sqlite3 \
		* $(APP_DIST)

	# Copy deploy scripts
	cp -r deploy/* $(DIST)/.


local_rpm: dist

	fpm -s dir -t rpm -n $(APP) -v $(VERSION) -C $(DIST) \
		--depends gcc \
		--depends python-virtualenv \
		--config-files /etc/ecix/python/__init__.py \
		--config-files /etc/ecix/python/settings_local_whoiscache.py \
		--after-install $(DIST)/after_install \
		--before-install $(DIST)/before_install \
		etc/ opt/

	# Move rpm to target directory
	mkdir -p $(LOCAL_RPMS)
	mv $(RPM) $(LOCAL_RPMS)/.



#
# BUILD the rpm on the build server
#
$(LOCAL_RPMS)/$(RPM): dist

	# Make build archive and copy to server
	tar czf $(BUILD_ARCHIVE) $(DIST)/*
	scp $(BUILD_ARCHIVE) $(BUILD_SERVER):.
	rm $(BUILD_ARCHIVE)

	# Unpack distribution  build server
	ssh $(BUILD_SERVER) -- rm -rf $(REMOTE_DIST)
	ssh $(BUILD_SERVER) -- mkdir  $(REMOTE_DIST)
	ssh $(BUILD_SERVER) -- "cd $(REMOTE_DIST) && tar xzf ../$(BUILD_ARCHIVE)"

	# Clean existing rpm on server
	ssh $(BUILD_SERVER) -- \
		rm -f $(RPM)

	ssh $(BUILD_SERVER) -- \
		fpm -s dir -t rpm -n $(APP) -v $(VERSION) -C $(REMOTE_DIST)/$(DIST) \
			--depends gcc \
			--depends python-virtualenv \
			--config-files /etc/ecix/python/__init__.py \
			--config-files /etc/ecix/python/settings_local_whoiscache.py \
			--after-install $(REMOTE_DIST)/$(DIST)/after_install \
			--before-install $(REMOTE_DIST)/$(DIST)/before_install \
			etc/ opt/

	# Get rpm from server
	scp $(BUILD_SERVER):$(RPM) $(LOCAL_RPMS)/.


test:
	.env/bin/nosetests -s -v tests

develop:
	bin/venv_init
	echo "Now activate the virtualenv by running: source venv/bin/activate"


deploy_staging: $(LOCAL_RPMS)/$(RPM)
	scp $(LOCAL_RPMS)/$(RPM) $(STAGING_SERVER):.
	ssh -t $(STAGING_SERVER) -- sudo yum install $(RPM)


clean:
	find . -name "*.pyc" -exec rm {} \;
	find . -name "__pycache__" -exec rm -fr {} \;
	rm -f *.pid
	rm -rf $(DIST)

tag:
	git tag v$(shell cat VERSION)
	git push origin v$(shell cat VERSION)

