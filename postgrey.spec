Summary: 	Postfix Greylisting Policy Server
Name:		postgrey
Version: 	1.32
Release:	%mkrel 4
License: 	GPL
Group: 		System/Servers
URL:		http://postgrey.schweikert.ch/
Source: 	http://postgrey.schweikert.ch/pub/%{name}-%{version}.tar.gz
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch:		postgrey-mdk.patch
BuildArch:	noarch
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires:	postfix
# These two are due to bugs in find-requires and Net::Server,
# remove after bugs have been fixed (#25086)
Requires:	perl(IO::Multiplex)
Requires:	perl(BerkeleyDB)
BuildRoot: 	%{_tmppath}/%{name}-%{version}-%{release}-buildroot/

%define confdir 	/etc/postfix
%define queue_directory %{_var}/spool/postfix

%description
Postgrey is a Postfix policy server implementing greylisting.
When a request for delivery of a mail is received by Postfix 
via SMTP, the triplet CLIENT_IP / SENDER / RECIPIENT is built. 
If it is the first time that this triplet is seen, or if the 
triplet was first seen less than 5 minutes, then the mail gets 
rejected with a temporary error. Hopefully spammers or viruses 
will not try again later, as it is however required per RFC.
Edit your configuration files:
/etc/postfix/main.cf:
  smtpd_recipient_restrictions = ...
    check_policy_service unix:extern/postgrey/socket, ...
or if you like to use inet sockets (modify the IP if needed):
/etc/sysconfig/postgrey:
  OPTIONS="--inet=127.0.0.1:10023"
/etc/postfix/main.cf:
  smtpd_recipient_restrictions = ...
    check_policy_service inet:127.0.0.1:10023, ...


%prep

%setup -q -n %{name}-%{version}
%patch -p1 -b .mdk

%build

pod2man -s 8 -c "" postgrey > postgrey.8
pod2man -s 8 -c "" contrib/postgreyreport > contrib/postgreyreport.8

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}%{_initrddir}
install %{SOURCE1} %{buildroot}%{_initrddir}/%{name}

mkdir -p %{buildroot}%{_sysconfdir}/postfix
cp postgrey_whitelist_clients %{buildroot}%{_sysconfdir}/postfix
cp postgrey_whitelist_recipients %{buildroot}%{_sysconfdir}/postfix
touch %{buildroot}%{_sysconfdir}/postfix/postgrey_whitelist_clients.local

mkdir -p %{buildroot}%{_sbindir}
install postgrey %{buildroot}%{_sbindir}/postgrey
install contrib/postgreyreport %{buildroot}%{_sbindir}/postgreyreport

mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
cp -p %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/%{name}

mkdir -p %{buildroot}%{queue_directory}/extern/%{name}
mkdir -p %{buildroot}%{_localstatedir}/lib/%{name}

mkdir -p %{buildroot}%{_mandir}/man8
cp postgrey.8 contrib/postgreyreport.8 %{buildroot}%{_mandir}/man8

%clean
rm -rf %{buildroot}

%pre
%_pre_useradd %{name} %{_localstatedir}/lib/%{name} /bin/false

%post
%_post_service %{name}

%preun
%_preun_service %{name}

%postun
%_postun_userdel %{name}

%files
%defattr(644,root,root,755)
%doc README Changes
%attr(0755,root,root) %{_initrddir}/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%config(noreplace) %{confdir}/postgrey_whitelist_clients
%config(noreplace) %{confdir}/postgrey_whitelist_recipients
%config(noreplace) %{confdir}/postgrey_whitelist_clients.local
%attr(755, root, root) %{_sbindir}/postgrey
%attr(755, root, root) %{_sbindir}/postgreyreport
%{_mandir}/man8/postgrey.8*
%{_mandir}/man8/postgreyreport.8*
%dir %attr(0750, postgrey, postfix) %{queue_directory}/extern/%{name}
%dir %attr(0750, postgrey, postgrey) %{_localstatedir}/lib/%{name}

