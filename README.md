### Configuration 

You will need to set some parameters in `etc/tempest.conf` in your local tempest workspace. 

Config for health monitor will look something like this:
```
[healthmon]
image = d2ac6a57-3669-44aa-a9f3-9690647ad1c5
ssh_user = cirros
flavor = 1
image = 580b618f-25b8-4c4b-b6f4-0d9d59596184
ssh_user = ubuntu
flavor = 2
```

where `ssh_users` correspond to the images provided. It doesn't matter what order you put `flavor/image/ssh_user`, however the `ssh_user` that will be used for each image needs to be in the same order as the images (i.e. user `cirros` will be used for the image `d2ac...`, `ubuntu` will be used for image `580b...` etc). HealthMonitor will run through all combinations of flavors and images. Additionally, you can set `flavors_alt`, `images_alt` and `ssh_users_alt` for a second group of compatible images/flavors that will also be run. 

`validation` will also need to be set in `tempest.conf`:
```
[validation]
connect_method = fixed
network_for_ssh = stackhpc-ipv4-vlan-v2
ip_version_for_ssh = 4
```

Looking something like this. Don't worry about image_ssh_user, this is overridden by healthmon config section. network_for_ssh will need to be the corresponding floating network or normal network, depending on whether you need floating ips to access machines on the network they are being created on from the network this test suite is running on. If you do need floating ips, you need to set: 

```
[network_feature_enabled]
floating_ips=True
```
and
```
[network]
public_network_id = a56b71cc-2220-479d-97a5-082b722e9e4c
floating_network_name = {something}
```
`public_network_id` is the network that VMs will be instantiated on - you need this regardless of floating ips. 