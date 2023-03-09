# Import required libraries
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import os
from pathlib import Path
import sys
import json
import traceback

# Get the version of Python being used
py_ver = sys.version.split('.')[0] + '.' + sys.version.split('.')[1]
print(f"Python version used to compile: {py_ver}")

# Ask user if they want to compile the app with Cython
run_compile = False
if input('Compile app with Cython? (y/n)').lower() == 'y':
    run_compile = True

# Ask user if they want to make an executable binary from compiled files
build = False
do_build_app = input('Make an executable binary from compiled files? (y/n)')
if do_build_app.lower() == 'y':
    build = True


# List available projects from the applications directory
def list_from_json():
    instructions = False
    if os.path.isdir("applications"):
        if os.path.isfile("applications/config.json"):
            with open("applications/config.json") as appslist:
                res = json.load(appslist)
                return res
        else:
            instructions = True
    else:
        instructions = True
        os.mkdir('applications')

    if instructions:
        print("Missing config.json file in applications directory")
        print("Creating file now. Add app root folder to applications directory and edit config.json")
        mkconf = {"1": "appname", "2": "another_appname"}
        with open('applications/config.json', 'w') as conf:
            json.dump(mkconf, conf)
        return None


# Create the cython_output directory if it doesn't already exist
if os.path.isdir("cython_output") is False:
    os.mkdir("cython_output")

# Get the list of available projects
projects_available = list_from_json()

print("Choose Project ID Number: ")
d_apps = projects_available
try:
    # Print the available projects for the user to choose from
    for k, v in d_apps.items():
        print(k, v)
except Exception:
    print(traceback.format_exc())

home = str(Path.home())

# Get the project name from the user
project_name = d_apps[str(input("Project ID: "))]
ext_modules = []
test_modules = []

if project_name in projects_available:
    print(f"Project name: {project_name}")


# Prepare for building the app
def prep_build():
    if os.path.isdir(f'{project_name}'):
        os.system(f'rm -Rf {project_name}')
    # os.mkdir(f'{project_name}')
    os.system(f'cp -Rf applications/{project_name} ./')
    os.system(f'rm {project_name}/main.py')
    # move this file to parent
    os.system('cp compile.py applications/compile_backup.py')
    # remove old build
    os.system(f'rm -Rf cython_output/{project_name}')


# Remove unnecessary files from the app release folder
def clean_release(cmd):
    os.system(cmd)


# Get the name and path of the module to be built
def get_module_data(f, sub_level_dirs):
    module_name = ''
    pathstr = ''
    if len(f) > 0:
        if '.py' in f:
            if 'compile.py' not in f:
                file_name = f.split('.')[0]
                if f'{project_name}.py' in f:
                    module_name = f"""{file_name}"""
                else:
                    if len(sub_level_dirs[0].split('/')) > 2:
                        module_name = f"""{sub_level_dirs[0].split('/')[1]}.{sub_level_dirs[0].split('/')[2]}.{file_name}"""
                    else:
                        if len(sub_level_dirs[0].split('/')) > 1:
                            module_name = f"""{sub_level_dirs[0].split('/')[1]}.{file_name}"""
                pathstr = f"""{sub_level_dirs[0]}/{f}"""
    return [module_name, pathstr]


def build_modules():
    top_level_dirs = [x[0] for x in os.walk(".") if 'pycache' not in x[0] and 'applications' not in x[0]]
    for d in top_level_dirs:
        sub_level_dirs = [xx[0] for xx in os.walk(d) if 'pycache' not in xx[0]]
        for f1 in os.listdir(sub_level_dirs[0]):
            moduledata = get_module_data(f1, sub_level_dirs)
            if len(moduledata[0]) > 0:
                ext_modules.append(Extension(moduledata[0], [moduledata[1]]))
                test_modules.append([moduledata[0], [moduledata[1]]])


