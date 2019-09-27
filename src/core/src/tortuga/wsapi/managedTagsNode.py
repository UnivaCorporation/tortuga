#############################################################################
#
# This code is the Property, a Trade Secret and the Confidential Information
# of Univa Corporation.
#
# Copyright 2008-2018 Univa Corporation. All Rights Reserved. Access is Restricted.
#
# It is provided to you under the terms of the
# Univa Term Software License Agreement.
#
# If you have any questions, please contact our Support Department.
#
# http://www.univa.com
#
#############################################################################

import os
import logging
from tortuga.os_utility import tortugaSubprocess
from tortuga.exceptions.commandFailed import CommandFailed
from tortuga.wsapi.nodeWsApi import NodeWsApi

logger = logging.getLogger(__name__)

class NodeManagedTags:
    managed_prefix = "managed:"
    managed_prefix_len = len(managed_prefix)
    node_api = NodeWsApi()
    env = {**os.environ,
        'PATH': '/opt/tortuga/bin:' + os.environ['PATH'],
        'TORTUGA_ROOT': '/opt/tortuga'}

    def __init__(self, script):
        self.script = script

    def update(self, update):
        previous_tags = update['previous_tags']
        logger.warn("previous_tags={}".format(previous_tags))
        previous_managed_tags = {i[self.managed_prefix_len:].replace(' ','_'):previous_tags[i].replace(' ','_') for i in previous_tags if i.startswith(self.managed_prefix)}

        tags = update['tags']
        logger.warn("tags={}".format(tags))

        managed_tags = {i[self.managed_prefix_len:].replace(' ','_'):tags[i].replace(' ','_') for i in tags if i.startswith(self.managed_prefix)}
        unmanaged_tags = ';'.join('{}:{}'.format(k.replace(' ','_'),v.replace(' ','_') if v is not None else 'None')
                                for k,v in sorted({i:tags[i] for i in tags if not i.startswith(self.managed_prefix)}.items()))
        logger.warn('unmanaged_tags={}'.format(unmanaged_tags))

        removed_tags = {k: previous_managed_tags[k] for k in
                        set(previous_managed_tags) - set(managed_tags)}
        added_tags = {k: managed_tags[k] for k in set(managed_tags) - set(previous_managed_tags)}
        modified_tags = {k: managed_tags[k] for k in previous_managed_tags if
                         k in managed_tags and managed_tags[k] != previous_managed_tags[k]}
        logger.warn('added_tags={}'.format(added_tags))
        logger.warn('removed_tags={}'.format(removed_tags))
        logger.warn('modified_tags={}'.format(modified_tags))

        node = self.node_api.getNodeById(update['id'])
        software_profile = node.getSoftwareProfile()
        logger.warn('node={}, software_profile={}'.format(node, software_profile))
        if software_profile['metadata'].get('uge'):
            for cluster in software_profile['metadata']['uge']['clusters']:
                cluster_name = cluster['name']
                for setting in cluster['settings']:
                    if setting['key'] == 'sge_root':
                        uge_root = setting['value']
                        break

                cell_dir = os.path.join(uge_root, cluster_name)

                cmd = ('. {}/common/settings.sh; '
                    '{} '
                    '--software-profile {} '
                    '--cell-dir {} '
                    '{} {} {} {} {}'.format(
                    cell_dir,
                    self.script,
                    software_profile['name'],
                    cell_dir,
                    '--added-tags ' + ','.join('{}={}'.format(k, v) for k, v in
                                            added_tags.items()) if added_tags else '',
                    '--removed-tags ' + ','.join('{}={}'.format(k, v) for k, v in
                                                removed_tags.items()) if removed_tags else '',
                    '--modified-tags ' + ','.join('{}={}'.format(k, v) for k, v in
                                                modified_tags.items()) if modified_tags else '',
                    '--unmanaged-tags ' + '"' + unmanaged_tags + '"' if unmanaged_tags else '',
                    '--node ' + node.getName()))

                logger.warn('Calling cmd: {}'.format(cmd))

                p = tortugaSubprocess.TortugaSubprocess(cmd, env=self.env,
                                                        useExceptions=False)
                p.run()
                logger.warn('stdout: {}'.format(p.getStdOut().decode().rstrip()))
                logger.warn('stderr: {}'.format(p.getStdErr().decode().rstrip()))
                es = p.getExitStatus()
                logger.warn('exit status: {}'.format(es))
                if es != 0:
                    raise CommandFailed(str(p.getStdErr().decode().rstrip()))
        else:
            logger.warn('Managed tagging supported only on UGE cluster, metadata: {}'.format(software_profile['metadata']))



