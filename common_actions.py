"""
常用动作封装模块。

该模块提供了 CommonActions 类，用于封装 Android UI 自动化中常见的操作。
它是整个自动化框架中最高频使用的组件，几乎所有的自动化步骤都依赖于它。

主要功能分类：
1. 元素点击操作：通过文本、描述、ID、坐标等方式点击元素
2. 文本输入操作：向输入框输入文本
3. 等待操作：等待元素出现/消失、等待指定时间
4. 按键操作：模拟物理按键（返回、主页、最近应用）
5. 截图操作：截取当前屏幕
6. 滑动操作：上下左右滑动屏幕
7. 设备信息获取：获取屏幕尺寸等

设计理念：
- 简洁易用：对 uiautomator2 的复杂 API 进行封装，提供简单直观的接口
- 智能判断：点击操作会先判断元素是否存在，避免异常
- 坐标支持：支持相对坐标和绝对坐标两种方式
- 容错机制：点击失败时返回 False，让上层可以处理

依赖关系：
- 依赖 uiautomator2 库提供底层设备操作能力
- 被 AppAutomation 类持有和使用
- 与 AppController 各司其职

使用示例：
    import uiautomator2 as u2
    from common_actions import CommonActions
    
    # 连接设备
    device = u2.connect()
    
    # 创建通用操作实例
    actions = CommonActions(device)
    
    # 点击元素
    actions.click_by_text("我的")
    
    # 等待3秒
    actions.wait_seconds(3)
    
    # 向上滑动
    actions.swipe_up()
    
    # 返回主页
    actions.press_home()

注意事项：
- 所有操作都依赖于当前的 UI 状态，元素不存在时可能失败
- 坐标操作需要考虑屏幕尺寸和分辨率的适配
- 等待时间需要根据实际设备性能调整
"""

from __future__ import annotations

import time
from typing import Optional, Tuple

import uiautomator2 as u2


