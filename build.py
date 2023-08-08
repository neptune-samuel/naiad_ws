#!/usr/bin/env python3

## build.py -l --list
## build.py naiad_chassis 
## build.py  -- 编译所有 
## build.py -r chassis 
## build.py -r fog 

import argparse
import subprocess
import sys
import os
import shutil
import json

packages_name = {}
remote_info = ''

def full_package_name(brief):
    global packages_name
    if brief in packages_name:
        return packages_name[brief]
    return brief

def load_packages_name():
    global packages_name
    config_file = 'packages.json'
    if os.path.exists(config_file):
        with open(config_file, 'r') as fp:
            packages_name = json.load(fp)

def load_remote_info():
    config_file = 'remote.json'
    if os.path.exists(config_file):
        with open(config_file, 'r') as fp:
            info = json.load(fp)    
            if 'ssh' in info and 'target' in info:
                return info['ssh'] + ':' + info['target']
            else:
                print("***Invalid remote info file, 'ssh' or 'target' missed")
    return ''                

def workspace_path(sub_folder=None):
    script_path = os.path.abspath(__file__)
    ws_path = os.path.dirname(script_path)
    if sub_folder:
        return os.path.join(ws_path, sub_folder)
    else:
        return ws_path
    
def command_string(cmds):
    s = ''
    for cmd in cmds:
        s +=' ' + cmd
    return s
    
def get_all_packages():
    ws = workspace_path()
    src = os.path.join(ws, 'src')
    pkgs = []
    for item in os.listdir(src):
        if not item.startswith('.'):
            path = os.path.join(src, item)
            if os.path.isdir(path):
                pkgs.append(path)
    return pkgs

def arguments():
    parser = argparse.ArgumentParser(description="Ros packages building helpers")
    parser.add_argument('-l', '--list', action='store_true', help="List all packages")
    parser.add_argument('-c', '--cross', action='store_true', help="Cross comipler")
    # 有指定-S 但无参数，使用const, 未使用-S，使用default
    parser.add_argument('-S', '--sync', metavar='REMOTE', nargs='?', const='', default=None, help="Sync install folder to REMOTE")
    #parser.add_argument('-r', '--run', action='store_true', help="Run package")
    parser.add_argument('-D', '--distclean', action='store_true', help="Clean workspace")    
    parser.add_argument('-g', '--git', action='store_true', help="Use git command for all packages")    
    # nargs = ？ 表示支持允许为空或1个
    parser.add_argument('package', nargs='*', metavar='', help="Target package")

    return parser.parse_args()

def list_packages():
    subprocess.run(['colcon', 'list'], check=True)


def print_result(result, pkg_name=""):
    if result.returncode == 0:
        print("==> Build %s success" % pkg_name)
        return True
    else:
        print("==> Build %s failed, ret=%d" % (pkg_name, result.returncode))
        return False
    

def build_packages(pkgs, cross_build):
    alias = []
    for pkg in pkgs:
        alias.append(full_package_name(pkg))

    print("-- building packages --")
    print("=> packages   :", alias)
    print("=> cross build:", cross_build)

    colcon_build = ['colcon', 'build', '--merge-install']
    if cross_build:
        colcon_build.append('--cmake-args')
        colcon_build.append('-DCMAKE_TOOLCHAIN_FILE=/opt/nano/cross.cmake')

    if len(pkgs) == 0:
        # 编译所有
        result = subprocess.run(colcon_build, check=True)
        print_result(result, 'all')
    else:
        for pkg in alias:
            cmd = colcon_build
            cmd.append('--packages-select')
            cmd.append(pkg)
            result = subprocess.run(cmd, check=True)
            print_result(result, pkg)

def distclean():
    build = workspace_path('build')
    install = workspace_path('install')
    log = workspace_path('log')
    print("-- dist clean --")
    print("=> remove", build)
    if os.path.exists(build):
        shutil.rmtree(build)
    print("=> remove", install)
    if os.path.exists(install):
        shutil.rmtree(install)
    print("=> remove", log)
    if os.path.exists(log):
        shutil.rmtree(log)
    print("=> done")


def sync_install(remote):
    """
    -avz选项用于指定同步时的参数，含义如下：
    -a：以归档模式同步，保留文件的所有属性，包括权限、所有者和组、时间戳等。
    -v：显示详细输出，以便查看同步过程。
    -z：启用压缩传输，减少网络传输的数据量。    
    """
    print("==> Start sync %s to %s" % (workspace_path('install'), remote))
    rsync_cmd = ['rsync', '-avz', '-e', 'ssh', workspace_path('install'), remote]
    result = subprocess.run(rsync_cmd, check=True)
    if result.returncode == 0:
        print("==> Sync %s success" % remote)        
    else:
        print("==> Sync %s failed, ret=%d" % (remote, result.returncode))        

def run_package(pkg):
    pass

def run_git_command(cmds):
    ## pkgs is git command 
    pkgs = get_all_packages()    
    if len(pkgs) == 0:
        print("***No packages found")
        sys.exit(1)
    if len(cmds) == 0:
        print("***No git command specified")
        sys.exit(1)
    for pkg in pkgs:
        git_cmd = ['git']
        for cmd in cmds:
            git_cmd.append(cmd)
        print("==> enter project:", pkg)
        print("==> execute command:", command_string(git_cmd))
        subprocess.run(git_cmd, check=True, cwd=pkg)


if __name__ == "__main__":
    args = arguments()
    #print(args)
    load_packages_name()
    
    if args.list:
        list_packages()
    elif args.distclean:
        distclean()
    # elif args.run:
    #     if len(args.package) < 1:
    #         print("***Please input package name")
    #         sys.exit(1)
    #     run_package(args.package[0])
    elif args.sync != None:
        remote = ''
        if args.sync:
            remote = args.sync
        else:
            remote = load_remote_info()
        if remote:            
            sync_install(remote)
        else:
            print("***Please input remote info: e.g. neptune@192.168.2.100:/home/neptune/")
    elif args.git:
        run_git_command(args.package)
    else:
        ## build packages 
        build_packages(args.package, args.cross)        

