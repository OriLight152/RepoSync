import sqlite3

# repo 用户名/仓库名
# repo_name 仓库名
# sync_type 同步方式 1:克隆源代码 2:下载release
# sync_release_file 指定下载的release文件名称
# sync_folder 指定保留的文件夹
# local_tag 本地版本

conn = sqlite3.connect("repo.db")
conn.execute("CREATE TABLE IF NOT EXISTS repo (repo TEXT PRIMARY KEY,repo_name TEXT,sync_type INT,sync_release_file TEXT,sync_folder TEXT,local_tag TEXT);")

sql_insert = "INSERT INTO repo (repo, repo_name, sync_type, sync_release_file, sync_folder, local_tag) values(?, ?, ?, ?, ?, ?)"
data=("alist-org/alist-web","alist-web","1","","","")
conn.execute(sql_insert,data)
conn.commit()
conn.close()