import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import sys
import os

class TailscaleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tailscale GUI 工具 - 无控制台版本")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        self.setup_ui()
        self.setup_bindings()
        self.show_welcome_message()
    
    def setup_ui(self):
        """设置用户界面"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 命令选择区域
        command_frame = ttk.LabelFrame(main_frame, text="命令配置", padding="5")
        command_frame.grid(row=0, column=0, columnspan=3, sticky=tk.W+tk.E, pady=5)
        command_frame.columnconfigure(1, weight=1)
        
        # 命令选择
        ttk.Label(command_frame, text="选择命令:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.command_var = tk.StringVar(value="status")
        commands = ["status", "up", "down", "login", "logout", "netcheck", "ping", "version", "ip", "web"]
        self.command_combo = ttk.Combobox(command_frame, textvariable=self.command_var, 
                                        values=commands, state="readonly", width=15)
        self.command_combo.grid(row=0, column=1, sticky=tk.W, pady=2, padx=5)
        
        # 参数输入
        ttk.Label(command_frame, text="参数:").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.param_var = tk.StringVar()
        self.param_entry = ttk.Entry(command_frame, textvariable=self.param_var, width=40)
        self.param_entry.grid(row=0, column=3, sticky=tk.W+tk.E, pady=2, padx=5)
        command_frame.columnconfigure(3, weight=1)
        
        # 执行按钮
        self.run_button = ttk.Button(command_frame, text="执行命令", command=self.execute_command, width=15)
        self.run_button.grid(row=0, column=4, padx=10)
        
        # 快捷命令按钮
        quick_frame = ttk.Frame(main_frame)
        quick_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        quick_commands = [
            ("状态检查", "status", ""),
            ("连接网络", "up", "--accept-routes"),
            ("断开连接", "down", ""),
            ("网络诊断", "netcheck", ""),
            ("显示IP", "ip", ""),
        ]
        
        for i, (text, cmd, param) in enumerate(quick_commands):
            ttk.Button(quick_frame, text=text, 
                      command=lambda c=cmd, p=param: self.set_command(c, p))\
                      .grid(row=0, column=i, padx=2)
        
        # 输出区域
        output_frame = ttk.LabelFrame(main_frame, text="输出结果", padding="5")
        output_frame.grid(row=2, column=0, columnspan=3, sticky=tk.N+tk.S+tk.W+tk.E, pady=5)
        main_frame.rowconfigure(2, weight=1)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        # 输出文本框
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, 
                                                   font=("Consolas", 10))
        self.output_text.grid(row=0, column=0, sticky=tk.N+tk.S+tk.W+tk.E)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, columnspan=3, sticky=tk.W+tk.E, pady=5)
    
    def setup_bindings(self):
        """设置事件绑定"""
        self.root.bind('<Return>', lambda e: self.execute_command())
        self.root.bind('<F1>', lambda e: self.show_help())
        self.command_combo.bind('<<ComboboxSelected>>', self.on_command_change)
    
    def set_command(self, command, params=""):
        """设置命令和参数"""
        self.command_var.set(command)
        self.param_var.set(params)
        self.param_entry.focus()
    
    def on_command_change(self, event):
        """当命令改变时的回调"""
        command = self.command_var.get()
        defaults = {
            "ping": "100.64.0.1",
            "ssh": "username@hostname",
            "funnel": "on 8080"
        }
        if command in defaults:
            self.param_var.set(defaults[command])
    
    def show_welcome_message(self):
        """显示欢迎信息"""
        welcome_msg = """Tailscale GUI 工具 - 无控制台版本

此版本已修复CMD黑窗口弹出问题。

常用操作:
• 选择命令并点击"执行命令"或按回车键
• 使用上方快捷按钮快速执行常用命令
• 在参数框中输入命令参数

示例命令:
• 查看网络状态: status
• 连接到Tailscale: up --accept-routes  
• 检查网络连接: netcheck
• Ping测试: ping 100.64.0.1
• 查看IP地址: ip

