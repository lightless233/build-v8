#!/usr/bin/env python3

import os
import subprocess

V8_GIT_TAG = os.environ.get("V8_VERSION", "9.9.115.9")
V8_GIT_URL = "https://chromium.googlesource.com/v8/v8.git"
DEPOT_GIT_URL = "https://chromium.googlesource.com/chromium/tools/depot_tools.git"

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
DEPOT_HOME = os.path.join(CURRENT_DIR, "depot_tools")
V8_HOME = os.path.join(CURRENT_DIR, "v8")
print(f"{CURRENT_DIR=}, {DEPOT_HOME=}")
gn_args = {
    "dcheck_always_on": "true" if os.environ.get("STPYV8_DEBUG") else "false",
    "is_component_build": "false",
    "is_debug": "true" if os.environ.get("STPYV8_DEBUG") else "false",
    "treat_warnings_as_errors": "false",
    "use_custom_libcxx": "false",
    "v8_deprecation_warnings": "true",
    "v8_enable_disassembler": "false",
    "v8_enable_i18n_support": "true",
    "v8_enable_pointer_compression": "false",
    "v8_enable_31bit_smis_on_64bit_arch": "false",
    "v8_imminent_deprecation_warnings": "true",
    "v8_monolithic": "true",
    "v8_use_external_startup_data": "false",
    "v8_symbol_level": "0",
}
GN_ARGS = ' '.join(f"{key}={value}" for key, value in gn_args.items())


def exec_cmd(cmdline, cwd="."):
    proc = subprocess.Popen(cmdline, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    exit_code = proc.returncode
    return exit_code, stdout.decode("utf-8"), stderr.decode("utf-8")


# setup depot_tools
cmd = f"git clone {DEPOT_GIT_URL} {DEPOT_HOME}"
print(f"[-] step1: get depot tools, cmd: {cmd}")
print(exec_cmd(cmd))

# update gclient
gclient = os.path.join(DEPOT_HOME, "gclient")
cmd = f"{gclient} --version"
print(f"[-] step2: try update gclient, cmd: {cmd}")
print(exec_cmd(cmd))

# fetch v8 code
fetch = os.path.join(DEPOT_HOME, "fetch")
cmd = f"{fetch} v8"
print(f"[-] step3: try fetch v8 code, cmd: {cmd}")
print(exec_cmd(cmd))

# fetch v8 code's all tags
cmd = f"git fetch --tags"
print(f"[-] step4: fetch v8 code's all tag, cmd: {cmd}")
print(exec_cmd(cmd, cwd=V8_HOME))

# debug: show all tags
# cmd = f"git --no-pager tag"
# print(f"[+] debug step: show all tags, cmd: {cmd}")
# exit_code, stdout, stderr = exec_cmd(cmd, cwd=V8_HOME)
# print(f"{exit_code=}")
# print(f"{stdout=}")
# print(f"{stderr=}")

# checkout to target tag
cmd = f"git checkout {V8_GIT_TAG}"
print(f"[-] step5: checkout to target tag, {cmd=}")
print(exec_cmd(cmd, cwd=V8_HOME))

# sync latest v8 code
cmd = f"{gclient} sync -D"
print(f"[-] step6: sync v8 code, {cmd=}")
print(exec_cmd(cmd, cwd=V8_HOME))

# try to generate build config
gn = os.path.join(DEPOT_HOME, "gn")
cmd = f"{gn} gen out.gn/x64.release.sample --args='{GN_ARGS}'"
print(f"[-] step7: Generate build scripts for V8 (v{V8_GIT_TAG}), {cmd=}")
exit_code, stdout, stderr = exec_cmd(cmd, cwd=V8_HOME)
print(f"{exit_code=}")
print(f"{stdout=}")
print(f"{stderr=}")


# try build via ninja
ninja = os.path.join(DEPOT_HOME, "ninja")
cmd = f"{ninja} -C out.gn/x64.release.sample v8_monolith"
print(f"[-] step8: build via ninja, {cmd=}")
exit_code, stdout, stderr = exec_cmd(cmd, cwd=V8_HOME)
print(f"{exit_code=}")
print(f"{stdout=}")
print(f"{stderr=}")
