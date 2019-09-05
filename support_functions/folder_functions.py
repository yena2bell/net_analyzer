import os

def folder_making(s_address):
    """
    sub function of 'directory_making' function
    """
    if os.path.isdir(s_address):
        print(s_address+" folder exists")
        return
    else:
        s_root, s_folder = os.path.split(s_address)
        if not s_folder:
            print("error!!! maybe you are using wrong drive address")
        folder_making(s_root)
        os.mkdir(os.path.join(s_root, s_folder))
        print(s_address+" folder does not exist. so created it")
        return

def directory_making(s_address):
    """
    check if the folder of s_address exists.
    if not exists, then make that folder.
    if s_address is the address of file (not folder),
    then check the existence of folder of that file.
    and make that folder (if not exists)
    """
    if os.path.exists(s_address):
        print(s_address+" folder (or file) exists")
        return
    s_address, s_ext = os.path.splitext(s_address)
    if s_ext:
        s_address = os.path.split(s_address)[0]
        if os.path.isdir(s_address):
            print(s_address+" folder exists")
            return
    
    folder_making(s_address)

    return

    
    
