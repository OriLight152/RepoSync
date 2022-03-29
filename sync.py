import sys,os,time,logging,json,shutil
from pymysql import NULL
from pyparsing import Or
import requests
import sqlite3

root_path = os.path.dirname((os.path.abspath(__file__)))
github_api = "https://api.github.com"
github_base = "https://github.91chi.fun/https://github.com"
bark_url = "http://push.api.amarea.cn/w7Wa4cZqemGL3T3Gs3S6u4/"
log_file = "sync.log"
conn = sqlite3.connect('repo.db')

def main(argv=None):
    LogInit()
    logging.info("————————————")
    logging.info("同步程序开始执行")
    repos = GetRepoList()
    logging.info(f"在数据库中读取到{len(repos)}个repo")
    for repo_data in repos:
        CheckRepo(repo_data[0],repo_data[1],repo_data[2],repo_data[3])
    logging.info("同步程序执行完毕")
    logging.info("————————————")
    conn.close()

def GetRepoList():
    sql_query = "SELECT * FROM repo"
    data = conn.execute(sql_query)
    return list(data.fetchall())

def GetTagName(repo):
    response = requests.get(f"{github_api}/repos/{repo}/releases/latest")
    return response.json()["tag_name"]

def CheckRepo(repo,repo_name,sync_folder,local_tag):
    tag_name = GetTagName(repo)
    if tag_name != local_tag :
        logging.info(f"{repo} 最新版本 {tag_name} 本地版本 {local_tag}")
        logging.info(f'尝试同步 {repo} 的 {tag_name} 版本')
        SaveRepo(repo,repo_name,sync_folder,tag_name)
    else:
        logging.info(f"{repo} 最新版本 {tag_name} 本地版本 {local_tag} 无需更新")

def SaveRepo(repo,repo_name,sync_folder,tag):
    os.system(f"git clone -b {tag} --depth=1 {github_base}/{repo}")
    if not os.path.exists(f"{root_path}/lib"): 
        os.mkdir(f"{root_path}/lib")
    if not os.path.exists(f"{root_path}/lib/{repo_name}"): 
        os.mkdir(f"{root_path}/lib/{repo_name}")
    try:
        if sync_folder == None or sync_folder == "":
            os.rename(f"{root_path}/{repo_name}",f"{root_path}/lib/{repo_name}/{tag}")
        else:
            os.rename(f"{root_path}/{repo_name}/{sync_folder}",f"{root_path}/lib/{repo_name}/{tag}")
            # shutil.rmtree(f"{root_path}/{repo_name}")
        conn.execute(f"UPDATE repo SET local_tag = '{tag}' WHERE repo = '{repo}'")
        conn.commit()
        data = {"title":"LibSync","body":f"已同步 {repo_name} 的 {tag} 版本"}
        response = requests.post(url=bark_url,data=data)
        str = json.loads(response.text)
        if str['message'] == "success":
            logging.info("通知推送成功")
        else:
            logging.warning("通知推送失败")
    except Exception as e:
        logging.exception(e)

def LogInit():
    logger_raw = logging.getLogger()
    logger_raw.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s]: %(message)s")
    formatter.converter = lambda x: time.localtime(x + 28800 + time.timezone)
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(formatter)
    logger_raw.addHandler(console_handler)
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger_raw.addHandler(file_handler)
    except:
        ...

if __name__ == "__main__":
    sys.exit(main())