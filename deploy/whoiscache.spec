# Needs these variables prepended
# define version ...
# define with_prod_python ...

%define name whoiscache
%define unmangled_version %{version}
%define release 1
# This is to stop yum from generating .py files with
# the system-wide installed python
%global __os_install_post %{nil}

Summary: Cache service for WHOIS data
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: UNKNOWN
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: sadler@port-zero.com <UNKNOWN>

%description
UNKNOWN

%prep
%setup -n %{name}-%{unmangled_version}

%build
%{with_prod_python} python -m compileall .

%install
od=`pwd`
mkdir $RPM_BUILD_ROOT/opt
cp -r . $RPM_BUILD_ROOT/opt/%{name}
cp -r deploy/etc $RPM_BUILD_ROOT/etc
cd $RPM_BUILD_ROOT
find . | cut -c2- > $od/INSTALLED_FILES

%post
%{with_prod_python} /opt/%{name}/bin/venv_init

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
