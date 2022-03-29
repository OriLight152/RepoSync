import sqlite3

conn = sqlite3.connect("repo.db")
conn.execute("CREATE TABLE IF NOT EXISTS repo (repo TEXT PRIMARY KEY,repo_name TEXT,sync_folder TEXT,local_tag TEXT);")
sql_insert = "INSERT INTO repo (repo, repo_name, sync_folder, local_tag) values(?, ?, ?, ?)"
data=("alist-org/alist-web","alist-web","","0")
conn.execute(sql_insert,data)
conn.commit()
conn.close()