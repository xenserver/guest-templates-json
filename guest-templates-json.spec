Name:    guest-templates-json
Summary: Creates the default guest templates
Version: @VERSION@
Release: @RELEASE@
License: BSD
Source0: guest-templates-json-%{version}.tar.bz2
BuildArch: noarch

Requires: xapi-core
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

%define templatedir %{_datadir}/xapi/vm-templates

%prep
%setup -q

%build
%{__python2} setup.py build

%install
%{__python2} setup.py install --root %{buildroot}

install -d %{buildroot}%{templatedir}
install -m 644 json/*.json %{buildroot}%{templatedir}
install -d %{buildroot}%{_sysconfdir}/xapi.d/vm-templates

install -d %{buildroot}%{_sysconfdir}/firstboot.d
install -m 755 62-create-guest-templates %{buildroot}%{_sysconfdir}/firstboot.d

%post
/usr/bin/create-guest-templates > /dev/null ||:

%post data-linux
/usr/bin/create-guest-templates > /dev/null ||:

%post data-windows
/usr/bin/create-guest-templates > /dev/null ||:

%post data-xenapp
/usr/bin/create-guest-templates > /dev/null ||:

%post data-other
/usr/bin/create-guest-templates > /dev/null ||:

%files
%defattr(-,root,root,-)
%{_bindir}/*
%{python2_sitelib}/*
%dir %{templatedir}
%{_sysconfdir}/xapi.d/*
%{_sysconfdir}/firstboot.d/*

%files data-linux
%defattr(-,root,root,-)
%{templatedir}/base-debian*.json
%{templatedir}/base-el*.json
%{templatedir}/base-hvmlinux.json
%{templatedir}/base-pvlinux.json
%{templatedir}/base-sl*.json
%{templatedir}/base-ubuntu*.json
%{templatedir}/centos*.json
%{templatedir}/coreos.json
%{templatedir}/debian*.json
%{templatedir}/oel*.json
%{templatedir}/rhel*.json
%{templatedir}/sl*.json
%{templatedir}/ubuntu*.json

%files data-windows
%defattr(-,root,root,-)
%{templatedir}/base-windows*.json
%{templatedir}/windows*.json

%files data-xenapp
%defattr(-,root,root,-)
%{templatedir}/base-xenapp*.json
%{templatedir}/xenapp*.json

%files data-other
%defattr(-,root,root,-)
%{templatedir}/other-install-media.json

%changelog
