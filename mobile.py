# coding: utf-8
import time
import tkinter
from tkinter import ttk
import sv_ttk
from loger import HandleLog
import tkinter.messagebox as msgbox
import base
import os


logo_path = os.path.join(os.path.dirname(__file__), 'icon.png')
db_name = "loader_temp_" + time.strftime("%Y%m%d", time.localtime())
default_formats = {
    # 终端输出格式
    'color_format': '%(log_color)s%(asctime)s-%(name)s-%(filename)s-[line:%(lineno)d]-%(levelname)s-[日志信息]: %(message)s',
    # 日志输出格式
    'log_format': '%(asctime)s-%(name)s-%(filename)s-[line:%(lineno)d]-%(levelname)s-[日志信息]: %(message)s'
}
log = HandleLog()
log.formats = default_formats

class Mobile:
    def __init__(self) -> None:
        self.root = tkinter.Tk()
        self.db_status = tkinter.StringVar()
       
        sv_ttk.use_light_theme()
        self.root.title("喂料机配方状态-移动端")
        self.root.iconphoto(True, tkinter.PhotoImage(file=logo_path))
        self.root.geometry("600x1024")
        self.root.protocol("WM_DELETE_WINDOW", self.closewin)
        self.nr_ball_option_var = tkinter.StringVar()
        self.interface()
        self.db = base.loader_db(user="sijiyihao", passwd="anquandiyi")
        if self.db.connect():
            self.db_status.set("数据库连接成功")
            if self.data_update() == -1:
                msgbox.showerror("错误", "暂无今日数据，请联系配方员添加任务单！")
                self.root.destroy()
                self.db.cleanup()
                exit()
            log.info("数据库连接成功")
        else:
            log.error("数据库连接失败")
            msgbox.showerror("错误", "数据库连接失败，请联系管理员！")
            self.root.quit()
        self.mat= self.db.update_material()
        ttk.Style().configure("TButton", font=("YouYuan", 40))
        self.root.mainloop()    
    
    def closewin(self):
        if msgbox.askokcancel("退出", "是否退出程序?"):
            self.root.destroy()
            self.db.cleanup()
            log.info("退出程序")


    def interface(self):
        self.data_frame = tkinter.Frame(self.root)
        self.data_frame.pack(expand=1,fill='both')
        self.treev()
        self.nr_ball_select_func()
        self.ctl_frame = tkinter.Frame(self.root, height = 100)
        self.ctl_frame.pack(side="bottom",expand = 0, fill="both")
        q = ttk.Button(self.ctl_frame, text="退出",command=self.closewin)
        q.pack(side="bottom", fill="both",expand = 1, ipady=30)

    def nr_ball_select_func(self):
        self.nr_select = tkinter.Frame(self.data_frame)
        self.nr_select.pack(side="top", fill="both", anchor="nw")
        ttk.Label(self.nr_select, text="请选择球磨机号：", font=("YouYuan", 40)).pack(side="top", fill="both", ipady=30,padx=30)
        option = ['01号球磨机', '02号球磨机', '03号球磨机', '04号球磨机', '05号球磨机', '06号球磨机', '07号球磨机', '08号球磨机', '09号球磨机', '10号球磨机', '11号球磨机', '12号球磨机', '13号球磨机', '14号球磨机', '15号球磨机', '16号球磨机', '17号球磨机', '18号球磨机', '19号球磨机','20号球磨机']
        tmp = tkinter.OptionMenu(self.nr_select, self.nr_ball_option_var, *option, command=self.nr_ball_comf_func )
        tmp.config(width=20, height=1, font=("YouYuan", 40))
        tmp['menu'].config(font=("YouYuan", 20))
        tmp.pack(side="top", fill="both", ipady=30,padx=30)


    def nr_ball_comf_func(self,data):
        if msgbox.askyesno("确认", "是否确认选择{}？".format(data)):
            self.nr_ball_nr = data[0:2]
            self.nr_select.pack_forget()
            self.display.pack(side="left", fill="y", anchor="sw")
        else:
            self.mr_ball_option_var.set("")

    def treev(self):
        ttk.Label(self.data_frame, textvariable=self.db_status).pack(
            padx=(10, 0), pady=(10, 0), side="top", anchor="nw")
        self.display = tkinter.Frame(self.data_frame)
        self.ybar = tkinter.Scrollbar(
            self.display, orient='vertical', width=60)
        self.tv = ttk.Treeview(self.display, columns=('id', 'name', 'status'),
                               show='headings', height=1,  selectmode='browse', yscrollcommand=self.ybar.set)
        ttk.Style().configure("Treeview", font=("YouYuan", 20), rowheight=50)
        self.tv.heading('id', text='ID')
        self.tv.column('id', width=80,anchor='center')
        self.tv.heading('name', text='名称')
        self.tv.column('name', width=260,anchor='center')
        self.tv.heading('status', text='状态')
        self.tv.column('status',  width=200,anchor='center')
        # 修改treeview标题的字体
        ttk.Label(self.display, text="双击选择配方，右侧为滚动条",font=("YouYuan",20)).pack(side="top", fill="x")
        self.tv.pack(side="left", fill="y")
        self.tv.bind("<Double-1>", self.on_tree_select)
        self.ybar.config(command=self.tv.yview)
        self.ybar.pack(side="right", fill="y")

    def on_tree_select(self, event):
        if self.tv.focus() == "":
            return
        item = self.tv.focus()
        print(item)
        index = int(item)
        print(self.data[index])
        sql = "UPDATE `{}` SET `status`='作业中',`nr_ball`={} WHERE `id`={};".format(db_name,self.nr_ball_nr, self.data[index]['id'])
        print(sql)
        #self.db.query(sql)
        self.display.pack_forget()
        self.working_frame = tkinter.Frame(self.data_frame)
        self.working_frame.pack(side="left", fill="y", anchor="sw")
        self.working_frame.pack_propagate(0)
        
        pass

    def rev_data_format(self, data):
        id = data['id']
        name = data['name']
        status = data['status']
        rest_weight = 0
        for i in range(0, 30):
            if data['m_'+str(i)] == None:
                break
            tmp = data['m_'+str(i)].split(';')
            rest_weight += int(tmp[2])
        ret = (id, name, status)
        return ret

    def data_update(self):
        try:
            self.data = self.db.query("SELECT * FROM `{}`;".format(db_name))
        except:
            self.db_status.set("数据库连接失败")
            return -1
        for i,n in enumerate(self.data):
            self.tv.insert('', 'end', id=i, values=self.rev_data_format(n))
        if len(self.tv.get_children()) > 30:
            self.ybar.pack(side="right", fill="y")
        log.info("数据更新时间:"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))


if __name__ == "__main__":
    Mobile()
