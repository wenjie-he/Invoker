import yaml
import git
import os
import re
from git import Repo

# 读入传入的yaml路径 文件列表参数$1
# 遍历路径读取yaml文件 获取depend配置
# 根据depend分析依赖关系，去除递进式的依赖A->B C, B->C，那么只需要A->B B->C
# 根据具体的依赖关系开始生成Makefile并存放在对应的目录中
def ReadBuildYaml(repo):
    yaml_file_dir = repo[0]
    with open("/codebase/" + yaml_file_dir + "/BUILD.yaml", "r", encoding = "utf-8") as file:
        file_stream = file.read()
    yaml_root = yaml.load(file_stream, yaml.FullLoader)
    return yaml_root

def GetDependLists(yaml_root):
    depend_lists = []
    for label in yaml_root["BUILD_TARGET"]:
        if not yaml_root[label].__contains__("DEPS"):
            continue
        depends = yaml_root[label]["DEPS"]
        for d in depends:
            depend_lists.append((d["REPO"], d["BRANCH"]))
    
    return depend_lists

def GetLocalRepoInfo():
    return ("git@code.devops.xiaohongshu.com:meow.git", "master")

def GetDirFromUrl(url_str):
    match = re.findall(r"git@code.devops.xiaohongshu.com:(.+?).git", url_str)
    return match

def FetchRepo(repo_tuple):
    remote_url = repo_tuple[0]
    repo_branch = repo_tuple[1]
    repo_dir = "/codebase/" + GetDirFromUrl(remote_url)[0]
    repo = git.Repo
    if not os.path.exists(repo_dir):
        repo = git.Repo.clone_from(url = remote_url, to_path = repo_dir, branch = "master")
    else:
        repo = git.Repo(repo_dir)
    repo_branches = []
    for b in repo.branches:
        repo_branches.append(b.name)
    if repo_branch not in repo.branches:
        print (repo_branch)
        print (repo_branches)
        #repo = git.Repo.clone_from(url = remote_url, to_path = repo_dir, branch = repo_branch)
        repo.git.checkout(repo_branch)
    branch_repo_dir = repo_dir
    if  repo.active_branch.name != repo_branch:
        branch_repo_dir = repo_dir + "_" + repo_branch
        if os.path.exists(branch_repo_dir):
            repo.git.pull()
        else:
            repo = git.Repo.clone_from(url = repo_dir, to_path = branch_repo_dir, branch = repo_branch)


    return True



if __name__ == '__main__':
    argv = sys.argv
    print (argv)
    # read all depend library

    depend_map = {}
    for repo in argv:
        depend_map[repo] = GetDependLists(repo)

    dependee_map = {}
    for repo in depend_map:
        for depend_repo in depend_map[repo]:
            if not dependee_map.__contains__(depend_repo):
                dependee_map[depend_repo] = []
            dependee_map[depend_repo].append(repo)

    success = True
    current_pr = 0
    prority_map = []
    depend_map_temp = depend_map.copy()
    while len(depend_map_temp) > 0:
        empty_list = []
        for repo in dependee_map:
            if len(dependee_map[repo]) == 0:
                empty_list = dependee_map[repo]
        # 剩下的无法形成依赖分析  出错
        if len(empty_list) == 0:
            success = false
            break
        for e in empty_list:
            prority_map[e] = current_pr
            depend_map.pop(e)
            for r in dependee_map[e]:
                depend_map_temp.pop(r)
        ++current_pr

    if not success:
        exit()

    # prority_map是依赖的优先级
