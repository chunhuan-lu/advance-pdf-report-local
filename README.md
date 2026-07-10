# Advance Report Studio

本地优先的 Safety & Compliance 报告工具：网页填表 → 预览 → 导出 PDF（Gas / Smoke Alarm）。
支持导入历史表单式 PDF 回填再编辑，照片、报告、数据全部存在本机 `local_store/`。

## 使用（给最终用户）

**双击 `start.bat`。** 脚本会自动：

1. 查找 Python 3.10+（没有则先用 winget、再从 python.org 静默安装 3.12）
2. 创建虚拟环境并安装依赖（首次需要联网，失败自动切清华镜像）
3. 初始化数据库并启动服务，自动打开浏览器 `http://127.0.0.1:8000`

手机使用：手机与电脑连同一 Wi-Fi，浏览器打开启动窗口里显示的 `http://<电脑IP>:8000`。

## 功能

- **新建报告**：Gas（封面 + 证书 + 服务表 + 照片页）、Smoke Alarm（封面 + 合规证书，烟感器数量不限，每 3 个一组自动分页）
- **照片上传**：每个槽位一张，重传自动覆盖（按 `报告ID/槽位ID` 存固定文件名）
- **预览 → 下载**：预览直接回传 PDF 字节（不落盘）；确认后生成正式 PDF 存 `local_store/media/reports/`
- **历史报告**：所有报告 JSON 存 SQLite，可随时打开再编辑、重新导出
- **导入 PDF**：
  - 本系统导出的 PDF：内嵌了完整 JSON（`report_data.json` 附件），100% 无损回填
  - 历史 Word 模板 PDF（AcroForm 表单）：读表单域 + 抽取内嵌照片回填（Gas / Smoke 模板均已适配）

## 目录结构

```
config/          Django 配置（settings/urls/wsgi）
reports/         API：报告 CRUD、照片上传、生成、解析
pdfgen/
  common/        封面、页眉、勾选框、字体样式、图片/时间工具
  gas/           Gas 报告绘制（certificate/service/appliance_report）
  smoke/         Smoke 报告绘制（动态烟感器分组）
  generate.py    按 baseInfo.type 分发
  embed.py       PDF 内嵌/提取 JSON
  parse.py       AcroForm 模板解析（字段名归一化 + 照片抽取）
  storage.py     本地/S3 存储切换
  constants.py   备选项字典（提取自官方 Word 模板表单域）
statics/         前端（Vue3 本地化，无构建链）+ app.js/app.css
templates/       index.html（SPA 壳）
local_store/     运行时数据（git 忽略）：db.sqlite3、media/photos、media/reports
```

## API

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/reports/` | 报告列表（摘要） |
| POST | `/api/reports/` | 保存草稿 `{id, data}` |
| GET/PUT/DELETE | `/api/reports/<id>/` | 详情 / 更新 / 删除 |
| POST | `/api/photos/` | multipart `file` + `key`，同 key 覆盖，返回 URL |
| POST | `/api/generate/` | `{id, data, mode: preview\|final}`；preview 返回 PDF 字节，final 存盘并返回 `{url}` |
| POST | `/api/parse-pdf/` | multipart `file`，返回 `{data, source: embedded\|acroform}` |

报告 JSON 契约与旧项目 easy_make_pdf 的 `/generate-pdf/` 兼容（`baseInfo` + `gasCheckDetails`），
Smoke 为新增结构（`baseInfo` + `smokeCheckDetails`）。

## 切换 S3 存储（可选）

默认全本地。要挂到服务器并使用 S3：

```
pip install boto3
set STORAGE_MODE=s3
set S3_BUCKET=advance-essentials
set S3_REGION=ap-southeast-2
```

并配置 AWS 凭证（环境变量或 `aws configure`）。

## 开发

```
.venv\Scripts\python manage.py runserver
```

注意：requirements.txt / start.bat 保持纯 ASCII——中文 Windows 默认 GBK 编码，
pip 和 cmd 读到 UTF-8 中文会出错。

## 已知边界

- Electrical 报告未实现（v1 范围外），生成/解析会明确报错
- 解析仅支持：本系统 PDF（嵌入 JSON）和官方 Word 模板导出的 AcroForm PDF；
  纯扫描件/压平后的 PDF 无法解析
- 本地服务无鉴权，仅限本机/可信局域网使用
