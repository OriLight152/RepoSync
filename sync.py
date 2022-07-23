import sys, os, time, logging, shutil, json
import requests, tarfile

ROOT_PATH = os.path.dirname((os.path.abspath(__file__)))
GITHUB_API_BASE = "https://api.github.com"
GITHUB_BASE = "https://github.com"
GITHUB_PROXY = "https://github.91chi.fun/https://github.com"
BARK_URL = "https://api.day.app/yourkey/"
DATABASE_FILE = 'repos.json'
LOG_FILE = "sync.log"


def main(argv=None):
    LogInit()
    logging.info("————————————")
    logging.info("同步程序开始执行")
    repos = GetRepoList()
    if repos != None:
        logging.info(f"在数据库中读取到{len(repos)}个repo")
        for repo_data in repos:
            CheckRepo(repo_data)
    logging.info("同步程序执行完毕")
    logging.info("————————————")


def GetRepoList():
    sql_query = "SELECT * FROM repo"
    try:
        conn = sqlite3.connect('repo.db')
        data = conn.execute(sql_query).fetchall()
    except:
        logging.warning("数据库错误或无数据")
        conn.close()
        return None
    conn.close()
    return list(data)


def GetTagName(repo):
    response = requests.get(f"{GITHUB_API_BASE}/repos/{repo}/releases/latest")
    return response.json()["tag_name"]


def UpdateLocalTag(repo, new_tag):
    try:
        conn = sqlite3.connect('repo.db')
        conn.execute(
            f"UPDATE repo SET local_tag = '{new_tag}' WHERE repo = '{repo}'")
        conn.commit()
        conn.close()
    except Exception as e:
        logging.warning("本地tag更新失败")
        logging.exception(e)


def CheckRepo(repo_data):
    repo = repo_data[0]
    repo_name = repo_data[1]
    sync_type = repo_data[2]
    sync_release_file = repo_data[3]
    sync_folder = repo_data[4]
    local_tag = repo_data[5]
    tag_name = GetTagName(repo)
    if tag_name != local_tag:
        logging.info(f"{repo} 最新版本 {tag_name} 本地版本 {local_tag}")
        logging.info(f'尝试同步 {repo} 的 {tag_name} 版本')
        if sync_type == 1:
            SaveRepoViaClone(repo, repo_name, sync_folder, tag_name)
        elif sync_type == 2:
            SaveRepoViaRelease(repo, repo_name, sync_release_file, sync_folder,
                               tag_name)
    else:
        logging.info(f"{repo} 最新版本 {tag_name} 本地版本 {local_tag} 无需更新")


def SaveRepoViaClone(repo, repo_name, sync_folder, tag):
    os.system(f"git clone -b {tag} --depth=1 {GITHUB_PROXY}/{repo}")
    if not os.path.exists(f"{ROOT_PATH}/lib"):
        os.mkdir(f"{ROOT_PATH}/lib")
    if not os.path.exists(f"{ROOT_PATH}/lib/{repo_name}"):
        os.mkdir(f"{ROOT_PATH}/lib/{repo_name}")
    try:
        if sync_folder == None or sync_folder == "":
            os.rename(f"{ROOT_PATH}/{repo_name}",
                      f"{ROOT_PATH}/lib/{repo_name}/{tag}")
        else:
            os.rename(f"{ROOT_PATH}/{repo_name}/{sync_folder}",
                      f"{ROOT_PATH}/lib/{repo_name}/{tag}")
            # shutil.rmtree(f"{root_path}/{repo_name}")
        UpdateLocalTag(repo, tag)
        BarkPush("RepoSync", f"已同步 {repo_name}@{tag}")
    except Exception as e:
        logging.warning(f"{repo}的同步出现错误")
        logging.exception(e)


def SaveRepoViaRelease(repo, repo_name, sync_release_file, sync_folder, tag):
    try:
        response = requests.get(f"{GITHUB_API_BASE}/repos/{repo}/releases/latest")
        for asset in response.json()["assets"]:
            f_url = asset["browser_download_url"].replace(
                GITHUB_BASE, GITHUB_PROXY)
            if os.path.basename(f_url) == sync_release_file:
                r = requests.get(f_url, allow_redirects=True)
                with open(sync_release_file, 'wb') as f:
                    f.write(r._content)
                    f.close()
                tarExt(sync_release_file, repo_name)
                os.remove(f"./{sync_release_file}")
                if not os.path.exists(f"{ROOT_PATH}/lib"):
                    os.mkdir(f"{ROOT_PATH}/lib")
                if not os.path.exists(f"{ROOT_PATH}/lib/{repo_name}"):
                    os.mkdir(f"{ROOT_PATH}/lib/{repo_name}")
                if sync_folder == None or sync_folder == "":
                    os.rename(f"{ROOT_PATH}/{repo_name}",
                              f"{ROOT_PATH}/lib/{repo_name}/{tag}")
                else:
                    os.rename(f"{ROOT_PATH}/{repo_name}/{sync_folder}",
                              f"{ROOT_PATH}/lib/{repo_name}/{tag}")
                    shutil.rmtree(f"{ROOT_PATH}/{repo_name}")
                UpdateLocalTag(repo, tag)
                BarkPush("RepoSync", f"已同步 {repo_name}@{tag}")
                break
    except Exception as e:
        logging.warning(f"{repo}的同步出现错误")
        logging.exception(e)


def tarExt(filename, folder):
    try:
        r_file = tarfile.open(filename)
        r_file.extractall(path=f"./{folder}/")
        r_file.close()
        return True
    except Exception as e:
        logging.exception(e)
        return False


def BarkPush(title, message):
    try:
        data = {"title": f"{title}", "body": f"{message}"}
        response = requests.post(url=BARK_URL, data=data)
        if response.json()['message'] == "success":
            logging.info("通知推送成功")
        else:
            logging.warning("通知推送失败")
    except Exception as e:
        logging.warning("通知推送失败")
        logging.exception(e)


def LogInit():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s]: %(message)s")
    formatter.converter = lambda x: time.localtime(x + 28800 + time.timezone)
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    try:
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except:
        ...


if __name__ == "__main__":
    sys.exit(main())