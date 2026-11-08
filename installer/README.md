# installer 目录说明

## 为什么没有 BaseSystem.dmg

macOS 恢复镜像约 **848 MB**，超过 GitHub 单文件 100 MB 限制，因此**不入库**。

## 怎么获取

### 方式 A：用 macrecovery 重新下载（推荐）

~~~bash
cd scripts
python3 macrecovery.py -b Mac-XXXXXXXX -m 0000000000000000 download
~~~

> 注意：不要用 `-os latest`（本次踩坑：会下到 1MB 坏文件），要指定具体 build。

### 方式 B：从 Apple 官方恢复

在任意 Mac 上用「macOS 恢复」或 `softwareupdate --fetch-full-installer` 获取。

## 文件说明

| 文件 | 说明 |
|---|---|
| `BaseSystem.chunklist` | 完整性清单（小文件，已入库） |
| `config-EFI-0.8.8.plist` | 当前 OpenCore 配置样本 |
| `fetch-installer.sh` | 一键下载脚本 |