class CommonActions:
    """
    通用 UI 操作封装类，提供常见 UI 操作的简单封装。
    
    该类是自动化框架的核心操作层，封装了 uiautomator2 的底层 API，
    提供了更简洁、更易用的接口。所有的自动化步骤都通过这个类来执行。
    
    属性说明：
        d: uiautomator2 的 Device 对象，用于执行实际的设备操作
    
    设计特点：
    1. 分层封装：将底层操作封装为语义化的方法名
    2. 安全点击：点击操作先检查元素是否存在，避免空指针异常
    3. 坐标智能：支持相对坐标（0.0-1.0）和绝对坐标两种方式
    4. 链式调用：部分方法返回 self，支持链式调用
    
    主要功能：
    - 元素定位与点击：支持多种定位策略
    - 文本输入：支持清空和追加两种模式
    - 等待机制：显式等待和隐式等待
    - 手势操作：滑动、点击等手势
    - 系统按键：模拟物理按键
    
    使用场景：
    - 自动化测试中的 UI 交互
    - 应用内的页面导航
    - 表单填写和提交
    - 页面滚动和浏览
    
    与其他组件的关系：
    - 被 AppAutomation 类持有和使用
    - 依赖 DeviceManager 连接的设备
    - 不依赖 AppController，各司其职
    """

    def __init__(self, device: u2.Device) -> None:
        """
        初始化 CommonActions 实例。
        
        参数：
            device: uiautomator2 的 Device 对象，必须是已连接的有效设备
            
        初始化过程：
        1. 保存传入的设备对象到实例变量 d
        2. 该设备对象将用于后续所有 UI 操作
        
        注意事项：
            - 传入的 device 必须是已经成功连接的设备对象
            - 如果 device 无效，后续操作将抛出异常
            
        使用示例：
            import uiautomator2 as u2
            
            # 直接连接设备
            device = u2.connect()
            actions = CommonActions(device)
            
            # 通过 DeviceManager（推荐）
            from device_manager import DeviceManager
            dm = DeviceManager()
            device = dm.connect()
            actions = CommonActions(device)
        """
        self.d = device

    def click_if_exists(self, timeout: float = 3, **selector: str) -> bool:
        """
        元素存在则点击并返回 True，否则返回 False。
        
        这是一个通用的安全点击方法，是其他点击方法的基础。
        它会先等待元素出现，如果在超时时间内元素出现，则点击它。
        
        参数：
            timeout: 等待元素出现的超时时间（秒），默认为 3 秒
            **selector: 元素选择器，支持以下参数：
                - text: 通过文本内容定位
                - description: 通过 content-description 定位
                - resourceId: 通过 resource-id 定位
                - className: 通过类名定位
                - 其他 uiautomator2 支持的选择器
                
        返回值：
            bool: 是否成功点击
                - True: 元素存在且点击成功
                - False: 元素不存在或超时
                
        执行流程：
        1. 根据选择器创建元素对象
        2. 等待元素出现，最多等待 timeout 秒
        3. 如果元素出现，点击并返回 True
        4. 如果元素未出现，返回 False
        
        设计意图：
        - 安全性：避免元素不存在时抛出异常
        - 灵活性：支持任意 uiautomator2 选择器
        - 可读性：方法名清晰表达意图
        
        使用示例：
            # 通过文本点击
            actions.click_if_exists(text="我的", timeout=5)
            
            # 通过 resource-id 点击
            actions.click_if_exists(resourceId="com.eg.android.AlipayGphone:id/tv_my")
            
            # 通过 description 点击
            actions.click_if_exists(description="返回按钮")
            
        注意事项：
            - 超时时间应根据页面加载速度合理设置
            - 如果元素在超时后才出现，将不会被点击
            - 此方法是其他点击方法的基础实现
        """
        obj = self.d(**selector)
        if obj.wait(timeout=timeout):
            obj.click()
            return True
        return False

    def click_by_text(self, text: str, timeout: float = 3) -> bool:
        """
        通过文本点击元素。
        
        通过元素的 text 属性定位并点击元素。这是最常用的点击方式之一。
        
        参数：
            text: 要点击的元素的文本内容
            timeout: 等待元素出现的超时时间（秒），默认为 3 秒
            
        返回值：
            bool: 是否成功点击
            
        使用场景：
            - 按钮上有明确的文本标签
            - 菜单项有文本描述
            - 列表项有文本标识
            
        使用示例：
            # 点击"我的"按钮
            actions.click_by_text("我的")
            
            # 点击"签到"按钮，等待5秒
            actions.click_by_text("签到", timeout=5)
            
            # 点击"确定"按钮
            actions.click_by_text("确定")
            
        注意事项：
            - 文本必须完全匹配（区分大小写）
            - 如果有多个相同文本的元素，会点击第一个
            - 某些应用的文本可能是动态变化的
        """
        return self.click_if_exists(timeout=timeout, text=text)

    def click_by_description(self, description: str, timeout: float = 3) -> bool:
        """
        通过 content-description 点击元素。
        
        通过元素的 content-description 属性定位并点击元素。
        content-description 是 Android 为无障碍功能设计的属性。
        
        参数：
            description: 要点击的元素的 content-description 内容
            timeout: 等待元素出现的超时时间（秒），默认为 3 秒
            
        返回值：
            bool: 是否成功点击
            
        使用场景：
            - 图标按钮没有文本，只有 content-description
            - 无障碍测试场景
            - 某些应用使用 description 而不是 text
            
        使用示例：
            # 点击"返回"按钮（通常是图标）
            actions.click_by_description("返回")
            
            # 点击"菜单"按钮
            actions.click_by_description("菜单")
            
            # 点击"搜索"图标
            actions.click_by_description("搜索")
            
        注意事项：
            - 不是所有元素都有 content-description
            - 某些应用的 description 可能与实际功能不符
            - 需要查看 UI 结构确定 description 的值
        """
        return self.click_if_exists(timeout=timeout, description=description)

    def click_by_resource_id(self, resource_id: str, timeout: float = 3) -> bool:
        """
        通过 resource-id 点击元素。
        
        通过元素的 resource-id 属性定位并点击元素。
        resource-id 是 Android 布局中最精确的定位方式之一。
        
        参数：
            resource_id: 要点击的元素的完整 resource-id，格式通常为：
                        "包名:id/控件名"，例如 "com.eg.android.AlipayGphone:id/tv_my"
            timeout: 等待元素出现的超时时间（秒），默认为 3 秒
            
        返回值：
            bool: 是否成功点击
            
        优点：
            - 定位最精确，不易受文本变化影响
            - 性能最好，直接通过 ID 查找
            
        缺点：
            - 需要知道确切的 resource-id
            - 不同版本的应用 ID 可能变化
            - 某些第三方应用可能混淆了 ID
            
        使用示例：
            # 通过完整 ID 点击
            actions.click_by_resource_id("com.eg.android.AlipayGphone:id/tv_my")
            
            # 等待10秒
            actions.click_by_resource_id("com.tencent.mm:id/bottom_tab_button_icon", timeout=10)
            
        注意事项：
            - resource-id 格式必须正确，包括包名部分
            - 某些应用可能没有设置 resource-id
            - 混淆后的应用 ID 可能难以识别
        """
        return self.click_if_exists(timeout=timeout, resourceId=resource_id)

    def click_by_coordinates(self, x: float, y: float) -> None:
        """
        通过坐标点击屏幕。支持相对坐标和绝对坐标两种方式。
        
        这是最直接的点击方式，不依赖任何 UI 属性，直接点击指定位置。
        
        参数：
            x: 点击位置的 x 坐标
               - 如果在 0.0-1.0 之间，视为相对坐标（占屏幕宽度的比例）
               - 如果大于 1，视为绝对坐标（像素值）
            y: 点击位置的 y 坐标
               - 如果在 0.0-1.0 之间，视为相对坐标（占屏幕高度的比例）
               - 如果大于 1，视为绝对坐标（像素值）
               
        坐标说明：
            相对坐标的优势：
            - 不受屏幕分辨率影响
            - 在不同尺寸的设备上都能正常工作
            - 推荐使用相对坐标
            
            绝对坐标的问题：
            - 依赖具体的屏幕分辨率
            - 在不同设备上可能点击位置不同
            - 只适合特定设备的测试
            
        常用相对坐标位置：
            - 左上角: (0.1, 0.1)
            - 右上角: (0.9, 0.1)
            - 左下角: (0.1, 0.9)
            - 右下角: (0.9, 0.9)
            - 屏幕中心: (0.5, 0.5)
            - 底部导航栏: (0.5, 0.95)
            
        使用示例：
            # 点击右下角（相对坐标）
            actions.click_by_coordinates(0.85, 0.95)
            
            # 点击屏幕中心（相对坐标）
            actions.click_by_coordinates(0.5, 0.5)
            
            # 点击绝对坐标（100, 200）
            actions.click_by_coordinates(100, 200)
            
        注意事项：
            - 相对坐标是相对于当前屏幕尺寸的
            - 绝对坐标需要考虑屏幕分辨率
            - 不同应用的布局可能不同，坐标需要调整
            - 这是最后的备选方案，优先使用文本或 ID 点击
        """
        if 0 <= x <= 1 and 0 <= y <= 1:
            self.d.click(x, y)
        else:
            self.d.click(int(x), int(y))

    def input_text(self, text: str, clear: bool = True, **selector: str) -> bool:
        """
        向指定元素输入文本。
        
        用于在输入框中输入文本，支持清空原有内容和追加两种模式。
        
        参数：
            text: 要输入的文本内容
            clear: 是否先清空原有内容，默认为 True
                   - True: 先调用 clear_text() 清空，再输入新文本
                   - False: 直接追加文本到现有内容之后
            **selector: 元素选择器，用于定位输入框元素
                        支持 text、description、resourceId 等选择器
                        
        返回值：
            bool: 是否成功输入
                - True: 元素存在且输入成功
                - False: 元素不存在
                
        执行流程：
        1. 根据选择器定位元素
        2. 检查元素是否存在
        3. 如果不存在，返回 False
        4. 如果 clear=True，清空元素内容
        5. 设置新的文本内容
        6. 返回 True
        
        使用场景：
            - 登录表单输入用户名和密码
            - 搜索框输入搜索关键词
            - 注册表单填写个人信息
            - 评论框输入评论内容
            
        使用示例：
            # 通过 resource-id 定位输入框并输入
            actions.input_text("13800138000", resourceId="com.eg.android.AlipayGphone:id/et_phone")
            
            # 通过文本定位并输入，不清空原有内容
            actions.input_text("追加内容", clear=False, text="请输入")
            
            # 通过 description 定位
            actions.input_text("搜索关键词", description="搜索框")
            
        注意事项：
            - 确保元素是可输入的（EditText 或类似控件）
            - 某些应用的输入框可能有特殊的交互逻辑
            - 密码输入框可能需要特殊处理
            - 输入特殊字符时需要考虑编码问题
        """
        obj = self.d(**selector)
        if not obj.exists:
            return False
        if clear:
            obj.clear_text()
        obj.set_text(text)
        return True

    def wait_seconds(self, seconds: float) -> None:
        """
        显式等待指定秒数。
        
        这是最简单的等待方式，直接暂停执行指定的时间。
        
        参数：
            seconds: 要等待的时间（秒），可以是浮点数，如 0.5 表示 500 毫秒
            
        使用场景：
            - 等待页面动画完成
            - 等待网络请求返回
            - 等待应用启动
            - 简单的同步等待
            
        与其他等待方式的比较：
            - wait_seconds: 固定等待时间，最简单但最不智能
            - wait_for_element: 等待元素出现，更智能但需要知道元素
            - wait_for_element_gone: 等待元素消失
            
        使用示例：
            # 等待3秒
            actions.wait_seconds(3)
            
            # 等待500毫秒
            actions.wait_seconds(0.5)
            
            # 等待10秒
            actions.wait_seconds(10)
            
        注意事项：
            - 固定等待可能导致测试不稳定
            - 网络差时可能需要更长时间
            - 建议优先使用条件等待（wait_for_element）
            - 仅在必要时使用固定等待
        """
        time.sleep(seconds)

    def wait_for_element(self, timeout: float = 10, **selector: str) -> bool:
        """
        等待元素出现，返回是否成功。
        
        等待指定的元素在超时时间内出现在屏幕上。
        这是一种条件等待，比固定等待更智能。
        
        参数：
            timeout: 等待的超时时间（秒），默认为 10 秒
            **selector: 元素选择器，用于定位要等待的元素
            
        返回值：
            bool: 元素是否在超时时间内出现
                - True: 元素出现
                - False: 超时后元素仍未出现
                
        执行流程：
        1. 根据选择器创建元素对象
        2. 调用 wait() 方法等待元素出现
        3. 返回等待结果
        
        使用场景：
            - 等待页面加载完成
            - 等待弹窗出现
            - 等待异步操作完成
            - 等待列表加载更多数据
            
        使用示例：
            # 等待"登录"按钮出现，最多等10秒
            actions.wait_for_element(timeout=10, text="登录")
            
            # 等待 loading 图标消失前先等待出现
            actions.wait_for_element(resourceId="com.app:id/progress_bar")
            
            # 等待弹窗标题出现
            actions.wait_for_element(description="提示")
            
        注意事项：
            - 超时时间应根据实际情况设置
            - 如果元素已经存在，会立即返回 True
            - 这是主动等待，会定期检查元素状态
            - 与 wait_seconds 不同，元素出现后会立即继续
        """
        obj = self.d(**selector)
        return obj.wait(timeout=timeout)

    def wait_for_element_gone(self, timeout: float = 10, **selector: str) -> bool:
        """
        等待元素消失，返回是否成功。
        
        等待指定的元素在超时时间内从屏幕上消失。
        常用于等待加载完成、弹窗关闭等场景。
        
        参数：
            timeout: 等待的超时时间（秒），默认为 10 秒
            **selector: 元素选择器，用于定位要等待消失的元素
            
        返回值：
            bool: 元素是否在超时时间内消失
                - True: 元素已消失
                - False: 超时后元素仍然存在
                
        使用场景：
            - 等待加载动画消失
            - 等待进度条完成
            - 等待弹窗关闭
            - 等待页面跳转完成
            
        使用示例：
            # 等待加载动画消失
            actions.wait_for_element_gone(resourceId="com.app:id/loading_view")
            
            # 等待进度条消失
            actions.wait_for_element_gone(description="加载中")
            
            # 等待弹窗关闭
            actions.wait_for_element_gone(text="确定")
            
        注意事项：
            - 如果元素本来就不存在，会立即返回 True
            - 常用于等待异步操作完成
            - 与 wait_for_element 配合使用效果更好
        """
        obj = self.d(**selector)
        return obj.wait_gone(timeout=timeout)

    def press_back(self) -> None:
        """
        执行返回键操作。
        
        模拟按下 Android 设备的物理返回键。
        
        效果：
            - 返回上一个页面
            - 关闭当前弹窗
            - 退出当前应用（如果是最后一个页面）
            
        使用场景：
            - 页面导航返回
            - 关闭弹窗
            - 取消操作
            - 多级返回
            
        使用示例：
            # 返回上一页
            actions.press_back()
            
            # 连续返回两次
            actions.press_back()
            actions.press_back()
            
        注意事项：
            - 返回行为由当前应用的 Activity 栈决定
            - 某些应用可能拦截返回键
            - 返回键和 press_home 的区别：
              - back: 返回上一级
              - home: 回到桌面
        """
        self.d.press("back")

    def press_home(self) -> None:
        """
        执行主页键操作。
        
        模拟按下 Android 设备的物理主页键。
        
        效果：
            - 将当前应用切换到后台
            - 显示设备的主屏幕（Launcher）
            - 不会销毁应用，应用仍在后台运行
            
        使用场景：
            - 自动化完成后返回桌面
            - 多应用切换时返回桌面
            - 测试结束后的清理操作
            
        使用示例：
            # 返回桌面
            actions.press_home()
            
        注意事项：
            - 应用只是被切换到后台，并未被销毁
            - 与 stop_app 会销毁应用进程
            - 再次启动应用会从后台恢复
        """
        self.d.press("home")

    def press_recent(self) -> None:
        """
        执行最近应用键操作。
        
        模拟按下 Android 设备的最近应用键（多任务键）。
        
        效果：
            - 显示最近使用的应用列表
            - 可以在应用之间切换
            - 可以关闭最近应用
            
        使用场景：
            - 多应用切换测试
            - 查看后台运行的应用
            - 清理后台应用
            
        使用示例：
            # 显示最近应用
            actions.press_recent()
            
        注意事项：
            - 不同设备的最近应用键实现可能不同
            - 某些设备可能没有物理最近应用键
            - 某些自定义 ROM 可能有不同的行为
        """
        self.d.press("recent")

    def screenshot(self, filename: str) -> None:
        """
        截图并保存到指定文件。
        
        截取当前屏幕并保存为图片文件。
        
        参数：
            filename: 保存截图的文件路径，可以是相对路径或绝对路径
                      支持的格式通常为 PNG 格式
                      
        效果：
            - 截取当前屏幕的完整截图
            - 保存到指定路径
            - 如果文件已存在会被覆盖
            
        使用场景：
            - 测试失败时保存证据
            - 记录测试过程
            - 调试 UI 问题
            - 生成测试报告
            
        使用示例：
            # 保存到当前目录
            actions.screenshot("screenshot.png")
            
            # 保存到指定路径
            actions.screenshot("/tmp/test_result.png")
            
            # 带时间戳的文件名
            import time
            actions.screenshot(f"screenshot_{int(time.time())}.png")
            
        注意事项：
            - 确保有写入文件的权限
            - 目录必须存在，否则会失败
            - 文件名应该以 .png 结尾
            - 截图包含状态栏和导航栏
        """
        self.d.screenshot(filename)

    def get_screen_size(self) -> Tuple[int, int]:
        """
        获取屏幕尺寸。
        
        返回设备屏幕的宽度和高度（像素）。
        
        返回值：
            Tuple[int, int]: 包含两个整数的元组
                - 第一个元素：屏幕宽度（像素）
                - 第二个元素：屏幕高度（像素）
                
        使用场景：
            - 计算相对坐标计算
            - 滑动操作的起点和终点计算
            - 判断设备适配
            - 布局验证
            
        使用示例：
            width, height = actions.get_screen_size()
            print(f"屏幕尺寸: {width} x {height}")
            
            # 计算中心坐标
            center_x = width / 2
            center_y = height / 2
            
        注意事项：
            - 返回的是物理像素，不是 dp 不是 dp
            - 不同设备的屏幕尺寸不同
            - 考虑屏幕旋转的影响
            - 某些设备可能有虚拟导航栏
        """
        return self.d.window_size()

    def swipe(self, start_x: float, start_y: float, end_x: float, end_y: float, duration: float = 0.5) -> None:
        """
        滑动屏幕。支持相对坐标和绝对坐标两种方式。
        
        从起点坐标滑动到终点坐标，执行时间为 duration 秒。
        
        参数：
            start_x: 滑动起点的 x 坐标
            start_y: 滑动起点的 y 坐标
            end_x: 滑动终点的 x 坐标
            end_y: 滑动终点的 y 坐标
            duration: 滑动持续时间（秒），默认为 0.5 秒
                      时间越短，滑动速度越快
            
        坐标说明：
            - 如果所有坐标都在 0.0-1.0 之间，视为相对坐标
            - 否则视为绝对坐标（像素值）
            
        滑动方向：
            - 向上滑动：y 从大到小
            - 向下滑动：y 从小到大
            - 向左滑动：x 从大到小
            - 向右滑动：x 从小到大
            
        使用示例：
            # 相对坐标：从底部向上滑动
            actions.swipe(0.5, 0.8, 0.5, 0.2)
            
            # 绝对坐标：从 (100, 1000) 滑动到 (100, 200)
            actions.swipe(100, 1000, 100, 200)
            
            # 快速滑动（0.2 秒）
            actions.swipe(0.5, 0.8, 0.5, 0.2, duration=0.2)
            
        注意事项：
            - 滑动时间影响滑动的距离和速度
            - 相对坐标更适合跨设备使用
            - 滑动可能触发不同的 UI 行为
            - 某些应用可能有自定义的滑动手势
        """
        if all(0 <= coord <= 1 for coord in [start_x, start_y, end_x, end_y]):
            self.d.swipe(start_x, start_y, end_x, end_y, duration=duration)
        else:
            self.d.swipe(int(start_x), int(start_y), int(end_x), int(end_y), duration=duration)

    def swipe_up(self, duration: float = 0.5) -> None:
        """
        向上滑动屏幕。
        
        从屏幕中下部向上滑动到中上部，用于查看页面下方的内容。
        
        参数：
            duration: 滑动持续时间（秒），默认为 0.5 秒
            
        滑动范围：
            - 起点：屏幕水平中心，垂直 80% 位置（中下部）
            - 终点：屏幕水平中心，垂直 20% 位置（中上部）
            
        效果：
            - 页面内容向下滚动（显示更多下方内容）
            - 列表向上滚动
            - 查看更多内容
            
        使用场景：
            - 浏览长页面
            - 查看列表下方内容
            - 滚动到页面底部
            - 刷新页面（某些应用）
            
        使用示例：
            # 默认速度向上滑动
            actions.swipe_up()
            
            # 快速滑动
            actions.swipe_up(duration=0.2)
            
            # 连续滑动多次
            for i in range(5):
                actions.swipe_up()
                actions.wait_seconds(1)
            
        注意事项：
            - 滑动距离是固定的相对比例
            - 不同屏幕尺寸的实际滑动距离不同
            - 某些应用可能有自定义的滚动行为
            - 滑动到顶部后继续滑动可能触发刷新
        """
        width, height = self.get_screen_size()
        self.swipe(width / 2, height * 0.8, width / 2, height * 0.2, duration)

    def swipe_down(self, duration: float = 0.5) -> None:
        """
        向下滑动屏幕。
        
        从屏幕中上部向下滑动到中下部，用于查看页面上方的内容或刷新页面。
        
        参数：
            duration: 滑动持续时间（秒），默认为 0.5 秒
            
        滑动范围：
            - 起点：屏幕水平中心，垂直 20% 位置（中上部）
            - 终点：屏幕水平中心，垂直 80% 位置（中下部）
            
        效果：
            - 页面内容向上滚动（显示更多上方内容）
            - 列表向下滚动
            - 某些应用会触发下拉刷新
            
        使用场景：
            - 回到页面顶部
            - 下拉刷新页面
            - 查看页面上方内容
            - 关闭某些特殊交互
            
        使用示例：
            # 默认速度向下滑动
            actions.swipe_down()
            
            # 快速滑动
            actions.swipe_down(duration=0.2)
            
            # 下拉刷新
            actions.swipe_down()
            
        注意事项：
            - 滑动距离是固定的相对比例
            - 某些应用下拉会触发刷新
            - 滑动到顶部后继续滑动可能没有效果
            - 与 swipe_up 方向相反
        """
        width, height = self.get_screen_size()
        self.swipe(width / 2, height * 0.2, width / 2, height * 0.8, duration)

    def swipe_left(self, duration: float = 0.5) -> None:
        """
        向左滑动屏幕。
        
        从屏幕右部向左滑动到左部，用于水平滚动或切换页面。
        
        参数：
            duration: 滑动持续时间（秒），默认为 0.5 秒
            
        滑动范围：
            - 起点：垂直中心，水平 80% 位置（右部）
            - 终点：垂直中心，水平 20% 位置（左部）
            
        效果：
            - 页面内容向右滚动
            - ViewPager 切换到下一页
            - 某些列表项显示操作按钮
            
        使用场景：
            - 轮播图切换
            - ViewPager 页面切换
            - 水平列表滚动
            - 某些应用的侧滑菜单
            
        使用示例：
            # 默认速度向左滑动
            actions.swipe_left()
            
            # 快速滑动
            actions.swipe_left(duration=0.2)
            
            # 切换多页
            for i in range(3):
                actions.swipe_left()
                actions.wait_seconds(1)
            
        注意事项：
            - 滑动距离是固定的相对比例
            - 某些应用可能有自定义的侧滑菜单
            - 滑动可能触发删除等操作
            - 与 swipe_right 方向相反
        """
        width, height = self.get_screen_size()
        self.swipe(width * 0.8, height / 2, width * 0.2, height / 2, duration)

    def swipe_right(self, duration: float = 0.5) -> None:
        """
        向右滑动屏幕。
        
        从屏幕左部向右滑动到右部，用于水平滚动或切换页面。
        
        参数：
            duration: 滑动持续时间（秒），默认为 0.5 秒
            
        滑动范围：
            - 起点：垂直中心，水平 20% 位置（左部）
            - 终点：垂直中心，水平 80% 位置（右部）
            
        效果：
            - 页面内容向左滚动
            - ViewPager 切换到上一页
            - 关闭侧滑菜单
            
        使用场景：
            - 轮播图切换到上一页
            - ViewPager 返回上一页
            - 水平列表滚动
            - 关闭侧滑菜单
            
        使用示例：
            # 默认速度向右滑动
            actions.swipe_right()
            
            # 快速滑动
            actions.swipe_right(duration=0.2)
            
            # 关闭侧滑菜单
            actions.swipe_right()
            
        注意事项：
            - 滑动距离是固定的相对比例
            - 某些应用的侧滑菜单需要向右滑动关闭
            - 与 swipe_left 方向相反
            - 滑动到最右侧后继续滑动可能没有效果
        """
        width, height = self.get_screen_size()
        self.swipe(width * 0.2, height / 2, width * 0.8, height / 2, duration)
