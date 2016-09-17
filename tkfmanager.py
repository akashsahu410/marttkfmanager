# MartTKfManager - Martin's File Manager (TK version)
version = "ALPHA v0.1.2"
cur_year = "2016"

from tkinter import *
from tkinter.ttk import *
from PIL import ImageTk, Image
import sys, os, time, pwd, grp, subprocess, re

pos = 0
home = os.path.expanduser("~") # home directory
history = [os.getcwd()]
show_hidden_files = False
access_info = ''

# Dependencies (Based on Debian package names,
# these may differ in other distros)

# python3
# tkinter            <-- For GUI
# python-gstreamer   <-- For video
# python-gobject     <-- playing
# python-pil         <-- For images

def conf_read():
    try:
        cf_file = open(home+'/.marttkfmanagerrc', 'r')
        cf_file = cf_file.readlines()
    except:                             # if the marttkfmanagerrc file is missing
        cf_file = ['[TAG]\n', 'images:feh\n', 'videos:mpv\n', 'text:st -e vim\n', '[/TAG]\n', '\n', '[EXTENTION]\n', '*:text:Unknown File Type\n', 'rc:text:Configuration File\n', 'jpg:images:Joint Photographic Experts Group\n', 'jpeg:images:Joint Photographic Experts Group\n', 'png:images:Portable Network Graphic\n', 'mkv:videos:Matroska Multimedia Container\n', 'mp4:videos:MPEG-4\n', 'txt:text:Text File\n', 'c:text:C Source Code\n', 'py:text:Python Source Code\n', 'html:text:HTML File\n', 'htm:text:HTML File\n', 'php:text:PHP File\n', 'sh:text:Shell Script\n', '[/EXTENTION]\n', '\n', '\n']
    for itr in range(0, len(cf_file)):
        cf_file[itr] = cf_file[itr][:-1]
    cf_file.append('EXIT')
    return cf_file

