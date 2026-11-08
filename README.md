# 联想拯救者 Y7000 黑苹果完整归档（hackintosh_y7000）

> **机器**：Lenovo Legion Y7000（81FW，2018 款）· i7-8750H · 24 GB · UHD 630 + GTX 1050 Ti
> **系统**：macOS Sequoia **15.8.2 (24H232)** · 引导 **OpenCore 0.8.8** · 机型 MacBookPro16,3
> **结果**：单系统 macOS 安装成功，日常开发可用；WiFi / 蓝牙 / HDMI 为硬件级限制
> **时间**：2026-11-07 ~ 2026-11-08（两天，约 12 小时，23 个坑）

---

# ⚠️ 先看这五个坑（会浪费你一整天）

| 优先级 | 坑 | 一句话结论 |
|---|---|---|
| 🔴 **必看** | **卡在 `EXITBS:START` 黑屏** | **不是配置问题，是 BIOS 4 个隐藏项没改**（CFG Lock / DVMT / KernelDebug / GPIO）——不改永远进不去 |
| 🔴 **必看** | **OpenCore 版本** | **本机只能用 0.8.8**；1.0.7 / 1.0.8 全部卡 EXITBS，别浪费时间升级 |
| 🟠 高 | **菜单黑屏（无画面）** | `Resources` 缺失 + Builtin 渲染失败 → 解法是 **`DirectGopRendering = true`** |
| 🟠 高 | **安装卷不显示** | `ScanPolicy` 必须为 `0`（诊断期），否则只显示隐藏卷 |
| 🟡 中 | **iCloud 登不上** | 可能是**账号被风控**，不是配置；先用另一个新号验证 |

**完整 23 个坑见 `docs/01-完整踩坑总结.md`**（现象 / 根因 / 解决 / 证据）。

---

# 一、机器完整信息

## 1.1 基本信息

| 项目 | 值 |
|---|---|
| 品牌 | 联想 Lenovo |
| 型号 | Legion Y7000（拯救者 Y7000） |
| 型号编号 | 81FW（2018 款） |
| 出厂年份 | 2018 |
| 主板芯片组 | Intel HM370 |
| BIOS | InsydeH2O（联想定制，含隐藏项） |
| 固件报告版本 | `1916.40.8.0.0`（OpenCore 读取值） |
| **当前模拟机型** | **MacBookPro16,3** |
| 序列号（SMBIOS） | `C02DG1ZKP3XY` |
| MLB | `C02039401J900001M` |
| 硬件 UUID | `B9DC3BBB-85A9-5256-8EEF-101EB3D1B8AB` |
| ROM（网卡 MAC） | `e8:6a:64:bf:6a:d8` |

## 1.2 处理器

| 项目 | 值 |
|---|---|
| 型号 | Intel Core i7-8750H（第 8 代 Coffee Lake-H） |
| 核心/线程 | 6 核 12 线程 |
| 基础频率 | 2.20 GHz |
| 最大睿频 | 4.10 GHz（单核）/ 实测全核 3.30 GHz |
| 缓存 | L2 256 KB×6 / L3 9 MB |
| TDP | 45 W |
| 变频方案 | XCPM（`machdep.xcpm.mode = 1`） |

## 1.3 显卡（双显卡）

| 项目 | 核显 | 独显 |
|---|---|---|
| 型号 | Intel UHD Graphics 630 | NVIDIA GeForce GTX 1050 Ti |
| 设备 ID | `0x3e9b` | `0x1c8c`（Pascal） |
| 显存 | 动态 1536 MB（DVMT 64MB） | 4 GB GDDR5 |
| macOS 支持 | ✅ **Metal 3** 加速 | ⛔ **无驱动** |
| 当前状态 | 主力显示 | **已被 SSDT-DDGPU 屏蔽** |
| 驱动 kext | `AppleIntelCFLGraphicsFramebuffer` + `AppleIntelKBLGraphics` | — |

> ⚠️ GTX 1050 Ti 在 macOS 下**永远无解**（Pascal 架构无驱动）。它被屏蔽后，**HDMI 口也跟着失效**（HDMI 物理接在独显上）。

