# Version must be defined here

%global __os_install_post %{nil}
%define name whoiscache
%define unmangled_version %{version}
%define release 1

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
python -m compileall .

%install
od=`pwd`
mkdir $RPM_BUILD_ROOT/opt
cp -r . $RPM_BUILD_ROOT/opt/%name
cd $RPM_BUILD_ROOT
find . | cut -c2- > $od/INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
