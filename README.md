[![Build Status](https://travis-ci.org/open-io/ansible-role-openio-gridinit.svg?branch=master)](https://travis-ci.org/open-io/ansible-role-openio-gridinit)
# Ansible role `gridinit`

An Ansible role for gridinit. Specifically, the responsibilities of this role are to:

- install gridinit
- configure service(s)
- remove unnecessary service(s)

## Requirements

- Ansible 2.4+

## Role Variables

| Variable   | Default | Comments (type) |
| :---       | :---    | :---            |
| `openio_gridinit_user` | `root` | User to run |
| `openio_gridinit_group` | `root` | Group to run |
| `openio_gridinit_config_file` | `/etc/gridinit.conf` | Path to the parent configuration file |
| `openio_gridinit_conf_confd` | `/etc/gridinit.d` | Path to the service's folder (by namespace) |
| `openio_gridinit_rundir` | `/run/gridinit` | Path to the tmpfs subfolder |
| `openio_gridinit_limits` | `dict` | Defines the max open files and limits for coredump |
| `openio_gridinit_services` | `[]` | Defines services to configure |

## Dependencies

- You have to use this role after the role `ansible-role-openio-repository` (like [this](https://github.com/open-io/ansible-role-openio-gridinit/blob/docker-tests/test.yml#L7))

## Example Playbook

```yaml
- hosts: all
  gather_facts: true
  become: true
  roles:
    - role: ansible-role-gridinit
      openio_gridinit_services:
        - name: meta1-1
          namespace: OPENIO
          type: meta1
          configuration:
            command: /bin/true
            enabled: true
            start_at_boot: true
            on_die: respawn
            uid: root
            gid: root
            env_PATH: /usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin

        - name: rawx-1
          namespace: OPENIO2
          type: rawx
          state: absent 
          configuration:
            command: /bin/true
            enabled: true
            start_at_boot: true
            on_die: respawn
            group: bar
            uid: root
            gid: root
```


```ini
[servers]
node1 ansible_host=192.168.1.173
```
## Service

A `service` is a dict like this. Commented keys are optional.

```yaml
openio_gridinit_services:
  - name: meta1-1
    namespace: OPENIO
    #state: present
    type: meta1
    configuration:
      command: /bin/true
      enabled: true
      start_at_boot: true
      on_die: respawn
      #group: foo
      uid: root
      gid: root
      #env_PATH: /usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin
      #env_LD_LIBRARY_PATH: 
```

## Contributing

Issues, feature requests, ideas are appreciated and can be posted in the Issues section.

Pull requests are also very welcome. The best way to submit a PR is by first creating a fork of this Github project, then creating a topic branch for the suggested change and pushing that branch to your own fork. Github can then easily create a PR based on that branch.

## License

Apache License, Version 2.0

## Contributors

- [Cedric DELGEHIER](https://github.com/cdelgehier/) (maintainer)