## 1.4 内存（两条混插）

| 插槽 | 容量 | 品牌 | 型号 | 频率 | 类型 |
|---|---|---|---|---|---|
| BANK 0 / ChannelA | **8 GB** | Samsung | `M471A1K43CB1-CTD` | 2400 MHz | DDR4 SODIMM |
| BANK 2 / ChannelB | **16 GB** | Kingston | `KHX2666C15S4/16G` | 2400 MHz | DDR4 SODIMM |
| 合计 | **24 GB** | | | | |

**影响**：Intel Flex Mode 下只有 8+8 走双通道，剩余 8GB 单通道 → **核显共享内存带宽下降**，UI 动画可能轻微掉帧。
**建议**：换 16+16 对称内存。

## 1.5 存储

| 盘位 | 型号 | 容量 | 接口 | 序列号 | 用途 |
|---|---|---|---|---|---|
| NVMe（系统盘） | **WDC PC SN720** `SDAPNTW-512G-1101` | 512.11 GB | PCIe 3.0 x4 / 8.0 GT/s | `184862801788` | macOS 系统 |
| SATA（数据盘） | **WDC WD10JPLX** `-00MBPT0` | 1 TB | SATA 6 Gb/s | `JR1000BN2REZPE` | `data` + `TimeMachine` |

**当前分区布局**：

~~~
disk0 (NVMe 512GB)
├─ disk0s1  EFI            209.7 MB   ← OpenCore 0.8.8
└─ disk0s2  APFS Container 511.9 GB
           ├─ macos            系统（只读密封快照）
           ├─ macos - 数据     用户数据
           ├─ Preboot / Recovery / VM

disk1 (HDD 1TB)
├─ disk1s1  EFI            209.7 MB
└─ disk1s2  APFS Container 1000 GB
           ├─ data             数据卷
           └─ TimeMachine      备份卷
~~~

## 1.6 音频

| 项目 | 值 |
|---|---|
| Codec | **Realtek ALC236**（CodecID `0x10EC0236`） |
| 驱动 | AppleALC 1.9.7 |
| layout-id | **18** |
| 已验证 | 扬声器 ✅ / 麦克风 ✅ / 耳机口 ✅ |
| Codec 配置来源 | `ALC236 for Lenovo LEGION Y7000/Y530 by xiaoM` |

## 1.7 网络

| 类型 | 芯片 | 状态 | 驱动 |
|---|---|---|---|
| **有线** | Realtek **RTL8111**（MAC `e8:6a:64:bf:6a:d8`） | ✅ 1000baseT 全双工 | RealtekRTL8111 3.0.4 |
| **无线** | Realtek **RTL8822BE** | ⛔ **无驱动** | 无（芯片不支持） |
| **蓝牙** | Realtek（USB `0bda:b023`） | ⛔ **无驱动** | 无 |

> **唯一解**：换 **博通 BCM94360NG**（M.2 2230，几十元），换完 WiFi / 蓝牙 / AirDrop / Handoff 全通。

## 1.8 输入设备

| 设备 | 接口 | 驱动 | 状态 |
|---|---|---|---|
| 键盘 | PS/2（内置） | VoodooPS2Controller 2.3.7 | ✅ |
| 触控板 | I2C（Synaptics） | VoodooI2C 2.9.1 + VoodooI2CHID | ✅ 手势正常 |
| 亮度键 F11/F12 | — | BrightnessKeys 1.0.3 | ✅ |

## 1.9 其他外设

| 设备 | 标识 | 状态 |
|---|---|---|
| 摄像头 | SunplusIT UVC `5986:2113` | ✅ 已识别 |
| 电池 | InternalBattery，2723 mAh，416 循环 | ⚠️ 可用但**健康度差**（建议维修） |
| 屏幕 | 15.6 英寸 1920×1080 | ✅ |
| 读卡器 | — | 未测试 |
| HDMI | 接独显 | ⛔ 无解 |

