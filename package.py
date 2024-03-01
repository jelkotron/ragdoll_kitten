#!/usr/bin/python3
import sys
import os
import zipfile
import ast

SOURCE_FOLDER = "src"
TARGET_FOLDER = "packages"
README_NAME = 'README.md'
LICENSE_NAME = 'LICENSE'


def addon_version_get(init):
    
    with open(init, 'r') as file:
        node = ast.parse(file.read())

        for child in ast.walk(node):
            for b in child.body:
                if isinstance(b, ast.Assign) and isinstance(b.value, ast.Dict) and (
                        any(t.id == 'bl_info' for t in b.targets)):
                    bl_info_dict = ast.literal_eval(b.value)
                    return bl_info_dict['version']

    raise ValueError('Cannot find bl_info')


def src_info_get(source_dir, target_dir):
    dir = sys.path[0]
    src_info = {}
    if os.path.exists(os.path.join(dir, source_dir)):
            addon_name = (os.path.split(dir)[-1])
            src_info["addon_name"] = addon_name

            zip_name = os.path.join(addon_name, ".zip")

            src_info["zip_name"] = zip_name
            src_info["links"] = {}
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    source = os.path.join(root, file)
                    root = os.path.split(root)[-1]
                    target = os.path.join(addon_name, file)
                    if root != os.path.split(source_dir)[-1]:
                        target = os.path.join(addon_name, root, file)
                    
                    if file == '__init__.py':
                        major, minor, patch = addon_version_get(source)
                        version = "-%s.%s.%s"%(major, minor, patch)
                        src_info["version"] = version
                        if version:
                            zip_name = addon_name + version + ".zip"

                    if file == 'README.md':
                        src_info["readme"] = {source: target}

                    if file == 'LICENCSE':
                        src_info["license"] = {source: target}
            
                    src_info["links"][source] = target

            if not "readme" in src_info.keys():
                if os.path.exists(os.path.join(dir, 'README.md')):
                    source = os.path.join(dir, 'README.md')
                    target = os.path.join(src_info["addon_name"], 'README.md')
                    src_info["links"][source] = target

            if not "license" in src_info.keys():
                if os.path.exists(os.path.join(dir, 'LICENSE')):
                    source = os.path.join(dir, 'LICENSE')
                    target = os.path.join(src_info["addon_name"], 'LICENSE')
                    src_info["links"][source] = target
                    


            if target_dir != None:
                zip_name = os.path.join(target_dir, zip_name)
            
            src_info["zip_name"] = zip_name
    
    return src_info


def compress():
    dir = sys.path[0]
    source_dir = None
    target_dir = None

    if len(sys.argv) > 1:
        source_dir = os.path.abspath(sys.argv[1])
    
    if len(sys.argv) > 2:
        target_dir = os.path.abspath(sys.argv[2])

    if not source_dir:
        if os.path.isdir(os.path.join(dir, SOURCE_FOLDER)):
            source_dir = os.path.join(dir, SOURCE_FOLDER)
    
    if not target_dir:
        target_dir = os.path.join(dir, TARGET_FOLDER)
    
    if not os.path.isdir(target_dir):
        os.makedirs(target_dir)
    
    if source_dir and target_dir:
        if os.path.isdir(os.path.join(dir, source_dir)):
            info = src_info_get(source_dir, target_dir)
        
            zip_file = zipfile.ZipFile(info["zip_name"], 'w', zipfile.ZIP_DEFLATED)
            
            for source, target in info["links"].items():
                zip_file.write(source, target)        
            
            zip_file.close()


if __name__ == '__main__':
    compress()