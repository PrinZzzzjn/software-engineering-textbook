# 实训 16-1 起点：15-1 完成态

本目录直接复用 15-1 的单位管理页（假数据版），作为 16-1 的起点。

## 运行

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## 与 15-1 项目的差异

只有文件头注释不同；页面代码与 15-1 完成态一致，便于学员对照改造前后。

## 下一步

按 [起点说明.md](起点说明.md) 的五块补 `config.py`、`api_client.py`、登录、真实列表与三态。完成态见 `../项目/`。
