"""
设备连接与基础信息管理模块。

该模块提供了 DeviceManager 类，负责管理 Android 设备的连接和应用包名查找。
它是整个自动化框架的基础设施层，为上层提供设备访问能力。

主要功能：
1. 设备连接管理：连接单个或多个 Android 设备
2. 应用包名管理：获取已安装应用列表，通过关键字查找包名
3. 多设备支持：支持通过序列号指定特定设备

设计理念：
- 封装底层连接逻辑：对 uiautomator2 的连接 API 进行封装
- 灵活的设备选择：支持默认设备和指定序列号的设备
- 智能包名查找：支持模糊匹配，大小写不敏感

依赖关系：
- 依赖 uiautomator2 库提供底层设备连接能力
- 依赖 adb 命令行工具获取已安装应用列表
- 被 AppAutomation 类使用，作为设备连接的入口

使用示例：
    from device_manager import DeviceManager
    
    # 连接默认设备
    dm = DeviceManager()
    device = dm.connect()
    
    # 连接指定设备（通过序列号）
    dm = DeviceManager("127.0.0.1:5555")
    device = dm.connect()
    
    # 查找应用包名
    package = dm.find_package_by_keyword("AlipayGphone")
    print(f"找到包名: {package}")

注意事项：
- 设备必须已通过 ADB 连接（USB 或无线调试）
- 设备必须开启 USB 调试模式
- 部分系统应用可能无法被普通用户访问
"""

from __future__ import annotations

import re
import subprocess
from typing import List, Optional

import uiautomator2 as u2