提示: 按 F1 查看详细帮助
"""
        self.output_text.insert(tk.END, welcome_msg + "="*60 + "\n")
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
Tailscale 命令帮助:

status    - 显示当前连接状态
up        - 启动并连接Tailscale
down      - 断开Tailscale连接  
login     - 登录Tailscale账户
logout    - 登出当前账户
netcheck  - 检查网络连接状态
ping      - 测试到其他节点的连接
version   - 显示Tailscale版本
ip        - 显示Tailscale IP地址
web       - 打开Web管理界面
ssh       - SSH连接到其他节点
funnel    - 管理Funnel服务

更多信息请参考: https://tailscale.com/kb/
"""
        messagebox.showinfo("Tailscale 命令帮助", help_text)
    
    def execute_command(self):
        """执行Tailscale命令 - 无控制台窗口版本"""
        def run_command():
            self.run_button.config(state="disabled")
            self.status_var.set("执行中...")
            
            command = self.command_var.get().strip()
            params = self.param_var.get().strip()
            
            # 构建命令
            cmd_list = ["tailscale", command]
            if params:
                cmd_list.extend(params.split())
            
            try:
                # 显示执行的命令
                self.output_text.insert(tk.END, f"$ {' '.join(cmd_list)}\n")
                self.output_text.see(tk.END)
                self.root.update()
                
                # 关键修复：使用 startupinfo 隐藏控制台窗口
                if sys.platform == "win32":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = 0  # SW_HIDE
                else:
                    startupinfo = None
                
                # 执行命令，隐藏控制台窗口
                result = subprocess.run(
                    cmd_list, 
                    capture_output=True, 
                    text=True, 
                    timeout=60,
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW  # 关键：不创建控制台窗口
                )
                
                # 显示结果
                self.output_text.insert(tk.END, "="*50 + "\n")
                
                if result.returncode == 0:
                    if result.stdout:
                        self.output_text.insert(tk.END, "输出:\n")
                        self.output_text.insert(tk.END, result.stdout)
                    if result.stderr:
                        self.output_text.insert(tk.END, "\n警告信息:\n")
                        self.output_text.insert(tk.END, result.stderr)
                else:
                    self.output_text.insert(tk.END, "错误信息:\n")
                    self.output_text.insert(tk.END, result.stderr)
                    if result.stdout:
                        self.output_text.insert(tk.END, "\n标准输出:\n")
                        self.output_text.insert(tk.END, result.stdout)
                
                self.output_text.insert(tk.END, "\n" + "="*50 + "\n")
                self.status_var.set(f"命令执行完成 (退出码: {result.returncode})")
                
            except FileNotFoundError:
                error_msg = "错误: 未找到 tailscale 命令。请确保 Tailscale 已安装并在系统 PATH 中。"
                self.output_text.insert(tk.END, error_msg + "\n")
                self.status_var.set("错误: Tailscale 未找到")
                messagebox.showerror("错误", error_msg)
            except subprocess.TimeoutExpired:
                error_msg = "错误: 命令执行超时（超过60秒）"
                self.output_text.insert(tk.END, error_msg + "\n")
                self.status_var.set("错误: 执行超时")
            except Exception as e:
                error_msg = f"异常错误: {str(e)}"
                self.output_text.insert(tk.END, error_msg + "\n")
                self.status_var.set("错误: 发生异常")
                messagebox.showerror("异常", error_msg)
            finally:
                self.run_button.config(state="normal")
                self.output_text.see(tk.END)
        
        # 在新线程中执行命令
        thread = threading.Thread(target=run_command)
        thread.daemon = True
        thread.start()

def main():
    """主函数"""
    # 检查Tailscale是否可用
    try:
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0
            subprocess.run(["tailscale", "version"], capture_output=True, timeout=5, 
                         startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            subprocess.run(["tailscale", "version"], capture_output=True, timeout=5)
    except FileNotFoundError:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Tailscale 未找到", 
            "未检测到 Tailscale 安装。请先安装 Tailscale：\n\n"
            "1. 访问 https://tailscale.com/download 下载安装\n"
            "2. 确保 tailscale 命令在系统 PATH 中\n"
            "3. 重新启动本程序"
        )
        root.destroy()
        return
    except Exception as e:
        print(f"检查Tailscale时出错: {e}")
    
    # 创建主界面
    root = tk.Tk()
    app = TailscaleGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
