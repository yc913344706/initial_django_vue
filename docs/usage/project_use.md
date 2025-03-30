## 如何项目使用

```bash
git clone https://your-git-repo/your-project.git project_dir

# 克隆项目
project_dir="your_project_dir"
git clone https://github.com/yc913344706/initial_django_vue.git && \
mv initial_django_vue/* initial_django_vue/.gitignore $project_dir/ && \
rm -rf initial_django_vue

cd project_dir
git add .
git commit -m "Initial commit" --allow-empty

./bin/debug_backend_docker.sh -E dev
./bin/debug_frontend_docker.sh -E dev
./bin/start_backend_api_doc.sh

git push
```
