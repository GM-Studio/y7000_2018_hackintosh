# 02 · BIOS 修改记录

> ⚠️ **这是整个项目最关键的一步。不改这 4 个变量，OpenCore 永远卡在 `EXITBS:START`。**

## 一、为什么必须改

联想拯救者 Y7000（2018）的 InsydeH2O BIOS 默认：

- 开启 CFG Lock（锁 MSR 0xE2）
- DVMT 显存 32MB（核显不够用）
- 8 代平台 Kernel Debug 锁
- GPIO 中断关闭（触控板不工作）

macOS 内核在 `EXITBS` 阶段需要这些条件，否则直接卡死（无任何报错）。

## 二、需要修改的 4 个变量

| 变量名 | Setup 区 | 偏移 | 原值 | 新值 | 作用 |
|---|---|---|---|---|---|
| CFG Lock | `CpuSetup` | `0x3E` | `01` | **`00`** | 关闭 MSR 0xE2 写保护 |
| DVMT Pre-Allocated | `SaSetup` | `0x107` | `01` | **`02`** | 显存 32MB → **64MB** |
| Kernel Debug | `PchSetup` | `0x08` | `03` | **`00`** | 关闭 8 代调试锁 |
| GPIO IRQ | `PchSetup` | `0x18` | `00` | **`01`** | 开启触控板中断 |

## 三、操作步骤

### 1. 准备（在 Windows 下）

1. 下载 `xiaoMGitHub/LEGION_Y7000Series_Insyde_Advanced_Settings_Tools`
2. 解压到任意目录（本归档已带：`BiosTools\`）
3. **关闭杀毒软件**（会误报 WDFInst）

### 2. 执行

~~~
右键「双击执行.bat」→ 以管理员身份运行
→ 自动安装驱动、备份原始变量到 Backup\
→ 按提示修改 4 个变量
→ 选择 Verify 重新读取确认
~~~

### 3. 验证（必须做）

改完后**重新读一遍**，确认写入生效：

~~~
CpuSetup 0x3E  = 00
SaSetup  0x107 = 02
PchSetup 0x08  = 00
PchSetup 0x18  = 01
~~~

### 4. 重启

进 OpenCore → 应该能直接通过 EXITBS。

## 四、注意事项

| 事项 | 说明 |
|---|---|
| 变量存在固件里 | 断电、换系统都不会丢 |
| **刷 BIOS 会重置** | 以后刷 BIOS 必须重做这 4 项 |
| 备份目录 | `BiosTools\Backup\*_Original.txt` 是原始值，别删 |
| 换主板 | 需要重新确认偏移（不同型号不同） |
| 风险 | 只改这 4 个已知偏移是安全的；**不要乱改其他项** |

## 五、副作用与已知影响

- CFG Lock 关闭后：Windows 下也不再有该锁（无影响）
- DVMT 改 64MB 后：显存占用增加，系统可用内存减少 32MB（可忽略）
- GPIO 开启后：触控板中断正常（Windows 下也正常）

## 六、如果没改会怎样

~~~
OC: 显示菜单 → 选择 macOS → 黑屏
日志末尾: AAPL: #[EB|LOG:EXITBS:START]
然后永久卡住（不会自己重启）
~~~

这就是本次耗时 3.5 小时的那个坑。
