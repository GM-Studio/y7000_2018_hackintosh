# 联想 Legion Y7000 黑苹果安装踩坑全记录

> 机器：Lenovo Legion Y7000（81FW，2018 款）· i7-8750H · UHD 630 + GTX 1050 Ti · 16 GB
> 目标：单系统 macOS（NVMe 装系统，1TB 机械盘做数据盘），不保留 Windows
> 结果：**2026-11-08 凌晨成功装上 macOS Ventura 13.4.1**，约 4 小时，其中 3.5 小时卡在引导
> 记录：AI 助手（B 机）· 操作：用户（A 机现场）

---

## 0. 一分钟结论

| 问题 | 最终原因 | 解法 |
|---|---|---|
| **引导卡在 EB|LOG:EXITBS:START（卡了 3.5 小时）** | **BIOS 隐藏变量没改**：CFG Lock 未关、DVMT 未调 64 MB、8 代 CPU 的 Kernel Debug Serial Port 未关、GPIO 中断未开 | 用 H2OUVE 直接写 BIOS 变量（教程一键脚本的 1/2/4/5 项） |
| 改完 BIOS 后"苹果标一闪就回 Windows" | SecureBootModel = j680，恢复镜像没有对应签名清单，boot.efi 校验失败主动重启 | SecureBootModel 改为 Disabled |
| 恢复环境里键鼠不能动 | 内置键盘 PS/2、触控板 I2C，恢复环境驱动未生效 | 插 USB 键鼠完成安装，装完再调内置设备 |
| 安装显示"剩余 2 小时 17 分" | 恢复镜像只有 700 MB，系统本体 12 GB 要现场从 Apple CDN 下载 | 无解（一次性），实测 CDN 单连接约 3.1 MB/s |

**一句话教训：黑苹果卡在 EXITBS:START，先怀疑固件（BIOS 隐藏项），不要先怀疑 config、kext 或镜像版本。**

---

## 1. 硬件与初始状态

| 部件 | 型号 / 参数 | macOS 支持 |
|---|---|---|
| 机型 | Legion Y7000（81FW），BIOS 8JCN56WW，UEFI + GPT | 是 |
| CPU | Intel i7-8750H（6C12T，Coffee Lake-H） | 是 |
| 核显 | Intel UHD 630（内屏 BOE 1920x1080） | 是，原生 |
| 独显 | NVIDIA GTX 1050 Ti（GP107） | 否，无驱动，必须屏蔽 |
| 内存 | 16 GB DDR4 | 是 |
| 系统盘 | WDC PC SN720 512 GB（NVMe） | 是 |
| 数据盘 | WDC WD10JPLX 1 TB（SATA） | 是 |
| 有线网卡 | Realtek RTL8168 | 是，开源 kext |
| 无线/蓝牙 | **Realtek 8822BE**（二合一） | **否，任何 macOS 版本都无驱动** |
| 声卡 | Realtek ALC236 | 是，AppleALC |
| 键盘 | PS/2（ACPI\MSFT0001） | 是，VoodooPS2 |
| 触控板 | Synaptics I2C（ACPI\SYNA2B46） | 是，VoodooI2C + GPIO 中断 |
| 摄像头 | USB 5986:2113 | 是，UVC 免驱 |
| 原系统 | Windows 10 专业版 1909（18363），无 BitLocker、无 TPM | 最终被抹掉 |

---

## 2. 时间线（2026-11-07 ~ 11-08）

| 时间 | 事件 |
|---|---|
| 18:20 | 开始。B 机探测 A 机 192.168.0.238，全端口超时 |
| 18:30 | 发现 A 机 7680 端口有响应 → 机器活着，只是 22 没开 |
| 18:40 | A 上开启 sshd + 防火墙放行 22，SSH 连通 |
| 19:00 | 硬件采集完成；确认不做双系统 |
| 19:10 | 备份用户数据（520 MB）+ 1TB 盘清空格式化 |
| 19:20 | C: 从 476.3 GB 缩到 296.3 GB，空出 180 GB |
| 19:30-21:00 | **引导排错**：Sequoia / Ventura、4 套 quirk、2 种介质形态、OC 1.0.7/1.0.8，全部卡 EXITBS:START |
| 21:30 | 用户提供 xiaoMGitHub/LEGION_Y7000Series_Hackintosh v5.0.0 教程 |
| 21:50 | U 盘按教程重做（OC 0.8.8 + config_8300H_8750H + Ventura 13.4.1） |
| 22:05 | **跑教程的 BIOS 一键脚本，改 4 个隐藏变量** |
| 22:16 | **苹果 logo 出现 → EXITBS 通过** |
| 22:18 | 苹果标一闪回 Windows → 日志显示 Secure Boot 校验失败 |
| 22:25 | 改 SecureBootModel = Disabled |
| 22:26 | 进入 macOS 恢复界面，开始安装（提示剩余 2 小时 17 分） |
| 次日凌晨 | 安装完成，macOS 13 跑起来 |

