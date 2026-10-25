#!/usr/bin/env python3
"""Terminal 11: Raspberry Pi OS graphical shell demo (Tkinter)."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import subprocess, datetime, os, json, ast, operator, platform, shutil, webbrowser, random, time

HOME = Path.home()
ROOT = HOME / '.terminal11'
ROOT.mkdir(exist_ok=True)
CFG = ROOT / 'settings.json'
DEFAULT = {'theme':'dark','accent':'#4cc2ff'}
try: settings = {**DEFAULT, **json.loads(CFG.read_text())}
except (OSError, ValueError): settings = DEFAULT.copy()

class Desktop:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Terminal 11 Ultimate — Raspberry Pi 4')
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        self.root.bind('<F11>', lambda e: self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen')))
        self.root.bind('<Control-q>', lambda e: self.root.destroy())
        self.windows=[]
        self.start_open=False
        self.draw()
        self.tick()

    def palette(self):
        if settings['theme']=='light': return '#dceefa','#ffffff','#172235','#eef4fb'
        return '#101a30','#202b40','#f5f8ff','#2d3c55'

    def draw(self):
        bg, panel, fg, button = self.palette()
        self.root.configure(bg=bg)
        for widget in self.root.winfo_children(): widget.destroy()
        self.bg,self.panel,self.fg,self.button=bg,panel,fg,button
        self.wall=tk.Canvas(self.root, bg=bg, highlightthickness=0)
        self.wall.pack(fill='both', expand=True)
        self.wall.bind('<Configure>', self.paint_wallpaper)
        self.desktopicons=tk.Frame(self.wall,bg=bg)
        self.desktopicons.place(x=24,y=26)
        for name,action in [('📁  Files',self.explorer),('📝  Notepad',self.notepad),('⌨  Terminal',self.terminal),('⚙  Settings',self.preferences),('🧮  Calculator',self.calculator),('🎮  Game Maker',self.game_maker)]:
            tk.Button(self.desktopicons,text=name,command=action,fg=fg,bg=bg,activebackground=button,activeforeground=fg,bd=0,font=('DejaVu Sans',12),width=17,anchor='w',pady=13).pack(anchor='w')
        self.bar=tk.Frame(self.root,bg=panel,height=62)
        self.bar.pack(side='bottom',fill='x')
        self.bar.pack_propagate(False)
        tk.Frame(self.bar,bg=panel,width=1).pack(side='left',expand=True)
        for label,action in [('⊞',self.start_menu),('⌕',self.search),('📁',self.explorer),('📝',self.notepad),('⌨',self.terminal),('⚙',self.preferences)]:
            tk.Button(self.bar,text=label,command=action,bg=panel,fg=fg,activebackground=button,activeforeground=fg,bd=0,font=('DejaVu Sans',19),width=4).pack(side='left',padx=3,pady=7)
        tk.Frame(self.bar,bg=panel,width=1).pack(side='left',expand=True)
        self.clock=tk.Label(self.bar,bg=panel,fg=fg,font=('DejaVu Sans',10),justify='right',width=18)
        self.clock.pack(side='right',padx=12)

    def paint_wallpaper(self,event=None):
        c=self.wall; c.delete('wallpaper')
        w,h=c.winfo_width(),c.winfo_height()
        if w<10:return
        for i,color in enumerate(['#10244b','#153b75','#1b57a0','#2175c6','#4a9ce0']):
            m=i*min(w,h)*0.09
            c.create_oval(w*.38-m,h*.18-m,w*.9+m,h*.95+m,fill=color,outline='',tags='wallpaper')
        c.create_text(w*.65,h*.49,text='11',font=('DejaVu Sans',120,'bold'),fill='#a3d9ff',tags='wallpaper')
        c.tag_lower('wallpaper')

    def tick(self):
        try:self.clock.config(text=datetime.datetime.now().strftime('%I:%M %p\n%b %d, %Y'))
        except tk.TclError:return
        self.root.after(1000,self.tick)

    def window(self,title,width=720,height=510):
        win=tk.Toplevel(self.root)
        win.title(title)
        win.geometry(f'{width}x{height}+{max(10,(self.root.winfo_screenwidth()-width)//2)}+{max(10,(self.root.winfo_screenheight()-height)//2)}')
        win.configure(bg=self.panel)
        self.windows.append(win)
        return win

    def start_menu(self):
        if self.start_open and hasattr(self,'start') and self.start.winfo_exists():
            self.start.destroy();self.start_open=False;return
        self.start_open=True
        self.start=self.window('Start — Terminal 11',490,520)
        self.start.protocol('WM_DELETE_WINDOW',lambda:(self.start.destroy(),setattr(self,'start_open',False)))
        tk.Label(self.start,text='Terminal 11',font=('DejaVu Sans',25,'bold'),bg=self.panel,fg=self.fg).pack(pady=20)
        grid=tk.Frame(self.start,bg=self.panel);grid.pack(padx=20,pady=15)
        apps=[('Files',self.explorer),('Notepad',self.notepad),('Terminal',self.terminal),('Calculator',self.calculator),('Settings',self.preferences),('Code Maker',self.code_maker),('Game Maker',self.game_maker),('Search',self.search)]
        for i,(name,cmd) in enumerate(apps):
            tk.Button(grid,text=name,command=lambda c=cmd:(self.start.destroy(),setattr(self,'start_open',False),c()),bg=self.button,fg=self.fg,bd=0,width=17,height=3).grid(row=i//2,column=i%2,padx=8,pady=8)
        tk.Button(self.start,text='⏻  Shut down',command=self.shutdown,bg=self.button,fg=self.fg).pack(side='bottom',pady=20)

    def explorer(self):
        win=self.window('File Explorer',850,570)
        current=tk.StringVar(value=str(HOME))
        top=tk.Frame(win,bg=self.panel);top.pack(fill='x',padx=12,pady=12)
        entry=tk.Entry(top,textvariable=current,font=('DejaVu Sans',11));entry.pack(side='left',fill='x',expand=True)
        body=tk.Listbox(win,font=('DejaVu Sans',12),bg=self.button,fg=self.fg,selectbackground='#2475ba',bd=0)
        body.pack(fill='both',expand=True,padx=12,pady=(0,12))
        def load(path=None):
            p=Path(path or current.get()).expanduser()
            try:
                items=sorted(p.iterdir(),key=lambda x:(not x.is_dir(),x.name.lower()))
                body.delete(0,'end')
                for item in items:body.insert('end',('📁  ' if item.is_dir() else '📄  ')+item.name)
                current.set(str(p));win.items=items
            except OSError as ex:messagebox.showerror('Explorer',str(ex),parent=win)
        def open_selected(e=None):
            s=body.curselection()
            if not s:return
            p=win.items[s[0]]
            if p.is_dir():load(p)
            else:self.notepad(p)
        tk.Button(top,text='Go',command=load,bg=self.button,fg=self.fg).pack(side='left',padx=5)
        tk.Button(top,text='↑',command=lambda:load(Path(current.get()).parent),bg=self.button,fg=self.fg).pack(side='left')
        body.bind('<Double-Button-1>',open_selected)
        body.bind('<Return>',open_selected)
        load()

    def editor(self,title,path=None,code=False):
        win=self.window(title,900,650)
        text=tk.Text(win,undo=True,wrap='none',font=('DejaVu Sans Mono',12),bg=self.button,fg=self.fg,insertbackground=self.fg)
        text.pack(fill='both',expand=True,padx=8,pady=8)
        active=[Path(path) if path else None]
        if active[0]:
            try:text.insert('1.0',active[0].read_text(encoding='utf-8'))
            except (OSError,UnicodeError) as ex:messagebox.showerror('Open',str(ex),parent=win)
        def open_file():
            p=filedialog.askopenfilename(parent=win)
            if p:
                try:text.delete('1.0','end');text.insert('1.0',Path(p).read_text(encoding='utf-8'));active[0]=Path(p)
                except (OSError,UnicodeError) as ex:messagebox.showerror('Open',str(ex),parent=win)
        def save_as():
            p=filedialog.asksaveasfilename(parent=win,defaultextension='.py' if code else '.txt')
            if p:active[0]=Path(p);save()
        def save():
            if not active[0]:save_as();return
            try:active[0].write_text(text.get('1.0','end-1c'),encoding='utf-8');win.title(f'{title} — {active[0].name}')
            except OSError as ex:messagebox.showerror('Save',str(ex),parent=win)
        menu=tk.Menu(win);file=tk.Menu(menu,tearoff=False)
        file.add_command(label='Open',command=open_file);file.add_command(label='Save',command=save);file.add_command(label='Save as',command=save_as)
        menu.add_cascade(label='File',menu=file)
        if code:
            def run_code():
                save()
                if active[0] and active[0].exists() and messagebox.askyesno('Run Python','Run this Python file? Only run code you trust.',parent=win):
                    subprocess.Popen(['x-terminal-emulator','-e','python3',str(active[0])])
            menu.add_command(label='▶ Run (F5)',command=run_code)
            win.bind('<F5>',lambda e:run_code())
        win.config(menu=menu)
        win.bind('<Control-s>',lambda e:save())

    def notepad(self,path=None):self.editor('Notepad',path)
    def code_maker(self):self.editor('Code Maker',code=True)

    def terminal(self):
        try:subprocess.Popen(['x-terminal-emulator'])
        except OSError:messagebox.showinfo('Terminal','Install xterm or another terminal emulator.')

    def calculator(self):
        win=self.window('Calculator',340,420)
        expr=tk.StringVar()
        tk.Entry(win,textvariable=expr,font=('DejaVu Sans',24),justify='right').pack(fill='x',padx=12,pady=18)
        def calculate():
            try:
                node=ast.parse(expr.get(),mode='eval').body
                ops={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv,ast.Pow:operator.pow}
                def ev(n):
                    if isinstance(n,ast.Constant) and type(n.value) in (int,float):return n.value
                    if isinstance(n,ast.UnaryOp) and isinstance(n.op,ast.USub):return -ev(n.operand)
                    if isinstance(n,ast.BinOp) and type(n.op) in ops:return ops[type(n.op)](ev(n.left),ev(n.right))
                    raise ValueError('Invalid expression')
                result=ev(node)
                if abs(result)>1e20:raise ValueError('Result too large')
                expr.set(str(result))
            except (ValueError,ZeroDivisionError,OverflowError,SyntaxError):expr.set('Error')
        grid=tk.Frame(win,bg=self.panel);grid.pack(expand=True,fill='both',padx=12,pady=8)
        for i,key in enumerate(['7','8','9','/','4','5','6','*','1','2','3','-','C','0','=','+']):
            cmd=calculate if key=='=' else (lambda k=key:expr.set('' if k=='C' else expr.get()+k))
            tk.Button(grid,text=key,command=cmd,bg=self.button,fg=self.fg,font=('DejaVu Sans',17),bd=0).grid(row=i//4,column=i%4,sticky='nsew',padx=3,pady=3)
        for i in range(4):grid.rowconfigure(i,weight=1);grid.columnconfigure(i,weight=1)

    def preferences(self):
        win=self.window('Settings',470,300)
        tk.Label(win,text='Personalization',font=('DejaVu Sans',20,'bold'),bg=self.panel,fg=self.fg).pack(pady=22)
        def set_theme(theme):
            settings['theme']=theme;CFG.write_text(json.dumps(settings));win.destroy();self.draw()
        for theme in ('dark','light'):
            tk.Button(win,text=theme.title()+' theme',command=lambda t=theme:set_theme(t),bg=self.button,fg=self.fg,width=24,height=2).pack(pady=9)
        tk.Label(win,text='F11: fullscreen  •  Esc: windowed  •  Ctrl+Q: quit',bg=self.panel,fg=self.fg).pack(pady=12)

    def search(self):
        win=self.window('Search',450,210)
        tk.Label(win,text='Search apps',bg=self.panel,fg=self.fg,font=('DejaVu Sans',18)).pack(pady=15)
        term=tk.Entry(win,font=('DejaVu Sans',14));term.pack(fill='x',padx=20)
        apps={'files':self.explorer,'notepad':self.notepad,'terminal':self.terminal,'calculator':self.calculator,'settings':self.preferences,'code':self.code_maker,'game':self.game_maker}
        def go(e=None):
            q=term.get().lower().strip()
            matches=[v for k,v in apps.items() if q in k]
            if matches:win.destroy();matches[0]()
            else:messagebox.showinfo('Search','No matching app.',parent=win)
        term.bind('<Return>',go)
        tk.Button(win,text='Open',command=go,bg=self.button,fg=self.fg).pack(pady=12)
        term.focus_set()

    def game_maker(self):
        win=self.window('Game Maker — Maze',650,580)
        tk.Label(win,text='Maze editor: # wall, P player, G goal, space floor',bg=self.panel,fg=self.fg).pack(pady=8)
        editor=tk.Text(win,font=('DejaVu Sans Mono',17),wrap='none',height=13,bg=self.button,fg=self.fg,insertbackground=self.fg)
        editor.pack(fill='both',expand=True,padx=12)
        editor.insert('1.0','###########\n#P        #\n# ### ### #\n#   #     #\n### # #####\n#       G #\n###########')
        def play():
            lines=editor.get('1.0','end-1c').splitlines()
            if not lines or len(lines)>35 or max(map(len,lines))>60:return messagebox.showerror('Game','Maze must be 35 rows or fewer and 60 columns or fewer.',parent=win)
            board=[list(line.ljust(max(map(len,lines)))) for line in lines]
            positions=[(y,x) for y,row in enumerate(board) for x,c in enumerate(row) if c=='P']
            goals=[(y,x) for y,row in enumerate(board) for x,c in enumerate(row) if c=='G']
            if len(positions)!=1 or len(goals)!=1:return messagebox.showerror('Game','Place exactly one P and one G.',parent=win)
            y,x=positions[0];board[y][x]=' '
            game=self.window('Playing Maze — arrow keys',600,460)
            view=tk.Label(game,font=('DejaVu Sans Mono',15),justify='left',bg=self.button,fg=self.fg)
            view.pack(expand=True,fill='both',padx=10,pady=10)
            pos=[y,x]
            def refresh():view.config(text='\n'.join(''.join('P' if (r,c)==tuple(pos) else cell for c,cell in enumerate(row)) for r,row in enumerate(board)))
            def move(e):
                delta={'Up':(-1,0),'Down':(1,0),'Left':(0,-1),'Right':(0,1)}.get(e.keysym)
                if not delta:return
                ny,nx=pos[0]+delta[0],pos[1]+delta[1]
                if 0<=ny<len(board) and 0<=nx<len(board[ny]) and board[ny][nx]!='#':
                    pos[:]=[ny,nx];refresh()
                    if (ny,nx)==goals[0]:messagebox.showinfo('You win!','Maze complete!',parent=game)
            game.bind('<Key>',move);refresh();game.focus_force()
        tk.Button(win,text='▶ Play (F5)',command=play,bg=self.button,fg=self.fg,height=2).pack(pady=10)
        win.bind('<F5>',lambda e:play())

    def shutdown(self):
        if messagebox.askyesno('Shut down','Shut down the Raspberry Pi?'):
            try:subprocess.Popen(['systemctl','poweroff'])
            except OSError:messagebox.showerror('Shutdown','Unable to request shutdown.')

    def run(self):self.root.mainloop()



class UltimateDesktop(Desktop):
    """Cross-platform Windows-inspired desktop with extra built-in applications."""
    def __init__(self):
        self.notes_dir = ROOT / 'notes'
        self.notes_dir.mkdir(parents=True, exist_ok=True)
        self.notifications = []
        super().__init__()
        self.root.title('Terminal 11 Ultimate')
        self.root.bind('<Control-Alt-t>', lambda e: self.terminal())
        self.root.bind('<Control-Alt-e>', lambda e: self.explorer())
        self.root.bind('<Control-Alt-n>', lambda e: self.notepad())
        self.root.bind('<Control-Alt-s>', lambda e: self.start_menu())
        self.notify('Welcome to Terminal 11 Ultimate!')

    def apps(self):
        return [
            ('📁 Files', self.explorer), ('📝 Notepad', self.notepad),
            ('⌨ Terminal', self.terminal), ('⚙ Settings', self.preferences),
            ('🧮 Calculator', self.calculator), ('🎮 Maze Maker', self.game_maker),
            ('💻 Code Maker', self.code_maker), ('🎨 Paint', self.paint),
            ('📅 Calendar', self.calendar), ('🕒 Clock', self.clock_app),
            ('🗒 Sticky Notes', self.sticky_notes), ('🌐 Browser', self.browser),
            ('📊 Task Manager', self.task_manager), ('❎ Tic Tac Toe', self.tic_tac_toe),
            ('🐍 Snake', self.snake), ('🔔 Notifications', self.notification_center),
            ('ℹ About', self.about),
        ]

    def draw(self):
        super().draw()
        # Replace starter desktop shortcuts with the expanded launcher.
        for widget in self.desktopicons.winfo_children(): widget.destroy()
        for name, action in self.apps()[:11]:
            tk.Button(self.desktopicons, text=name, command=action, fg=self.fg, bg=self.bg,
                      activebackground=self.button, activeforeground=self.fg, bd=0,
                      font=('DejaVu Sans', 11), width=19, anchor='w', pady=7).pack(anchor='w')
        tk.Button(self.bar, text='🔔', command=self.notification_center, bg=self.panel,
                  fg=self.fg, bd=0, font=('DejaVu Sans', 15)).pack(side='right', padx=5)
        self.wall.bind('<Button-3>', self.desktop_menu)

    def desktop_menu(self, event):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label='Refresh desktop', command=self.draw)
        menu.add_command(label='Open File Explorer', command=self.explorer)
        menu.add_command(label='Personalize', command=self.preferences)
        menu.add_command(label='About Terminal 11', command=self.about)
        menu.tk_popup(event.x_root, event.y_root)

    def notify(self, message):
        self.notifications.insert(0, datetime.datetime.now().strftime('%H:%M') + '  ' + message)
        self.notifications = self.notifications[:50]

    def start_menu(self):
        if self.start_open and hasattr(self, 'start') and self.start.winfo_exists():
            self.start.destroy(); self.start_open = False; return
        self.start_open = True
        self.start = self.window('Start — Terminal 11 Ultimate', 610, 660)
        self.start.protocol('WM_DELETE_WINDOW', lambda: (self.start.destroy(), setattr(self,'start_open',False)))
        tk.Label(self.start, text='⊞  Terminal 11 Ultimate', bg=self.panel, fg=self.fg,
                 font=('DejaVu Sans', 23, 'bold')).pack(pady=17)
        query = tk.StringVar()
        entry = tk.Entry(self.start, textvariable=query, font=('DejaVu Sans', 13))
        entry.pack(fill='x', padx=25, pady=8)
        tk.Label(self.start, text='Pinned apps • Search to filter', bg=self.panel, fg=self.fg).pack(anchor='w', padx=25)
        holder = tk.Frame(self.start, bg=self.panel); holder.pack(fill='both', expand=True, padx=16, pady=10)
        def launch(command):
            self.start.destroy(); self.start_open = False; command()
        def refresh(*_):
            for child in holder.winfo_children(): child.destroy()
            filtered = [(n, c) for n,c in self.apps() if query.get().lower() in n.lower()]
            for i,(name,command) in enumerate(filtered):
                tk.Button(holder, text=name, command=lambda c=command: launch(c),
                          bg=self.button, fg=self.fg, bd=0, width=19, height=2).grid(
                          row=i//3, column=i%3, padx=5, pady=5, sticky='nsew')
            for col in range(3): holder.columnconfigure(col, weight=1)
        query.trace_add('write', refresh); refresh()
        footer=tk.Frame(self.start,bg=self.panel); footer.pack(fill='x',padx=20,pady=12)
        tk.Label(footer,text=platform.node() or 'My Computer',bg=self.panel,fg=self.fg).pack(side='left')
        tk.Button(footer,text='⏻ Exit desktop',command=self.root.destroy,bg=self.button,fg=self.fg).pack(side='right')
        entry.focus_set()

    def terminal(self):
        """Built-in command console (Windows cmd / Raspberry Pi POSIX shell)."""
        import threading
        import queue

        win = self.window('Terminal 11 — Built-in Terminal', 900, 600)
        output = tk.Text(win, bg='#10151e', fg='#d7e5f5', insertbackground='white',
                         font=('Consolas' if os.name == 'nt' else 'DejaVu Sans Mono', 11),
                         wrap='word', state='disabled')
        output.pack(fill='both', expand=True, padx=10, pady=(10, 4))
        bottom = tk.Frame(win, bg=self.panel)
        bottom.pack(fill='x', padx=10, pady=(0, 10))
        prompt = tk.StringVar()
        entry = tk.Entry(bottom, textvariable=prompt, font=('Consolas' if os.name == 'nt' else 'DejaVu Sans Mono', 11))
        entry.pack(side='left', fill='x', expand=True)
        cwd = [Path.home()]
        running = [False]
        process = [None]
        messages = queue.Queue()
        history = []
        history_index = [0]

        def write(message):
            if not win.winfo_exists():
                return
            output.configure(state='normal')
            output.insert('end', message)
            output.see('end')
            output.configure(state='disabled')

        def poll():
            if not win.winfo_exists():
                return
            try:
                while True:
                    kind, data = messages.get_nowait()
                    if kind == 'text':
                        write(data)
                    elif kind == 'done':
                        running[0] = False
                        process[0] = None
                        write('\n' if data == 0 else f'\n[Exit code: {data}]\n')
            except queue.Empty:
                pass
            win.after(80, poll)

        def execute(event=None):
            command = prompt.get().strip()
            prompt.set('')
            if not command:
                return
            if running[0]:
                write('\nA command is still running. Press Stop first.\n')
                return
            history.append(command)
            history_index[0] = len(history)
            write(f'\n{cwd[0]}> {command}\n')
            cmd_lower = command.lower()
            if cmd_lower in ('clear', 'cls'):
                output.configure(state='normal')
                output.delete('1.0', 'end')
                output.configure(state='disabled')
                return
            if cmd_lower in ('help', '?'):
                write('Built-ins: help, clear/cls, cd, pwd, exit\n')
                write('Other commands run using your real system shell.\n')
                write('Windows: dir, ipconfig, python ...\n')
                write('Raspberry Pi: ls, uname -a, python3 ...\n')
                return
            if cmd_lower == 'exit':
                win.destroy()
                return
            if cmd_lower == 'pwd':
                write(str(cwd[0]) + '\n')
                return
            if cmd_lower == 'cd' or cmd_lower.startswith('cd '):
                target = command[2:].strip().strip('"')
                new_path = Path(target).expanduser() if target else Path.home()
                if not new_path.is_absolute():
                    new_path = cwd[0] / new_path
                try:
                    new_path = new_path.resolve()
                    if not new_path.is_dir():
                        raise NotADirectoryError(str(new_path))
                    cwd[0] = new_path
                except OSError as ex:
                    write(f'{ex}\n')
                return
            running[0] = True

            def worker():
                try:
                    proc = subprocess.Popen(command, shell=True, cwd=str(cwd[0]),
                                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                            stdin=subprocess.DEVNULL, text=True,
                                            errors='replace', bufsize=1)
                    process[0] = proc
                    for line in proc.stdout:
                        messages.put(('text', line))
                    messages.put(('done', proc.wait()))
                except Exception as ex:
                    messages.put(('text', f'Error: {ex}\n'))
                    messages.put(('done', 1))
            threading.Thread(target=worker, daemon=True).start()

        def stop():
            if process[0] and process[0].poll() is None:
                process[0].terminate()
                write('\n[Stop requested]\n')

        def navigate(delta):
            if history:
                history_index[0] = max(0, min(len(history), history_index[0] + delta))
                prompt.set(history[history_index[0]] if history_index[0] < len(history) else '')
                entry.icursor('end')

        entry.bind('<Return>', execute)
        entry.bind('<Up>', lambda e: (navigate(-1), 'break')[1])
        entry.bind('<Down>', lambda e: (navigate(1), 'break')[1])
        tk.Button(bottom, text='Run', command=execute, bg=self.button, fg=self.fg).pack(side='left', padx=5)
        tk.Button(bottom, text='Stop', command=stop, bg=self.button, fg=self.fg).pack(side='left')
        write('Terminal 11 Built-in Terminal\n')
        write(f'System: {platform.system()} | Working directory: {cwd[0]}\n')
        write('Type help for commands. Commands execute on the host computer.\n')
        entry.focus_set()
        poll()

    def editor(self, title, path=None, code=False):
        # Base editor is reused, but code execution must be cross-platform.
        if not code: return super().editor(title,path,False)
        win=self.window(title,900,650)
        top=tk.Frame(win,bg=self.panel);top.pack(fill='x',padx=10,pady=8)
        content=tk.Text(win,undo=True,wrap='none',font=('DejaVu Sans Mono',12),
                        bg=self.button,fg=self.fg,insertbackground=self.fg)
        content.pack(fill='both',expand=True,padx=10,pady=6)
        active=[Path(path) if path else None]
        if active[0] and active[0].exists(): content.insert('1.0',active[0].read_text(encoding='utf-8'))
        def save():
            if not active[0]:
                chosen=filedialog.asksaveasfilename(parent=win,defaultextension='.py',filetypes=[('Python','*.py')])
                if not chosen:return False
                active[0]=Path(chosen)
            active[0].write_text(content.get('1.0','end-1c'),encoding='utf-8')
            win.title('Code Maker — '+active[0].name);return True
        def run_code():
            if not save():return
            if not messagebox.askyesno('Run code','Run this Python program on your computer? Only run code you trust.',parent=win):return
            try:
                subprocess.Popen([__import__('sys').executable,str(active[0])],cwd=str(active[0].parent))
            except OSError as ex: messagebox.showerror('Run',str(ex),parent=win)
        tk.Button(top,text='💾 Save (Ctrl+S)',command=save,bg=self.button,fg=self.fg).pack(side='left',padx=4)
        tk.Button(top,text='▶ Run (F5)',command=run_code,bg=self.button,fg=self.fg).pack(side='left',padx=4)
        win.bind('<Control-s>',lambda e:save());win.bind('<F5>',lambda e:run_code())

    def preferences(self):
        win=self.window('Settings • Personalization',520,420)
        tk.Label(win,text='⚙ Personalization',font=('DejaVu Sans',22,'bold'),bg=self.panel,fg=self.fg).pack(pady=20)
        def set_theme(theme):
            settings['theme']=theme;CFG.write_text(json.dumps(settings),encoding='utf-8')
            win.destroy();self.draw();self.notify('Theme changed to '+theme)
        for theme in ('dark','light'):
            tk.Button(win,text=theme.title()+' theme',command=lambda t=theme:set_theme(t),
                      bg=self.button,fg=self.fg,width=28,height=2).pack(pady=7)
        tk.Label(win,text='F11 = fullscreen  •  Esc = windowed\nCtrl+Alt+T = terminal  •  Ctrl+Alt+S = Start\nCtrl+Q = exit',
                 bg=self.panel,fg=self.fg,justify='center').pack(pady=16)
        tk.Button(win,text='Exit fullscreen',command=lambda:self.root.attributes('-fullscreen',False),
                  bg=self.button,fg=self.fg).pack()

    def paint(self):
        win=self.window('Paint',960,660)
        toolbar=tk.Frame(win,bg=self.panel);toolbar.pack(fill='x',padx=8,pady=7)
        color=[settings.get('accent','#4cc2ff')];size=tk.IntVar(value=5)
        canvas=tk.Canvas(win,bg='white',cursor='crosshair');canvas.pack(fill='both',expand=True,padx=8,pady=8)
        last=[None]
        def start(e):last[0]=(e.x,e.y)
        def drag(e):
            if last[0]:canvas.create_line(*last[0],e.x,e.y,fill=color[0],width=size.get(),capstyle='round',smooth=True);last[0]=(e.x,e.y)
        canvas.bind('<Button-1>',start);canvas.bind('<B1-Motion>',drag);canvas.bind('<ButtonRelease-1>',lambda e:last.__setitem__(0,None))
        for shade in ('#101828','#e53935','#ff9800','#f5ce42','#3bad5d','#2878e3','#9334d5','#ffffff'):
            tk.Button(toolbar,bg=shade,width=3,command=lambda c=shade:color.__setitem__(0,c)).pack(side='left',padx=3)
        tk.Scale(toolbar,from_=1,to=20,orient='horizontal',variable=size,bg=self.panel,fg=self.fg,label='Brush').pack(side='left',padx=8)
        tk.Button(toolbar,text='Clear',command=lambda:canvas.delete('all')).pack(side='right',padx=5)
        def save():
            p=filedialog.asksaveasfilename(parent=win,defaultextension='.ps',filetypes=[('PostScript','*.ps')])
            if p:canvas.postscript(file=p,colormode='color');self.notify('Drawing saved')
        tk.Button(toolbar,text='Save drawing (.ps)',command=save).pack(side='right',padx=5)

    def calendar(self):
        import calendar
        win=self.window('Calendar',520,480)
        now=datetime.date.today();year=[now.year];month=[now.month]
        heading=tk.Label(win,bg=self.panel,fg=self.fg,font=('DejaVu Sans',20,'bold'));heading.pack(pady=12)
        text=tk.Label(win,bg=self.button,fg=self.fg,font=('DejaVu Sans Mono',15),justify='left');text.pack(fill='both',expand=True,padx=15,pady=12)
        def refresh():
            heading.config(text=f'{calendar.month_name[month[0]]} {year[0]}')
            text.config(text=calendar.month(year[0],month[0]))
        def move(delta):
            total=year[0]*12+month[0]-1+delta;year[0],m=divmod(total,12);month[0]=m+1;refresh()
        buttons=tk.Frame(win,bg=self.panel);buttons.pack(pady=8)
        tk.Button(buttons,text='◀ Previous',command=lambda:move(-1)).pack(side='left',padx=12)
        tk.Button(buttons,text='Next ▶',command=lambda:move(1)).pack(side='left',padx=12)
        refresh()

    def clock_app(self):
        win=self.window('Clock & Stopwatch',480,330)
        clock=tk.Label(win,bg=self.panel,fg=self.fg,font=('DejaVu Sans',35,'bold'));clock.pack(pady=25)
        elapsed=tk.Label(win,bg=self.panel,fg=self.fg,font=('DejaVu Sans',20));elapsed.pack(pady=8)
        state={'start':None,'total':0.0}
        def tick():
            if not win.winfo_exists():return
            clock.config(text=datetime.datetime.now().strftime('%H:%M:%S'))
            value=state['total']+(time.monotonic()-state['start'] if state['start'] else 0)
            elapsed.config(text=f'Stopwatch: {value:.1f}s')
            win.after(100,tick)
        def toggle():
            if state['start'] is None:state['start']=time.monotonic();button.config(text='Pause')
            else:state['total']+=time.monotonic()-state['start'];state['start']=None;button.config(text='Start')
        row=tk.Frame(win,bg=self.panel);row.pack(pady=12)
        button=tk.Button(row,text='Start',command=toggle,width=12);button.pack(side='left',padx=6)
        tk.Button(row,text='Reset',command=lambda:state.update(start=None,total=0.0)).pack(side='left',padx=6)
        tick()

    def sticky_notes(self):
        win=self.window('Sticky Notes',470,430)
        note=tk.Text(win,bg='#fff3b0',fg='#2b2516',font=('DejaVu Sans',13),wrap='word')
        note.pack(fill='both',expand=True,padx=9,pady=9)
        p=self.notes_dir/'sticky_note.txt'
        if p.exists():note.insert('1.0',p.read_text(encoding='utf-8'))
        def save():p.write_text(note.get('1.0','end-1c'),encoding='utf-8');self.notify('Sticky note saved')
        tk.Button(win,text='💾 Save note',command=save).pack(pady=6)
        win.bind('<Control-s>',lambda e:save())
        win.protocol('WM_DELETE_WINDOW',lambda:(save(),win.destroy()))

    def browser(self):
        win=self.window('Web Browser Launcher',620,220)
        tk.Label(win,text='🌐 Open a website in your default browser',bg=self.panel,fg=self.fg,
                 font=('DejaVu Sans',16)).pack(pady=18)
        url=tk.StringVar(value='https://www.wikipedia.org')
        entry=tk.Entry(win,textvariable=url,font=('DejaVu Sans',13));entry.pack(fill='x',padx=20,pady=8)
        def open_url():
            address=url.get().strip()
            if not address.startswith(('https://','http://')):address='https://'+address
            webbrowser.open(address)
        tk.Button(win,text='Go',command=open_url,width=16).pack(pady=8)
        entry.bind('<Return>',lambda e:open_url())

    def task_manager(self):
        win=self.window('Task Manager',630,450)
        tk.Label(win,text='Task Manager • Terminal 11 windows',bg=self.panel,fg=self.fg,
                 font=('DejaVu Sans',18,'bold')).pack(pady=12)
        listing=tk.Listbox(win,bg=self.button,fg=self.fg,font=('DejaVu Sans',12));listing.pack(fill='both',expand=True,padx=14,pady=8)
        active=[]
        def refresh():
            listing.delete(0,'end');active.clear()
            for window in self.windows:
                try:
                    if window.winfo_exists():active.append(window);listing.insert('end',window.title())
                except tk.TclError:pass
        def focus():
            if listing.curselection():active[listing.curselection()[0]].lift()
        def close():
            if listing.curselection():
                target=active[listing.curselection()[0]]
                if target!=win:target.destroy()
                refresh()
        buttons=tk.Frame(win,bg=self.panel);buttons.pack(pady=8)
        for label,cmd in [('Refresh',refresh),('Switch to',focus),('Close selected',close)]:
            tk.Button(buttons,text=label,command=cmd).pack(side='left',padx=8)
        refresh()

    def tic_tac_toe(self):
        win=self.window('Tic Tac Toe',410,470)
        board=['']*9;turn=['X'];buttons=[]
        label=tk.Label(win,text='X to play',font=('DejaVu Sans',19),bg=self.panel,fg=self.fg);label.pack(pady=16)
        grid=tk.Frame(win,bg=self.panel);grid.pack(expand=True)
        lines=((0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6))
        def reset():
            board[:]=['']*9;turn[0]='X';label.config(text='X to play')
            for b in buttons:b.config(text='',state='normal')
        def play(i):
            if board[i]:return
            board[i]=turn[0];buttons[i].config(text=turn[0])
            winner=next((board[a] for a,b,c in lines if board[a] and board[a]==board[b]==board[c]),None)
            if winner or all(board):
                label.config(text=f'{winner} wins!' if winner else 'Draw!')
                for b in buttons:b.config(state='disabled')
            else:turn[0]='O' if turn[0]=='X' else 'X';label.config(text=turn[0]+' to play')
        for i in range(9):
            b=tk.Button(grid,text='',font=('DejaVu Sans',30,'bold'),width=4,height=2,
                        command=lambda n=i:play(n));b.grid(row=i//3,column=i%3,padx=4,pady=4);buttons.append(b)
        tk.Button(win,text='New game',command=reset).pack(pady=12)

    def snake(self):
        win=self.window('Snake — Arrow keys',580,570)
        area=tk.Canvas(win,width=480,height=440,bg='#111a27',highlightthickness=0)
        area.pack(pady=12)
        cell=20;cols=24;rows=22
        snake=[(12,11),(11,11),(10,11)];direction=[(1,0)];pending=[(1,0)]
        food=[(18,11)];running=[True];score=[0]
        label=tk.Label(win,text='Score: 0  •  Arrow keys to move',bg=self.panel,fg=self.fg);label.pack()
        def key(e):
            dirs={'Up':(0,-1),'Down':(0,1),'Left':(-1,0),'Right':(1,0)}
            if e.keysym in dirs:
                d=dirs[e.keysym]
                if d!=(-direction[0][0],-direction[0][1]):pending[0]=d
        win.bind('<Key>',key);win.focus_force()
        def frame():
            if not win.winfo_exists() or not running[0]:return
            direction[0]=pending[0];x,y=snake[0];dx,dy=direction[0];head=(x+dx,y+dy)
            eating=head==food[0]
            if not (0<=head[0]<cols and 0<=head[1]<rows) or head in (snake if eating else snake[:-1]):
                running[0]=False;label.config(text=f'Game over! Score: {score[0]}');return
            snake.insert(0,head)
            if eating:
                score[0]+=1;label.config(text=f'Score: {score[0]}')
                available=[(a,b) for a in range(cols) for b in range(rows) if (a,b) not in snake]
                if not available:running[0]=False;label.config(text='You win!');return
                food[0]=random.choice(available)
            else:snake.pop()
            area.delete('all')
            for sx,sy in snake:area.create_rectangle(sx*cell,sy*cell,(sx+1)*cell,(sy+1)*cell,fill='#4ade80',outline='#142a1b')
            fx,fy=food[0];area.create_oval(fx*cell,fy*cell,(fx+1)*cell,(fy+1)*cell,fill='#ff637d',outline='')
            win.after(max(65,145-score[0]*4),frame)
        frame()

    def notification_center(self):
        win=self.window('Notification Center',520,400)
        tk.Label(win,text='🔔 Notifications',bg=self.panel,fg=self.fg,font=('DejaVu Sans',21,'bold')).pack(pady=15)
        items=tk.Listbox(win,bg=self.button,fg=self.fg,font=('DejaVu Sans',11))
        items.pack(fill='both',expand=True,padx=15,pady=10)
        for notice in self.notifications:items.insert('end',notice)
        def clear():self.notifications.clear();items.delete(0,'end')
        tk.Button(win,text='Clear all',command=clear).pack(pady=10)

    def about(self):
        messagebox.showinfo('About Terminal 11 Ultimate',
                            'Terminal 11 Ultimate — graphical desktop simulator\n'
                            'Built with Python and Tkinter.\n'
                            'Runs on Windows and Raspberry Pi OS.\n\n'
                            'Not affiliated with Microsoft or Windows.')

    def shutdown(self):
        if messagebox.askyesno('Exit Terminal 11','Close Terminal 11 Ultimate?'):
            self.root.destroy()


if __name__ == '__main__':
    UltimateDesktop().run()
