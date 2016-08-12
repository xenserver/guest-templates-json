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

%files
%defattr(-,root,root,-)
%{_bindir}/*
%{python2_sitelib}/*
%{_datadir}/xapi/*
%{_sysconfdir}/xapi.d/*
%{_sysconfdir}/firstboot.d/*

%changelog
