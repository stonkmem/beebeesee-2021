# -*- coding: utf-8 -*-
# Oscar Saharoy 2017

# TODO - test on various machines and versions of Python.

try:
    import Tkinter as tkinter
    import tkFont
except ImportError:
    import tkinter
    from tkinter import font as tkFont
import time, random, math, sys

from tkinter import Message, Checkbutton, LabelFrame


class GooeyException(Exception):
    pass


class ReConfig(object):
    # Redefines configure and cget methods in order to cooperate with new gooey keywords.

    def __init__(self, kw=None, unfocus=True):

        ''' Instantiating self.gooey_kw dictionary to avoid problems later.
            self.gooey_kw is a dictionary that holds non-tkinter keywords for gooey widgets to use.'''
        self.gooey_kw = {}

        # Establishing bindings to change the value associated with KW when the mouse hovers over the widget.
        if kw:
            self.bind('<Enter>', lambda e: self._enter(kw))
            self.bind('<Leave>', lambda e: self._leave(kw))
            self._default_value = None

    def configure(self, cnf=None, **kw):
        ''' Configure method can be called like
            widget.configure( keyword1=value1, keyword2=value2, ... )
            using any available Tkinter or gooey-based keyword of widget and any suitable value. '''

        cnf = tkinter._cnfmerge((cnf, kw))

        # Set value in self.gooey_kw for each gooey keyword in cnf.
        for key in cnf:
            if key in self.gooey_kw:
                self.gooey_kw[key] = cnf[key]

        # Filter out gooey keywords from cnf and then send remainder to regular _configure method.
        cnf = {key: cnf[key] for key in cnf if not (key in self.gooey_kw)}
        if cnf:
            return self._configure('configure', cnf, {})

    config = configure

    def cget(self, key):
        # Return the value associated with KEY if it is part of self.gooey_kw.
        if key in self.gooey_kw:
            return self.gooey_kw[key]

        # Otherwise get value using tk.call method as usual.
        return self.tk.call(self._w, 'cget', '-' + key)

    __getitem__ = cget

    def _enter(self, kw):
        '''Changes the value of KW to the widget's hovercolor if its state is not disabled,
           and stores the previous value as an attribute to switch it back later. '''
        if self['state'] != 'disabled':
            self._default_value = self[kw]
            self.configure({kw: self['hovercolor']})

    def _leave(self, kw):
        # Tries to switch KW back to self._default_value, and then resets self._default_value to None.
        try:
            self.configure({kw: self._default_value})
        except:
            pass
        self._default_value = None


'''
Color Scheme Hexcodes
grey40     = #666666
grey80     = #cccccc
grey90     = #e6e6e6
grey95     = #f5f5f5
white      = #ffffff
black      = #000000
turquoise3 = #00c5cd
'''


class Tk(tkinter.Tk):
    def __init__(self):
        tkinter.Tk.__init__(self)
        self.focus_force()

        # Setting a default font, background colour of 'white' and foreground of 'black' to the window.
        segoe_ui_10 = tkFont.Font(family='Segoe UI', size=10)
        self.option_add("*Font", segoe_ui_10)
        self.tk_setPalette(background='white', foreground='black', activeBackground='grey80', activeForeground='black',
                           disabledForeground='grey80')

        # Bindings to defocus certain widgets when a click is made on the background.
        self._focusey_widgets = []
        # self.bind('<Button-1>', self._focuser)

    def _focuser(self, e):
        # Gives focus to the clicked widget if it is 'focusey' - Text and Entry widgets at this time.
        if e.widget in self._focusey_widgets:
            e.widget.focus_set()

        # Otherwise moves focus to root window.
        else:
            self.focus_set()


class Frame(ReConfig, tkinter.Frame):
    def __init__(self, parent, hovercolor='grey40', state='disabled', highlightbackground='grey40',
                 highlightthickness=4, **kwargs):
        tkinter.Frame.__init__(self, parent, highlightbackground=highlightbackground,
                               highlightthickness=highlightthickness, **kwargs)
        ReConfig.__init__(self, kw='highlightbackground')
        self.gooey_kw = {'hovercolor': hovercolor, 'state': state}


class Message(ReConfig, tkinter.Message):
    def __init__(self, parent, width=None, fg='grey40', hovercolor='grey80', state='disabled', **kwargs):
        tkinter.Message.__init__(self, parent, width=width, fg=fg, **kwargs)
        ReConfig.__init__(self, kw='highlightbackground')
        self.gooey_kw = {'hovercolor': hovercolor, 'state': state}


class Label(ReConfig, tkinter.Label):
    def __init__(self, parent, **kwargs):
        ReConfig.__init__(self, unfocus=False)
        tkinter.Label.__init__(self, parent, **kwargs)


class Button(ReConfig, tkinter.Button):
    def __init__(self, parent, bd=0, hovercolor='grey90', state='normal', **kwargs):
        tkinter.Button.__init__(self, parent, bd=bd, state=state, **kwargs)
        ReConfig.__init__(self, kw='bg')
        self.gooey_kw = {'hovercolor': hovercolor}


class Toplevel(tkinter.Toplevel):
    def __init__(self, parent, **kwargs):
        tkinter.Toplevel.__init__(self, parent, **kwargs)


class Entry(ReConfig, tkinter.Entry):
    def __init__(self, parent, allowed=None, resize=False, hovercolor='grey40', bd=0, bg='white', highlightthickness=4,
                 highlightbackground='grey90', highlightcolor='turquoise3', **kwargs):

        # Registering validation command so that 'allowed' keyword functions cleanly.
        vcmd = (parent.register(self.onValidate), '%S')

        tkinter.Entry.__init__(self, parent, bd=bd, bg=bg, highlightthickness=highlightthickness,
                               highlightbackground=highlightbackground, highlightcolor=highlightcolor, validate="key",
                               validatecommand=vcmd, **kwargs)
        ReConfig.__init__(self, kw='highlightbackground')
        self.gooey_kw = {'allowed': allowed, 'resize': resize, 'hovercolor': hovercolor, 'defaultsize': self['width']}

        # Adding the widget to focusey widgets as it should gain focus when clicked.
        self.winfo_toplevel()._focusey_widgets += [self]

    def onValidate(self, S):
        if self.gooey_kw['allowed']:
            for char in S:
                if char not in self.gooey_kw['allowed']:
                    self.bell()
                    return False

        # Resize method included here so it is called whenever a character is added to the entry.
        if self.gooey_kw['resize']:
            self.resize()

        # Validation command must return True or False to function.
        return True

    def resize(self):
        # Resizes widget to fit length of text inputted.
        text = self.get()
        self.config(width=max(len(text), self.gooey_kw['defaultsize']))

    def flash(self):
        # Causes highlight of widget to flash rapidly.
        c = 0
        bg = self['highlightbackground']

        def toggle():
            if c != 10:
                self['highlightbackground'] = (bg if self['highlightbackground'] == 'turqoise3' else 'turqoise3')
                c += 1
                self.after(30, lambda: toggle())

        toggle()


