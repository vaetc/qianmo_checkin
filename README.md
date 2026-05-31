# QMJ 自动签到脚本

<p align="center">
  <img src="https://img.shields.io/badge/GitHub%20Actions-Automation-brightgreen?style=for-the-badge&logo=githubactions" />
  <img src="https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge" />
  <img src="https://img.shields.io/badge/License-MIT-orange?style=for-the-badge" />
</p>

<p align="center">
  基于 GitHub Actions 的QMJ自动签到脚本。
  <br />
  支持每日签到、每日威望任务、积分信息获取、邮件通知和旧运行记录自动清理。
</p>

---

## 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
  - [1. Fork 本仓库](#1-fork-本仓库)
  - [2. 获取 Cookie](#2-获取-cookie)
  - [3. 配置 GitHub Secrets](#3-配置-github-secrets)
  - [4. 启用 GitHub Actions](#4-启用-github-actions)
  - [5. 手动测试运行](#5-手动测试运行)
- [运行时间](#运行时间)
- [Secrets 配置说明](#secrets-配置说明)
- [Workflow 配置](#workflow-配置)
- [邮件通知配置](#邮件通知配置)
- [自动清理旧运行记录](#自动清理旧运行记录)
- [运行日志示例](#运行日志示例)
- [常见问题](#常见问题)
- [注意事项](#注意事项)
- [免责声明](#免责声明)

---

## 项目简介

本项目用于在 GitHub Actions 中自动执行QMJ签到任务。

脚本会自动完成：

1. 验证登录状态
2. 每日签到
3. 每日威望红包任务
4. 获取威望、铜币、积分信息
5. 发送邮件通知
6. 自动清理旧的 GitHub Actions 运行记录

适合希望使用 GitHub Actions 定时执行签到任务的个人用户。

---

## 功能特性

| 功能 | 说明 |
|---|---|
| 自动签到 | 每天定时执行论坛签到 |
| 每日任务 | 自动申请并完成每日威望红包任务 |
| 积分查询 | 获取威望、铜币、积分等信息 |
| 邮件通知 | 执行完成后发送结果通知 |
| 手动触发 | 支持在 GitHub Actions 页面手动运行 |
| 运行日志 | 输出详细执行日志，方便排查问题 |
| 自动清理 | 可自动删除旧的 Actions 运行记录 |

---

## 项目结构

```text
.
├── README.md
├── requirements.txt
├── qianmo_checkin.py
└── .github
    └── workflows
        ├── qianmo_checkin.yml
        └── cleanup_workflow_runs.yml
```

| 文件 | 说明 |
|---|---|
| `README.md` | 项目说明文档 |
| `requirements.txt` | Python 依赖列表 |
| `qianmo_checkin.py` | 自动签到主脚本 |
| `.github/workflows/qianmo_checkin.yml` | 自动签到 Workflow |
| `.github/workflows/cleanup_workflow_runs.yml` | 自动清理旧运行记录 Workflow |

---

## 快速开始

### 1. Fork 本仓库

点击页面右上角的 **Fork** 按钮，将本项目复制到你的 GitHub 账号下。

---

### 2. 获取 Cookie

1. 登录 [QMJ](https://www.1000qm.vip/)
2. 按 `F12` 打开浏览器开发者工具
3. 切换到 **Network / 网络** 标签
4. 刷新页面
5. 随便点击一个请求
6. 找到 `Request Headers`
7. 复制完整的 `Cookie` 值

Cookie 示例：

```text
bKHu_2132_saltkey=xxx; bKHu_2132_auth=xxx; bKHu_2132_sid=xxx
```

<details>
<summary>展开查看 Cookie 获取提示</summary>

不同浏览器的入口名称可能略有不同：

| 浏览器 | 开发者工具快捷键 |
|---|---|
| Chrome | `F12` 或 `Ctrl + Shift + I` |
| Edge | `F12` 或 `Ctrl + Shift + I` |
| Firefox | `F12` 或 `Ctrl + Shift + I` |

进入 Network 页面后，刷新网页，点击任意请求，在 Headers 中找到 Cookie 并完整复制。

请确保复制的是完整 Cookie，而不是其中某一小段。

</details>

---

### 3. 配置 GitHub Secrets

进入你 Fork 后的仓库：

```text
Settings -> Secrets and variables -> Actions -> New repository secret
```

添加以下 Secrets。

#### 必填配置

| Secret 名称 | 是否必填 | 说明 |
|---|---:|---|
| `QIANMO_COOKIE` | 是 | QMJ登录 Cookie |

#### 邮件通知配置

| Secret 名称 | 是否必填 | 说明 |
|---|---:|---|
| `SMTP_HOST` | 否 | SMTP 服务器地址，例如 `smtp.qq.com` |
| `SMTP_PORT` | 否 | SMTP 端口，通常为 `465` |
| `SMTP_USER` | 否 | 发件邮箱 |
| `SMTP_PASS` | 否 | 邮箱授权码，不是邮箱登录密码 |
| `MAIL_TO` | 否 | 收件邮箱，多个邮箱使用英文逗号分隔 |

> 如果不配置邮件相关 Secrets，脚本会跳过邮件通知，不影响签到功能。

---

### 4. 启用 GitHub Actions

1. 进入仓库的 **Actions** 页面
2. 如果看到提示，点击：

```text
I understand my workflows, go ahead and enable them
```

3. 选择 **阡陌居自动签到**
4. 点击 **Enable workflow**

---

### 5. 手动测试运行

1. 打开仓库的 **Actions** 页面
2. 选择 **QMJ自动签到**
3. 点击 **Run workflow**
4. 等待执行完成
5. 查看运行日志和邮件通知结果

---

## 运行时间

默认定时任务配置：

| 类型 | 时间 |
|---|---|
| 自动运行 | 每天北京时间 `00:01` |
| 手动运行 | 任意时间，可在 Actions 页面触发 |

GitHub Actions 的 `cron` 使用 UTC 时间。

北京时间 `00:01` 对应 UTC 时间 `16:01`，所以 workflow 中通常写作：

```yaml
cron: '01 16 * * *'
```

---

## Secrets 配置说明

### 最小可用配置

只需要配置一个 Secret：

| Secret | 值 |
|---|---|
| `QIANMO_COOKIE` | 你的QMJ Cookie |

### 完整推荐配置

| Secret | 示例 |
|---|---|
| `QIANMO_COOKIE` | `bKHu_2132_saltkey=xxx; bKHu_2132_auth=xxx;` |
| `SMTP_HOST` | `smtp.qq.com` |
| `SMTP_PORT` | `465` |
| `SMTP_USER` | `example@qq.com` |
| `SMTP_PASS` | `邮箱授权码` |
| `MAIL_TO` | `example@qq.com` |

---

## Workflow 配置

### 自动签到 Workflow

文件路径：

```text
.github/workflows/qianmo_checkin.yml
```

示例内容：

```yaml
name: QMJ自动签到

on:
  schedule:
    # 每天北京时间 00:01 执行
    - cron: '01 16 * * *'

  workflow_dispatch:

jobs:
  checkin:
    name: 自动签到
    runs-on: ubuntu-latest

    steps:
      - name: 检出代码
        uses: actions/checkout@v4

      - name: 设置 Python 环境
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: 安装依赖
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: 执行签到脚本
        env:
          QIANMO_COOKIE: ${{ secrets.QIANMO_COOKIE }}
          SMTP_HOST: ${{ secrets.SMTP_HOST }}
          SMTP_PORT: ${{ secrets.SMTP_PORT }}
          SMTP_USER: ${{ secrets.SMTP_USER }}
          SMTP_PASS: ${{ secrets.SMTP_PASS }}
          MAIL_TO: ${{ secrets.MAIL_TO }}
        run: |
          python qianmo_checkin.py
```

---

## 邮件通知配置

脚本支持使用 SMTP 发送邮件通知。

### QQ 邮箱示例

| Secret | 值 |
|---|---|
| `SMTP_HOST` | `smtp.qq.com` |
| `SMTP_PORT` | `465` |
| `SMTP_USER` | `你的QQ邮箱@qq.com` |
| `SMTP_PASS` | `QQ邮箱授权码` |
| `MAIL_TO` | `接收通知的邮箱` |

### 163 邮箱示例

| Secret | 值 |
|---|---|
| `SMTP_HOST` | `smtp.163.com` |
| `SMTP_PORT` | `465` |
| `SMTP_USER` | `你的163邮箱@163.com` |
| `SMTP_PASS` | `163邮箱授权码` |
| `MAIL_TO` | `接收通知的邮箱` |

<details>
<summary>展开查看邮件配置说明</summary>

大多数邮箱使用 SMTP 发信时，都需要开启 SMTP 服务，并生成授权码。

常见注意点：

- `SMTP_PASS` 通常不是邮箱登录密码，而是授权码
- `SMTP_PORT` 推荐使用 `465`
- 如果使用 `465`，一般对应 SSL 连接
- 如果使用 `587`，一般对应 STARTTLS
- 收件邮箱可以和发件邮箱相同

</details>

---

## 自动清理旧运行记录

GitHub Actions 会保留运行记录。如果长期每天执行，记录会越来越多。

你可以添加一个清理 Workflow，定期删除旧运行记录。

文件路径：

```text
.github/workflows/cleanup_workflow_runs.yml
```

内容：

```yaml
name: 清理旧的 Workflow 运行记录

on:
  schedule:
    # 每周日北京时间 03:00 执行
    # GitHub Actions 使用 UTC 时间，所以这里是周六 19:00 UTC
    - cron: '0 19 * * 6'

  workflow_dispatch:

permissions:
  actions: write
  contents: read

jobs:
  cleanup:
    name: 清理旧运行记录
    runs-on: ubuntu-latest

    steps:
      - name: 删除旧的阡陌居签到运行记录
        uses: Mattraks/delete-workflow-runs@v2
        with:
          token: ${{ github.token }}
          repository: ${{ github.repository }}
          workflow: qianmo_checkin.yml
          retain_days: 7
          keep_minimum_runs: 10
```

### 参数说明

| 参数 | 说明 |
|---|---|
| `workflow` | 指定要清理的 workflow 文件 |
| `retain_days` | 保留最近多少天的运行记录 |
| `keep_minimum_runs` | 至少保留多少条运行记录 |

如果你希望清理所有 workflow 的旧运行记录，可以删除：

```yaml
workflow: qianmo_checkin.yml
```

---

## 运行日志示例

```text
==================================================
QMJ自动签到脚本
运行时间: 2025-01-15 00:01:00
==================================================

🔄 验证登录状态...
✅ 登录验证成功，用户: XXX

🔄 开始签到...
✅ 签到成功

🔄 开始处理每日任务...
📋 任务进行中: 每日威望红包
🎁 完成任务成功，获得 1 威望

🔄 获取威望信息...
📊 威望: 1250 | 铜币: 3000 | 积分: 3500

==================================================
✅ 所有任务完成
==================================================
📧 邮件发送成功
```

---

## 常见问题

### 1. 签到失败怎么办？

请依次检查：

| 检查项 | 说明 |
|---|---|
| Cookie 是否过期 | 重新登录网站并复制新的 Cookie |
| Cookie 是否完整 | 确保复制了完整 Cookie |
| 网站是否可访问 | 检查阡陌居是否正常打开 |
| Actions 日志 | 查看具体报错信息 |

---

### 2. 任务领取失败怎么办？

可能原因：

- 今日任务已经完成
- 账号权限不足
- 网站规则或接口发生变化
- Cookie 失效
- 请求被临时限制

建议先查看 Actions 的详细日志。

---

### 3. 邮件发送失败怎么办？

请检查：

| 检查项 | 说明 |
|---|---|
| SMTP 服务 | 确认邮箱已开启 SMTP |
| 授权码 | 确认使用的是授权码，不是登录密码 |
| 端口 | QQ / 163 邮箱一般使用 `465` |
| 收件人 | 多个收件人请使用英文逗号分隔 |

---

### 4. 为什么定时任务没有准点执行？

GitHub Actions 的定时任务可能存在延迟，尤其在整点附近较明显。

建议：

- 避免使用 `0 0 * * *` 这种整点时间
- 使用 `01 16 * * *`、`13 16 * * *` 这类非整点时间
- 如果任务延迟几分钟，属于正常情况

---

### 5. 如何更新 Cookie？

1. 重新登录阡陌居
2. 按照获取 Cookie 的步骤复制新 Cookie
3. 进入仓库：

```text
Settings -> Secrets and variables -> Actions
```

4. 找到 `QIANMO_COOKIE`
5. 点击更新

---

## 注意事项

### Cookie 安全

- Cookie 包含登录凭证，请妥善保管
- 不要将 Cookie 写入代码
- 不要将 Cookie 提交到 GitHub
- 不要在 Issue、截图、日志中公开 Cookie

### 使用限制

- 请遵守网站规则
- 不建议频繁运行脚本
- 建议仅用于个人账号
- 不建议多个账号共用同一个仓库频繁运行

### GitHub Actions 限制

- GitHub Actions 的定时任务可能会延迟
- Public 仓库和 Private 仓库的 Actions 配额规则不同
- 如果仓库长期无活动，定时任务可能会被 GitHub 暂停

---

## 免责声明

本项目仅供学习和交流使用。

使用本项目产生的任何后果由使用者自行承担。请遵守相关网站的用户协议和社区规则，合理使用自动化工具。

---

## Star History

如果这个项目对你有帮助，欢迎点一个 Star。

你也可以 Fork 本项目后根据自己的需求进行修改。
