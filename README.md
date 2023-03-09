
## This is a build system that uses Cython to compile Python code into C extensions.

### It supports compiling individual modules or an entire project. The system is built to use distutils and cython packages, and it includes the ability to create a binary executable from the compiled files using makeself.

## Requirements

### This build system requires distutils, cython, pathlib, and json libraries. Please make sure you have them installed.
### Usage

- Clone the repository.
- copy app root folder to ./applications
- Edit the ./applications/config.json file to list your app root folders.
The format for the config file is simple
```json
    {
    "1": "another_app_directory_name",
    "2": "another_app_directory_name",
    ...
}
```
- Run either run.sh (python <= 3.10) or run_py311.sh (python 3.11)
- Choose the project ID number from the list of available projects.
- The system will compile the modules and produce the C extensions.
- Optionally, build an executable binary file from the compiled C extensions using makeself.

### Compilation

 The system will ask if you want to compile the app with Cython. If you choose "y", it will compile the app and produce the C extensions in the cython_output folder. If you choose "n", it will use the existing C extensions in the cython_output folder.

### Executable Binary

The system will ask if you want to make an executable binary from the compiled files. If you choose "y", it will create an executable binary file in the build folder. If you choose "n", it will not create an executable binary. This binary is a self extracting archive made with makeself.

The executable will be located under ./bin
