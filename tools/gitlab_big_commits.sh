#!/bin/bash

# 设置阈值
THRESHOLD=5000

# 临时变量
commit=""
author=""
date=""
add=0
del=0

# 解析 git log 输出
git log --numstat --pretty=format:"%H %an %ad" --date=short | while read line; do
    if [[ $line =~ ^[a-f0-9]{40} ]]; then
        # 如果是提交哈希，先检查上一个提交是否超过阈值
        if (( add + del > THRESHOLD )); then
            echo "$commit $author $date Total Changes: $((add + del))"
        fi
        # 保存新的提交信息
        commit=$(echo "$line" | awk '{print $1}')
        author=$(echo "$line" | awk '{print $2}')
        date=$(echo "$line" | awk '{print $3}')
        # 重置统计变量
        add=0
        del=0
    elif [[ $line =~ ^[0-9]+[[:space:]]+[0-9]+ ]]; then
        # 如果是文件改动行数记录，累加新增和删除行数
        add=$((add + $(echo "$line" | awk '{print $1}')))
        del=$((del + $(echo "$line" | awk '{print $2}')))
    fi
done

# 检查最后一个提交是否超过阈值
if (( add + del > THRESHOLD )); then
    echo "$commit $author $date Total Changes: $((add + del))"
fi


# cat big_commits.txt | awk '{sum += $NF} END {print "Total Sum:", sum}'