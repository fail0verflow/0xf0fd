#!/usr/bin/python

################ PM hack #########################
import sys
gui_instance = None

def dbghook(type, value, tb):
    import traceback, pdb

    if gui_instance:
        gui_instance.except_shutdown()
    
    traceback.print_exception(type, value, tb)

    print
    pdb.pm()
#sys.excepthook = dbghook
############### END PM HACK ######################



import traceback
import sys
from idis.datastore import DataStore
import idis.tools

gui_instance = None

# HACK - differentiate gui types
DEFAULT_GUI_NAME = "qt"

def getGuiClass(gui_args):
    if gui_args:
        try:
            gui_name = gui_args[1]
        except IndexError:
            print "Error: -g flag needs argument, using QT gui"
            gui_name = DEFAULT_GUI_NAME
    else:
        gui_name = DEFAULT_GUI_NAME

    guis = {
        "qt": ("gui.qtgui", "gui.qtgui.QTGui"),
        "curses": ("gui.curses_gui", "gui.curses_gui.CursesGui")
        }

    if not gui_name in guis:
        print "Invalid gui name %s. Valid names are: %s" % (gui_name, " ".join(guis.keys()))
        return None

    import_name, gui_clsname = guis[gui_name]
    gui = __import__(import_name)
    return eval(gui_clsname)

# Handle args with optionparser
def main(args):
    try:
        gui_index = args.index("-g")
        gui_args = args[gui_index:gui_index+2]
        args = args[:gui_index] + args[gui_index+2:]

    except ValueError:
        gui_args = []


    gui_class = getGuiClass(gui_args)
    if not gui_class:
        return

    filenames = args

    global gui_instance
    gui_instance = gui_class()


    # Run the gui
    gui_instance.startup()
    gui_instance.mainloop(filenames)
    gui_instance.shutdown()
        
if __name__ == '__main__':
    main(sys.argv[1:])
