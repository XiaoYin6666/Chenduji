from ttkbootstrap.dialogs import Messagebox
from datetime import datetime as date
from ttkbootstrap.constants import *
from loger import log as logprint
import ttkbootstrap as ttk
import threading
import winreg
import random
import ctypes
import shutil
import json
import os


Name='晨读记'
Version='1.0'
themes=['darkly','solar','cerculean','cosmo']
theme=themes[2]
path=os.getcwd()
poems=open(f'{path}\\Resources\\poems.p',encoding='utf8').readlines()
author=r"""
 ________      ___    ___         ___    ___ ___  ________  ________           ___    ___ ___  ________      
|\   __  \    |\  \  /  /|       |\  \  /  /|\  \|\   __  \|\   __  \         |\  \  /  /|\  \|\   ___  \    
\ \  \|\ /_   \ \  \/  / /       \ \  \/  / | \  \ \  \|\  \ \  \|\  \        \ \  \/  / | \  \ \  \\ \  \   
 \ \   __  \   \ \    / /         \ \    / / \ \  \ \   __  \ \  \\\  \        \ \    / / \ \  \ \  \\ \  \  
  \ \  \|\  \   \/  /  /           /     \/   \ \  \ \  \ \  \ \  \\\  \        \/  /  /   \ \  \ \  \\ \  \ 
   \ \_______\__/  / /            /  /\   \    \ \__\ \__\ \__\ \_______\     __/  / /      \ \__\ \__\\ \__\
    \|_______|\___/ /            /__/ /\ __\    \|__|\|__|\|__|\|_______|    |\___/ /        \|__|\|__| \|__|
             \|___|/             |__|/ \|__|                                 \|___|/                         
"""
print(author)


def is_font_installed(font_name):
    """检查字体是否已安装"""
    reg_path = r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts'
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
            i = 0
            while True:
                try:
                    value_name, value_data, _ = winreg.EnumValue(key, i)
                    if font_name.lower() in value_name.lower():
                        return True
                    i += 1
                except OSError:
                    break
    except FileNotFoundError:
        pass
    return False



def install_font():
    font_path=fr'{path}\Resources\font\380-上首呆鹅体.ttf'
    font_name = os.path.basename(font_path)

    if is_font_installed(font_name):
        logprint(f"字体 {font_name} 已安装")
        return
    
    # 复制字体文件到系统字体目录
    shutil.copy(font_path, os.path.join(os.path.join(os.environ['SystemRoot'], 'Fonts'), font_name))

    # 更新注册表
    reg_path = r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts'
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, font_name, 0, winreg.REG_SZ, font_name)
        logprint(f"字体 {font_name} 安装成功")
    except Exception as e:
        logprint(f"安装字体出错: {e},请手动安装")
        main_window.destroy()



def update_datetime():
    #获取日期并更新
    date_now=str(date.now().date())[2:]
    date_label.config(text=date_now)

    #获取时间并更新
    time_now=str(date.now().time())[:-7]
    time_label.config(text=time_now)

    #循环更新 2Hz
    main_window.after(500,update_datetime)


def win_rec_on_closeing():
    result = Messagebox.show_question("确认关闭窗口？", "提示", parent=window_rec,buttons=['确定','取消'])
    if result == "确定":
        #保存log_dic到文件rec_logfile中
        json.dump(log_dic,rec_logfile,indent=4)
        rec_logfile.close()
        logprint('Saved as:'+str(rec_logfile.name))
        logprint('log_dic:'+str([f"{class_}:{score}" for class_, score in log_dic['log_score'].items()]))
        #销毁窗口，重现主窗口
        window_rec.destroy()
        main_window.deiconify()
        main_window.place_window_center()



