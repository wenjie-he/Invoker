recurse_dir_list=(`pwd`)
exsit_list=()

while [[ ${#recurse_dir_list[*]} -gt 0 ]];do
    temp_list=()
    for value in "${recurse_dir_list[@]}"
    do
        echo "find : "$value
        #判断value是否已经遍历过了，是的话就跳过
        if [[ "${exsit_list[@]}" =~ "$value" ]]; then
            break
        fi
        exsit_list+=($value)
        # python 读取repo 中的yaml文件的依赖项
        # 打印出依赖的库目录和依赖分支
        # 脚本根据支去输出依赖文件
        depend_result=`python ./get_depend_list.py $value`
        for d in "${depend_result[@]}"
        do
            # d格式为repo + branch，示例:lianjin/libtest master
            # 判断depend是否已经存在了
            repo_url=`echo $d | awk -F " " '{print $1}'`
            branch=`echo $d | awk -F " " '{print $2}'`
            local_dir=`echo $repo_url | awk -F ':' '{print $2}' | awk -F ".git" '{print $1}'`
            local_dir="~/codebase/"$local_dir
            # 判断本地是否存在repo和branch，不存在则创建
            if [ ! -d $local_dir ];then
                git clone -b $branch $repo_url $local_dir
            else
                current_branch=`cd $local_dir && git symbolic-ref --short -q HEAD`
                if [ "$current_branch" != "$branch" ]; then
                    branch_repo_dir=$local_dir"_"$branch
                    cd $local_dir && git fetch origin $branch:$branch
                    if [ ! -d $branch_repo_dir ];then
                        git clone -b $branch $local_dir $branch_repo_dir
                    fi
                    cd $branch_repo_dir && git fetch origin $branch
                    local_dir=$branch_repo_dir
                fi
            fi
            
            # $local_dir即是真正依赖的库的分支路径
            if [[ "${exsit_list[@]}" =~ "$local_dir" ]]; then
                temp_list+=($local_dir)
            fi
        done
    done
    recurse_dir_list=(`echo ${temp_list[*]}`)
done

echo "repo list : "${exsit_list[*]}
# exist_list是这个编译过程需要的所有的yaml绝对路径
# 上面的步骤获取编译链需要的所有的yaml文件
# 接下来根据python脚本根据yaml文件去分析依赖项，并输出Makefile