class Text(ReConfig, tkinter.Text):
    def __init__(self, parent, allowed=None, resize=False, hovercolor='grey40', wrap='word', bd=0, bg='white',
                 highlightthickness=5, highlightbackground='grey40', highlightcolor='grey40', **kwargs):
        tkinter.Text.__init__(self, parent, bd=bd, wrap=wrap, bg=bg, highlightthickness=highlightthickness,
                              highlightbackground=highlightbackground, highlightcolor=highlightcolor, **kwargs)
        # vcmd = (parent.register(self.onValidate),'%S')
        # tkinter.Text.configure(self, validate='key', validatecommand=vcmd)
        ReConfig.__init__(self, kw='highlightbackground')
        self.gooey_kw = {'allowed': allowed, 'resize': resize, 'hovercolor': hovercolor,
                         'defaultsize': [self['width'], self['height']]}

        self.bind('<KeyRelease>', lambda e: self.filter() if self.gooey_kw['allowed'] else None)
        self.bind('<KeyRelease>', lambda e: self.resize() if self.gooey_kw['resize'] else None)

        # Adding the widget to focusey widgets as it should gain focus when clicked.
        self.winfo_toplevel()._focusey_widgets += [self]

    def resize(self):
        lines = 0
        text = self.get(1.0, 'end').split('\n')
        lines = max(lines, len(text) - 1)
        maxline = len(max(text))

        self.config(width=max(maxline, self.gooey_kw['defaultsize'][0]),
                    height=max(lines, self.gooey_kw['defaultsize'][1]))

    def filter(self):
        start, end = 1.0, "end-1c"
        content = self.get(start, end)
        content = ''.join([x for x in content if x in self.gooey_kw['allowed']])
        self.delete(start, end)
        self.insert(start, content)

    def flash(self):
        c = 0
        bg = self['highlightbackground']

        def toggle():
            if c != 10:
                self['highlightbackground'] = (bg if self['highlightbackground'] == highlight else highlight)
                c += 1
                self.after(30, lambda: toggle())

        toggle()


class OptionMenu(ReConfig, tkinter.OptionMenu):

    # Updated and restructured OptionMenu widget. This widget is a mess to begin with, and I would recommend using a Combobox instead.
    def __init__(self, parent, borderwidth=0, activebackground='white', highlightthickness=4,
                 highlightbackground='grey90',
                 highlightcolor='turquoise3', relief='flat', anchor='w', width=16, hovercolor='grey80', command=None,
                 values=None, **kwargs):
        self.parent = parent
        self.gooey_kw = {'values': values, 'command': command, 'hovercolor': hovercolor}

        cnf = tkinter._cnfmerge(kwargs)
        cnf['textvariable'] = self._stringvar = tkinter.StringVar(parent)

        cnf = {key: cnf[key] for key in cnf if not (key in self.gooey_kw)}
        tkinter.Widget.__init__(self, parent, "menubutton", cnf,
                                {'borderwidth': borderwidth, 'relief': relief, 'highlightthickness': highlightthickness,
                                 'highlightbackground': highlightbackground,
                                 'highlightcolor': highlightcolor, "anchor": anchor, 'width': width,
                                 'activebackground': activebackground})

        self.widgetName = 'tk_optionMenu'
        menu = self.__menu = tkinter.Menu(self, name="menu", tearoff=0, font=tkFont.Font(family='Segoe UI', size=10))
        self.menuname = menu._w
        self["menu"] = menu
        self._inmenu = []
        self._setvalues(self.gooey_kw['values'])
        self._hover_binding('highlightbackground')

        self.bind('<Button-1>', lambda e: self.focus_force())

    def get(self):
        return self._stringvar.get()

    def _setvalues(self, values):
        try:
            length = len(values)
        except TypeError:
            raise TypeError('\'values\' must be of type list or NoneType')
        for v, _ in enumerate(self._inmenu):
            self.__menu.delete(0)
        self._inmenu = []

        if values:
            self._stringvar.set(values[0])
            for v in values:
                self.__menu.add_command(label=v, command=tkinter._setit(self._stringvar, v, self.gooey_kw['command']))
                self._inmenu += [v]
        else:
            self._stringvar.set(' ')

    def _setcommand(self, newcommand):
        for i, value in enumerate(self.gooey_kw['values']):
            self.__menu.entryconfigure(i, command=tkinter._setit(self._stringvar, value, newcommand))

    def configure(self, cnf=None, **kw):
        cnf = tkinter._cnfmerge((cnf, kw))
        for key in cnf:
            if key in self.gooey_kw:
                self.gooey_kw[key] = cnf[key]
        if 'values' in cnf:
            self._setvalues(cnf['values'])
        if 'command' in cnf:
            self._setcommand(cnf['command'])

        cnf = {key: cnf[key] for key in cnf if not (key in self.gooey_kw)}
        return self._configure('configure', cnf, {})

    config = configure


''' New CanvasLine, CanvasRectangle and CanvasText classes wrap original Tkinter bindings for creating shapes on the canvas,
    making the syntax more intuitive and object-oriented.'''


class CanvasLine(int):
    ''' Gooey's Canvas shapes are subclasses of int and store the parent canvas as self._parent.
        This means they can be controlled using the new methods below as well as those of the canvas. For example:
            line = CanvasLine(canvas,x0,y0,x1,y1)
        Is the same as
            line = canvas.create_line(x0,y0,x1,y1)
        except in the former case methods like line.coords can be used as well as the old canvas methods e.g. canvas.coords(line) '''

    def __new__(self, parent, *args, **kw):
        self._shape = parent.create_line(*args, **kw)
        self._parent = parent
        return int.__new__(self, self._shape)

    def move(self, dx, dy):
        return self._parent.move(self, dx, dy)

    @property
    def coords(self):
        return self._parent.coords(self)

    @coords.setter
    def coords(self, *args):
        return self._parent.coords(self, *args)

    @property
    def center(self):
        co = self._parent.coords(self)
        w, h = co[2] - co[0], co[3] - co[1]
        return [co[0] + w / 2.0, co[1] + h / 2.0]

    def itemconfigure(self, cnf=None, **kw):
        return self._parent.itemconfigure(self, cnf, **kw)

    itemconfig = itemconfigure

    def delete(self):
        return self._parent.delete(self)


