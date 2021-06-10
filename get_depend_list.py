#!/bin/python

import re
import yaml
import os
import sys

def ReadBuildYaml(repo):
    yaml_file_dir = repo
    with open(yaml_file_dir + "/BUILD.yaml", "r", encoding = "utf-8") as file:
        file_stream = file.read()
    yaml_root = yaml.load(file_stream, yaml.FullLoader)
    return yaml_root

def GetDependLists(yaml_root):
    depend_lists = []
    result = ""
    for label in yaml_root["BUILD_TARGET"]:
        if not yaml_root[label].__contains__("DEPS"):
            continue
        depends = yaml_root[label]["DEPS"]
        for d in depends:
            repo_url = d["REPO"]
            branch = d["BRANCH"]
            #repo_dir = re.findall(r"git@code.devops.xiaohongshu.com:(.+?).git", repo_url)
            depend_lists.append((repo_url, branch))
            result += repo_url + " " + branch + "\n"
            #print (repo_url, branch)
    print (result)
    return depend_lists


if __name__ == "__main__":
    yaml_dir = sys.argv[1]
    yaml_root = ReadBuildYaml(yaml_dir)
    GetDependLists(yaml_root)
