# Remote RPM building server
SRPM_BUILD_SERVER=build-srpm.ecix.net
VERSION=$(shell cat VERSION)

all:
	echo "Nothing to do"

test:
	.env/bin/nosetests -s -v tests

develop:
	bin/venv_init
	echo "Now activate the virtualenv by running: source venv/bin/activate"

srpm:
	bin/gen_srpm whoiscache $(VERSION) $(SRPM_BUILD_SERVER) deploy/whoiscache.spec
