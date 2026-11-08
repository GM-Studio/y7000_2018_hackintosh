# EFI 备份说明（已知可用状态）

- 备份时间：2026-11-08 13:31
- 机器：Lenovo Legion Y7000 (81FW) · i7-8750H · 24GB
- 系统：macOS Sequoia 15.8.2 (24H232)
- 引导：OpenCore **0.8.8**（安装 EFI 分区：NVMe disk0s1）
- 文件：EFI-backup-2026-11-08.zip（13.3 MB）
- SHA256：259fa74f69fb65425e74b21d1863793e205f3bb0976f53a6f33a313379f494b0
- 存放：本机 1TB 盘 /Volumes/data/EFI-backup-2026-11-08.zip + B 机 backups/ 目录

## 这份 EFI 已验证可用
- 能从硬盘独立启动（不需要 U 盘）
- UHD 630 核显 Metal 3 加速
- 声卡（扬声器/麦克风/耳机）
- 触控板 + 键盘 + 亮度键
- 有线网卡千兆
- 电池、摄像头
- 睡眠唤醒

## 关键 BIOS 变更（换主板/刷 BIOS 后必须重做）
| 项 | 变量 | 值 |
|---|---|---|
| CFG Lock 关闭 | CpuSetup 0x3E | 01 → 00 |
| DVMT 64MB | SaSetup 0x107 | 01 → 02 |
| 8代 Kernel Debug 关闭 | PchSetup 0x08 | 03 → 00 |
| GPIO 中断开启 | PchSetup 0x18 | 00 → 01 |
工具：xiaoMGitHub/LEGION_Y7000Series_Insyde_Advanced_Settings_Tools

## 恢复方法（系统还能进时）
```bash
sudo diskutil mount disk0s1
sudo rm -rf /Volumes/EFI/EFI
sudo unzip -q /Volumes/data/EFI-backup-2026-11-08.zip -d /Volumes/EFI/
```

## 恢复方法（系统进不去时）
1. 把 zip 解压到任意 FAT32 U 盘根目录，得到 EFI 文件夹
2. U 盘启动 → OpenCore → 选 macOS
3. 进系统后按上面的命令写回内部 ESP

## 已知限制
- WiFi / 蓝牙：Realtek 8822BE 无驱动（需换 BCM94360NG）
- HDMI：物理接 GTX 1050 Ti，无驱动
- 独显：已 SSDT 屏蔽
- 不要升级 macOS 大版本；升级前先复制本备份
