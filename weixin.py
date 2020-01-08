#!/usr/bin/env python
# coding=utf-8
import os
import glob
import time
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, filedialog
import re
import shutil
import configparser
import sys

replace_count = 0

cf = configparser.ConfigParser()
cf.read("peizhi.ini",encoding="utf-8")
secs = cf.sections()
options = cf.options("XINBA")
items = cf.items("XINBA")
baseDir = cf.get("XINBA", "baseDir").strip()
erweimaDirname = cf.get("XINBA", "erweimaDirName").strip()
erweimaFileName = cf.get("XINBA", "erweimaFileName").strip()


def copytree(src, baseDir, targetDir):
    if src.strip() == '' or (src.find('二维码')<0 and src.find('qrcode')<0 and src.find('erweima')<0):
        messagebox.showinfo("辛巴温馨提示:", "请选择含有二维码或qrcode或erweima的文件夹")
        os._exit()
    resultDirs = []
    resultDirs = findQrcodeDirs(
        baseDir, targetDir)
    for singleDir in resultDirs:
        copySingletree(src, singleDir)
    messagebox.showinfo("辛巴温馨提示:", "完成了转移!!!")


def findQrcodeDirs(dirname, targetDir):
    resultDir = []  # 所有的文件
    for maindir, subdir, file_name_list in os.walk(dirname):
        for sub in subdir:
            targetDirList = targetDir.split(",")
            for singleTarget in targetDirList:
                if sub == singleTarget.strip():
                    resultDir.append(os.path.join(maindir, sub))
    return resultDir


def copySingletree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def all_path(dirname, erweimaFileName):
    result = []  # 所有的文件
    for maindir, subdir, file_name_list in os.walk(dirname):
        for filename in file_name_list:
            apath = os.path.join(maindir, filename)  # 合并成一个完整路径
            erweimaList = erweimaFileName.split(",")
            for erweima in erweimaList:
                if filename == erweima.strip():
                    result.append(apath)
    return result


def repip_func(file_path, wx_no):
    wx_no = wx_no.strip()
    file = open(file_path, 'r+', encoding='UTF-8')
    all_the_lines = file.read()
    init_length = len(all_the_lines)
    file.seek(0)
    current_length = len(all_the_lines)

    f_regex = '[\s]*[\'|\"]'+wx_no+'[\'|\"][\s]*,'
    s_regex = ',[\s]*[\'|\"]'+wx_no+'[\'|\"]?'
    t_regex = '[[][\s]*[\'|\"]' + wx_no + '[\'|\"][\s]*[]]'

    t_trim_regex = '[\s]*[\'|\"]' + wx_no + '[\'|\"][\s]*'

    f_com = re.compile(f_regex)
    s_com = re.compile(s_regex)
    t_com = re.compile(t_regex)
    if(f_com.search(all_the_lines)):
        file.truncate()
        all_the_lines = re.sub(f_regex, '', all_the_lines, flags=re.IGNORECASE)
        file.write(all_the_lines)
        file.close()
    elif(s_com.search(all_the_lines)):
        file.truncate()
        all_the_lines = re.sub(s_regex, '', all_the_lines, flags=re.IGNORECASE)
        file.write(all_the_lines)
        file.close()
    elif(t_com.search(all_the_lines)):
        file.truncate()
        all_the_lines = re.sub(
            t_trim_regex, '', all_the_lines, flags=re.IGNORECASE)
        file.write(all_the_lines)
        file.close()

    global replace_count
    if(len(all_the_lines) < init_length):
        global replace_count
        replace_count = replace_count+1
    file.close()


filePaths = ""


def askopenfilename():
    global filePaths
    filePaths = filedialog.askdirectory()
    btn_selectfile["text"] = filePaths[-15:]
    print(filePaths)


def deleteWxno(baseDir, erweimaFile):
    if wxno.get().strip() == '' or len(wxno.get())<5:
        messagebox.showinfo("辛巴温馨提示:", "请输入有效的微信号!")
        os._exit()
    global replace_count
    replace_count = 0
    found_files = all_path(baseDir, erweimaFile)
    if len(found_files) == 0:
        messagebox.showinfo("辛巴温馨提示:", "对不起, 找不到文件。")
        os._exit()
    for single_file in found_files:
        repip_func(single_file, wxno.get())
    messagebox.showinfo("辛巴温馨提示:", "贵宝宝成功删除了"+str(replace_count)+"地方")

def rcpath(rel_path):
    return os.path.join(os.getcwd(), rel_path)

window = tk.Tk()
window.title('辛巴工具箱')

x = (window.winfo_screenwidth() - window.winfo_reqwidth()) / 2
y = (window.winfo_screenheight() - window.winfo_reqheight()) / 2
window.geometry("%dx%d+%d+%d" % (400, 180, x, y))

wxno = tk.StringVar()
tk.Label(window, text='要删除的微信号:').place(x=50, y=20)
tk.Entry(window, textvariable=wxno).place(x=150, y=20)

bt_confirm_sign_up = tk.Button(window, text='确认删除',
                               command=lambda: deleteWxno(baseDir, erweimaFileName))
bt_confirm_sign_up.place(x=310, y=15)

var_dir_name = tk.StringVar()
var_dir_type = tk.StringVar()

btn_selectfile = tk.Button(
    window, text="...选择要拷贝的文件夹", command=askopenfilename)
btn_selectfile.place(x=150, y=60)
tk.Label(window, text='选择文件目录:').place(x=50, y=65)

btn_submit = tk.Button(window, text="开始导入", command=lambda: copytree(
    filePaths, baseDir, erweimaDirname))
btn_submit.place(x=300, y=60)
window.mainloop()
