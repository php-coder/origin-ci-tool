# coding=utf-8
from __future__ import absolute_import, division, print_function

from click import command, pass_context

from .docker import docker_version_for_preset
from .golang import golang_version_for_preset
from ..util.common_options import ansible_output_options
from ..util.preset_option import Preset, preset_option


def install_dependencies_for_preset(context, _, value):
    """
    Installs the full set of dependencies on the remote host.

    Handles the special `--for` option, defaults to `origin/master` if
    a preset is not provided by the user.

    :param context: Click context
    :param _: command-line parameter
    :param value: version of OpenShift for which to install dependencies
    """
    if not value or context.resilient_parsing:
        return

    prepare_all(context.obj, value)
    context.exit()


_SHORT_HELP = 'Configure all dependencies on remote hosts.'


@command(
    name='all',
    short_help=_SHORT_HELP,
    help=_SHORT_HELP + '''

If a preset is chosen, default values for the other options are used
and user-provided options are ignored.

\b
Examples:
  Install dependencies for the default configuration
  $ oct prepare all
\b
  Install dependencies for a specific version of OpenShift
  $ oct prepare all --for=ose/enterprise-3.3
''',
)
@preset_option(
    help_action='Install dependencies',
    callback=install_dependencies_for_preset,
)
@ansible_output_options
@pass_context
def all_command(context, preset=None):
    """
    Installs the full set of dependencies on the remote host.

    :param context: Click context
    :param preset: version of OpenShift for which to install dependencies
    """
    prepare_all(context.obj, preset)


def prepare_all(client, preset):
    """
    Installs the full set of dependencies on the remote host.

    :param client: Ansible client
    :param preset: version of OpenShift for which to install dependencies
    """
    # we can't default on a eager option or it would always trigger,
    # so we default here instead
    if not preset:
        preset = Preset.origin_master

    playbook_variables = {
        'origin_ci_docker_version': docker_version_for_preset(preset),
        'origin_ci_golang_version': golang_version_for_preset(preset),
    }

    client.run_playbook(
        playbook_relative_path='prepare/main',
        playbook_variables=playbook_variables,
    )
