# Needs these variables prepended
# define version ...
# define with_prod_python ...

%define name whoiscache
%define unmangled_version %{version}
%define release 1
%define homedir /var/lib/ecix/%{name}
%define app_user whoiscache
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
Requires: python27

%description
Cache service for WHOIS data

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
find . | grep -v settings_local | cut -c2- > $od/INSTALLED_FILES

%post
%{with_prod_python} /opt/%{name}/bin/venv_init
mkdir -p %{homedir}/data
useradd --system -d %{homedir} %{app_user}
chown -R %{app_user}:%{app_user} %{homedir}

%postun
if [ "$1" = "0" ]; then
   userdel --force %{app_user} 2> /dev/null; true
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)

%config(noreplace) /etc/ecix/python/*
