import requests
import os
import subprocess
import csv
import json
import base64
import shutil
import time
import stat
from pathlib import Path
from nacl import encoding, # ----------------# ---------------# -----------------------------
# Push 文件到仓库（简化版）
# -----------------------------
def push_files(token, username, repo_name, files, keywords_path):
    repo_url = f"https://{username}:{token}@github.com/{username}/{repo_name}.git"
    tmp_dir = Path(f"./tmp_{repo_name}")

    # 强制清理临时文件夹
    if tmp_dir.exists():
        print(f"[INFO] Cleaning up existing temp directory: {tmp_dir}")
        force_remove_dir(tmp_dir)
        time.sleep(2)  # 等待文件系统同步

    # 创建临时目录
    tmp_dir.mkdir(exist_ok=True)
    print(f"[INFO] Created temp directory: {tmp_dir}")
    
    try:
        # 初始化git仓库
        subprocess.run(["git", "init"], cwd=str(tmp_dir), check=True)
        
        # 创建 .github/workflows 文件夹
        workflows_dir = tmp_dir / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)Push 文件到仓库（直接上传版）
# -----------------------------
def push_files(token, username, repo_name, files, keywords_path):
    """直接上传指定的文件到仓库，不克隆现有内容"""
    repo_url = f"https://{username}:{token}@github.com/{username}/{repo_name}.git"
    tmp_dir = Path(f"./tmp_{repo_name}")

    # 强制清理临时文件夹
    if tmp_dir.exists():
        print(f"[INFO] Cleaning up existing temp directory: {tmp_dir}")
        force_remove_dir(tmp_dir)
        time.sleep(2)  # 等待文件系统同步

    # 创建临时目录
    tmp_dir.mkdir(exist_ok=True)
    print(f"[INFO] Created temp directory: {tmp_dir}")

    try:ush 文件到仓库（直接上传版）
# -----------------------------
def push_files(token, username, repo_name, files, keywords_path):
    repo_url = f"https://{username}:{token}@github.com/{username}/{repo_name}.git"
    tmp_dir = Path(f"./tmp_{repo_name}")

    # 强制清理临时文件夹
    if tmp_dir.exists():
        print(f"[INFO] Cleaning up existing temp directory: {tmp_dir}")
        force_remove_dir(tmp_dir)
        time.sleep(2)  # 等待文件系统同步

    # 创建临时目录并初始化git
    tmp_dir.mkdir(exist_ok=True)
    print(f"[INFO] Created temp directory: {tmp_dir}")

    try:
        # 初始化新的git仓库
        subprocess.run(["git", "init"], cwd=str(tmp_dir), check=True)
        print("[INFO] Initialized new git repository")-----------------------
# 固定工作目录到脚本所在目录
# -----------------------------
script_dir = Path(__file__).parent.resolve()
os.chdir(script_dir)

# -----------------------------
# Helper: 强制删除文件夹（Windows兼容）
# -----------------------------
def force_remove_dir(path):
    """强制删除文件夹，处理Windows权限问题"""
    if not path.exists():
        return True
    
    def handle_remove_readonly(func, path, exc):
        """处理只读文件删除"""
        if os.path.exists(path):
            os.chmod(path, stat.S_IWRITE)
            func(path)
    
    try:
        shutil.rmtree(path, onerror=handle_remove_readonly)
        print(f"[INFO] Successfully removed {path}")
        return True
    except Exception as e:
        print(f"[WARN] Failed to remove {path}: {e}")
        # 尝试使用系统命令强制删除
        try:
            if os.name == 'nt':  # Windows
                subprocess.run(['rmdir', '/s', '/q', str(path)], shell=True, check=False)
            else:  # Unix/Linux
                subprocess.run(['rm', '-rf', str(path)], check=False)
            time.sleep(1)  # 等待文件系统同步
            return True
        except Exception as e2:
            print(f"[ERROR] Force remove also failed: {e2}")
            return False

