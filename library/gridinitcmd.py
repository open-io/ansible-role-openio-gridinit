#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# (c) 2017, Sebastien Lapierre <sebastien.lapierre@openio.io>
# (c) 2012, Matt Wright <matt@nobien.net>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: gridinitcmd
short_description: Manage the state of a program or group of programs running via OpenIO gridinit
description:
     - Manage the state of a program or group of programs running via OpenIO gridinit
version_added: "0.1"
options:
  name:
    description:
      - The name of the OpenIO service.
    required: true
    default: null
  state:
    description:
      - The desired state of OpenIO service/group.
    required: true
    default: null
    choices: [ "status", "start", "stop", "restart", "reload", "repair" ]
  socket:
    description:
      - Explicit unix socket path
    required: false
    default: null
notes:
  - When C(state) = I(status), the module will call C(gridinit_cmd status "service or @services") then C(gridinit_cmd status ) if the program/group has not been specified .
  - When C(state) = I(restarted), the module will call C(supervisorctl update) then call C(supervisorctl restart).
requirements: [ "gridinit_cmd" ]
author:
    - "sebastien Lapierre  (sebastien@openio.io)"
'''

EXAMPLES = '''
# Manage the state of program to be in 'started' state.
- gridinitcmd:
    name: service
    state: started

# Manage the state of program group to be in 'started' state.
- gridinitcmd:
    name: @service
    state: started

# Restart a service.
- gridinitcmd:
    name: service
    state: restarted

'''

import os
import re
from ansible.module_utils.basic import AnsibleModule, is_executable


def main():
    arg_spec = dict(
        name=dict(required=False),
        socket=dict(required=False, type='path'),
        gridinit_cmd_path=dict(required=False, type='path'),
        state=dict(required=True, choices=['status', 'start', 'restart', 'stop', 'reload', 'repair'])
    )

    module = AnsibleModule(argument_spec=arg_spec, supports_check_mode=True)

    name = module.params['name']
    state = module.params['state']
    socket = module.params.get('socket')
    gridinit_cmd_path = module.params.get('gridinit_cmd_path')

    # we check error message for a pattern, so we need to make sure that's in C locale
    module.run_command_environ_update = dict(LANG='C', LC_ALL='C', LC_MESSAGES='C', LC_CTYPE='C')
    if gridinit_cmd_path:
        if os.path.exists(gridinit_cmd_path) and is_executable(gridinit_cmd_path):
            gridinit_cmd_args = [gridinit_cmd_path]
        else:
            module.fail_json(
                msg="Provided path to gridinit_cmd does not exist or isn't executable: %s" % gridinit_cmd_path)
    else:
        gridinit_cmd_args = [module.get_bin_path('gridinit_cmd', True)]

    if socket:
        gridinit_cmd_args.extend(['-S', socket])

    def run_gridinit_cmd(cmd, name=None, **kwargs):
        args = list(gridinit_cmd_args)  # copy the master args
        args.append(cmd)
        if name:
            args.append(name)
        return module.run_command(args, **kwargs)

    def get_matched_processes():
        matched = []
        rc, out, err = run_gridinit_cmd('status')
        if name:
            group_name = name
            if re.search('@', name):
                group_name = name.split('@')[1]
        for line in out.splitlines():
                # One status line may look like one of these two:
                # Group/Key [service] matched no service
                # process in group:
                # OPENIO-rawx-1              UP        32381 SCALAIR,rawx,rawx-1
                fields = [field for field in line.split() if field != '']
                # fields = [field for field in line.split() if re.search(name,line)]
                process_name = fields[0]
                print(process_name+'\n')
                status = fields[1]
                # if process_name != name:
                if process_name == 'KEY':
                    continue
                if name:
                    if bool(group_name in process_name) is True:
                        matched.append((process_name, status))
                        break
                    else:
                        continue
                matched.append((process_name, status))
        return matched

    def take_action_on_processes(processes, status_filter, action, expected_result):
        to_take_action_on = []
        if action == 'reload':
            rc, out, err = run_gridinit_cmd(action)
            ret_format = out.splitlines()
            for line in out.splitlines():
                fields = [field for field in line.split() if field != '']
                status = fields[-1]
                subaction = fields[1]
                if status != 'Success':
                    module.fail_json(name=subaction, state=status,  msg="Reload failed")
            module.exit_json(changed=True, name=subaction, state=state, msg=ret_format)
        elif name is None:
            rc, out, err = run_gridinit_cmd(action)
            ret_format = out.splitlines()
            for line in out.splitlines():
                fields = [field for field in line.split() if field != '']
                process_name = fields[0]
                status = fields[1]
                if process_name == 'KEY':
                    continue
                if status != 'UP':
                    module.fail_json(name=process_name, state=status,  msg="Service is not working")
            module.exit_json(changed=True, name=name, state=state, msg=ret_format)
        else:
            for process_name, status in processes:
                if status_filter(status):
                    to_take_action_on.append(process_name)
            if len(to_take_action_on) == 0:
                module.exit_json(changed=False, name=name, state=state)
            if module.check_mode:
                module.exit_json(changed=True)
            for process_name in to_take_action_on:
                rc, out, err = run_gridinit_cmd(action, process_name, check_rc=True)
                ret_format = out.splitlines()
            module.exit_json(changed=True, name=name, state=state, affected=to_take_action_on, msg=ret_format)

    if state == 'restart':
        rc, out, err = run_gridinit_cmd('restart', check_rc=True)
        processes = get_matched_processes()
        if len(processes) == 0:
            module.fail_json(name=name, msg="ERROR (no such service)")
        take_action_on_processes(processes, lambda s: True, 'restart', 'Success')

    processes = get_matched_processes()

    if state == 'status':
        if len(processes) == 0:
            module.fail_json(name=name, msg="ERROR (no such service)")
        # take_action_on_processes(processes, lambda s: True, 'status', 'status')
        take_action_on_processes(processes, lambda s: True, 'status', 'UP')

    if state == 'start':
        if len(processes) == 0:
            module.fail_json(name=name, msg="ERROR (no such service)")
        take_action_on_processes(processes, lambda s: s not in 'UP', 'start', 'Success')

    if state == 'stop':
        if len(processes) == 0:
            module.fail_json(name=name, msg="ERROR (no such service)")
        take_action_on_processes(processes, lambda s: s not in 'DOWN', 'stop', 'Success')

    if state == 'reload':
#        if len(processes) == 0:
#            module.fail_json(name=name, msg="ERROR (no such service)")
        take_action_on_processes(processes, lambda s: True, 'reload', 'reload')

    if state == 'repair':
        if len(processes) == 0:
            module.fail_json(name=name, msg="ERROR (no such service)")
        take_action_on_processes(processes, lambda s: s in 'BROKEN', 'repair', 'repair')


if __name__ == '__main__':
    main()

