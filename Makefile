# Remote RPM building server
SRPM_BUILD_SERVER=build-srpm.ecix.net
VERSION=$(shell cat VERSION)

all:
	echo "Nothing to do"

test:
	.env/bin/nosetests -s -v tests

srpm:
	bin/gen_srpm.sh whoiscache $(VERSION) $(SRPM_BUILD_SERVER) deploy/whoiscache.spec	