def class_bt_press(class_, label):
    def entry_on_Focus():
        if entry.get() == "请输入分数 1-10":
            entry.delete(0, "end")
    def entry_out_Focus():
        if entry.get() == "":
            entry.insert(0,'请输入分数 1-10')


    def button_entry_pressing():
        try:
            entry_str=int(entry.get())
            if entry_str==None or entry_str=='':
                win_entry.destroy()

            elif entry_str>=0 and entry_str<=10:
                logprint(f'{class_}score:{entry_str}')
                log_dic['log_score'][class_]=entry_str
                label.config(text=f'得分{entry_str}')
                win_entry.destroy()

            else:
                Messagebox.show_error('请输入1-10的整数','错误',parent=win_entry)
                win_entry.destroy()
        except:
            Messagebox.show_error('请输入1-10的整数','错误',parent=win_entry)
            win_entry.destroy()


    win_entry=ttk.Toplevel(title='评分',
                           resizable=(False,False)
                           )
    entry=ttk.Entry(win_entry)
    entry.insert(0,'请输入分数 1-10')
    entry.bind("<Return>", lambda event:button_entry_pressing())
    entry.bind("<FocusOut>",lambda event:entry_out_Focus())
    entry.bind("<FocusIn>", lambda event:entry_on_Focus())
    button_entry=ttk.Button(win_entry,command=lambda:button_entry_pressing(),text='确定',style='font851class_bt.TButton')

    win_entry.place_window_center()
    entry.pack(side=LEFT,padx=10,pady=10)
    button_entry.pack(side=RIGHT,padx=10,pady=10)



