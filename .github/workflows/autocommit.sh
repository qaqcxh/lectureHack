#!/bin/bash

# 由于github对文件大小有限制，超过100M将不能push，所以ignore这些文件
basename $(find  -type f -size +100M) > $(pwd)/.gitignore
echo "__pycache__" >> $(pwd)/.gitignore
echo ".gitignore" >> $(pwd)/.gitignore
cat .gitignore

# 提交
git config --global user.email "actions@github.com"
git config --global user.name "github Actions"
git config --global core.quotepath false
git add --all
if [ -n $(git diff) ]; then
    git commit -m "auto commit: new lectures are added"
    git push
    echo "lectures are updated!"
fi 