# -----------------------------
# Helper: 获取 GitHub 仓库公钥
# -----------------------------
def get_public_key(token, username, repo_name):
    url = f"https://api.github.com/repos/{username}/{repo_name}/actions/secrets/public-key"
    headers = {"Authorization": f"token {token}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json()
    else:
        print(f"[ERROR] Failed to get public key for {repo_name}: {r.json()}")
        return None

# -----------------------------
# Helper: 加密 Secret
# -----------------------------
def encrypt_secret(public_key_str, secret_value):
    public_key = public.PublicKey(public_key_str.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

# -----------------------------
# 创建仓库（如果不存在）
# -----------------------------
def create_repo(token, username, repo_name):
    url_check = f"https://api.github.com/repos/{username}/{repo_name}"
    headers = {"Authorization": f"token {token}"}
    r = requests.get(url_check, headers=headers)
    if r.status_code == 200:
        print(f"[INFO] Repo {repo_name} already exists, skipping creation.")
        return True
    url_create = f"https://api.github.com/user/repos"
    data = {"name": repo_name, "private": False, "auto_init": True}
    r2 = requests.post(url_create, headers=headers, json=data)
    if r2.status_code == 201:
        print(f"[INFO] Repository {repo_name} created successfully.")
        return True
    else:
        print(f"[ERROR] Failed to create {repo_name}: {r2.json()}")
        return False

# -----------------------------
# 上传 Secrets
# -----------------------------
def set_secret(token, username, repo_name, secret_name, secret_value):
    if not secret_value:
        return
    key_info = get_public_key(token, username, repo_name)
    if not key_info:
        return
    encrypted_value = encrypt_secret(key_info["key"], secret_value)
    url = f"https://api.github.com/repos/{username}/{repo_name}/actions/secrets/{secret_name}"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    data = {"encrypted_value": encrypted_value, "key_id": key_info["key_id"]}
    r = requests.put(url, headers=headers, json=data)
    if r.status_code in [201, 204]:
        print(f"[INFO] Secret {secret_name} set for {repo_name}")
    else:
        print(f"[ERROR] Failed to set secret {secret_name} for {repo_name}: {r.json()}")

# -----------------------------
# Git推送重试函数
# -----------------------------
def git_push_with_retry(repo_url, max_retries=3, delay=5):
    """带重试机制的Git推送"""
    for attempt in range(1, max_retries + 1):
        try:
            print(f"[INFO] Push attempt {attempt}/{max_retries}...")
            
            # 先尝试设置Git配置以避免编码问题
            subprocess.run(["git", "config", "core.quotepath", "false"], check=False)
            subprocess.run(["git", "config", "i18n.logoutputencoding", "utf-8"], check=False)
            subprocess.run(["git", "config", "i18n.commitencoding", "utf-8"], check=False)
            
            # 推送到GitHub
            push_result = subprocess.run(
                ["git", "push", "-u", "origin", "main", "--force"], 
                capture_output=True, 
                text=True, 
                encoding='utf-8',
                errors='ignore',  # 忽略编码错误
                timeout=60,  # 60秒超时
                check=True
            )
            
            print(f"[INFO] Push successful on attempt {attempt}")
            if push_result.stdout:
                print(f"[INFO] Push stdout: {push_result.stdout}")
            if push_result.stderr:
                print(f"[INFO] Push stderr: {push_result.stderr}")
            return True
            
        except subprocess.TimeoutExpired:
            print(f"[WARN] Push attempt {attempt} timed out after 60 seconds")
            if attempt < max_retries:
                print(f"[INFO] Retrying in {delay} seconds...")
                time.sleep(delay)
            continue
            
        except subprocess.CalledProcessError as e:
            print(f"[WARN] Push attempt {attempt} failed with return code {e.returncode}")
            if hasattr(e, 'stderr') and e.stderr:
                error_msg = e.stderr.lower()
                if any(keyword in error_msg for keyword in ['connection', 'network', 'timeout', 'recv failure']):
                    print(f"[WARN] Network error detected: {e.stderr}")
                    if attempt < max_retries:
                        print(f"[INFO] Retrying in {delay} seconds...")
                        time.sleep(delay)
                        delay *= 2  # 增加延迟时间
                        continue
                else:
                    print(f"[ERROR] Non-recoverable error: {e.stderr}")
                    return False
            
            if attempt < max_retries:
                print(f"[INFO] Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2
            continue
            
        except Exception as e:
            print(f"[ERROR] Unexpected error on attempt {attempt}: {e}")
            if attempt < max_retries:
                print(f"[INFO] Retrying in {delay} seconds...")
                time.sleep(delay)
            continue
    
    print(f"[ERROR] All {max_retries} push attempts failed")
    return False

# -----------------------------
# Push 文件到仓库（智能更新版）
# -----------------------------
def push_files(token, username, repo_name, files, keywords_path):
    repo_url = f"https://{username}:{token}@github.com/{username}/{repo_name}.git"
    tmp_dir = Path(f"./tmp_{repo_name}")

    # 强制清理临时文件夹
    if tmp_dir.exists():
        print(f"[INFO] Cleaning up existing temp directory: {tmp_dir}")
        force_remove_dir(tmp_dir)
        time.sleep(2)  # 等待文件系统同步

    # 创建临时目录
    tmp_dir.mkdir(exist_ok=True)
    print(f"[INFO] Created temp directory: {tmp_dir}")

    try:
        # 克隆现有仓库
        print(f"[INFO] Cloning existing repository...")
        clone_result = subprocess.run(
            ["git", "clone", repo_url, str(tmp_dir)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        # 如果克隆失败（可能是新仓库），则初始化新的仓库
        if clone_result.returncode != 0:
            print(f"[INFO] Repository doesn't exist or is empty, initializing new one...")
            subprocess.run(["git", "init"], cwd=str(tmp_dir), check=True)

    try:
        # 创建 .github/workflows 文件夹
        workflows_dir = tmp_dir / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)

        # 复制文件
        copied_files = []
        for f in files:
            f_path = Path(f)
            if not f_path.exists():
                print(f"[WARN] File not found: {f_path}")
                continue
            
            if f_path.name.endswith(".yml") or f_path.name.endswith(".yaml"):
                dest = workflows_dir / f_path.name
            else:
                dest = tmp_dir / f_path.name
            
            try:
                shutil.copy2(f_path, dest)  # 使用copy2保留元数据
                copied_files.append(str(dest.relative_to(tmp_dir)))
                print(f"[INFO] Copied {f_path.name} to {dest.relative_to(tmp_dir)}")
            except Exception as e:
                print(f"[ERROR] Failed to copy {f_path}: {e}")
                continue

        # keywords.txt 单独处理
        keywords_file = tmp_dir / "keywords.txt"
        if keywords_path and keywords_path.exists():
            try:
                shutil.copy2(keywords_path, keywords_file)
                copied_files.append("keywords.txt")
                print(f"[INFO] Copied keywords.txt")
            except Exception as e:
                print(f"[WARN] Failed to copy keywords.txt: {e}")

        if not copied_files:
            print(f"[ERROR] No files were copied for {repo_name}")
            return False

        print(f"[INFO] Total files copied: {len(copied_files)}")

        # 切换到临时目录进行Git操作
        original_cwd = os.getcwd()
        os.chdir(tmp_dir)

        try:
            # Git 初始化和配置
            print("[INFO] Initializing git repository...")
            subprocess.run(["git", "init"], capture_output=True, text=True, encoding='utf-8', errors='ignore', check=True)
            
            # 设置 Git 配置
            subprocess.run(["git", "config", "user.name", "Administrator"], check=True)
            subprocess.run(["git", "config", "user.email", "admin@example.com"], check=True)
            subprocess.run(["git", "config", "core.autocrlf", "true"], check=False)  # 处理换行符
            subprocess.run(["git", "config", "core.safecrlf", "false"], check=False)  # 避免换行符警告

            # 检查文件状态（忽略编码错误）
            try:
                status_result = subprocess.run(["git", "status", "--porcelain"], 
                                             capture_output=True, text=True, 
                                             encoding='utf-8', errors='ignore', check=True)
                print(f"[INFO] Git status:\n{status_result.stdout}")
            except:
                print("[INFO] Git status check completed (with encoding issues)")

            # 添加文件
            print("[INFO] Adding files to git...")
            subprocess.run(["git", "add", "."], capture_output=True, text=True, encoding='utf-8', errors='ignore', check=True)
            
            # 检查添加后的状态
            try:
                status_result = subprocess.run(["git", "status", "--porcelain"], 
                                             capture_output=True, text=True,
                                             encoding='utf-8', errors='ignore', check=True)
                print(f"[INFO] Git status after add:\n{status_result.stdout}")
            except:
                print("[INFO] Git status after add completed (with encoding issues)")

            # 提交
            print("[INFO] Committing changes...")
            commit_result = subprocess.run(["git", "commit", "-m", "Add workflow and files"], 
                                         capture_output=True, text=True,
                                         encoding='utf-8', errors='ignore', check=True)
            print(f"[INFO] Commit completed")

            # 设置主分支
            subprocess.run(["git", "branch", "-M", "main"], check=True)

            # 移除可能存在的remote并添加新的
            subprocess.run(["git", "remote", "remove", "origin"], capture_output=True, check=False)
            subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)

            # 使用重试机制推送到GitHub
            print("[INFO] Pushing to GitHub with retry mechanism...")
            if git_push_with_retry(repo_url):
                print(f"[INFO] Successfully pushed files to {repo_name}")
                return True
            else:
                print(f"[ERROR] Failed to push files to {repo_name}")
                return False

        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Git command failed: {e}")
            print(f"[ERROR] Command: {e.cmd}")
            print(f"[ERROR] Return code: {e.returncode}")
            if hasattr(e, 'stdout') and e.stdout:
                print(f"[ERROR] Stdout: {e.stdout}")
            if hasattr(e, 'stderr') and e.stderr:
                print(f"[ERROR] Stderr: {e.stderr}")
            return False
        finally:
            # 确保切换回原目录
            os.chdir(original_cwd)

    except Exception as e:
        print(f"[ERROR] Exception in push_files: {e}")
        return False
    finally:
        # 清理临时文件夹
        os.chdir(script_dir)
        if tmp_dir.exists():
            print(f"[INFO] Cleaning up temp directory: {tmp_dir}")
            force_remove_dir(tmp_dir)

# -----------------------------
# 读取 CSV
# -----------------------------
def read_csv(csv_path):
    try:
        with open(csv_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            return [row for row in reader]
    except Exception as e:
        print(f"[ERROR] Failed to read CSV: {e}")
        return []

# -----------------------------
# 写回 CSV
# -----------------------------
def write_csv(csv_path, data, fieldnames):
    try:
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    except Exception as e:
        print(f"[ERROR] Failed to write CSV: {e}")

# -----------------------------
# 主函数
# -----------------------------
if __name__ == "__main__":
    print("[INFO] Script started")
    csv_file = Path("github_accounts.csv")
    accounts = read_csv(csv_file)
    if not accounts:
        print("[ERROR] No accounts found, exiting")
        exit()

    # 检查要上传的文件
    upload_folder = Path("需要上传的文件")
    if not upload_folder.exists():
        print(f"[ERROR] Upload folder not found: {upload_folder}")
        exit()
    
    files_to_upload = list(upload_folder.glob("*"))
    files_to_upload = [f for f in files_to_upload if f.is_file()]  # 只包含文件，不包含文件夹
    print(f"[INFO] Found {len(files_to_upload)} files to upload: {[f.name for f in files_to_upload]}")

    if not files_to_upload:
        print("[WARN] No files found to upload")
        
    success_count = 0
    total_count = len(accounts)

    for i, account in enumerate(accounts, 1):
        token = account.get("github_token")
        username = account.get("github_username")
        keywords_file_name = account.get("keywords_file", "")
        keywords_file = Path("KEYWORDS_FOLDER") / keywords_file_name if keywords_file_name else None

        if not token or not username:
            print(f"[ERROR] Missing token or username in CSV: {account}")
            continue

        repo_name = f"{username}.github.io"
        print(f"\n[INFO] Processing account {i}/{total_count}: {username} / repo {repo_name}")

        # 创建仓库
        if not create_repo(token, username, repo_name):
            continue

        # 设置Secrets
        set_secret(token, username, repo_name, "GDRIVE_SERVICE_ACCOUNT", account.get("gdrive_service_account", ""))
        set_secret(token, username, repo_name, "GDRIVE_FOLDER_ID", account.get("gdrive_folder_id", ""))

        # 推送文件
        if push_files(token, username, repo_name, files_to_upload, keywords_file):
            success_count += 1
            # 写回仓库 URL 和 Pages URL
            account["repo_url"] = f"https://github.com/{username}/{repo_name}"
            account["pages_url"] = f"https://{username}.github.io"
            print(f"[INFO] ✓ Successfully processed {username}")
        else:
            print(f"[ERROR] ✗ Failed to process {username}")
            print(f"[INFO] You may need to check your network connection or GitHub access")

        # 添加延迟避免API限制
        if i < total_count:
            print("[INFO] Waiting 5 seconds before next account...")
            time.sleep(5)

    # 写回 CSV
    if accounts:
        fieldnames = list(accounts[0].keys())
        write_csv(csv_file, accounts, fieldnames)

    print(f"\n[INFO] Script finished. Success: {success_count}/{total_count}")
    if success_count < total_count:
        print(f"[WARN] {total_count - success_count} accounts failed to process")
