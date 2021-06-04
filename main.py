

from config import TOKEN
from config import users_t as users
import config as config
import ftplib
import multiprocessing
import seafileapi

import asyncio
import time
import datetime

import io

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor



bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
message_last = 'test'
t_marker = False

@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    if message.from_user.id in users:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["/state", "/now"]
        keyboard.add(*buttons)
        await message.reply(text = 'Write /state or /now', reply_markup=keyboard)
    else:
        await message.reply(text = 'Бот только для избранных' + str(message.from_user.id))

@dp.message_handler(commands="state")
async def State(message: types.Message):
    if message.from_user.id in users:
        global message_last
        await message.reply(text = message_last)
    else:
        await message.reply(text = 'Бот только для избранных')

@dp.message_handler(commands="now")
async def State(message: types.Message):
    if message.from_user.id in users:
        global t_marker
        t_marker = True
        await message.reply(text = "Начинаю поиск файлов")
    else:
        await message.reply(text = 'Бот только для избранных')
            
@dp.message_handler()
async def echo_message(message: types.Message):
    if message.from_user.id in users:
        await message.reply(text = 'Write /start or /state or /now')
    else:
        await message.reply(text = 'Бот только для избранных')


class MySea:
    def __init__(self):
        import config
        self.host = config.host_sea
        self.user = config.user_sea
        self.passwd = config.passwn_sea
        self.repo_id =config.repo_id_sea
        self.path = '/data/'
        self.ftp = MyFtp()
        self.p = 'Downloading'

    def connect(self):
        self.client = seafileapi.connect(self.host, self.user, self.passwd)
        self.repo = self.client.repos.get_repo(self.repo_id)
        self.seafdir = self.repo.get_dir(self.path)

    def get_sea_files(self):
        self.lst = self.seafdir.ls(force_refresh=True)
        self.file_on_server = [dirent.name for dirent in self.lst]
        return self.file_on_server

    def upload_file(self, curfile):
        self.connect()
        #with open(os.path.join(dir_pc, f), 'rb') as fp:
            #seafdir.upload(fp, curfile['filename'])
        self.ftp.connect()
        self.ftp.login()
        self.ftp.cwd(curfile['remote_path'])
        #with open(host_file, 'wb') as local_file:
        file_data = io.BytesIO()
        self.ftp.retrbinary('RETR %s' % curfile['filename'], lambda data: file_data.write(data))
        file_data.seek(0)
        self.seafdir.upload(file_data.read(), curfile['filename'])

    def test_upload_file(self, curfile):
        self.connect()
        #with open(os.path.join(dir_pc, f), 'rb') as fp:
            #seafdir.upload(fp, curfile['filename'])
        self.ftp.connect()
        self.ftp.login()
        self.ftp.cwd(curfile['remote_path'])
        #with open(host_file, 'wb') as local_file:
    
        time.sleep(2)



class Animation:
    """Класс для включения анимации и сообщений в командной строке"""
    def __init__(self, process):
        self.process = process
        self.filename = ''
        self.chars = "/—\|"
        self.fail = False
        self.count = 0

    async def get_value_to_animation(self):
        while self.process.is_alive():
            if self.process.marker.value == 1:
                await self.search()
            elif self.process.marker.value == 2:
                await self.downloading()
            elif self.process.marker.value == -1:
                self.fail = True
            await asyncio.sleep(0.1)
    
    async def search(self):
        import sys, time, datetime
        cur_time_s = datetime.datetime.now()
        new_time_s = cur_time_s + datetime.timedelta(minutes = 10)
        while self.process.marker.value == 1 and cur_time_s <= new_time_s:
            for char in self.chars:
                sys.stdout.write('\r'+'Searching file '+char + ' '*100)
                await asyncio.sleep(.2)
                sys.stdout.flush()
        sys.stdout.write('\r')
        sys.stdout.flush()
        if cur_time_s >= new_time_s:
            self.process.terminate()
            sys.stdout.write('\rFail to find file' + ' '*100)
            sys.stdout.flush()
            self.fail = True

    async def downloading(self):
        import sys, time, datetime
        global message_last
        cur_time = datetime.datetime.now()
        start_time = datetime.datetime.now()
        new_time = cur_time + datetime.timedelta(hours=1)
        message_last = 'Скачивание файла №' + str(self.count + 1) + ' началось в' + start_time.strftime(' -- %d/%m/%Y  %H:%M:%S')

        while self.process.marker.value == 2 and cur_time <= new_time:
            for char in self.chars:
                sys.stdout.write('\r'+'Downloading file '+char + ' Start at ' + start_time.strftime(' -- %d/%m/%Y  %H:%M:%S') + '              ')
                await asyncio.sleep(.2)
                sys.stdout.flush()
                cur_time = datetime.datetime.now()
        sys.stdout.write('\r')
        if cur_time >= new_time:
            self.process.terminate()
            sys.stdout.write('\rFail to download file' + ' '*100)
            sys.stdout.flush()
            self.fail = True
        else:
            sys.stdout.write('\rfinished download '+' '*100+'\n')
            sys.stdout.flush()
            self.count += 1
    
