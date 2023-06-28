## Renamer Scipt ##

import maya.cmds as cmds

class Renamer():
    

    def __init__(self):##Runs automatically, UI interface
        
        window_name = "renamerWindow"
        window_title = "renamer"
        
        #if instance of window already open, close instance and reopen
        if cmds.window(window_name, q=True, exists =True):
            cmds.deleteUI(window_name)
            
        my_window = cmds.window(window_name, title = window_title)
        
        main_layout = cmds.columnLayout(adj =True)
        
        self.find_box = cmds.textFieldButtonGrp(label ="Find", text ="", adj= 2,  buttonLabel = "Select", bc=self.find_matches, cw = [1,50])
        self.replace_box = cmds.textFieldButtonGrp(label ="Replace", text ="", adj= 2,  buttonLabel = "Replace", bc = self.replace, cw = [1,50])
        self.prefix_box = cmds.textFieldButtonGrp(label ="Prefix", text ="", adj= 2,  buttonLabel = "Add", bc= self.add_prefix, cw = [1,50])
        self.suffix_box = cmds.textFieldButtonGrp(label ="Suffix", text ="", adj= 2,  buttonLabel = "Add", bc =self.add_suffix,  cw = [1,50])
        
        cmds.showWindow(my_window)
        
    def find_matches(self):##find strings entered
        find_string = cmds.textFieldButtonGrp(self.find_box, q=True,text =True)
        matches =cmds.ls("*"+ find_string +"*", type = "transform")
        if matches:
            cmds.select(matches, r=True)
        else:
            cmds.select(cl=True)
            
    def add_prefix(self):# Add prefix to selected string
        prefix = cmds.textFieldButtonGrp(self.prefix_box, q=True, text=True)
        selection =cmds.ls(sl=True)
        for sel in selection:
            new_name = prefix +"_"+sel
            cmds.rename(sel,new_name)
            
    def add_suffix(self):# Add suffix to selected string
        suffix = cmds.textFieldButtonGrp(self.suffix_box, q=True, text=True)
        selection =cmds.ls(sl=True)
        for sel in selection:
            new_name = sel + "_" + suffix 
            cmds.rename(sel,new_name)
            
    def replace(self):# replace selected string with new string
        find_string = cmds.textFieldButtonGrp(self.find_box, q=True,text =True)
        replace_string = cmds.textFieldButtonGrp(self.replace_box, q=True,text =True)
       
        selection =cmds.ls(sl=True)
        for sel in selection:
            new_name = sel.replace(find_string, replace_string)
            
            cmds.rename(sel, new_name)
Renamer()