class DeviceManager:
    """
    设备管理器类，负责连接 Android 设备并返回 uiautomator2 设备对象。
    
    该类是整个自动化框架的设备访问入口，提供了设备连接和应用包名管理功能。
    
    属性说明：
        serial: 可选的设备序列号，用于指定连接特定设备
               - 如果为 None，则连接第一个可用设备
               - 如果指定，则连接对应序列号的设备
    
    设计特点：
    1. 轻量级连接管理：封装 uiautomator2 的连接逻辑
    2. 多设备支持：通过序列号区分不同设备
    3. 智能包名查找：支持模糊匹配和正则表达式
    4. 命令行集成：通过 adb 命令获取应用信息
    
    主要功能：
    - connect(): 连接设备并返回 uiautomator2 设备对象
    - get_installed_packages(): 获取设备上所有已安装的应用包名
    - find_package_by_keyword(): 通过关键字查找单个应用包名
    - find_packages_by_keyword(): 通过关键字查找所有匹配的应用包名
    
    使用场景：
    - 自动化测试前连接设备
    - 多设备并行测试
    - 动态查找应用包名
    - 应用管理相关操作
    
    与其他组件的关系：
    - 被 AppAutomation 类持有和使用
    - 为 AppController 和 CommonActions 提供设备对象
    - 不依赖其他框架组件，是最底层的基础设施
    """

    def __init__(self, serial: str | None = None) -> None:
        """
        初始化 DeviceManager 实例。
        
        参数：
            serial: 可选的设备序列号，用于指定连接特定设备
                   - 如果为 None，则在 connect() 时连接第一个可用设备
                   - 如果指定序列号，则连接对应序列号的设备
                   
        设备序列号格式：
            - USB 连接：通常是一串字母数字，如 "emulator-5554" 或 "abc123def456"
            - 无线连接：IP 地址加端口，如 "192.168.1.100:5555"
            
        初始化过程：
        1. 保存传入的序列号到实例变量 serial
        2. 实际的设备连接在 connect() 方法中执行
        
        使用示例：
            # 方式1：使用默认设备
            dm = DeviceManager()
            device = dm.connect()
            
            # 方式2：指定设备序列号
            dm = DeviceManager("emulator-5554")
            device = dm.connect()
            
            # 方式3：无线连接
            dm = DeviceManager("192.168.1.100:5555")
            device = dm.connect()
            
        注意事项：
            - 初始化时不会立即连接设备
            - 设备连接是在 connect() 方法调用时才执行
            - 如果指定了错误的序列号，connect() 会抛出异常
        """
        self.serial = serial

    def connect(self) -> u2.Device:
        """
        连接设备并返回 uiautomator2 设备对象。
        
        这是 DeviceManager 的核心方法，用于建立与 Android 设备的连接。
        
        返回值：
            u2.Device: uiautomator2 的设备对象，可用于执行设备操作
            
        连接策略：
            - 如果初始化时指定了序列号：连接指定序列号的设备
            - 如果未指定序列号：自动连接第一个可用的设备
            
        执行流程：
        1. 检查是否指定了设备序列号
        2. 如果有指定序列号，调用 u2.connect(serial) 连接该设备
        3. 如果没有指定，调用 u2.connect() 连接默认设备
        4. 返回连接成功的设备对象
            
        异常处理：
            - 设备未连接：抛出 uiautomator2 相关异常
            - 序列号不存在：抛出连接异常
            - ADB 服务未启动：可能导致连接失败
            
        使用示例：
            # 基本使用
            dm = DeviceManager()
            device = dm.connect()
            
            # 连接后可直接使用设备对象
            device.app_start("com.eg.android.AlipayGphone")
            
        注意事项：
            - 确保设备已通过 ADB 连接（USB 或无线）
            - 确保设备已开启 USB 调试模式
            - 确保电脑已授权连接该设备
            - 多次调用 connect() 会返回同一个设备对象（如果已连接）
            
        前置条件：
            1. 设备已连接到电脑（USB 线或无线 ADB）
            2. 设备已开启 USB 调试
            3. 电脑已授权设备连接（首次连接时需要确认）
        """
        return u2.connect(self.serial) if self.serial else u2.connect()

    def get_installed_packages(self) -> List[str]:
        """
        获取设备上所有已安装的应用包名列表。
        
        通过执行 adb shell pm list packages 命令获取设备上所有已安装的应用包名。
        
        返回值：
            List[str]: 包含所有已安装应用包名的列表
                      - 如果获取失败，返回空列表
                      - 包名格式如 "com.eg.android.AlipayGphone"
                      
        执行流程：
        1. 构建 adb 命令：
           - 基础命令：adb shell pm list packages
           - 如果指定了设备序列号：adb -s <serial> shell pm list packages
        2. 执行命令并捕获输出
        3. 解析输出，提取包名：
           - 每行输出格式为 "package:com.example.app"
           - 去掉 "package:" 前缀，提取包名
        4. 返回包名列表
        
        命令输出格式示例：
            package:com.android.settings
            package:com.eg.android.AlipayGphone
            package:com.tencent.mm
            
        解析后结果：
            ["com.android.settings", "com.eg.android.AlipayGphone", "com.tencent.mm"]
            
        使用场景：
            - 查看设备上安装了哪些应用
            - 检查目标应用是否已安装
            - 通过关键字查找特定应用
            - 应用管理功能
            
        使用示例：
            dm = DeviceManager()
            packages = dm.get_installed_packages()
            
            # 打印所有应用包名
            for pkg in packages:
                print(pkg)
                
            # 检查支付宝是否已安装
            has_alipay = any("Alipay" in pkg for pkg in packages)
            
        注意事项：
            - 需要 ADB 命令行工具可用
            - 某些系统应用可能无法被普通用户访问
            - 执行命令需要一定时间，特别是应用较多时
            - 如果命令执行失败，返回空列表
            
        可能的失败原因：
            1. ADB 服务未启动
            2. 设备未连接
            3. 权限不足
            4. 设备离线
        """
        cmd = ["adb"]
        if self.serial:
            cmd.extend(["-s", self.serial])
        cmd.extend(["shell", "pm", "list", "packages"])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        packages = []
        
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if line.startswith("package:"):
                    package_name = line.split(":", 1)[1].strip()
                    packages.append(package_name)
        
        return packages

    def find_package_by_keyword(self, keyword: str) -> Optional[str]:
        """
        通过关键字模糊查找应用包名，返回第一个匹配的包名。
        
        在设备已安装的所有应用中，查找包名包含指定关键字的应用。
        匹配是大小写不敏感的，返回第一个匹配的包名。
        
        参数：
            keyword: 要搜索的关键字，可以是包名的任意部分
                    - 不区分大小写
                    - 支持部分匹配
                    
        返回值：
            Optional[str]: 第一个匹配的应用包名
                          - 如果找到匹配项，返回包名字符串
                          - 如果没有找到匹配项，返回 None
                          
        匹配规则：
            - 使用正则表达式进行模糊匹配
            - 大小写不敏感（re.IGNORECASE）
            - 关键字中的特殊字符会被转义（re.escape）
            - 只要包名中包含关键字，就算匹配成功
            
        执行流程：
        1. 调用 get_installed_packages() 获取所有已安装包名
        2. 编译正则表达式：
           - 使用 re.escape 转义关键字中的特殊字符
           - 使用 re.IGNORECASE 标志实现大小写不敏感
        3. 遍历包名列表，逐个检查是否匹配
        4. 返回第一个匹配的包名
        5. 如果遍历完都没有匹配，返回 None
        
        使用示例：
            dm = DeviceManager()
            
            # 查找支付宝（包名通常包含 AlipayGphone）
            alipay = dm.find_package_by_keyword("AlipayGphone")
            if alipay:
                print(f"找到支付宝: {alipay}")
            else:
                print("未找到支付宝")
                
            # 查找微信（包名通常包含 mm）
            wechat = dm.find_package_by_keyword("mm")
            if wechat:
                print(f"找到微信: {wechat}")
                
            # 查找汽水音乐（包名通常包含 luna.music）
            qishui = dm.find_package_by_keyword("luna.music")
            
        注意事项：
            - 关键字不需要完全匹配包名，部分匹配即可
            - 匹配是大小写不敏感的
            - 如果有多个应用匹配，只返回第一个
            - 如果需要所有匹配项，使用 find_packages_by_keyword()
            
        常见应用关键字示例：
            - 支付宝："AlipayGphone"
            - 微信："mm" 或 "tencent.mm"
            - QQ："qq" 或 "tencent.mobileqq"
            - 抖音："aweme" 或 "bytedance"
            - 汽水音乐："luna.music"
            
        与 find_packages_by_keyword 的区别：
            - find_package_by_keyword: 返回第一个匹配项（单个）
            - find_packages_by_keyword: 返回所有匹配项（列表）
        """
        packages = self.get_installed_packages()
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        
        for package in packages:
            if pattern.search(package):
                return package
        
        return None

    def find_packages_by_keyword(self, keyword: str) -> List[str]:
        """
        通过关键字模糊查找所有匹配的应用包名，返回所有匹配的包名列表。
        
        与 find_package_by_keyword 不同，该方法会返回所有匹配的包名，
        而不仅仅是第一个。这在有多个应用包含相同关键字时很有用。
        
        参数：
            keyword: 要搜索的关键字，可以是包名的任意部分
                    - 不区分大小写
                    - 支持部分匹配
                    
        返回值：
            List[str]: 所有匹配的应用包名列表
                      - 如果找到匹配项，返回包含所有匹配包名的列表
                      - 如果没有找到匹配项，返回空列表
                      
        匹配规则：
            - 与 find_package_by_keyword 相同
            - 使用正则表达式进行模糊匹配
            - 大小写不敏感（re.IGNORECASE）
            - 关键字中的特殊字符会被转义
            
        执行流程：
        1. 调用 get_installed_packages() 获取所有已安装包名
        2. 编译正则表达式（与 find_package_by_keyword 相同）
        3. 遍历包名列表，收集所有匹配的包名
        4. 返回匹配的包名列表
        5. 如果没有匹配项，返回空列表
        
        使用场景：
            - 查找所有包含特定关键字的应用
            - 检查是否有多个应用匹配
            - 批量操作匹配的应用
            - 应用分类管理
            
        使用示例：
            dm = DeviceManager()
            
            # 查找所有包含 "music" 的应用
            music_apps = dm.find_packages_by_keyword("music")
            print(f"找到 {len(music_apps)} 个音乐应用:")
            for app in music_apps:
                print(f"  - {app}")
                
            # 查找所有腾讯系应用
            tencent_apps = dm.find_packages_by_keyword("tencent")
            print(f"找到 {len(tencent_apps)} 个腾讯应用:")
            for app in tencent_apps:
                print(f"  - {app}")
                
            # 检查是否有多个匹配
            matches = dm.find_packages_by_keyword("qq")
            if len(matches) > 1:
                print(f"找到多个 QQ 相关应用: {matches}")
                
        注意事项：
            - 返回的是所有匹配项，而不仅仅是第一个
            - 匹配规则与 find_package_by_keyword 相同
            - 列表顺序与 get_installed_packages() 返回的顺序一致
            - 空列表表示没有找到任何匹配项
            
        与 find_package_by_keyword 的区别：
            - 返回类型不同：
              - find_package_by_keyword: 返回单个字符串或 None
              - find_packages_by_keyword: 返回列表（可能为空）
            - 使用场景不同：
              - find_package_by_keyword: 已知只有一个匹配时使用
              - find_packages_by_keyword: 需要所有匹配时使用
              
        实际应用示例：
            # 场景1：不确定关键字是否唯一
            matches = dm.find_packages_by_keyword("video")
            if len(matches) == 0:
                print("未找到视频应用")
            elif len(matches) == 1:
                print(f"找到视频应用: {matches[0]}")
            else:
                print(f"找到多个视频应用: {matches}")
                
            # 场景2：批量操作
            browser_apps = dm.find_packages_by_keyword("browser")
            for browser in browser_apps:
                print(f"检查浏览器: {browser}")
        """
        packages = self.get_installed_packages()
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        
        matched_packages = []
        for package in packages:
            if pattern.search(package):
                matched_packages.append(package)
        
        return matched_packages
