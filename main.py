"""入口脚本：通用应用自动化测试流程示例。"""

from __future__ import annotations

from app_automation import AppAutomation, create_alipay_config, create_wechat_config, create_qishui_music_config, AppConfig
from config import DEFAULT_DEVICE_SERIAL


def run_alipay_flow() -> None:
    """运行支付宝自动化流程示例。"""
    print("=" * 50)
    print("支付宝自动化测试流程")
    print("=" * 50)
    
    automation = AppAutomation(DEFAULT_DEVICE_SERIAL)
    alipay_config = create_alipay_config()
    
    success = automation.run_app_flow(alipay_config)
    
    if success:
        print("\n✓ 支付宝自动化流程执行成功！")
    else:
        print("\n✗ 支付宝自动化流程执行失败！")


def run_qishui_music_flow() -> None:
    """运行汽水音乐自动化流程示例。"""
    print("=" * 50)
    print("汽水音乐自动化测试流程")
    print("=" * 50)
    
    automation = AppAutomation(DEFAULT_DEVICE_SERIAL)
    qishui_config = create_qishui_music_config()
    
    success = automation.run_app_flow(qishui_config)
    
    if success:
        print("\n✓ 汽水音乐自动化流程执行成功！")
    else:
        print("\n✗ 汽水音乐自动化流程执行失败！")


def list_installed_payment_apps() -> None:
    """列出设备上所有支付相关的应用。"""
    print("\n" + "=" * 50)
    print("设备上的支付相关应用")
    print("=" * 50)
    
    automation = AppAutomation(DEFAULT_DEVICE_SERIAL)
    payment_apps = automation.find_all_app_packages("pay")
    
    if payment_apps:
        for i, app in enumerate(payment_apps, 1):
            print(f"{i}. {app}")
    else:
        print("未找到支付相关应用")


def list_installed_music_apps() -> None:
    """列出设备上所有音乐相关的应用。"""
    print("\n" + "=" * 50)
    print("设备上的音乐相关应用")
    print("=" * 50)
    
    automation = AppAutomation(DEFAULT_DEVICE_SERIAL)
    music_apps = automation.find_all_app_packages("music")
    
    if music_apps:
        for i, app in enumerate(music_apps, 1):
            print(f"{i}. {app}")
    else:
        print("未找到音乐相关应用")


def show_menu() -> None:
    """显示主菜单。"""
    print("\n" + "=" * 50)
    print("自动化测试流程选择")
    print("=" * 50)
    print("1. 支付宝签到流程")
    print("2. 汽水音乐金币流程")
    print("3. 查看设备上的支付相关应用")
    print("4. 查看设备上的音乐相关应用")
    print("0. 退出")
    print("=" * 50)


def main() -> None:
    """主函数：显示菜单并让用户选择运行哪个流程。"""
    while True:
        show_menu()
        choice = input("\n请输入选项编号: ").strip()
        
        if choice == "1":
            run_alipay_flow()
        elif choice == "2":
            run_qishui_music_flow()
        elif choice == "3":
            list_installed_payment_apps()
        elif choice == "4":
            list_installed_music_apps()
        elif choice == "0":
            print("退出程序...")
            break
        else:
            print("无效的选项，请重新输入。")


if __name__ == "__main__":
    main()
