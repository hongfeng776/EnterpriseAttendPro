import sys


def show_start_menu():
    print("\n" + "=" * 60)
    print("  企业级员工考勤管理系统")
    print("=" * 60)
    print("\n请选择启动方式:")
    print("  1. Web 前端界面（推荐，可在浏览器中使用）")
    print("  2. 命令行界面")
    print("  3. 帮助说明")
    print("  0. 退出")
    print("-" * 60)


def show_help():
    print("\n" + "=" * 60)
    print("  使用帮助")
    print("=" * 60)
    print("\n【Web 前端界面】")
    print("  • 启动后自动打开浏览器访问 http://localhost:8080")
    print("  • 员工端: 输入员工编号登录后可申请请假")
    print("  • 管理员端: 访问 http://localhost:8080/admin 进行审批")
    print("\n【功能说明】")
    print("  • 员工可申请年假、病假、事假等多种类型请假")
    print("  • 管理员可查看所有待审批申请并进行审批")
    print("  • 请假批准后自动豁免对应日期的考勤")
    print("\n【默认员工】")
    print("  • 如果系统中没有员工，请先使用命令行添加")
    print("  • 或者在首次使用时添加测试员工")
    print("")


def run_web_mode():
    from src.web.server import WebUI
    web_ui = WebUI(port=8080)
    web_ui.run()


def run_cli_mode():
    from src.ui.menu import AttendanceSystem
    system = AttendanceSystem()
    system.run()


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["web", "--web", "-w"]:
            run_web_mode()
            return
        elif arg in ["cli", "--cli", "-c"]:
            run_cli_mode()
            return
        elif arg in ["help", "--help", "-h"]:
            show_help()
            return

    while True:
        show_start_menu()
        try:
            choice = input("请选择 [0-3]: ").strip()
            if choice == "1":
                run_web_mode()
                break
            elif choice == "2":
                run_cli_mode()
                break
            elif choice == "3":
                show_help()
                input("\n按回车键返回菜单...")
            elif choice == "0":
                print("\n感谢使用企业级员工考勤管理系统，再见！\n")
                break
            else:
                print("\n  无效的选择，请重新输入！")
        except KeyboardInterrupt:
            print("\n\n已取消操作。")
            break


if __name__ == "__main__":
    main()