class SearchProcess(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.ftp = None
        self.marker = multiprocessing.Value('i', 1)
        self.list_file = None

    def connect(self):
        """Метод для соединения с ftp"""
        self.ftp = MyFtp()
        self.ftp.connect()
        self.ftp.login()
        self.ftp.cwd('/')
        self.sea_server.connect()


    def run(self):
        """Запуск потока скачивания"""
        import time, sys, os, datetime
        try:
            self.sea_server = MySea()
            self.sea_server.connect()
            self.file_on_server = self.sea_server.get_sea_files()
            self.connect()
            self.list_file = FileList(self.file_on_server, self.sea_server.repo, self.sea_server.path)
            self.list_file.connect_ftp()
            self.list_file.get_list()
            num_files = self.list_file.len()

            for i in range(self.list_file.len()):
                self.connect()
                curfile = self.list_file.get_next_file()
                sys.stdout.write('\rFile ' + curfile['filename'] + '\n')
                sys.stdout.flush()
                self.marker.value = 2
                self.ftp.cwd(curfile['remote_path'])
                try:
                    self.sea_server.upload_file(curfile)
                except:
                    sys.stdout.write('\rFail to downloading File: ' + curfile['filename'] + '\n')
                    sys.stdout.flush()
                    time.sleep(2)

                self.marker.value = 0
                time.sleep(5)
            self.ftp.quit()
            self.marker.value = 0
            time.sleep(3)
            sys.stdout.write('\r'+datetime.datetime.now().strftime(' -- %d/%m/%Y  %H:%M:%S') + '\n')
            sys.stdout.write('Скачано новых файлов: ' + str(num_files))
        except:
            print('Ошибка при работе с сервером')
            self.marker.value = -1
            time.sleep(60)

class MyFtp (ftplib.FTP):
    """Класс переопределяет стандартный, чтобы задать все параметры соединение в одном месте"""
    def __init__(self):
        import config
        self.host = config.host
        self.user = config.user
        self.passwd = config.passwd
        self.ftp_path = config.ftp_path
        self.timeout = 1800
        super(MyFtp, self).__init__()

    def connect(self):
        super(MyFtp, self).connect(self.host, timeout=self.timeout)

    def login(self):
        super(MyFtp, self).login(user=self.user, passwd=self.passwd)

    def dirpath(self):
        super(MyFtp, self).cwd(self.ftp_path)

    def quit(self):
        super(MyFtp,self).quit()

class FileList:
    """Класс для работы со списком загружаемых файлов"""
    def __init__(self, file_on_server, sea_repo, sea_path):
        self.repo = sea_repo
        self.path = sea_path
        self.ftp = None
        self.downloaded = file_on_server
        self.file_list = []

    def connect_ftp(self):
        import sys
        self.ftp = MyFtp()
        self.ftp.connect()
        self.ftp.login()
        self.ftp.dirpath()
        self.ftp.__class__.encoding = sys.getfilesystemencoding()

    def get_list(self):
        """Метод для получения списка всех файлов с ftp-сервера."""
        import os
        for dirname in self.ftp.nlst():
            try:
                self.ftp.size(dirname)
                if not self.downloaded.count(dirname):
                    entry_file_list = {}
                    entry_file_list['remote_path'] = self.ftp.pwd()  #путь до файла
                    entry_file_list['filename'] = dirname  #имя файла
                    self.file_list.append(entry_file_list)
                else:
                    seafile = self.repo.get_file(self.path + dirname)
                    if self.ftp.size(dirname) != seafile.size:
                        print(dirname, 'Отличается по размеру, я бы его удалил')
                        seafile.moveTo(self.path + 'br/')
                        entry_file_list = {}
                        entry_file_list['remote_path'] = self.ftp.pwd()  #путь до файла
                        entry_file_list['filename'] = dirname  #имя файла
                        self.file_list.append(entry_file_list)
            except:
                path = os.path.join(self.ftp.pwd(), dirname)
                self.ftp.cwd(dirname)
                self.get_list()
                self.ftp.cwd('..')

    def get_next_file(self):
        return self.file_list.pop()

    def len(self):
        return len(self.file_list)

async def main():
    import os, sys
    import datetime
    import time

    global message_last
    global t_marker

    now = datetime.datetime.today().strftime("%Y%m%d")
    cur_time = datetime.datetime.now()
    new_time = cur_time + datetime.timedelta(hours=8)
    new_time = cur_time

    while True:
        try:
            if (datetime.datetime.now() > new_time) or t_marker:
                t_marker = False
                message_last = 'Поиск новых файлов' + datetime.datetime.now().strftime(' -- %d/%m/%Y  %H:%M:%S')
                for user_i in users:
                    await bot.send_message(chat_id=user_i, text = message_last)
                p = SearchProcess()
                anim = Animation(p)
                p.start()
                task_1 = asyncio.create_task(anim.get_value_to_animation())
                await task_1
                p.join()
                cur_time = datetime.datetime.now()
                if anim.fail:
                    print('Ошибка при работе с сервером')
                    new_time = cur_time
                    for user_i in users:
                        await bot.send_message(chat_id=user_i, text = 'Произошла ошибка при скачавании, попробую ещё раз' + datetime.datetime.now().strftime('-- %d/%m/%Y  %H:%M:%S'))
                else:

                    new_time = cur_time + datetime.timedelta(hours=8)
                    for user_i in users:
                        if anim.count != 0:
                            await bot.send_message(chat_id=user_i, text = 'Скачано новых файлов: '+str(anim.count) + datetime.datetime.now().strftime(' -- %d/%m/%Y  %H:%M:%S'))
                        else:
                            await bot.send_message(chat_id=user_i, text = 'Новых файлов не найдено' + datetime.datetime.now().strftime(' -- %d/%m/%Y  %H:%M:%S'))
                p = None
                anim = None
                print('\n')
                t_marker = False

            num_time = (new_time - datetime.datetime.now()).seconds
            message_last = 'Начну снова искать через ' + '{}:{}:{}'.format(num_time//3600, (num_time%3600)//60, num_time%60)
            #sys.stdout.write('\rStart after ' + '{:s[0:8]}'.format(str(new_time - datetime.datetime.now()))+ '         ')
            sys.stdout.write('\rStart after ' + '{}:{}:{}'.format(num_time//3600, (num_time%3600)//60, num_time%60) + ' '*50)
            await asyncio.sleep(0.1)
            sys.stdout.flush()
        except:
            print('Проблемы с соединением')
            for user_i in users:
                await bot.send_message(chat_id=user_i, text = 'Проблемы с соединением, пойду посплю минутку ' + datetime.datetime.now().strftime('-- %d/%m/%Y  %H:%M:%S'))
            await asyncio.sleep(60)



if __name__ == "__main__":
    host = config.host
    user = config.user
    passwd = config.passwd
    ftp_path = config.ftp_path
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    executor.start_polling(dp, skip_updates=True)

    #main()