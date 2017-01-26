#!/usr/bin/python
#coding: utf-8 -*-

DOCUMENTATION = """
---
author: Cheng Li
module: service_flag
short_description: Save/read flags for triggering event like service restart
description: Sometimes we use a flag/variable to mark if a service should be
            restarted. But there could be many tasks before restarting service.
            If any of these tasks fails, we are not able to restart the service.
            When you run playbook again, the flag may not be true any more.
            This module is to make flag persistent to make sure service restarted.
options:
  name:
    description:
      - Name to mark the service.
    required: True
  livetrue:
    description:
      - If the flag is true. Default is false
    default: false
  state:
    description:
      - Two available options: [merge, absent]. Default value is merge.
        When you want to make flag persistent, use merge.
        To delete flag after service is restarted, use absent.
    default: 'absent'
"""

EXAMPLES = """
- name: ceph service restart flag
  service_flag:
    name: ceph
    livetrue: "{{ ceph_conf.changed }}"
    state: merge
- name: restart ceph service
  service: name=ceph-osd state=restarted
  when: service_flag.ceph|default(false)

"""

import os, pickle


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            livetrue=dict(type='bool', default=False),
            state=dict(default='merge'),
        ),
    )
    name = module.params.get('name')
    livetrue = module.params.get('livetrue')
    state = module.params.get('state')
    
    flagpath = '/tmp/.ansible_service_flags'
    if os.path.isfile(flagpath):
        with open(flagpath, 'r') as flagfile:
            try:
                flags = pickle.load(flagfile)
            except:
                flags = {}
    else:
        flags = {}
    persis_state = flags.get(name, False)
    merged_state = None
    if state == 'merge':
        merged_state = persis_state or livetrue
        flags[name] = merged_state
    elif state == 'absent':
        flags.pop(name, None)
    else:
        module.fail_json(msg='%s is not an valid state' % state)
    with open(flagpath, 'w') as flagfile:
        pickle.dump(flags, flagfile)

    module.exit_json(ansible_facts={'service_flag': flags})

from ansible.module_utils.basic import *
main()