---

## 3. 阶段 00：连接（坑 1-4）

### 坑 1｜"OpenSSH 已安装"不等于"能连上"

**现象**：用户说 sshd 装好了，但 B 机扫 22 / 135 / 139 / 445 / 3389 / 80 全部超时。

**排查**：
1. 全网段扫 192.168.0.0/24 的 22 和 3389 → 零响应（排除"IP 变了"）
2. 扫全端口 → **只有 7680 有响应**（Windows 传递优化）→ 证明 A 活着、网络通
3. 结论：默认防火墙挡入站，且 sshd 没在监听

**教训**：装好不等于在跑，不等于防火墙放行，不等于同网段，四件事要分别验证。判断机器是否活着可以用 7680 这种系统自带端口。

### 坑 2｜助手机的命令执行器坏了

**现象**：所有命令返回 3221225794（0xC0000142，DLL 初始化失败），连 whoami 都不行。

**影响**：无法 SSH、无法跑控制器，只能退化为"网络探测 + 人工指导"。

**解决**：用户调整权限策略后恢复。**教训**：环境能力要第一时间验证。

### 坑 3｜SSH 会话是"管理员"，但存储接口仍拒绝访问

**现象**：whoami 显示 High Mandatory Level、net session 正常，但 Repair-Volume、Get-PartitionSupportedSize、Resize-Partition 全部返回 **0x5 拒绝访问**。

**原因**：Windows OpenSSH 会话令牌虽提权，但对存储 WMI/API 仍被 UAC 边界挡住。

**解决**：改用计划任务以 SYSTEM 身份执行：

~~~
schtasks /Create /TN dsh_task /TR "powershell -NoProfile -ExecutionPolicy Bypass -File C:\path\task.ps1" /SC ONCE /ST 00:00 /RL HIGHEST /RU SYSTEM /F
schtasks /Run /TN dsh_task
~~~

任务脚本把结果写文件并写 .done 标记，B 机轮询读取。

### 坑 4｜计划任务"排队中"，但返回码是 0（假成功）

**现象**：任务创建成功、/Run 成功、上次结果 0，但目标文件一个都没生成。

**原因**：笔记本在用电池（BatteryStatus=1，75%，交流电未接）。Windows 计划任务默认"只有在交流电时才启动"，任务一直排队。

**解决**：

~~~
$x = Get-ScheduledTask -TaskName dsh_task
$x.Settings.DisallowStartIfOnBatteries = $false
$x.Settings.StopIfGoingOnBatteries = $false
Set-ScheduledTask -TaskName dsh_task -Settings $x.Settings
~~~

**教训（重要）**：命令成功、返回码 0、实际什么都没做——最危险的一类坑。所有磁盘操作后来都改成"先执行、再独立回读验证"。

---

## 4. 阶段 02：备份与分区（坑 5-7）

### 坑 5｜用户目录"16 GB"是假象

Get-ChildItem -Recurse 报 57,703 个文件 / 11.9 GB，实际只有 **2,948 个文件 / 520 MB**。

**原因**：用户目录里的旧式目录联接（Application Data、Local Settings、Documents and Settings）指回自己，递归统计重复计数。

**正确做法**：统计/复制时跳过 ReparsePoint（robocopy 用 /XJ），或手写栈式遍历跳过联接。

### 坑 6｜62 个文件复制失败——全是正在用的注册表

失败的全是 NTUSER.DAT、ntuser.dat.LOG1/2、settings.dat.LOG2，被登录会话锁死。

**解决**：
- 用户配置用 reg save 单独导出：reg save HKU\<SID> D:\backup\registry\NTUSER.DAT
- 试过 VSS 卷影快照，但从 \\?\GLOBALROOT\... 复制返回 code 16，未成功
- 剩余差异如实记录，不假装"完整备份"

### 坑 7｜跨机备份要校验

tar 打包后经 SFTP 拉回 B 机，两端 SHA256 一致（d7be122f…d9377c，483.3 MB）才算数。

---

## 5. 阶段 03：引导排错（核心，坑 8-12）