class CanvasRectangle(CanvasLine):
    def __new__(self, parent, *args, **kw):
        self._shape = parent.create_rectangle(*args, **kw)
        self._parent = parent
        return int.__new__(self, self._shape)


class CanvasText(CanvasLine):
    def __new__(self, parent, *args, **kw):
        self._shape = parent.create_text(*args, **kw)
        self._parent = parent
        return int.__new__(self, self._shape)


class Canvas(ReConfig, tkinter.Canvas):
    def __init__(self, parent, state='active', hovercolor='white', bg='grey40', highlightthickness=4,
                 highlightbackground='grey40', highlightcolor='turquoise3', **kwargs):
        tkinter.Canvas.__init__(self, parent, bg=bg, highlightthickness=highlightthickness,
                                highlightbackground=highlightbackground, highlightcolor=highlightcolor, **kwargs)
        ReConfig.__init__(self, kw='highlightbackground')
        self.gooey_kw = {'state': state, 'hovercolor': hovercolor}


class EdgeButton(ReConfig, tkinter.Frame):

    # Regular button within a frame - composite widget which allows buttons to have a highlight around them. used to make the Combobox.
    def __init__(self, parent, hovercolor='grey80', state='normal', highlightbackground='grey90', highlightthickness=4,
                 highlightcolor='turquoise3', bd=0, padx=3, pady=3, compound='right', **kwargs):
        tkinter.Frame.__init__(self, parent, highlightbackground=highlightbackground,
                               highlightthickness=highlightthickness, highlightcolor=highlightcolor)
        ReConfig.__init__(self, kw='highlightbackground')
        self.parent = parent
        self.gooey_kw = {'hovercolor': hovercolor}

        # Keywords in self.frame_kw apply changes to the frame when altered using configure method; other keywords affect the embedded button.
        self.frame_kw = ['highlightbackground', 'highlightthickness', 'highlightcolor', 'hovercolor']

        # Ensures button resizes to fill frame.
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Creating button. Since it is not the main widget, customizability is limited.
        # However, the button can be changed by calling methods like edgebutton._button.configure().
        self._button = Button(self, bd=bd, state=state, hovercolor='white', bg='white', activebackground='grey90',
                              padx=padx, pady=pady, compound=compound, **kwargs)
        self._button.grid(sticky='nswe')

    def configure(self, cnf=None, **kw):
        cnf = tkinter._cnfmerge((cnf, kw))

        # Filters out keywords in self.frame_kw and applies them to the frame.
        forframe = {}
        for key in cnf:
            if key in self.frame_kw:
                forframe[key] = cnf[key]
        if forframe:
            ReConfig.configure(self, cnf=forframe)

        # Applies remaining keywords to the button.
        cnf = {key: cnf[key] for key in cnf if not (key in self.frame_kw)}
        if cnf:
            ReConfig.configure(self._button, cnf=cnf)

    config = configure

    def cget(self, key):
        # If the key is in self.frame_kw, returns the associated value of the frame.
        # Otherwise returns that of the button.
        if key in self.frame_kw:
            return ReConfig.cget(self, key)
        return ReConfig.cget(self._button, key)

    __getitem__ = cget


class ButtonsMenu(Frame):
    # A menu-style composite widget made of a frame containing a number of buttons. Used to make the Combobox.
    def __init__(self, parent, values=[], highlightthickness=2, highlightbackground='grey80', **kwargs):
        self.frame_kw = ['highlightbackground', 'highlightthickness', 'bd', 'relief', 'width', 'height']
        Frame.__init__(self, parent, highlightthickness=highlightthickness, highlightbackground=highlightbackground)
        self.gooey_kw['values'] = values
        self.unbind('<Enter>')
        self.grid_propagate(False)
        self.columnconfigure(0, weight=1)

        self._buttons = []
        self._buttondict = {}
        for i, value in enumerate(self.gooey_kw['values']):
            self.rowconfigure(i, weight=1)
            button = Button(self, text=value, bg='grey95', hovercolor='grey90', anchor='w', **kwargs)
            self._buttons += [button]
            self._buttondict[value] = button
            button.grid(sticky='snew')

        root = self.winfo_toplevel()
        root.bind('<Button-1>', lambda e: self._close(e), add='+')

    def _close(self, e):
        if not e.widget in self._buttons:
            self.place_forget()

    def configure(self, cnf=None, **kw):
        cnf = tkinter._cnfmerge((cnf, kw))

        forframe = {}
        for key in cnf:
            if key in self.frame_kw:
                forframe[key] = cnf[key]
        if forframe:
            ReConfig.configure(self, cnf=forframe)

        cnf = {key: cnf[key] for key in cnf if not (key in self.frame_kw)}
        if cnf:
            for button in self._buttons:
                ReConfig.configure(button, cnf=cnf)

    config = configure

    def cget(self, key):
        if key in self.frame_kw:
            return ReConfig.cget(self, key)
        return ReConfig.cget(self._buttons[0], key)

    __getitem__ = cget


