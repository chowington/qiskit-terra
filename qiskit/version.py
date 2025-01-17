# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2017, 2018.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

# pylint: disable=no-name-in-module,broad-except,cyclic-import

"""Contains the terra version."""

import os
import subprocess
import sys


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def _minimal_ext_cmd(cmd):
    # construct minimal environment
    env = {}
    for k in ['SYSTEMROOT', 'PATH']:
        v = os.environ.get(k)
        if v is not None:
            env[k] = v
    # LANGUAGE is used on win32
    env['LANGUAGE'] = 'C'
    env['LANG'] = 'C'
    env['LC_ALL'] = 'C'
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env,
                            cwd=os.path.join(os.path.dirname(ROOT_DIR)))
    out = proc.communicate()[0]
    if proc.returncode > 0:
        raise OSError
    return out


def git_version():
    """Get the current git head sha1."""
    # Determine if we're at master
    try:
        out = _minimal_ext_cmd(['git', 'rev-parse', 'HEAD'])
        git_revision = out.strip().decode('ascii')
    except OSError:
        git_revision = "Unknown"

    return git_revision


with open(os.path.join(ROOT_DIR, "VERSION.txt"), "r") as version_file:
    VERSION = version_file.read().strip()


def get_version_info():
    """Get the full version string."""
    # Adding the git rev number needs to be done inside
    # write_version_py(), otherwise the import of scipy.version messes
    # up the build under Python 3.
    full_version = VERSION

    if not os.path.exists(os.path.join(os.path.dirname(ROOT_DIR), '.git')):
        return full_version
    try:
        release = _minimal_ext_cmd(['git', 'tag', '-l', '--points-at', 'HEAD'])
    except Exception:  # pylint: disable=broad-except
        return full_version
    git_revision = git_version()
    if not release:
        full_version += '.dev0+' + git_revision[:7]

    return full_version


__version__ = get_version_info()


def _get_qiskit_versions():
    out_dict = {}
    out_dict['qiskit-terra'] = __version__
    try:
        from qiskit.providers import aer
        out_dict['qiskit-aer'] = aer.__version__
    except Exception:
        pass
    try:
        from qiskit import ignis
        out_dict['qiskit-ignis'] = ignis.__version__
    except Exception:
        pass
    try:
        from qiskit.providers import ibmq
        out_dict['qiskit-ibmq-provider'] = ibmq.__version__
    except Exception:
        pass
    try:
        from qiskit import aqua
        out_dict['qiskit-aqua'] = aqua.__version__
    except Exception:
        pass

    cmd = [sys.executable, '-m', 'pip', 'freeze']
    try:
        reqs = _minimal_ext_cmd(cmd)
    except Exception:
        return out_dict
    reqs_dict = {}
    for req in reqs.split():
        req_parts = req.decode().split('==')
        if len(req_parts) == 1 and req_parts[0].startswith('git'):
            if 'qiskit' in req_parts[0]:
                package = req_parts[0].split('#egg=')[1]
                sha = req_parts[0].split('@')[-1].split('#')[0]
                reqs_dict[package] = 'dev-' + sha
            continue
        elif len(req_parts) == 1:
            continue
        reqs_dict[req_parts[0]] = req_parts[1]
    # Dev/Egg _ to - conversion
    for package in ['qiskit_terra', 'qiskit_ignis', 'qiskit_aer',
                    'qiskit_ibmq_provider', 'qiskit_aqua']:
        if package in reqs_dict:
            if package.replace('_', '-') in out_dict:
                continue
            out_dict[package.replace('_', '-')] = reqs_dict[package]

    for package in ['qiskit', 'qiskit-terra', 'qiskit-ignis', 'qiskit-aer',
                    'qiskit-ibmq-provider', 'qiskit-aqua']:
        if package in out_dict:
            continue
        if package in reqs_dict:
            out_dict[package] = reqs_dict[package]
        else:
            out_dict[package] = None
    return out_dict


__qiskit_version__ = _get_qiskit_versions()
