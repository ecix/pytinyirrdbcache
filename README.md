# TinyIRRDBCache

Manages a local cache of various Internet Routing Registry Databases (IRRDs) for quick lookups.
A tiny web service to provide a JSON interface to upstream WHOIS providers.

This is a rewrite of [ecix/tinyirrdbcache](https://github.com/ecix/tinyirrdbcache) in python.

## Testing

    sudo apt-get install libxml2-dev libxslt1-dev
    make test

## Deployment

    make rpm 

    make remote_rpm BUILD_SERVER=build-my-rpm.example.com


## See Also

https://www.ripe.net/manage-ips-and-asns/db/support/documentation/mirroring


