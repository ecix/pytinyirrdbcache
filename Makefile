# Remote RPM building server
SRPM_BUILD_SERVER=build-srpm.ecix.net
RPM_BUILD_SERVER=build.ecix.net
VERSION=$(shell cat VERSION)
SRPM=whoiscache-$(VERSION)-1.src.rpm

all:
	echo "Nothing to do"

test:
	venv/bin/nosetests -s -v tests

develop:
	bin/venv_init
	echo "Now activate the virtualenv by running: source venv/bin/activate"

srpm:
	bin/gen_srpm whoiscache $(VERSION) $(SRPM_BUILD_SERVER) deploy/whoiscache.spec

rpm:
	[ -f dist/$(SRPM) ] || make srpm
	scp dist/$(SRPM) $(RPM_BUILD_SERVER):
	ssh -t $(RPM_BUILD_SERVER) "sudo cp $(SRPM) /usr/local/src/srpms/"
	@echo "$(SRPM) deployed to build server"