class Combobox(EdgeButton):
    class Menu_Set(object):

        # Wrapper class similar to Tkinter._setit. Applies changes to the Combobox based on which button is selected.
        def __init__(self, master, value, func=None):
            self.master = master
            self.value = value
            self.func = func

        def __call__(self):
            m = self.master

            # Resets currently selected button to have a bg of grey95 and hovercolor of grey90 as usual.
            if m.gooey_kw['value'] in m.gooey_kw['values']:
                m._menu._buttondict[m.gooey_kw['value']].config(bg='grey95', hovercolor='grey90')

            # Sets newly selected button to have a turqoise bg and darker turqoise hovercolor to highlight it.
            if self.value in m.gooey_kw['values']:
                m.after(2, lambda: m._menu._buttondict[self.value].config(bg='#80f5f5', hovercolor='#60e6e6'))
                m._menu._buttondict[self.value]._default_value = '#80f5f5'

                # Sets master.index to the index of the selected button for positioning of menu later.
                m.index = m.gooey_kw['values'].index(self.value)

            # Sets various resources and then hides the ButtonsMenu.
            m.gooey_kw['value'] = self.value
            m._button['text'] = self.value
            m._menu.place_forget()

            # Calls the attached function if it exists.
            if self.func:
                self.func()

    ''' The ComboBox is a composite widget intended to improve upon the OptionMenu, improving ease of use and customisability.
        It is modelled after a similar widget I saw in a Windows 10 menu.
        It is an EdgeButton which places a ButtonsMenu on top of itself when clicked.
    '''

    def __init__(self, parent, command=None, width=16, height=1, anchor='w', values=None, default=None, **kwargs):
        EdgeButton.__init__(self, parent, width=width, height=height, text=values[0], anchor=anchor,
                            command=self._pop_up, **kwargs)
        self.gooey_kw['command'] = command
        self.gooey_kw['values'] = values
        self.gooey_kw['default'] = default
        self.gooey_kw['value'] = values[0]

        # Instatiating the dropdown ButtonsMenu.
        self._menu = ButtonsMenu(self.winfo_toplevel(), values=values)
        self._update_menu()

        # Handling the case of a default value, for example 'please select', to appear before a selection is made.
        default = (self.gooey_kw['default'] if self.gooey_kw['default'] else self.gooey_kw['value'])
        self.index = None
        self.set(default)

    def get(self):
        return self.gooey_kw['value']

    def set(self, value):
        self.Menu_Set(self, value)()

    def _pop_up(self):
        root = self.winfo_toplevel()
        padx, pady = root['padx'], root['pady']

        # Code to handle placement of the ButtonsMenu so that it aligns above the EdgeButton.
        # TODO - menu should close when window is resized.
        pos = self.winfo_geometry()
        s, x, y = pos.split('+')
        w, h = (int(x) for x in s.split('x'))
        h -= 2 * self._menu['highlightthickness']

        x = self.winfo_rootx() - root.winfo_rootx()
        y = self.winfo_rooty() - root.winfo_rooty()

        index = (self.index if self.index is not None else 0)
        px, py = int(x) - padx, int(y) - pady - h * index

        self._menu['width'] = w
        self._menu['height'] = h * 3 + self._menu['highlightthickness'] * 2
        self.columnconfigure(0, weight=1)
        self._menu.place(relx=0, rely=0, x=px, y=py, anchor="nw")
        self._menu.lift()

    def _update_menu(self):

        # Sets padx and pady on the menu so that it matches the size of the EdgeButton.
        border = self['highlightthickness'] + self['bd']
        bdx, bdy = border + self['padx'], border + self['pady']
        menuborder = self._menu['highlightthickness'] + self._menu['bd']
        padx, pady = bdx - menuborder, bdy - menuborder

        self._menu.config(padx=padx, pady=pady, width=self['width'])

        # Configuring commands for each button in the ButtonsMenu.
        for i, button in enumerate(self._menu._buttons):
            button.config(command=self.Menu_Set(self, button['text'], self.gooey_kw['command']))

    def configure(self, cnf=None, **kw):
        cnf = tkinter._cnfmerge((cnf, kw))

        # Applies gooey keywords to self.gooey_kw.
        for key in cnf:
            if key in self.gooey_kw:
                self.gooey_kw[key] = cnf[key]

        # Filters out gooey keywords and applies the rest to Edgebutton.configure()
        cnf1 = {key: cnf[key] for key in cnf if not (key in self.gooey_kw)}
        EdgeButton.configure(self, cnf=cnf1)

        # Thge ButtonsMenu must be updated to avoid issues caused by changing these keywords.
        for key in ['highlightthickness', 'bd', 'padx', 'pady', 'width', 'command']:
            if key in cnf:
                self._update_menu()
                break

    config = configure


class Tooltip(ReConfig, tkinter.Toplevel):
    ''' The Tooltip is a Toplevel widget that follows the mouse upon mousover of widgets.
        It contains a label whose text can be changed to anything.
        It is created similarly to other widgets; for example
            button  = gooey.Button(root)
            button.grid()
            tooltip = gooey.Tooltip(button,text='tip')
        However, tooltip.grid() or other placement methods are not required as they are controlled from within the widget.'''

    def __init__(self, parent, text=None, delayin=400, delayout=100, offset=[1, 1], bd=0, highlightthickness=4,
                 highlightbackground='turquoise3', highlightcolor='turquoise3', pady=10, padx=10, **kwargs):
        tkinter.Toplevel.__init__(self, bd=bd, highlightthickness=highlightthickness,
                                  highlightbackground=highlightbackground, highlightcolor=highlightcolor, pady=pady,
                                  padx=padx, **kwargs)

        # Removes the windows border of the Toplevel widget.
        self.wm_overrideredirect(True)

        self.gooey_kw = {'delayin': delayin, 'delayout': delayout, 'offset': offset}

        # Instantiating embedded Label widget.
        self.label_kw = {'text': text, 'font': None, 'fg': None}
        self.label = Label(self, text=text)
        self.label.grid()

        # Establishing some parent attributes, so that the Tooltip can be referred to as parent.tooltip or parent['tooltip'].
        self.parent = parent
        self.parent.tooltip = self
        self.parent.gooey_kw['tooltip'] = self

        # Bindings to link Tooltip to entering and leaving parent widget.
        self.x, self.y = 0, 0
        self.parent.bind('<Enter>', lambda e: self._in(), add='+')
        self.parent.bind('<Leave>', lambda e: self._out(), add='+')

        self._testout()
        self._close()

    def _in(self):
        # Called on mouse entry into widget, and after a time of self['delayin'], calls self._open().
        self._lastcall = 'in'
        self.after(self.gooey_kw['delayin'], self._open)

    def _open(self):
        # Opens the Tooltip if self._lastcall is 'in'; i.e. self._out() has not been called.
        if self._lastcall == 'in':
            self._opened = True
            self.deiconify()
            self._position()

    def _out(self):
        # Called on mouse exit from widget. Calls self._close after a time of self['delayout'].
        self._lastcall = 'out'
        self.after(self.gooey_kw['delayout'], self._close)

    def _close(self):
        # If self._lastcall is out - if the mouse is outside the widget - withdraws the Tooltip.
        if self._lastcall == 'out':
            self._opened = False
            self.withdraw()

    def _position(self):
        # Places the tooltip on the screen, at an offset from the mouse determined by self['offset'].
        if self._opened:
            x, y = self.parent.winfo_pointerx(), self.parent.winfo_pointery()
            if self.x != x or self.y != y:
                self.geometry("+%s+%s" % (x + self.gooey_kw['offset'][0], y + self.gooey_kw['offset'][1]))
                self.x, self.y = x, y
            self.after(1, self._position)

    def grid(self, cnf={}, **kwargs):
        # Redefines pack, place and grid to stop their use.
        raise GooeyException(
            'Tooltip.grid(),Tooltip.pack() and Tooltip.place() are not supported. The tooltip is placed using internal methods automatically on parent widget mouseover.')

    pack = place = grid


