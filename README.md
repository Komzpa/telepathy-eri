telepathy-eri
=============

VK Connection Manager for Telepathy.

Run requirements
------------

* python-mechanize
* python-lxml

Build requirements
------------

* make
* automake
* libxslt
* xsltproc
* libtool

How to install
--------------

```
$ git submodule update --init
$ pushd telepathy-python/
$ make distclean
$ ./autogen.sh
$ make
$ popd

$ make
# make install
```

How to use
----------

1. /usr/libexec/telepathy-eri
2. Open empathy-accounts or gnome-online-accounts
3. Add vk account

If you have troubles adding your account in KDE, add via command line:

```
mc-tool add eri/vk komzpa string:account=user@email_provi.der string:password=pAsSw0rD
```



How to remove
-------------

```
# make uninstall
```

Some ubuntu-specific notes
---------------------------

For 12.10+ ubuntus copy files from accounts/* to /usr/share/accounts in order to use with online-accounts

Token authorization
-------------------

At adding account use wrong password.

Open link: https://oauth.vk.com/authorize?client_id=3821026&scope=friends,messages,offline&redirect_uri=https://oauth.vk.com/blank.html&v=5.0&response_type=token

In response you will have redirect and in address-string you will have alike:
```
#access_token=[THIS]&expires_in=0&user_id=1361145746
```

1. Open additional settings
2. Into Token-parameter enter "THIS"

Connection manager prefer token if it set.
