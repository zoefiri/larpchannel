from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from random import seed, choice
import time
from os import remove
from os import path

def get_rand_card():
    if path.exists('card.png'):
        remove('card.png')

    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    file_list = drive.ListFile({'q': "'16bhwbOOTIxeVPqTnJHOf6wjS0oozbfIY' in parents and trashed=false"}).GetList()
    seed(time.time())
    rand_card = choice(file_list)
    rand_card.GetContentFile('card.png')