def Win_Rec():
    global window_rec
    global log_dic,rec_logfile

    main_window.withdraw()
    now=date.now()
    str_now=f'{now.date()} {str(now.time()).replace(':','-')}'
    rec_logfile=open(fr'{path}\Resources\data\record\{str_now}.json',mode='w+',encoding='utf8')#创建logfile
    classes = [class_bt.strip() for class_bt in open(fr'{path}\Resources\classes.txt', encoding='utf8').readlines() if class_bt.strip()]  # 读取班级并去除换行符
    log_dic={}
    log_dic['time']=str(now)#记录时间
    log_dic['timestamp']=str(now.timestamp())#记录时间戳
    log_dic['classes']=classes#记录班级
    log_dic['log_score']={}#记录日志


    #创建子窗口-开始记录
    window_rec=ttk.Toplevel(title=f'{Name} V{Version}',
                            resizable=(False,False)
                            )
    if len(classes)==0:
        logprint('未设置班级')
        Messagebox.show_error('未设置班级','错误',parent=window_rec)
        window_rec.destroy()

    window_rec.iconbitmap(fr'{path}\Resources\main64.ico')
    window_rec.iconphoto(True,ttk.PhotoImage(file=fr'{path}\Resources\mainico.png'))

    frame_classes=ttk.LabelFrame(window_rec,text='班级',bootstyle=ttk.constants.PRIMARY)#班级按钮frame
    frame_buttons=ttk.LabelFrame(window_rec,text='操作',bootstyle=ttk.constants.PRIMARY)#按钮frame

    logprint(classes)
    #创建班级按钮
    ttk.Style().configure('font851class_bt.TButton',font=('380-上首呆鹅体',20))
    for i, class_bt in enumerate(classes):
        log_dic['log_score'][class_bt]=0#初始化班级评分字典
        label = ttk.Label(frame_classes, text=f'得分0', font=('380-上首呆鹅体', 12))#得分label
        label.grid(row=i // 5 * 2, column=i % 5, padx=10)
        ttk.Button(frame_classes,text=class_bt,command=lambda class_bt=class_bt, label=label: class_bt_press(class_bt, label),style='font851class_bt.TButton').grid(row=i // 5 * 2 + 1, column=i % 5, padx=10, pady=5)

    ttk.Button(frame_buttons,text='完成',command=win_rec_on_closeing,style='font851class_bt.TButton').pack(padx=10,pady=10)


    frame_classes.pack(side=LEFT,padx=10,pady=10)
    frame_buttons.pack(side=RIGHT,padx=10,pady=10,fill=BOTH)

    
    window_rec.protocol("WM_DELETE_WINDOW", win_rec_on_closeing)#监听关闭事件
    window_rec.place_window_center()
    window_rec.mainloop()



def Win_his():
    global window_his
    log_dic_list=[]
    
    #创建子窗口-查看历史
    window_his=ttk.Toplevel(title=f'{Name} V{Version}',
                            resizable=(True,True)
                            )
    window_his.maxsize(1100,600)


    #读取record文件夹下的json文件
    json_logfiles = [f for f in os.listdir(fr'{path}\Resources\data\record') if f.endswith('.json')]
    for json_logfile in json_logfiles:
        dic_logfile=json.loads(open(fr'{path}\Resources\data\record\{json_logfile}',encoding='utf8',mode='r').read())
        log_dic_list.append(dic_logfile)

    if len(log_dic_list)==0:
        logprint('NO history',0)
        window_his.destroy()
        Messagebox.show_error('没有历史记录','错误',parent=main_window)
        return


    #创建树视图，展示历史记录用
    ttk.Style().configure("Treeview", background="white", foreground="black", fieldbackground="blue",rowheight=20*len(log_dic_list[0]['classes']))
    TreeView=ttk.Treeview(window_his,columns=('id','time','classes'),show='headings',style='Treeview')


    TreeView.heading('id',text='ID',anchor=NW)
    TreeView.heading('time',text='时间',anchor=NW)
    TreeView.heading('classes',text='班级得分',anchor=NW)

    TreeView.column('id',width=60,anchor=NW)
    TreeView.column('time',anchor=NW)
    TreeView.column('classes',anchor=NW)

    #插入数据
    for i,log in enumerate(log_dic_list):
        TreeView.insert('','end',
                        values=(i+1,
                                log['time'],
                                '\n'.join([f"{class_}:{score}" for class_, score in log['log_score'].items()])
                                )
                        )


    window_his.iconbitmap(fr'{path}\Resources\main64.ico')
    window_his.iconphoto(True,ttk.PhotoImage(file=fr'{path}\Resources\mainico.png'))



    TreeView.pack(side=LEFT,padx=10,pady=10,fill=BOTH,expand=True)
    window_his.place_window_center()



#创建线程函数，供按钮调用
def Creat_win_rec():
    threading.Thread(name='win_rec',target=Win_Rec).run()
def Creat_win_his():
    threading.Thread(name='win_his',target=Win_his).run()



def Win_main():
    global date_label
    global time_label
    global main_window
    global Scale_Factor_W,Scale_Factor_H



    #主窗口
    main_window= ttk.Window(title=f'{Name} V{Version}',
                            themename=theme,
                            resizable=(False,False)
                            )

    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('main_window')#创建进程ID
    main_window.iconbitmap(fr'{path}\Resources\main64.ico')
    main_window.iconphoto(True,ttk.PhotoImage(file=fr'{path}\Resources\mainico.png'))


    #获取屏幕大小，计算缩放系数
    screen_width=main_window.winfo_screenwidth()
    screen_height=main_window.winfo_screenheight()
    Scale_Factor_W=int(screen_width/1920)
    Scale_Factor_H=int(screen_height/1080)
    logprint(f'W-H:{screen_width}x{screen_height}')
    logprint(f'ScaleFactor:W{Scale_Factor_W} H{Scale_Factor_H}')


    lb_datetime=ttk.Labelframe(main_window,text='时间',bootstyle=ttk.constants.PRIMARY)
    lb_button=ttk.Labelframe(main_window,text='操作',bootstyle=ttk.constants.PRIMARY)

    #日期标签
    date_label=ttk.Label(lb_datetime,font=("380-上首呆鹅体",35),bootstyle=ttk.constants.PRIMARY)
    date_label.pack(side=TOP,padx=10,pady=9)

    #时间标签
    time_label=ttk.Label(lb_datetime,font=('380-上首呆鹅体',35),bootstyle=ttk.constants.PRIMARY)
    time_label.pack(side=TOP,padx=10,pady=10)

    #励志语句标签
    ttk.Label(text=random.choice(poems).strip(),font=('微软雅黑',17)).pack(side=BOTTOM,pady=10)

    #开始记录按钮
    ttk.Style().configure('font851.TButton',font=('380-上首呆鹅体',27))
    button_record=ttk.Button(lb_button,text='开始新记录',style='font851.TButton',command=lambda:threading.Thread(name='win_rec',target=Win_Rec).run()).pack(side=TOP,padx=10,pady=10)

    #查看历史按钮
    button_history=ttk.Button(lb_button,text='查看历史',style='font851.TButton',command=lambda:threading.Thread(name='win_his',target=Win_his).run()).pack(side=TOP,padx=10,pady=10,fill=X)


    lb_datetime.pack(side=LEFT,padx=10,pady=10,fill=BOTH)
    lb_button.pack(side=LEFT,padx=10,pady=10,fill=BOTH)


    main_window.place_window_center()
    update_datetime()
    main_window.mainloop()


if __name__=='__main__':
    install_font()
    Win_main()