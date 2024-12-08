#!/usr/bin/env python3

import argparse
import subprocess
import os

def check_return_code(return_code:int,what:str,force_yes:bool = False):
    if return_code == 0:
        return
    if force_yes:
        print("Got return code = " + str(return_code) + " while " + what + ". Continuing.")
    s = input("Got return code = "+str(return_code)+" while "+what+" do you want to continue? [Y/n]: ")
    s = s.lower()
    if s != 'y':
        exit(return_code)

def inform_about_instaling_package(package_name:str):
    print(f"\nInstalling {package_name}\n")

APTS = [
    "x11-apps",
    "libxkbcommon0",
    "libxinerama1",
    "libxrandr2",
    "libxi6",
    "libdbus-1-3",
    "libasound2",
    "bash-completion",
    "build-essential",
    "cmake",
    "python3",
    "python3-venv",
    "g++-mingw-w64-x86-64"
]

def check_distrobox_name(name:str):
    if len(name) <= 0:
        raise ValueError("Name is to short.")
    Allowed_Characters = ['1','2','3','4','5','6','7','8','9','0']
    for i in range(97,123):
        Allowed_Characters.append(chr(i))
    for i in range(65,91):
        Allowed_Characters.append(chr(i))
    c = name[0]
    if not c in Allowed_Characters:
        raise ValueError(f"Character {c} is not allowed as beginning of name.")
    Allowed_Characters += ['_','.','-']
    for c in name[1:]:
        if not c in Allowed_Characters:
            raise ValueError(f"Character {c} is not allowed.")