## 1.10 设备 ID 速查（排障用）

| 设备 | ID |
|---|---|
| CPU | `i7-8750H` |
| 核显 | `0x3e9b`（UHD 630） |
| 独显 | `0x1c8c`（GTX 1050 Ti） |
| 声卡 | `0x10EC0236`（ALC236） |
| 有线网卡 | `0x10EC8168`（RTL8111） |
| 无线网卡 | `0x10ECB822`（RTL8822BE） |
| 蓝牙 | USB `0bda:b023` |
| 摄像头 | USB `5986:2113` |

---

# 二、软件环境

## 2.1 操作系统

| 项目 | 值 |
|---|---|
| 系统 | macOS Sequoia |
| 版本 | **15.8.2 (24H232)** |
| 内核 | Darwin 24.6.0 (xnu-11417.140.69.713.47) |
| SIP | 已启用 |
| FileVault | **关闭**（黑苹果必须） |
| Time Machine | 已配置到内置 1TB 盘 |

## 2.2 引导器

| 项目 | 值 |
|---|---|
| OpenCore | **0.8.8**（教程版本的二进制） |
| 位置 | NVMe `disk0s1`（ESP） |
| 菜单 | Builtin + `DirectGopRendering = true` |
| 日志 | 已关闭（`Target = 0`） |
| boot-args | `keepsyms=1 -no_compat_check -lilubetaall ipc_control_port_options=0 -wegnoegpu` |

## 2.3 kext 清单（27 个文件 / 21 个启用）

| 类别 | kext | 版本 |
|---|---|---|
| 框架 | Lilu | 1.7.2 |
| SMC | VirtualSMC / SMCBatteryManager / SMCProcessor / SMCSuperIO | 1.3.7 |
| 显卡 | WhateverGreen | 1.7.0 |
| 声卡 | AppleALC | 1.9.7 |
| 键盘 | VoodooPS2Controller | 2.3.7 |
| 触控板 | VoodooI2C / VoodooI2CHID / VoodooInput | 2.9.1 / 1.1.6 |
| 网卡 | RealtekRTL8111 | 3.0.4 |
| 存储 | NVMeFix | 1.1.3 |
| 亮度 | BrightnessKeys | 1.0.3 |
| 电源 | CPUFriend / CPUFriendDataProvider | — |
| 休眠 | HibernationFixup | — |
| 其他 | RestrictEvents / USBInjectAll / XHCI-unsupported | — |

> 另有 Broadcom 系列（AirportBrcmFixup / BrcmPatchRAM3 等）已禁用——本机没有博通卡。

## 2.4 ACPI（11 张）

| 表 | 作用 |
|---|---|
| SSDT-AWAC | 修复 AWAC 计时器 |
| **SSDT-DDGPU** | **屏蔽 GTX 1050 Ti** |
| SSDT-EC-USBX-LAPTOP | 嵌入式控制器 + USB 电源 |
| SSDT-I2C | 触控板 I2C |
| SSDT-PLUG | CPU 电源管理 |
| SSDT-PMC | 原生 NVRAM |
| SSDT-PNLF-CFL | 背光控制 |
| SSDT-PS2K | PS/2 键盘 |
| SSDT-PTSWAK | 睡眠/唤醒 |
| SSDT-XCPM | XCPM 变频 |
| SSDT-XOSI | 操作系统判断（Windows 路径） |

---

# 三、环境准备清单（重装前必备）

## 3.1 硬件

| 物品 | 规格 | 说明 |
|---|---|---|
| **U 盘** | ≥ 32 GB（做急救盘）/ ≥ 64 GB（要整机镜像） | 会被清空 |
| **另一台电脑** | Windows 或 macOS | 用来做 U 盘、查资料、远程排障 |
| **网线** | 普通网线 | 安装必须联网（下载 12 GB） |
| **USB 键鼠** | 有线 | **安装阶段内置键盘/触控板可能不工作** |
| 螺丝刀 | 十字 | 拆后盖（换内存/网卡时） |

## 3.2 软件与文件

