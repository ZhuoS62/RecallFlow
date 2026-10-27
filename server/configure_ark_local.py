from getpass import getpass
from pathlib import Path

key = getpass("请输入换新的方舟 API Key（输入不显示，粘贴后回车）：").strip()
if not key or any(c.isspace() for c in key):
    raise SystemExit("密钥为空或包含空白，配置未修改。")
path = Path(__file__).resolve().parent / ".env"
lines = path.read_text().splitlines()
lines = ["OPENAI_API_KEY=" + key if line.startswith("OPENAI_API_KEY=") else line for line in lines]
path.write_text("\n".join(lines) + "\n")
path.chmod(0o600)
print("方舟密钥已保存在本机私密配置中。可以返回会话继续部署。")
