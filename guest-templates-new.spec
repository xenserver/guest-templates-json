Name:    guest-templates-new
Summary: Creates the default guest templates
Version: @VERSION@
Release: @RELEASE@
License: BSD
Source0: guest-templates-new-%{version}.tar.bz2
BuildArch: noarch

BuildRequires: python2-devel
BuildRequires: python-setuptools

%description
Creates the default guest templates during first boot or package
install/upgrade.

%package data-linux
Summary: Contains the default Linux guest templates
Requires(post): %{name} = %{version}-%{release}

%description data-linux
Contains the default Linux guest templates.

%package data-windows
Summary: Contains the default Windows guest templates
Requires(post): %{name} = %{version}-%{release}

%description data-windows
Contains the default Windows guest templates.

%package data-xenapp
Summary: Contains the default XenApp guest templates
Requires: %{name}-data-windows = %{version}-%{release}
Requires(post): %{name} = %{version}-%{release}

%description data-xenapp
Contains the default XenApp guest templates.

%package data-other
Summary: Contains the default other guest templates
Requires(post): %{name} = %{version}-%{release}

%description data-other
Contains the default other guest templates.

%prep
%setup -q

%build
%{__python2} setup.py build

%install
%{__python2} setup.py install --root %{buildroot}

install -d %{buildroot}%{_datadir}/xapi/vm-templates
install -m 644 json/*.json %{buildroot}%{_datadir}/xapi/vm-templates
install -d %{buildroot}%{_sysconfdir}/xapi.d/vm-templates

install -d %{buildroot}%{_sysconfdir}/firstboot.d
install -m 755 62-create-guest-templates %{buildroot}%{_sysconfdir}/firstboot.d

%post
/usr/bin/create-guest-templates > /dev/null ||:

%post data-linux
/usr/bin/create-guest-templates > /dev/null ||:

%post data-windows
/usr/bin/create-guest-templates > /dev/null ||:

%post data-other
/usr/bin/create-guest-templates > /dev/null ||:

%files
%defattr(-,root,root,-)
%{_bindir}/*
%{python2_sitelib}/*
%dir %{_datadir}/xapi/vm-templates
%{_sysconfdir}/xapi.d/*
%{_sysconfdir}/firstboot.d/*

%files data-linux
%defattr(-,root,root,-)
%{_datadir}/xapi/vm-templates/centos*.json
%{_datadir}/xapi/vm-templates/coreos.json
%{_datadir}/xapi/vm-templates/debian*.json
%{_datadir}/xapi/vm-templates/el*.json
%{_datadir}/xapi/vm-templates/hvmlinux.json
%{_datadir}/xapi/vm-templates/oracle*.json
%{_datadir}/xapi/vm-templates/pvlinux.json
%{_datadir}/xapi/vm-templates/rhel*.json
%{_datadir}/xapi/vm-templates/sl*.json
%{_datadir}/xapi/vm-templates/suse*.json
%{_datadir}/xapi/vm-templates/ubuntu*.json

%files data-windows
%defattr(-,root,root,-)
%{_datadir}/xapi/vm-templates/windows*.json

%files data-xenapp
%defattr(-,root,root,-)
%{_datadir}/xapi/vm-templates/xenapp*.json

%files data-other
%defattr(-,root,root,-)
%{_datadir}/xapi/vm-templates/other-install-media.json

%changelog