### 坑 8｜EXITBS:START —— 最致命的卡点

**现象**：OpenCore 菜单选安装项后，屏幕停在白字最后一行：

~~~
AAPL: #[EB|LOG:EXITBS:START]
~~~

**排查路径（全部失败）**：

| 假设 | 实验 | 结果 |
|---|---|---|
| 配置有问题 | 用 OpenCore 1.0.8 官方 Sample.plist 按本机硬件重写，ocvalidate 0 问题 | 同一行卡死 |
| quirk 组合不对 | 4 套：新组合 / 旧组合 / +ForceExitBootServices / +DevirtualiseMmio / SetupVirtualMap=false | 同一行卡死 |
| macOS 版本问题 | 换 Ventura 13.4.1（boot.efi 577~170，比 Sequoia 的 583~900 早两年） | 同一行卡死 |
| 介质形态问题 | BaseSystem 写到 U 盘真实 HFS+ 分区（不走内存 DMG） | 同一行卡死 |
| OpenCore 版本回归 | 换 1.0.7（社区在同类机型验证过的版本） | 同一行卡死 |

**关键判断依据**：不同版本下日志行数 27 → 92 → 97 变化，但最后 5 行一字不差：

~~~
EB.BST.FBS|!   Err(0xE)
EB|LOG:DT
EB|LOG:EXITBS:START
~~~

说明卡点不在上层（配置/kext/镜像），而在 **ExitBootServices() —— 固件把控制权交给内核的那一刻**。

**最终解法**：改 BIOS 隐藏变量（见第 6 节）。改完第一次启动就出现苹果 logo。

### 坑 9｜顺带发现的"假配置错误"

社区 EFI 的 config.plist 用 ocvalidate 1.0.8 检查有 17 个错误（DeviceProperties 非法字符、UEFI->Output->InitialMode 非法、15 个缺键），但重写后照样卡死，说明这些不是卡死原因。

**教训**：配置校验通过不等于能启动；卡在固件层时配置再干净也没用。

### 坑 10｜ocvalidate 必须和 OpenCore 版本配对

HideVerbose 这个键是 1.0.8 才有的：

- 用 1.0.8 的 ocvalidate 检查 1.0.7 配置 → 报缺少 HideVerbose
- 把带 HideVerbose 的配置喂给 1.0.7 的 OpenCore → 启动日志刷 No schema for HideVerbose

**教训**：配置文件和二进制必须成对；升级一起换。

### 坑 11｜Secure Boot 校验失败导致"苹果标一闪就重启"

**现象**：BIOS 改好后终于出现苹果 logo，几秒后自动重启回 Windows。

**日志证据**：

~~~
EB|SB:P 0x1                          <- 安全启动校验激活
EB|SB:SBGMFNS j680ap.im4m            <- 找 j680 机型的签名清单
EB.SB.VK|! Err(0xE)                  <- 校验失败
EB|R:SRBM secure-boot                <- 触发原因：secure-boot
EB|RESET 1                           <- 主动重启
~~~

**原因**：教程 config 里 SecureBootModel = j680，要求内核集合带对应机型的苹果签名；BaseSystem 恢复镜像里没有这份清单，校验失败后 boot.efi 直接 reset。

**解决**：Misc -> Security -> SecureBootModel 改为 Disabled（黑苹果安装阶段标准设置）。

### 坑 12｜恢复环境里内置键盘/触控板不能动

**现象**：进了 macOS 恢复界面，笔记本键盘和触控板都没反应。

**原因**：键盘是 PS/2、触控板是 I2C，恢复环境里 VoodooPS2 / VoodooI2C 未生效。

**解决**：插 USB 键鼠完成安装，装完系统后再调内置设备。

---

## 6. BIOS 修改详解（真正的破局点）

### 6.1 缺的是什么，为什么缺

这台机器是 **InsydeH2O** BIOS，普通界面（F2）只有：
- Security：Secure Boot / PTT / SGX / 安全启动模式
- Configuration：时间日期 / WLAN / VT-x / 超线程 / DPTF / Storage

**没有**：CFG Lock、DVMT、Above 4G Decoding、VT-d、Fast Boot、CSM。

这些选项被厂商藏在"高级设置"里，普通界面看不到，**所以不管怎么调 OpenCore 的 quirk 都没用——底层固件状态是错的**。

2018 款可以通过 **FN + D** 进 BIOS 高级模式；2019/2020 款进不去，作者才写了一键脚本，用 **H2OUVE（Insyde UEFI Variable Editor）** 直接改 BIOS 变量。