| 文件 | 来源 | 用途 |
|---|---|---|
| OpenCore 0.8.8 包 | `docs/../EFI/`（本归档已含） | 引导器 |
| `BaseSystem.dmg` | 本归档 `installer/` | 恢复镜像（848 MB） |
| BIOS 工具 | 本归档 `BiosTools/` | 改 4 个隐藏项 |
| `macserial` | 本归档 `tools/` | 生成三码 |
| `ocvalidate` | 本归档 `tools/` | 校验配置 |
| 7-Zip | 官网 | 解 DMG 提取 HFS 分区 |
| Python 3 | 官网 | 跑 macrecovery 等脚本 |

## 3.3 时间预算（实际）

| 阶段 | 耗时 |
|---|---|
| BIOS 改隐藏项 | 30 分钟 |
| 做 U 盘 | 40 分钟 |
| 排 EXITBS | **3.5 小时**（改了 BIOS 就是 0） |
| 安装系统 | 1.5 小时 |
| 外设驱动调优 | 2 小时 |
| 三码 / EFI 落盘 / 备份 | 1 小时 |
| **合计** | **约 9 小时**（顺利的话 4 小时） |

---

# 四、⚠️ 23 个坑速查

> 完整的现象/根因/解决见 `docs/01-完整踩坑总结.md`

| # | 坑 | 根因 | 解决 |
|---|---|---|---|
| 1 | SSH 连不上 | 防火墙 | 关闭防火墙 |
| 2 | 远程执行器 0xC0000142 | 服务会话缺桌面 | 用 SYSTEM 计划任务 |
| 3 | 存储 WMI 报 0x5 | 管理员令牌不完整 | SYSTEM 计划任务 |
| 4 | 计划任务假成功 | 电池时被挂起 | `DisallowStartIfOnBatteries=$false` |
| **5** | **EXITBS:START 卡死** | **BIOS 4 个隐藏项** | **H2OUVE 改值** |
| 6 | 仍不进系统 | SecureBootModel=j680 | 改 **Disabled** |
| 7 | OC 拒绝启动 | Vault=Secure 无签名 | 改 **Optional** |
| 8 | 安装卷不显示 | ScanPolicy≠0 | 改 **0** |
| 9 | ACPI 报错 | SSDT-GPRW 缺失 | 从配置移除 |
| 10 | 菜单黑屏 | Resources 缺失 | 补 22 个图标 |
| **11** | **Builtin 也黑屏** | **GOP 文本模式不刷新** | **DirectGopRendering=true** |
| 12 | kext 注入失败 | UTBMap 无二进制 | 禁用该 kext |
| **13** | **配置校验报错** | **schema 与版本不匹配** | **降级 0.8.8 全套** |
| 14 | 安装界面键鼠不动 | 内置驱动未加载 | 插 USB 键鼠 |
| 15 | 镜像只有 1MB | `-os latest` 行为异常 | 指定具体 build |
| 16 | 安装要联网 | 恢复镜像不含本体 | 插网线（12 GB） |
| 17 | 三码是假的 | 手写序列号 | `macserial` 生成 |
| 18 | iCloud 登不上 | **账号被风控** | Apple 支持解锁 |
| **19** | **TM 备份到 U 盘失败** | **容量差 5 GB** | **换 64GB 或放弃** |
| 20 | 孤儿备份占 21GB | 误删目标 | 删快照重建 |
| **21** | **改分辨率黑屏** | **核显不支持该缩放** | **删 windowserver 偏好** |
| 22 | 桌面一堆磁盘 | dmg 挂载未弹出 | 弹出 + 关显示 |
| 23 | 系统字小 | 1080P 默认偏小 | 缩放 + 应用字体 |

---

# 五、目录结构