class Spacer(tkinter.Frame):
    ''' A Frame which has a fixed size. This widget can be used to create whitespace between widgets to aid in GUI contruction.
        It is not recommended to use this widget as a container for others.'''

    def __init__(self, parent, **kwargs):
        self._check(kwargs)
        tkinter.Frame.__init__(self, parent, **kwargs)

        self.pack_propagate(False)
        self.grid_propagate(False)

    def _check(self, kwargs):
        # Blocks use of keywords other than width, height and bg.
        for kw in kwargs:
            if kw not in ['width', 'height', 'bg']:
                raise GooeyException('Spacer widget keywords are width, height and bg only.')

    def configure(self, cnf={}, **kwargs):
        cnf = tkinter._cnfmerge(cnf, kwargs)
        self._check(cnf)

        tkinter.Frame.configure(self, cnf)

    config = configure


class Scale(Canvas):
    '''Rebuilt scale widget is a canvas with a square which can be dragged across it.
       Some functionality, such as vertical orientation and a built-in label, is lost.
       However, the look of the widget is modernised.'''

    def __init__(self, parent, height=1, length=200, from_=0, to=100, highlightthickness=0, **kwargs):

        Canvas.__init__(self, parent, height=height, width=length, highlightthickness=highlightthickness)

        # Bindings

        self.bind('<Configure>', self.build)
        self.bind('<Motion>', self.motion)
        self.bind('<ButtonRelease-1>', self.motion)
        self.bind('<B1-Motion>', self.B1_motion)

        self.from_ = from_
        self.to = to

        self.val = from_
        self.on_knob = False

    def build(self, _):
        # Create the shapes on the canvas and set the value to self.val

        self.delete('all')

        self.h = self.winfo_height()
        self.w = self.winfo_width()
        self.s = 6
        self.d = self.h - self.s * 2
        self.r = self.d / 2.0

        self.line = CanvasLine(self, self.r + self.s, self.h / 2.0, self.w - self.r - self.s, self.h / 2.0, width=2,
                               fill='grey50')
        self.knob = CanvasRectangle(self, self.s, self.s, self.h - self.s, self.h - self.s, width=5, outline='grey80',
                                    fill='white')

        self.set(self.val)

    def motion(self, e):
        # colours the outline of the knob darker on mouseover, and sets on_knob.

        x, y = e.x, e.y
        knob = self.coords(self.knob)
        self.x = x

        if (knob[0] <= x and x <= knob[2]) and not self.on_knob:
            if knob[1] <= y and y <= knob[3]:
                self.on_knob = True
                self.itemconfig(self.knob, outline='grey70')

        elif (knob[0] > x or x > knob[2]) and self.on_knob:
            self.on_knob = False
            self.itemconfig(self.knob, outline='grey80')

        elif (knob[1] > y or y > knob[3]) and self.on_knob:
            self.on_knob = False
            self.itemconfig(self.knob, outline='grey80')

    def B1_motion(self, e):
        # Moves the knob along the canvas when B1 is held down

        dx = e.x - self.x
        self.x = e.x

        if self.on_knob:

            self.move(self.knob, dx, 0)
            knob = self.coords(self.knob)

            pos = (knob[0] + knob[2]) / 2.0

            # if the knob reaches the end of the line, it stops in place.

            if pos < self.r + self.s:
                self.coords(self.knob, self.s, knob[1], self.h - self.s, knob[3])

            elif pos > self.w - self.r - self.s:
                self.coords(self.knob, self.w - self.d - self.s, knob[1], self.w - self.s, knob[3])

    def get(self):

        # retrieve the value from the scale - distance along line divided by length of line

        try:

            l = self.w - self.d - self.s * 2

            knob = self.coords(self.knob)
            pos = (knob[0] + knob[2]) / 2.0 - self.r - self.s

            d = self.to - self.from_
            val = self.from_ + (pos / l) * d

            self.val = val

        except AttributeError:

            # if this fails (widget is not built yet) then self.val is returned
            pass

        return self.val

    def set(self, val):

        self.val = val

        try:
            w = self.w
            # try to find self.w
        except AttributeError:
            # if self.w does not exist, the widget is not yet built
            self.after(3, lambda: self.set(val))  # call self.est again later, when the widget is built
            return

        if val < min(self.from_, self.to) or val > max(self.from_, self.to):
            # if val not inside range throw an error

            raise ValueError('value must be inside scale range')

        l = self.w - self.d - self.s * 2
        d = self.to - self.from_
        pos = (val - self.from_) / float(d) * l + self.r + self.s

        # set knob to correct place

        self.coords(self.knob, pos - self.r, self.s, pos + self.r, self.h - self.s)


