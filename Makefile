# Remote RPM building server
SRPM_BUILD_SERVER=build-srpm.ecix.net
VERSION=$(shell cat VERSION)

all:
	echo "hi"

srpm:
	bin/gen_srpm.sh whoiscache $(VERSION) $(SRPM_BUILD_SERVER) deploy/whoiscache.spec	