~~~
F:\hackintosh_y7000\            (893 MB, 225 个文件)
├── README.md                      ← 本文件
├── SHA256SUMS.txt                 ← 大文件校验值
├── docs\                          ← 60 KB
│   ├── 00-第一版总结-Ventura阶段.md
│   ├── 01-完整踩坑总结.md           ← 主文档
│   ├── 02-BIOS修改记录.md
│   ├── 03-硬件验收与已知限制.md
│   ├── 04-维护与恢复手册.md
│   ├── 05-脚本与工具说明.md
│   ├── README-EFI备份说明.md
│   └── 急救盘使用说明.md
├── EFI\                           ← 40 MB
│   ├── EFI-backup-2026-11-08.zip     13.9 MB
│   └── EFI\ (BOOT + OC: 27 kext / 11 ACPI / 4 driver)
├── installer\                     ← 848 MB
│   ├── BaseSystem.dmg                Sequoia 15.6.1 恢复镜像
│   ├── BaseSystem.chunklist
│   └── config-EFI-0.8.8.plist
├── scripts\                       ← macrecovery.py / run_system_task.py
├── tools\                         ← macserial / macserial.exe / ocvalidate.exe
└── BiosTools\                     ← 联想 BIOS 隐藏项工具（含原始备份）
~~~

---

# 六、快速使用

## 6.1 系统崩了要恢复

~~~
U 盘启动 → OpenCore → macOS Base System → 从时间机器恢复（选内置 TimeMachine 卷）
~~~

## 6.2 EFI 坏了（黑屏/进不去）

~~~bash
sudo diskutil mount disk0s1
sudo rm -rf /Volumes/EFI/EFI
sudo cp -R /Volumes/<U盘>/EFI /Volumes/EFI/
sudo diskutil unmount disk0s1
~~~

## 6.3 全新安装（顺序不能变）

~~~
1. BIOS 改 4 个隐藏项        ← 不做必卡 EXITBS
2. U 盘：ESP 放本归档 EFI + 安装卷
3. F12 启动 U 盘 → OpenCore → 安装
4. 装完进系统 → 挂载 ESP → 写回 EFI
5. 生成三码 → 重启 → 登录 iCloud
6. 配 Time Machine + 做急救盘
~~~

## 6.4 校验文件完整性

~~~bash
shasum -a 256 EFI/EFI-backup-2026-11-08.zip
# 259fa74f69fb65425e74b21d1863793e205f3bb0976f53a6f33a313379f494b0
~~~

---

# 七、当前状态与已知限制

## 7.1 能做什么

| 用途 | 评价 |
|---|---|
| 日常上网 / 办公 | ✅ 流畅 |
| 写代码（VS Code / IDEA / 终端） | ✅ 6 核 12 线程 + NVMe，够用 |
| 大型项目编译 | ✅ 可以（24 GB 内存） |
| Docker / 容器 | 🟡 可用，内存吃紧 |
| 视频剪辑 / 3D / 游戏 / 本地 AI | ❌ 无独显加速 |

## 7.2 硬件限制（改不掉）

| 项 | 原因 | 解法 |
|---|---|---|
| WiFi | RTL8822BE 零驱动 | 换 BCM94360NG |
| 蓝牙 | 同上 | 同上 |
| HDMI | 物理接独显 | 无解（可试 USB-C/DP） |
| 独显 GTX 1050 Ti | Pascal 无驱动 | 已屏蔽 |

## 7.3 使用纪律

| 禁止 | 原因 |
|---|---|
| 升级 macOS 大版本 | 必挂 |
| 开启 FileVault | 引导失败 |
| 删掉唯一能启动的 U 盘 | 没法救 |
| 乱改 BIOS 其他项 | 变砖风险 |

---

## 附：文档索引

| 想了解 | 看哪个 |
|---|---|
| 每个坑怎么踩的、怎么解决的 | `docs/01-完整踩坑总结.md` |
| BIOS 到底改了什么 | `docs/02-BIOS修改记录.md` |
| 哪个硬件能用/不能用 | `docs/03-硬件验收与已知限制.md` |
| 日常怎么维护、坏了怎么救 | `docs/04-维护与恢复手册.md` |
| 脚本和工具怎么用 | `docs/05-脚本与工具说明.md` |
| U 盘急救盘怎么用 | `docs/急救盘使用说明.md` |