class Graph(Canvas):
    ''' A graphing tool which allows data to be plotted on various scales, including a different scale on the x and y axes.
        Panning, zooming and centering of the graph is handled by internal methods, and data can be added and removed dynamically.
        A Bezier curve spline can be created to pass through all points on the graph smoothly.
        TODO - support multiple datasets being plotted at once in different colours and with independant spline curves.'''

    def __init__(self, parent, labelx=None, labely=None, dragable=True, span='all', title=None, data=[], **kwargs):

        # gooey.Graph inherits from gooey.Canvas follows its style. Gooey's CanvasLine, CanvasRectangle and CanvasText classes can also be used with it.
        Canvas.__init__(self, parent, **kwargs)
        self.parent = parent
        self._inside = False

        self.gooey_kw['labelx'] = labelx
        self.gooey_kw['labely'] = labely
        self.gooey_kw['dragable'] = dragable
        self.gooey_kw['span'] = span
        self.gooey_kw['title'] = title
        self.gooey_kw['data'] = data

        self.bind('<Button-1>', self._startpan)
        self.bind('<B1-Motion>', self._pan)
        self.bind('<Motion>', self._track)
        self.bind('<Enter>', self._mousein, add='+')
        self.bind('<Leave>', self._mouseout, add='+')
        self.bind_all('<MouseWheel>', self._zoom)

        # Binds construction of graph to <Configure> event, so that self._build() is called on initial placement of the widget.
        self.bind('<Configure>', lambda e: self._build())

    def _build(self):
        # Resetting <Configure> event binding to call self._scale() rather than self._build().
        self.bind('<Configure>', lambda e: self._scale())

        self.w, self.h = w, h = self.winfo_width(), self.winfo_height()
        # self.sq is the regular measument unit of the graph, and is the distance between the edges of the Canvas and the x and y axes.
        self.sq = sq = 80.0
        # self._origin contains the co-ordinates of the origin of the Graph on the Canvas.
        self._origin = o = [w / 2.0, h / 2.0]

        # self._xpx and self._ypx are the number of pixels per background grid square, and are used to calculate placement of objects.
        self._xpx = self._ypx = self.sq
        # self._xst and self._yst are the scales of the x and y axes, and are also used to calculate placement of objects.
        self._xst = self._yst = 1.0

        # The moving axes move along with panning of the Graph. They intersect at self._origin.
        self._moving_x_axis = CanvasLine(self, o[0], sq, o[0], self.h - sq, width=2, fill='grey40', tag='moving_axis')
        self._moving_y_axis = CanvasLine(self, sq, o[1], self.w - sq, o[1], width=2, fill='grey40', tag='moving_axis')

        # The bounding boxes lie between the outer axes and the Canvas edge, and hide elements which make it outside the Graph area.
        self._bounding_boxes = [
            CanvasRectangle(self, 0, 0, sq, self.h, outline='white', fill='white', tag='bounding_box'),
            CanvasRectangle(self, 0, self.h - sq, w, h, outline='white', fill='white', tag='bounding_box'),
            CanvasRectangle(self, self.w - sq, 0, w, h, outline='white', fill='white', tag='bounding_box'),
            CanvasRectangle(self, 0, 0, self.w, sq, outline='white', fill='white', tag='bounding_box')]

        # These axes are fixed and have the labels and units moving along them.
        self._y_axis = CanvasLine(self, sq, sq, sq, self.h - sq + 1, width=3, fill='grey40', tag='fixed_axis')
        self._x_axis = CanvasLine(self, sq - 1, h - sq, w - sq, h - sq, width=3, fill='grey40', tag='fixed_axis')

        self._update_title()
        self._update()

    def graphx(self, value):
        # Takes an x-value on the graph in units and returns its position on the Canvas in pixels.
        try:
            value = float(value)
        except ValueError:
            raise GooeyException('Expected 1 number as argument; got ' + str(args))

        return self._origin[0] + value / self._xst * self._xpx

    def graphy(self, value):
        # Takes a y-value on the graph in units and returns its position on the Canvas in pixels.
        try:
            value = float(value)
        except ValueError:
            raise GooeyException('Expected 1 number as argument; got ' + str(args))

        return self._origin[1] - value / self._yst * self._ypx

    def graph_coords(self, *args):
        # Takes a point on the graph in units and returns its position on the Canvas in pixels.
        point = tkinter._flatten(args)

        try:
            point = [float(x) for x in point]
            assert len(point) == 2
        except (AssertionError, ValueError):
            raise GooeyException('Expected 2 numbers as arguments; got ' + str(args))

        return [self.graphx(point[0]), self.graphy(point[1])]

    def shift(self, *args):
        # Shifts the position of the origin over by a given number of units.
        delta = tkinter._flatten(args)
        delta = delta[0] / self._xst * self._xpx, delta[1] / self._yst * self._ypx

        self._origin[0] -= delta[0]
        self._origin[1] += delta[1]

        self._drawlines()

    def center(self):
        # Centers the Graph to show its entire contents if self['span'] is 'all'.
        # When span is a number the Graph will center to show this number of units back from the furthest x-value along.

        # If the Graph has not been placed in the window yet, wait 5 ms and call self.center again.
        if (self.winfo_width(), self.winfo_height()) == (1, 1):
            return self.after(5, self.center)

        data = self.gooey_kw['data']
        span = self.gooey_kw['span']

        # Creates an x_list of all x-values within the span as well as a y_list containing y-values within the span.
        if span and span != 'all':
            x_list = [x[0] for x in data if x[0] >= data[-1][0] - span]
            y_list = [x[1] for x in data if x[0] >= data[-1][0] - span]
            dist = span

            # If there are less than 2 elements in the lists, expand them to include the last 2 elements in self['data'].
            if len(x_list) < 2:
                x_list = [p[0] for p in data[-2:]]
                y_list = [p[1] for p in data[-2:]]
                dist = None

        else:
            x_list = [p[0] for p in data]
            y_list = [p[1] for p in data]
            dist = None

        # Code to correctly center the Graph.
        cx = (max(x_list) - min(x_list))
        cy = (max(y_list) - min(y_list))

        dist = dist if dist else cx
        pps = (self.w - self.sq * 3) * self._xst / dist

        self._xpx = pps

        yarea = self.h - self.sq * 3
        ydist = cy / self._yst * self._ypx
        ratio = ydist / yarea

        self._ypx /= ratio

        zx = max(x_list) - cx / 2.0
        zy = max(y_list) - cy / 2.0
        nx, ny = self.graph_coords(zx, zy)

        dx = self.w / 2.0 - nx
        dy = self.h / 2.0 - ny

        self._origin[0] += dx
        self._origin[1] += dy

        self._update()

    def _startpan(self, event):
        # Called at the start of a pan to hold variables to track the pan.
        self._panvar = {'x': event.x, 'y': event.y, 'dx': 0, 'dy': 0}

    def _pan(self, event):
        # Only called if self['dragable'] is True.
        if self.gooey_kw['dragable']:
            # Calculates dx and dy of the pan, and shifts the origin by these values.
            self._panvar['dx'] = dx = event.x - self._panvar['x']
            self._panvar['dy'] = dy = event.y - self._panvar['y']
            self._panvar['x'] = event.x
            self._panvar['y'] = event.y

            self._origin = [self._origin[0] + dx, self._origin[1] + dy]

            self._update()

    def _track(self, event):
        # Tracks the position of the mouse on the Graoh at all times.
        self._mouse_x, self._mouse_y = event.x, event.y

    def _mousein(self, event):
        self._inside = True

    def _mouseout(self, event):
        self._inside = False

    def _update_title(self):
        # Handles placement of the Graph's title as well as unit labels on the axes.
        self.delete('title')
        self.delete('unit')

        font = tkFont.Font(family='Segoe UI', size=14)
        font2 = tkFont.Font(family='Segoe UI', size=10)

        if self.gooey_kw['title']:
            CanvasText(self, self.w / 2.0, self.sq / 2.0, text=self.gooey_kw['title'], font=font, tag='title')
        if self.gooey_kw['labely']:
            CanvasText(self, self.sq, self.sq / 2.0, text=self.gooey_kw['labely'], font=font2, fill='grey40',
                       tag='unit')
        if self.gooey_kw['labelx']:
            CanvasText(self, self.w - self.sq / 2.0, self.h - self.sq, text=self.gooey_kw['labelx'], font=font2,
                       fill='grey40', tag='unit')

    def _zoom(self, event):
        # Zooms in or out, bound to the mousewheel. Also moves the origin by a certain amount to improve the feel of zooming.
        if self._inside and self.gooey_kw['dragable']:
            delta = event.delta / 1200.0
            self._xpx += self._xpx * delta
            self._ypx += self._ypx * delta

            distance = [self._mouse_x - self._origin[0], self._mouse_y - self._origin[1]]
            self._origin = [self._origin[0] - distance[0] * delta, self._origin[1] - distance[1] * delta]

            self._update()

    def _scale(self):
        # Scales objects on the Graph so that resizing the window resizes the Graph as well.
        prevw, prevh = self.w, self.h
        sq, w, h = _, self.w, self.h = self.sq, self.winfo_width(), self.winfo_height()
        ratio = self._origin[0] / prevw, self._origin[1] / prevh

        # Moves the origin according to the ratio of resizing if it is within the Graph area.
        if self._origin[0] > self.sq and self._origin[0] < self.w - self.sq:
            self._origin[0] = ratio[0] * self.w
        if self._origin[1] > self.sq and self._origin[1] < self.h - self.sq:
            self._origin[1] = ratio[1] * self.h

        # Moving the bounding boxes to ensure they lie between the Canvas edges and the fixed axes.
        boxes = self._bounding_boxes
        boxes[0].coords = (0, 0, sq, self.h)
        boxes[1].coords = (0, self.h - sq, self.w, self.h)
        boxes[2].coords = (self.w - sq, 0, self.w, self.h)
        boxes[3].coords = (0, 0, self.w, sq)

        # Moving the fixed axes to ensure they are exactly self.sq pixels from the edges of the Canvas.
        self._y_axis.coords = (sq, sq, sq, self.h - sq + 1)
        self._x_axis.coords = (sq - 1, self.h - sq, self.w - sq, self.h - sq)

        self._update()

    def _update(self):
        # Umbrella function to update Graph elements when changes are made to it.
        if not self.gooey_kw['dragable']:
            self.center()
        self._squaresize()
        self._drawlines()
        self._update_title()

    def _squaresize(self):
        # Changes the size of the background grid when the Graph is zoomed or scaled.
        while self.h // self._xpx > 30:
            self._xpx *= 10
            self._xst *= 10
        while self.h // self._xpx < 5:
            self._xpx /= 10
            self._xst /= 10
        while self.h // self._ypx > 30:
            self._ypx *= 10
            self._yst *= 10
        while self.h // self._ypx < 5:
            self._ypx /= 10
            self._yst /= 10

    def _controlpoints(self, x0, y0, x1, y1, x2, y2, t=0.25):
        # Calculates the position of control points for the spline curve around the point x1,y1
        d01 = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
        d12 = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5

        fa = t * d01 / (d01 + d12)
        fb = t - fa

        p1 = [x1 + fa * (x0 - x2)]
        p1 += [y1 + fa * (y0 - y2)]

        p2 = [x1 - fb * (x0 - x2)]
        p2 += [y1 - fb * (y0 - y2)]

        return [p1, p2]

    def _drawlines(self):
        # Main drawing function for the Graph.
        o, sq = self._origin, self.sq
        w, h = self.w, self.h = self.winfo_width(), self.winfo_height()

        # Clears old objects from the Graph.
        self.delete('background_line')
        self.delete('label')
        self.delete('point')
        self.delete('trendline')

        # Moves the moving x and y axes to cross at the origin.
        self._moving_x_axis.coords = (o[0], sq, o[0], self.h - sq)
        self._moving_y_axis.coords = (sq, o[1], self.w - sq, o[1])

        # Calculates the number of background gridlines before and after the origin in the x and y directions.
        x_lines_pre = int((self._origin[0] - sq) // self._xpx)
        x_lines_post = int((self.w - self._origin[0] - sq) // self._xpx)
        y_lines_pre = int((self._origin[1] - sq) // self._ypx)
        y_lines_post = int((self.h - self._origin[1] - sq) // self._ypx)

        x_lines = x_lines_pre + x_lines_post
        y_lines = y_lines_pre + y_lines_post
        x_labels = x_lines // 10 + 1
        y_labels = y_lines // 10 + 1

        # For each x-direction gridline, draws the gridline and places a label next to the fixed axis at regular intervals.
        for step in range(-x_lines_pre, x_lines_post + 1):
            m = self._origin[0] + self._xpx * step
            if step != 0:
                CanvasLine(self, m, sq, m, self.h - sq, fill='grey90', tag='background_line')
            if step % x_labels == 0:
                text = step * self._xst
                text = int(text) if text % 1 == 0 else text
                CanvasText(self, m, self.h - sq / 1.3, text=str(text), fill='grey80', tag='label')

        # For each y-direction gridline, draws the gridline and places a label next to the fixed axis at regular intervals.
        for step in range(-y_lines_pre, y_lines_post + 1):
            m = self._origin[1] + self._ypx * step
            if step != 0:
                CanvasLine(self, sq, m, self.w - sq, m, fill='grey90', tag='background_line')
            if step % y_labels == 0:
                text = -step * self._yst
                text = int(text) if text % 1 == 0 else text
                CanvasText(self, self.sq / 1.3, m, text=str(text)[:6], anchor='e', fill='grey80', tag='label')

        # Caluclates the position of each point in self['data'] and draws it if it is within the Grpah area.
        points = []
        for px, py in self.gooey_kw['data']:
            x, y = self.graph_coords(px, py)
            points += [[x, y]]
            if (x >= sq - 3 and x <= w - sq + 3) and (y >= sq - 3 and y <= h - sq + 3):
                CanvasRectangle(self, x - 3, y - 3, x + 3, y + 3, outline='turquoise3', width=3, fill='white',
                                tag='point')

        # Generates the path of the spline curve based on the points.
        path = []
        for x, p in enumerate(points):
            if x == 0 or x == len(points) - 1:
                path += [p, p]
            else:
                a, b = points[x - 1], points[x + 1]
                p1, p2 = self._controlpoints(*a + p + b)
                path += [p1, p, p2]

        # Draws the spline curve.
        for x, _ in enumerate(points[:-1]):
            n = x * 3
            m = n + 4
            CanvasLine(self, *path[n:m], fill='#bbffff', width=2, smooth=True, tag='trendline')

        # Configures elevation of various objects so they display correctly.
        self.tag_lower('trendline', 'bounding_box')
        self.tag_lower('point', 'bounding_box')
        self.tag_lower('background_line')

    def configure(self, cnf=None, **kw):
        cnf = tkinter._cnfmerge((cnf, kw))
        Canvas.configure(self, cnf)

        # Update the graph when certain kewords are changed to apply the changes.
        if 'data' in cnf:
            self._update()
        if 'title' in cnf or 'labelx' in cnf or 'labely' in cnf:
            self._update_title()

    config = configure


if __name__ == '__main__':

    class Test(Tk):
        ''' Mockup price tracking app for monitoring fluctuations in the cost of Oil, Silver and Gold.
            Shows off Combobox and Graph widgets as well as new behaviours of Button and Entry widgets.
            The revamped colour scheme is also apparent, modernising the TK/Python GUI.'''

        def __init__(self):
            Tk.__init__(self)
            self.config(padx=30, pady=30)

            self.columnconfigure(0, weight=1)
            self.rowconfigure(2, weight=1)

            self.datas = {
                'Gold': [(x, 50 / (x + 6.0) + 1.02 ** x + random.uniform(-1, 1) * random.uniform(-1, 1) * 5 + 10) for x
                         in range(30)],
                'Silver': [(x, 50 / (-1.0 - x) + 1.06 ** x + random.uniform(-1, 1) * random.uniform(-1, 1) * 12 + 50)
                           for x in range(35)],
                'Oil': [(x, 200.0 / (x + 1) + 10 * math.tanh(30 - x) + random.uniform(-1, 1) * random.uniform(-1,
                                                                                                              1) * 25 + 30)
                        for x in range(32)]}

            self.centering = True
            self.paused = False

            segoe_ui_18 = tkFont.Font(family='Segoe UI', size=18)
            segoe_ui_10 = tkFont.Font(family='Segoe UI', size=10)

            self.title1 = Label(self, text='Price Tracker', font=segoe_ui_18)
            self.title1.grid(sticky='w')
            Spacer(self, height=10).grid()

            self.graph = Graph(self, dragable=True, width=1000, height=500, data=self.datas['Gold'], title='Gold',
                               labelx='sec', labely='USD')
            self.graph.grid(sticky='nsew', row=2, rowspan=2)
            self.graph.bind('<B1-Motion>', self.motion, add='+')
            self.graph.bind_all('<MouseWheel>', self.motion, add='+')

            Spacer(self, width=20).grid(column=2)
            Spacer(self, width=2, bg='grey90').grid(column=3, row=0, rowspan=3, sticky='nswe')
            Spacer(self, width=20).grid(column=4)

            self.info_frame = Frame(self, highlightthickness=0)
            self.info_frame.grid(column=5, row=0, rowspan=5, sticky='n')

            self.title2 = Label(self.info_frame, text='Info', font=segoe_ui_18)
            self.title2.grid(sticky='sw')
            Spacer(self.info_frame, height=10).grid()

            self.show_label = Label(self.info_frame, text='  Show:       ', font=segoe_ui_10)
            self.show_label.grid(sticky='w', row=2)

            self.selector = Combobox(self.info_frame, values=['Gold', 'Silver', 'Oil'], font=segoe_ui_10,
                                     command=self.update_data)
            self.selector._menu['font'] = segoe_ui_10
            self.selector.grid(column=1, row=2, sticky='ew')
            Spacer(self.info_frame, height=10).grid()

            self.timespan_label = Label(self.info_frame, text='  Timespan:     ', font=segoe_ui_10)
            self.timespan_label.grid(sticky='w', row=4)

            self.entry = Entry(self.info_frame, font=segoe_ui_10)
            self.entry.grid(column=1, row=4, sticky='ew')
            self.entry.insert(0, 'all')
            self.entry.bind('<Return>', lambda e: self.graph_center())
            Spacer(self.info_frame, height=10).grid()

            self.centerbutton = Button(self.info_frame, text='Center', height=2, font=segoe_ui_10,
                                       command=self.graph_center)
            self.centerbutton.grid(columnspan=2, sticky='nsew')
            Spacer(self.info_frame, height=10).grid()

            self.pausebutton = Button(self.info_frame, text='Pause', height=2, font=segoe_ui_10, command=self.pause)
            self.pausebutton.grid(columnspan=2, sticky='nsew')
            Spacer(self.info_frame, height=10).grid()

            self.stats = Label(self.info_frame, text='Stats', font=segoe_ui_18)
            self.stats.grid(sticky='w')
            Spacer(self.info_frame, height=10).grid()

            self.goldlabel = Label(self.info_frame, text='  Gold', font=segoe_ui_10)
            self.goldlabel.grid(sticky='w')
            Spacer(self.info_frame, height=10).grid()
            self.silverlabel = Label(self.info_frame, text='  Silver', font=segoe_ui_10)
            self.silverlabel.grid(sticky='w')
            Spacer(self.info_frame, height=10).grid()
            self.oillabel = Label(self.info_frame, text='  Oil', font=segoe_ui_10)
            self.oillabel.grid(sticky='w')
            Spacer(self.info_frame, height=10).grid()

            bold_segoe_ui_10 = tkFont.Font(family='Segoe UI', size=10, weight='bold')

            self.goldstat = Label(self.info_frame, font=bold_segoe_ui_10)
            self.goldstat.grid(sticky='e', column=1, row=12)
            Spacer(self.info_frame, height=10).grid()
            self.silverstat = Label(self.info_frame, font=bold_segoe_ui_10)
            self.silverstat.grid(sticky='e', column=1, row=14)
            Spacer(self.info_frame, height=10).grid()
            self.oilstat = Label(self.info_frame, font=bold_segoe_ui_10)
            self.oilstat.grid(sticky='e', column=1, row=16)
            Spacer(self.info_frame, height=10).grid()

            self.after(150, self.grow_data)

            self.mainloop()

        def pause(self):
            if self.paused:
                self.pausebutton['text'] = 'Pause'
            else:
                self.pausebutton['text'] = 'Unpause'
            self.paused = not self.paused

        def motion(self, _):
            self.centering = False

        def graph_center(self):
            self.centering = True
            self.update_span()

        def colour(self, val):
            if val < -1:
                return 'firebrick1'
            elif val > 1:
                return 'chartreuse2'
            else:
                return 'DeepSkyBlue2'

        def update_stats(self):
            for name, label in [('Gold', self.goldstat), ('Silver', self.silverstat), ('Oil', self.oilstat)]:
                data = self.datas[name]
                val = data[-1][1] - data[-2][1]
                label['text'] = str(val)[:6]
                label['fg'] = self.colour(val)

        def update_span(self):
            val = self.entry.get()
            if val == 'all':
                self.graph['span'] = val
            else:
                self.graph['span'] = float(val)
            self.graph.center()

        def update_data(self):
            self.graph['data'] = self.datas[self.selector.get()]
            self.graph['title'] = self.selector.get()
            self.graph_center()

        def grow_data(self):
            if not self.paused:
                for key in self.datas:
                    data = self.datas[key]
                    newdata = [[data[-1][0] + 1 + random.uniform(-0.3, 0.3), data[-1][1] + random.uniform(-3, 3)]]
                    data += newdata
                    self.datas[key] = data

                self.graph['data'] = self.datas[self.selector.get()]
                self.update_stats()
                if self.centering:
                    self.graph.center()
            self.after(1500, self.grow_data)


    Test()