def human_readable_size(new_size):
    for unit in ['Bytes', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB']:
        if new_size < 1024:
            return str("%.2f" % new_size)+'\xa0'+unit
        new_size /= 1024
    return str("%.2f" % new_size)+'\xa0YiB'

def sort_file(fetch):                   # fetch == 'TAG': Returns the tags_conf | fetch == 'EXT': Returns the ext_conf | fetch == 'EXT_NAME': Returns the ext_conf_n
    conf_file = conf_read()
    tags_conf, ext_conf, ext_conf_n = {}, {}, {}
    tag_in = 'NONE'
    for itr in range(0, len(conf_file)):
        if conf_file[itr] == '[TAG]':
            tag_in = 'TAG'
        elif conf_file[itr] == '[/TAG]' or conf_file[itr] == '[/EXTENTION]':
            tag_in = 'NONE'
        elif conf_file[itr] == '[EXTENTION]':
            tag_in = 'EXT'
        elif conf_file[itr] == 'EXIT':
            break
        else:
            str_part = conf_file[itr].split(':')
            if tag_in == 'TAG':
                tags_conf[str_part[0]] = str_part[1]
            elif tag_in == 'EXT':
                ext_conf[str_part[0]] = str_part[1] 
                ext_conf_n[str_part[0]] = str_part[2]
    if fetch == 'TAG':
        return tags_conf
    elif fetch == 'EXT':
        return ext_conf
    elif fetch == 'EXT_NAME':
        return ext_conf_n

def dir_change_action(main, to_dir, pos_ch):
    global dir_info_01, dir_info_02, tree, pos, history, access_info
    pos += pos_ch
    if to_dir == history and ((pos != 0 and pos_ch == -1) or (pos != (len(history) -1) and pos_ch == 1)):
        try:
            os.chdir(history[pos])
        except:
            pass
    elif to_dir != 0: 
        history.append(os.getcwd())
        try:
            os.chdir(to_dir)
            access_info=''
        except:
            if os.path.isdir(to_dir) == True:
                access_info='     Access Denied'
            else:
                access_info='     Directory don\'t exist'
    main.title("MartTKfManager - "+os.getcwd())
    dir_info_01.destroy()
    dir_info_02.destroy()
    tree.destroy()
    main_list_dir(main)

def about():
    about_win = Tk()
    about_win.title("MartTKfManager - About")
    width, height = 400, 100
    about_win.resizable(width=False, height=False)
    about_win.geometry("%dx%d+%d+%d" % (width, height, 0, 0))
    about_text = Label(about_win, text="MartTKfManager (Martin's File Manager (TK version))\nVersion: "+version+"\nCopyright (c) "+cur_year)
    about_text.pack()
    about_exit = Button(about_win, text="Close", command=about_win.destroy)
    about_exit.pack()
    about_win.configure(background="#222")
    about_win.mainloop()

def main_buttons(main):
    def bck_dir():
        dir_change_action(main, history, -1)
    def frw_dir():
        dir_change_action(main, history, 1)
    def home_dir():
        global home
        dir_change_action(main, home, 1)

    button_bck = Button(main, text="<-", command=bck_dir)
    button_bck.grid(row=0, column=0)
    button_frw = Button(main, text="->", command=frw_dir)
    button_frw.grid(row=0, column=1)
    button_home = Button(main, text="~", command=home_dir)
    button_home.grid(row=0, column=2)
    button_home = Button(main, text="About", command=about)
    button_home.grid(row=0, column=3)
    button_quit = Button(main, text="Exit", command=sys.exit)
    button_quit.grid(row=0, column=4)

def main_list_dir(main):
    global history, dir_info_01, dir_info_02, show_hidden_files, tree, id_pos, access_info
    def goto_path(a):
        dir_change_action(main, cur_dir_entry.get(), 1)

    def dir_change(a):
        curItem = tree.item(tree.focus())['text']
        dir_change_action(main, curItem, 1)

    def ext_prog(a): # EXT_RUN
        file_focus = tree.item(tree.focus())['text']
        if file_focus[-2:] == 'rc':
            file_ext = 'rc' 
        elif '.' not in file_focus[1:]:
            file_ext = '*'
        else:
            file_ext = file_focus.split('.')
            file_ext = file_ext[len(file_ext)-1]
        tags_conf = sort_file('TAG')
        ext_conf = sort_file('EXT')
        try:
            ext_bind = tags_conf[ext_conf[file_ext]].split(' ')
        except:
            ext_bind = tags_conf[ext_conf['*']].split(' ')
        ext_bind.append(os.getcwd()+'/'+file_focus)
        subprocess.Popen(ext_bind)                      # Popen: files open in another process (preferred) | call: files open within this process
        dir_change_action(main, 0, 0)

    def up_dir(a):
        dir_change_action(main, '..', 1)

    def toggle_hidden(a):
        global show_hidden_files
        show_hidden_files = not show_hidden_files
        dir_change_action(main, 0, 0)

    def bind_cur_dir_entry(a):
        cur_dir_entry.focus_set()

    def refresh_dir(a):
        dir_change_action(main, 0, 0)

    def row_change(a, pos_change, id_list):
        global id_pos
        tree.focus_set()
        id_pos += pos_change
        if id_pos < 0 or pos_change == 0:
            id_pos = 0
        elif id_pos > len(id_list) - 1 or pos_change == 2:
            id_pos = len(id_list) - 1
        tree.focus(id_list[id_pos])

    cur_dir_entry = Entry(main, width=100)
    cur_dir_entry.grid(row=1, column=0, columnspan=10)
    cur_dir_entry.delete(0, 'end') 
    cur_dir_entry.insert(0, os.getcwd())
    cur_dir_entry.bind('<Return>', goto_path)
    cde_button = Button(main, text="Go", width=10, command=lambda:goto_path(0))
    cde_button.grid(row=1, column=11)

    row_place, col_place = 2, 0
    dir_ls = os.listdir(os.getcwd())
    dir_ls.sort()

    scrollbar = Scrollbar(main, orient=VERTICAL)
    scrollbar.grid(row=2, column=20, rowspan=15, sticky=N+S)

    tree = Treeview(main, height=19, columns=('size', 'last_mod', 'uid_gid', 'ext'), yscrollcommand=scrollbar.set)
    tree.grid(row=2, column=0, columnspan=20)
    tree.column('#0', width=300, anchor='w')
    tree.heading('#0', text='Filename')
    tree.column('size', width=120, anchor='w')
    tree.heading('size', text='Size')
    tree.column('last_mod', width=200, anchor='w')
    tree.heading('last_mod', text='Last Modified')
    tree.column('uid_gid', width=140, anchor='w')
    tree.heading('uid_gid', text='Owner/Group')
    tree.column('ext', width=140, anchor='w')
    tree.heading('ext', text='File type')
    total_dir, total_file, id_pos = 0, 0, 0
    id_list = []
    up_id = tree.insert('', 'end', text='..', tag=('up'), values=('UP\xa0DIRECTORY '))
    id_list.append(up_id)
    tree.focus_set()
    tree.focus(id_list[id_pos])
    for itr in range(0, len(dir_ls)):
        if (show_hidden_files == False and dir_ls[itr][0] != '.') or (show_hidden_files == True):
            las_mod_time = str(time.ctime(os.stat(dir_ls[itr]).st_mtime))
            las_mod_time = re.sub(r"\s+", '\xa0', las_mod_time)
            try:
                uid_gid_get = str(pwd.getpwuid(os.stat(dir_ls[itr]).st_uid)[0]+'/'+grp.getgrgid(os.stat(dir_ls[itr]).st_gid)[0]) # gets the uid/gid of the file, then convert that to the name of the uid/gid
                uid_gid_get = re.sub(r"\s+", '\xa0', uid_gid_get)
            except:
                uid_gid_get = str(os.stat(dir_ls[itr]).st_uid)+'/'+str(os.stat(dir_ls[itr]).st_gid) # if uid/gid is not found
            if os.path.isdir(dir_ls[itr]) == True:
                r_id = tree.insert('', 'end', text=dir_ls[itr], tag=('dir'), values=('DIRECTORY '+las_mod_time+' '+uid_gid_get+' DIRECTORY')) 
                id_list.append(r_id)
                total_dir += 1
            else:   # EXT_NAME
                if dir_ls[itr][-2:] == 'rc':
                    file_ext = 'rc'
                elif '.' not in dir_ls[itr][1:]:
                    file_ext = '*'
                else:
                    file_ext = dir_ls[itr].split('.')
                    file_ext = file_ext[len(file_ext)-1]
                ext_conf_n = sort_file('EXT_NAME')
                try:
                    file_ext_n = ext_conf_n[file_ext] 
                except:
                    file_ext_n = ext_conf_n['*']
                file_ext_n = re.sub(r"\s+", '\xa0', file_ext_n)
                r_id = tree.insert('', 'end', text=dir_ls[itr], tag=('file'), values=(human_readable_size(os.stat(dir_ls[itr]).st_size)+' '+las_mod_time+' '+uid_gid_get+' '+file_ext_n))
                id_list.append(r_id)
                total_file += 1
    tree.tag_configure('dir', background='#94bff3')
    tree.tag_configure('up', background='#d9d9d9')
    tree.tag_bind('dir', '<Double-Button-1>', dir_change)
    tree.tag_bind('file', '<Double-Button-1>', ext_prog)
    tree.tag_bind('up', '<Double-Button-1>', up_dir)
    tree.tag_bind('dir', '<Right>', dir_change)
    tree.tag_bind('file', '<Right>', ext_prog)
    tree.tag_bind('up', '<Right>', up_dir)
    scrollbar.config(command=tree.yview)

    sizestat = os.statvfs('/')
    lower_info_text = ' Total directories: '+str(total_dir)+'    Total files: '+str(total_file)+'    Hidden files shown: '+str(show_hidden_files)+'    Free Space: '+str(human_readable_size(sizestat.f_frsize * sizestat.f_bfree))+'    Total Space: '+str(human_readable_size(sizestat.f_frsize * sizestat.f_blocks))+access_info
    dir_info_01 = Label(main, text='Total files/directories: '+str(total_dir+total_file))
    dir_info_02 = Label(main, text=lower_info_text)
    dir_info_01.grid(row=0, column=6, columnspan=8, sticky='w')
    dir_info_02.grid(row=20, column=0, columnspan=8, sticky='w')

    main.bind('<Control-h>', toggle_hidden)
    main.bind('<Control-r>', refresh_dir)
    main.bind('<Control-l>', bind_cur_dir_entry)
    main.bind('<Left>', up_dir)
    main.bind('<Up>', lambda event: row_change(event, -1, id_list))
    main.bind('<Down>', lambda event: row_change(event, 1, id_list))
    main.bind('<Control-Up>', lambda event: row_change(event, -10, id_list)) 
    main.bind('<Control-Down>', lambda event: row_change(event, 10, id_list))
    main.bind('<Home>', lambda event: row_change(event, 0, id_list))
    main.bind('<End>', lambda event: row_change(event, 2, id_list))
    main.bind('<Control-q>', sys.exit)

def ttk_style(main):
    Style().configure("TButton", xpad=12, relief="flat", background="#ccc")
    main.configure(background="#EEE")

def main_window():
    global home
    os.chdir(home) 
    main = Tk()
    main.title("MartTKfManager - "+os.getcwd())
    width, height = 970, 470
    main.geometry("%dx%d+%d+%d" % (width, height, 0, 0))

    main_buttons(main)
    main_list_dir(main)
    ttk_style(main)
    main.update()

    main.mainloop()

main_window()
