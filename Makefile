#
# Ecix CSC API Server
#
# This makefile provides scripts for building
# the distribution and creating a .rpm file
#

# Remote RPM building server
BUILD_SERVER=build-srpm.ecix.net

STAGING_SERVER=portal2.dev.ecix.net

### END CONFIGURATION ###
#
# Do not change anything below this line, unless you
# really know what you are doing.
#

# The project to build
# When changing this, remember to update your startup scripts
# and other dependent config files.
PROG=pytinyirrdcache

# Distribution directory
DIST=DIST
REMOTE_DIST=$(PROG)-$(DIST)

APP_DIST=$(DIST)/opt/$(PROG)

LOCAL_RPMS=RPMS

# Package Version
APP_VERSION=$(shell cat VERSION)
VERSION=$(APP_VERSION)_$(shell git rev-parse --short HEAD)

RPM=$(PROG)-$(VERSION)-1.x86_64.rpm

all: remote_rpm

dist: clean

	mkdir -p $(LOCAL_RPMS)

	# Create dist filesystem
	mkdir -p $(DIST)/etc
	mkdir -p $(DIST)/etc/init
	mkdir -p $(DIST)/etc/default

	mkdir -p $(APP_DIST)/data
	mkdir -p $(APP_DIST)/db

	mkdir -p $(APP_DIST)

	# Copy configuration and startup
	cp config/whoisDatabases.json $(DIST)/etc/whoisDatabases.json
    
	cp etc/default/* $(DIST)/etc/default/.
	cp etc/init/* $(DIST)/etc/init/.

	# Copy app
	cp -r src/ $(APP_DIST)/
	cp -r bin/ $(APP_DIST)/

	cp -r VERSION   $(APP_DIST)/.
	cp -r requirements.txt $(APP_DIST)/.


rpm: dist
	# Create RPM from DIST/
	fpm -s dir -t rpm -n $(PROG) -v $(VERSION) -C $(DIST) \
		--depends gcc \
		--depends python-virtualenv \
		--config-files /etc/ \
		--after-install deploy/after_install \
	  --before-install deploy/before_install \
		etc/ opt/

remote_rpm: dist
	# Copy distribution to build server
	ssh $(BUILD_SERVER) -- rm -rf $(REMOTE_DIST)
	scp -r $(DIST) $(BUILD_SERVER):$(REMOTE_DIST)

	# Copy distribution scripts
	scp -r deploy/* $(BUILD_SERVER):$(REMOTE_DIST)/.

	# Clean existing rpm on server
	ssh $(BUILD_SERVER) -- \
		rm -f $(RPM)

	ssh $(BUILD_SERVER) -- \
		fpm -s dir -t rpm -n $(PROG) -v $(VERSION) -C $(REMOTE_DIST) \
			--depends gcc \
			--depends python-virtualenv \
			--depends mysql-devel \
			--config-files /etc/default/ \
			--config-files /etc/csc-api-server.cfg \
			--after-install $(REMOTE_DIST)/after_install \
			--before-install $(REMOTE_DIST)/before_install \
			etc/ opt/


	# Get rpm from server
	scp $(BUILD_SERVER):$(RPM) $(LOCAL_RPMS)/.

deploy_staging:
	scp $(LOCAL_RPMS)/$(RPM) $(STAGING_SERVER):.
	ssh -t $(STAGING_SERVER) -- sudo yum install $(RPM)


clean:
	find . -name "*.sw*" -exec rm {} \;
	find . -name "*.pyc" -exec rm {} \;
	find . -name "__pycache__" -exec rm -fr {} \;
	rm -rf $(DIST)

tag:
	git tag v$(shell cat VERSION)
	git push origin v$(shell cat VERSION)