def set_up(verbose:bool = False,verbose_distrobox:bool = False,force_yes = False,distrobox_name:str=""):
    try:
        check_distrobox_name(distrobox_name)
    except Exception as err:
        print(err,"Distrobox name must match [a-zA-Z0-9][a-zA-Z0-9_.-]* pattern.")
        return

    this_file_location = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(this_file_location)
    y_param = ""
    v_param = ""
    apt_v_param = ""
    if force_yes:
        y_param = "-y"
    if verbose:
        apt_v_param = "-oDebug::pkgAcquire::Worker=1"
    if verbose_distrobox:
        v_param = "--verbose"

    return_code = subprocess.call(f"distrobox create -i debian:10 --name {distrobox_name} {v_param}", shell=True)
    check_return_code(return_code, "creating distrobox", force_yes)
    inform_about_instaling_package("apt-file")
    return_code = subprocess.call(f"distrobox enter {distrobox_name} {v_param} -- sudo apt {apt_v_param} install apt-file {y_param}", shell=True)
    check_return_code(return_code, "installing apt-file", force_yes)
    return_code = subprocess.call(f"distrobox enter {distrobox_name} {v_param} -- sudo apt-file {v_param} update", shell=True)
    check_return_code(return_code, "upgrading using apt-file", force_yes)
    for package in APTS:
        inform_about_instaling_package(package)
        return_code = subprocess.call(f"distrobox enter {distrobox_name} {v_param} -- sudo apt {apt_v_param} install {package} {y_param}", shell=True)
        check_return_code(return_code, f"installing {package}", force_yes)
    print("\nUpgrading packages\n")
    return_code = subprocess.call(f"distrobox enter {distrobox_name} {v_param} -- sudo sudo apt {apt_v_param} full-upgrade {y_param}", shell=True)
    check_return_code(return_code, "upgradeing using apt full-upgrade", force_yes)
    return_code = subprocess.call(f"distrobox enter {distrobox_name} {v_param} -- python3 -m venv ../../venv-{distrobox_name}", shell=True)
    check_return_code(return_code, "creating python3 virtual enviroment", force_yes)
    inform_about_instaling_package("SCons")
    return_code = subprocess.call(f"distrobox enter {distrobox_name} {v_param} -- "+
                                  f"../../venv-{distrobox_name}/bin/pip install SCons==4.2.0", shell=True)
    check_return_code(return_code, "installing SCons in python3 virtual enviroment", force_yes)

    try:
        with open(
            os.path.join(".", ".distrobox_name.txt"),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            f.write(distrobox_name)
    except Exception as err:
        print(err)

def generate_md_docs(odir:str, lang:str, verbose:bool = False, force_colors:bool = False):
    color_param = ""
    v_param = ""
    if force_colors:
        color_param = "--color"
    if verbose:
        v_param = "--verbose"

    this_file_location = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(this_file_location)

    return_code = subprocess.call(f"../python\ md\ doc\ generator/.venv/bin/python3 "+
                                  f"../python\ md\ doc\ generator/make_md.py"+
                                  f" ../doc_classes/ ../python\ md\ doc\ generator/GDEngine_doc/ "+
                                  f"{color_param} {v_param} -o {odir} -l {lang}",
                                  shell=True)
    check_return_code(return_code, "generating markdown documentation using python md doc generator")

def load_distrobox_name()->str:
    cwd = os.getcwd()
    this_file_location = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(this_file_location)
    distrobox_name = ""

    try:
        with open(
            os.path.join(".", ".distrobox_name.txt"),
            "r",
            encoding="utf-8",
            newline="\n",
        ) as f:
            distrobox_name = f.read()
            distrobox_name = distrobox_name.replace("\n","")
    except Exception as err:
        print('Got error:"' + str(err) + '" while ' + "loading distrobox name from file.")
        exit(1)

    try:
        check_distrobox_name(distrobox_name)
    except Exception as err:
        print("Name in .distrobox_name.txt file is invalid.")
        print(err,"Distrobox name must match [a-zA-Z0-9][a-zA-Z0-9_.-]* pattern.")
        exit(1)

    os.chdir(cwd)
    return distrobox_name


def update_doc(platform:str , target:str, verbose:bool = False, verbose_distrobox:bool = False):
    this_file_location = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(this_file_location)

    distrobox_name = load_distrobox_name()

    v_param = ""
    d_v_param = "" # value of verbose parameter for distrobox
    if verbose:
        v_param = "--verbose"
    if verbose_distrobox:
        d_v_param = "--verbose"

    return_code = 1519#subprocess.call(f"distrobox enter {distrobox_name} {v_param} -- sudo apt {apt_v_param} install apt-file {y_param}", shell=True)
    check_return_code(return_code, "installing apt-file")

def set_up_main(args):
    print("Starting Setup")
    set_up(args.verbose, args.verbose_distrobox, args.yes, args.name)
    return

def compile_main(args):
    print("Starting Compilation")
    return

def update_doc_main(args):
    print("Starting Documantation Update")
    update_doc(args.platform, args.target, args.verbose, args.verbose_distrobox)
    return

def md_doc_main(args):
    odir = args.output
    if odir.startswith('res://'):
        this_file_location = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(this_file_location)
        odir = ".." + odir[5:]
    cwd = os.getcwd()
    odir = cwd + '/' + odir

    print("Starting Generation of MarkDown Documentation")
    generate_md_docs(odir, args.lang, args.verbose, args.color)
    return

def print_help(args):
    print("Invalid usage, try to run this program wiht `--help` parameter for more information.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="If passed, enables verbose printing.",
    )
    parser.add_argument(
        "--verbose-distrobox",
        "--verbose--d",
        action="store_true",
        help="If passed, enables verbose printing of distrobox itself.",
    )
    parser.set_defaults(func=print_help)
    subparsers = parser.add_subparsers(help='subcommand help')

    # create the parser for the "setup" command
    parser_setup = subparsers.add_parser('setup', help='If passed, program will install dependencies and generate virtual enviroments.')
    parser_setup.add_argument("--yes", "-y", action="store_true", help="If passed, program will not ask user it to continue.")
    parser_setup.add_argument("--name", "-n", default="debian-10-test", help="Name under wich distrobox will be created.")
    parser_setup.set_defaults(func=set_up_main)

    # create the parser for the "compile" command
    parser_compile = subparsers.add_parser('compile', help='Not useful yet.')
    parser_compile.add_argument("--lang", "-l", default="en", help="Language to use for section headings.")
    parser_compile.add_argument(
        "--color",
        action="store_true",
        help="If passed, force colored output even if stdout is not a TTY (useful for continuous integration).",
    )
    parser_compile.add_argument("--output", "-o", default="../", help="The directory to save output .zip files.")
    parser_compile.set_defaults(func=compile_main)

    # create the parser for the "update_doc" command
    parser_compile = subparsers.add_parser('update_doc', help='Udates .xml documentation based on source files. Then you can edit it manually.')
    parser_compile.add_argument("--platform", "-p", default="linux", help="Platform to use for documentation update, define if default value bild does not compile.")
    parser_compile.add_argument("--target", "-t", default="template_debug", help="Target to use for documentation update.")
    parser_compile.set_defaults(func=update_doc_main)

    # create the parser for the "md_doc" command
    parser_compile = subparsers.add_parser('md_doc', help='Generates markdown documentation files.')
    parser_compile.add_argument("--lang", "-l", default="en", help="Language to use for section headings.")
    parser_compile.add_argument(
        "--color",
        action="store_true",
        help="If passed, force colored output even if stdout is not a TTY (useful for continuous integration).",
    )
    parser_compile.add_argument("--output", "-o", default="res://markdown_doc/", help="The directory to save output .md files.")
    parser_compile.set_defaults(func=md_doc_main)
    
    args = parser.parse_args()
    args.func(args)
    return

if __name__ == '__main__':
    main()