### 6.2 改了哪 4 项

教程要求：依次执行 2、4、5，八代处理器额外执行 1（i7-8750H 是八代）。

| 序号 | 作用 | 变量 | 偏移 | 改前 → 改后 |
|---|---|---|---|---|
| 1 | 八代处理器装 macOS 10.15+ 必须项（Kernel Debug Serial Port） | PchSetup | 0x08 | 03 → **00** |
| 2 | 强制加载触控板（GPIO 中断模式） | PchSetup | 0x18 | 00 → **01** |
| 4 | **关闭 CFG Lock**（CPU MSR 锁） | CpuSetup | 0x3E | 01 → **00** |
| 5 | **DVMT 改为 64 MB**（核显显存） | SaSetup | 0x107 | 01 → **02** |

### 6.3 怎么改的

用作者的一键脚本（双击执行.bat + H2OUVE-W-CONSOLEx64.exe + WDFInst.exe）：

~~~
1. 先读三个变量表做备份（脚本自动）
   H2OUVE-W-CONSOLEx64.exe -gv Backup\CpuSetup_Original.txt  -n CpuSetup
   H2OUVE-W-CONSOLEx64.exe -gv Backup\SaSetup_Original.txt   -n SaSetup
   H2OUVE-W-CONSOLEx64.exe -gv Backup\PchSetup_Original.txt  -n PchSetup

2. 按脚本里的正则改写目标字节（PowerShell）
   例（CFG Lock）：
   (gc CpuSetup_Original.txt) -replace '00000030: (.{41}) 01 (.*)','00000030: $1 00 $2'

3. 写回
   H2OUVE-W-CONSOLEx64.exe -sv CpuSetup_new.txt -n CpuSetup

4. 重启生效
~~~

**注意**：脚本运行目录下必须有 Backup 文件夹，否则 H2OUVE 报 Fail to open Backup/...（第一次就是这样失败的）。

### 6.4 怎么确认改成功了

不看脚本的"成功"提示，重新读一遍变量逐字节比对：

~~~
PchSetup 00000000: 00 00 C4 3E 00 01 00 00 [00] 01 02 00 01 01 00 00   <- 03→00 OK
PchSetup 00000010: 01 01 02 03 00 00 01 01 [01] 00 00 01 00 01 01 FF   <- 00→01 OK
CpuSetup 00000030: 00 00 00 00 00 00 00 01 01 03 03 00 00 01 [00] 00   <- 01→00 OK
SaSetup  00000100: 04 00 00 1A 00 0B 00 [02] 02 00 01 01 00 01 00 00   <- 01→02 OK
~~~

回退方法：把 Backup\*_Original.txt 用 -sv 写回去即可。

### 6.5 为什么改完就好了

| 变量 | 为什么它卡死引导 |
|---|---|
| **CFG Lock** | CPU 的 MSR 写保护。macOS 电源管理（XCPM）要写 MSR，锁着就启动早期失败，表现为 ExitBootServices 前后卡死 |
| **DVMT 64 MB** | 核显在 UEFI 阶段只分到 32 MB 甚至更少，macOS 驱动要求至少 64 MB，否则图形初始化失败 |
| **Kernel Debug Serial Port** | 八代平台必需固件状态，不关会在内核接管时冲突 |
| **GPIO 中断模式** | I2C 触控板的前提（不然装完触控板也不动） |

**结论**：前三个（尤其 CFG Lock + DVMT）是 EXITBS:START 的直接原因；第四个决定触控板能不能用。

---

## 7. 系统安装阶段（坑 13-14）

### 坑 13｜安装要现场下载 12 GB

恢复镜像 BaseSystem.dmg 只有 700 MB，是"救援系统"，系统本体在安装时从 Apple CDN 下载。

实测（同出口，单连接）：oscdn.apple.com 约 **3.1 MB/s** → 12 GB 约 65 分钟，加写盘校验共 1.5-2 小时。

**为什么有线也跑不满**：恢复环境下载器是单连接，Apple CDN 对单连接有速率上限（2-5 MB/s），与本地带宽无关。

**注意**：别在助手机上下同样的包，会抢带宽让安装更慢。

### 坑 14｜进度条的"2 小时 17 分"不可信

macOS 按最差情况估算，中段通常大幅缩短。操作要点：插电源、不合盖、不点取消；10 分钟看一次进度条，完全不动才是真卡住。

---

## 8. 当前状态与遗留问题