def build():
    for e in ext_modules:
        e.cython_directives = {'language_level': "3"}
    setup(
        name=f"{project_name}",
        cmdclass={'build_ext': build_ext},
        ext_modules=ext_modules
    )


def cleanup():  # cleanup app release folder
    appfile = ''
    clean_release(f"find .{project_name} -name '*.py' ! -name 'compile.py' -exec rm -Rf {{}} + ")
    clean_release(f"find .{project_name} -name '*__pycache__*' -exec rm -Rf {{}} + ")
    clean_release(f"find .{project_name} -name '*.c' -exec rm -Rf {{}} + ")
    dirs = [fz[0] for fz in os.walk(".")]
    for d in dirs:
        if os.path.isdir(d):
            for file in os.listdir(d):
                # print(fi)
                if file != 'compile.py':
                    if '.so' in file:
                        print(file)
                        rename = file.split('.')[0] + '.so'

                        if f'{project_name}.so' == rename:
                            os.system(f'mv {file} {rename}')
                            appfile = rename
                        else:
                            os.system(f'mv {d}/{file} {d}/{rename}')
    print("APPFILE---", appfile)
    return appfile


def post_build():
    appfile = cleanup()
    print('appfile:', appfile)
    if len(appfile) > 0:
        os.system(f'mv {appfile} {project_name}/{appfile}')
        mainpy = f"""# -*- coding: utf-8 -*- \nimport {project_name} \n{project_name}.run()"""
        run_sh = f"""#!/bin/bash\npython{py_ver} main"""

        with open(f'{project_name}/main', 'w+') as pyfile:
            pyfile.write(mainpy)
        with open(f'{project_name}/main.py', 'w+') as pyfile:
            pyfile.write(mainpy)
        with open(f'{project_name}/run.sh', 'w+') as shfile:
            shfile.write(run_sh)

    os.system(f'chmod +x {project_name}/main')
    os.system(f'chmod +x {project_name}/run.sh')
    os.system("rm -Rf build")
    if os.path.isdir(f'cython_output/{project_name}'):
        os.system(f"rm -Rf cython_output/{project_name}")
    os.system(f"cp -Rf {project_name} cython_output/{project_name}")
    os.system(f"rm -Rf {project_name}")


if run_compile:
    # Prepare build
    print("Starting...be patient.")
    prep_build()

    # Remove docs and git data
    clean_release(f"rm -Rf {project_name}/docs")
    clean_release(f"rm -rf {project_name}/.git {project_name}/.gitignore")

    # rename main to {project_name}
    os.system(f"cp applications/{project_name}/main.py {project_name}/{project_name}.py")

    # Build project modules and paths
    build_modules()

    # build and compile
    build()

    # cleanup post build
    post_build()

    print(f"Done compiling {project_name}... cython program files are located in ./cython_output/{project_name}")
else:
    print("Please specify project name as existing project and try again! Goodbye...")

if build:
    if os.path.isdir("build"):
        if os.path.isdir(f'build/{project_name}'):
            os.system(f'rm -Rf build/{project_name}')
    else:
        os.system("mkdir build")

    os.system(f"cp -Rf cython_output/{project_name} build/{project_name}")
    print("Building...")
    if os.path.isdir("dist"):
        os.system(f'rm -Rf dist')
    os.system("mkdir dist")

    os.system(f"makeself/makeself.sh --nox11 --nocomp build/{project_name} dist/{project_name} '{project_name}' ./run.sh")

    os.system(f"""rm -Rf build/output/{project_name}""")
    if os.path.isdir("bin"):
        if os.path.isfile(f"bin/{project_name}"):
            os.system(f"rm -Rf bin/{project_name}")
    else:
        os.system("mkdir bin")
    os.system(f"""cp dist/{project_name} bin/{project_name}""")

    os.system(f"rm -Rf {project_name}")

    os.system("""rm -Rf build""")
    os.system("""rm -Rf dist""")

    print('Finished building. Executable can be found in ./bin')
    print("Goodbye...")


else:
    print('Not building. Goodbye...')
