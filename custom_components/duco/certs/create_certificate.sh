#!/bin/sh

openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out private.key

openssl req -new -key private.key -out certificate.csr -sha256 -subj "/CN=ServerDeviceCert"

#openssl x509 -req -days 3650 -in certificate.csr -signkey private.key -out certificate.pem -extensions v3_req -extfile <(echo -e "basicConstraints = critical,CA:FALSE\nkeyUsage = digitalSignature, keyEncipherment\nsubjectAltName = @alt_names\n\n[alt_names]\nDNS.1 = duco_415357\nDNS.2 = duco_415357.local\nIP.1 = 192.168.5.4")

echo "basicConstraints = critical,CA:FALSE\nkeyUsage = digitalSignature, keyEncipherment\nsubjectAltName = @alt_names\n\n[alt_names]\nDNS.1 = duco_415357\nDNS.2 = duco_415357.local\nIP.1 = 192.168.5.4" > v3.ext
openssl x509 -req -days 14610 -in certificate.csr -signkey private.key -out certificate.pem -extfile v3.ext

openssl x509 -in certificate.pem -text -noout