### 已完成
- macOS Ventura 13.4.1 安装成功（NVMe 系统盘）
- 1 TB 机械盘清空（可做 APFS 数据盘）
- Windows 用户数据备份在 B 机：backup-from-A.tar（483.3 MB，SHA256 一致）
- NTFS 体检通过（Repair-Volume -Scan = NoErrorsFound）
- 分区：C: 476.3 → 296.3 GB，空出 180 GB

### 待办（按优先级）

| 项 | 说明 |
|---|---|
| **SMBIOS 三码** | 当前用教程作者的假序列号 C02X1HACKGYG，iCloud / iMessage / App Store 大概率登不上，需生成自有三码 |
| **内置键盘/触控板** | 恢复环境里不可用；装完验证 VoodooPS2 / VoodooI2C，必要时调 SSDT-GPRW / GPIO |
| **睡眠唤醒** | 需现场逐项测试，可能要调 SSDT-PTSWAK / GPRW |
| **声卡 ALC236** | AppleALC layout-id 需要试（3 / 13 / 23 等） |
| **WiFi / 蓝牙** | 无解，除非换博通卡（BCM94360NG，M.2 2230，几十元） |
| **拔 U 盘冷启动** | 把 EFI 搬到硬盘 ESP，验证不插 U 盘能启动 |
| **版本升级** | 先稳在 Ventura 调通，再考虑 Sonoma 14 / Sequoia 15；Tahoe 26 风险最高（Intel 末代 + VoodooI2C 两年未更新） |

---

## 9. 可复用的经验清单

### 排查方法论
1. **先定位"层"，再改参数**：分层（配置/驱动/镜像/介质/固件）用对照实验逐个排除，依据是日志最后几行是否变化。
2. **看日志行数**：27 → 92 → 97，行数变化说明往前走了，最后几行不变说明卡在同一层。
3. **官方校验工具要配对版本**：ocvalidate 必须和 OpenCore 版本一致。
4. **配置通过不等于能启动**：固件层的问题，配置再干净也白搭。

### 环境陷阱
5. **"成功"可能是假成功**：计划任务排队、返回码 0、实际没执行 → 破坏性操作后必须独立回读。
6. **SSH 管理员不等于存储管理员**：磁盘操作走 SYSTEM 计划任务。
7. **笔记本电池会挂起计划任务**（只在交流电时启动）。
8. **junction 循环会骗统计**（16 GB 实际 520 MB）。

### 硬件事实
9. **Realtek 8822BE 在 macOS 上无解**（WiFi + 蓝牙都无驱动），换博通卡是唯一路。
10. **GTX 1050 Ti（Pascal）无解**，必须 SSDT 屏蔽，只靠 UHD 630。
11. **恢复镜像不含系统**，安装必须联网下载 12 GB，有线单连接也快不过 Apple CDN 限速。

### 针对"卡 EXITBS:START"的直接结论
12. **先查固件**：CFG Lock、DVMT、Kernel Debug Serial Port、GPIO 中断——普通 BIOS 看不到，必须 H2OUVE 或高级模式改。
13. **再查 SecureBootModel**：用恢复镜像安装必须 Disabled。
14. 以上都对了，OpenCore 配置反而没那么重要（官方模板 + ocvalidate 通过即可）。

---

## 10. 关键文件与命令备忘

| 用途 | 位置/命令 |
|---|---|
| U 盘 EFI | EFI/OC/config.plist（教程 v5.0.0 的 config_8300H_8750H.plist） |
| OpenCore 日志 | U 盘根目录 opencore-YYYY-MM-DD-HHMMSS.txt |
| 恢复镜像 | com.apple.recovery.boot/BaseSystem.dmg（Ventura 13.4.1，706 MB） |
| BIOS 变量备份 | A 机 C:\Users\sc\Desktop\biosfix\Backup\*_Original.txt |
| Windows 数据备份 | B 机 macos-install\backup-from-A.tar（SHA256 d7be122f…d9377c） |
| 生成恢复镜像 | python macrecovery.py -b board-id -os default download |
| 校验配置 | ocvalidate.exe config.plist（必须同版本） |
| 读 BIOS 变量 | H2OUVE-W-CONSOLEx64.exe -gv out.txt -n CpuSetup/SaSetup/PchSetup |
| 写 BIOS 变量 | H2OUVE-W-CONSOLEx64.exe -sv new.txt -n 变量名 |

---

*本文档根据 2026-11-07 ~ 11-08 实际操作记录整理，所有结论都有对应日志或回读证据；未验证部分已标注为待办。*
