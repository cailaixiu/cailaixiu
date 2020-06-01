#!/usr/bin/env python
import PySimpleGUI as sg
import io, os
import codecs
import requests
import json
import webbrowser
from uuid import getnode as get_mac
import pyautogui
import configparser
import psutil
import tkinter as tk
import platform
import base64
from peewee import *
import qrcode

db = SqliteDatabase('clx.db')
class Ticket(Model):
  tid = IntegerField(unique=True)
  body = TextField(default='')
  ack = TextField(default='')
  is_fixed = BooleanField(default=False)
  is_confirmed = BooleanField(default=False)
  at = CharField(default='')
  rat = CharField(default='')
  class Meta:
    database = db 

db.connect()
db.create_tables([Ticket])

root = tk.Tk()
max_width = root.winfo_screenwidth() - 200
root.destroy()
del root

config = configparser.ConfigParser()
try:
  config.read('config.ini')
  host = 'http://' + config['MAIN']['local_server']
except Exception as e:
  sg.popup('配置文件有误！')
  exit(1)

try:
  svmem = psutil.virtual_memory()
  mem = round(svmem.total/(1024*1024*1024))
  cpus = psutil.cpu_count(logical=False)
  payload = {'mac': get_mac(), 'sysrel': platform.system()+platform.release(),'mem': mem, 'cpus': cpus }
  r = requests.post(host+'/api/connect', data = payload, timeout=1.5).json()
except Exception as e:
  pass

def Launcher():
  sg.theme('DarkAmber')
  contact = ''
  cell = ''
  layout = [  [sg.Text('IT', size=(2,1), justification='center', auto_size_text=True, text_color='white'), 
            sg.Button('报修', key='-HELP-', focus=False, size=(4,1))] ]
  window = sg.Window('才来修', layout,
                     location=(max_width,100),
                     no_titlebar=True,
                     grab_anywhere=True,
                     keep_on_top=True,
                     element_padding=(0, 0),
                     margins=(0, 0))
  win2_active=False
  counter = 0
  while True:
    event, values = window.read(timeout=500)
    counter += 1

    to_be_fixed = (Ticket.select()
                      .where(Ticket.is_fixed == False)
                      .count())
    if to_be_fixed > 0 and counter % 10 == 0:
      try:
        r = requests.get(host+'/poll/'+str(get_mac()), timeout=0.5).json()
        for x in r:
          Ticket.update(is_fixed=True, ack= x['ack'], rat=x['rat']).where(Ticket.tid == x['_id']).execute()
      except Exception as e:
        pass

    to_be_confirmed = (Ticket.select()
                      .where((Ticket.is_confirmed == False) & (Ticket.is_fixed == True))
                      .count())

    if to_be_confirmed > 0:
      if (counter % 2 == 0):    
        window['-HELP-'].update(button_color=(sg.theme_text_color(),sg.theme_element_background_color()))
      else:
        window['-HELP-'].update(button_color=('black','orange'))

    if event is None:
      break
    if event == '-HELP-' and not win2_active:
      win2_active = True

      if to_be_confirmed > 0:
        row = Ticket.get(Ticket.is_confirmed == False, Ticket.is_fixed == True)
        layout_ask = [[sg.Text(row.body, text_color='white', pad=(5,10))],
                      [sg.Text('时间：'+row.at, text_color='silver')]]
        layout_ack = [[sg.Text(row.ack, text_color='white', pad=(5,10))],
                      [sg.Text('时间：'+row.rat, text_color='silver')]]
        layout2 = [[sg.Frame('报修问题', layout_ask)],
                   [sg.Frame('回复内容', layout_ack)],
                   [sg.Button('确认', bind_return_key=True, font=('Verdana', 16))]]
        win2 = sg.Window('回复确认', layout2)
        while True:
          ev2, vals2 = win2.Read()
          if ev2 is None or ev2 == '确认':
            Ticket.update(is_confirmed= True).where(Ticket.tid == row.tid).execute()
            win2.close()
            win2_active = False
            break

      else:
        img = pyautogui.screenshot()
        img_bytes = io.BytesIO()
        try:
          img.save(img_bytes, format='PNG')
          base64_data = codecs.encode(img_bytes.getvalue(), 'base64')
          base64_text = codecs.decode(base64_data, 'ascii')
        except Exception as e:
          base64_text = ''
        
        layout2 = [[sg.Text('问题描述')],
                   [sg.In(key='-ASK-')],
                   [sg.Text('联系人姓名', text_color='white')], 
                   [sg.In(contact, key='-CONTACT-')],
                   [sg.Text('联系人手机', text_color='white')], 
                   [sg.In(cell, key='-CELL-')],
                   [sg.Checkbox('当前页自动截屏', key='-SCRN-', default=True),sg.Checkbox('手机跟踪进度', key='-TRACK-', default=False)],
                   [sg.Button('提交', bind_return_key=True)]]

        win2 = sg.Window('报修内容', layout2, font=('Verdana', 16))
        while True:
          ev2, vals2 = win2.Read()
          if ev2 is None:
            win2.close()
            win2_active = False
            break
          if ev2 == '提交':
            ask = vals2['-ASK-'].strip()
            if len(ask) == 0:
              sg.popup('问题不能为空')
            elif len(ask) > 100:
              sg.popup('问题不需太长')
            else:
              track = 1 if vals2['-TRACK-'] else 0              
              contact = vals2['-CONTACT-'].strip()
              cell = vals2['-CELL-'].strip()
              if  vals2['-SCRN-'] is False:
                base64_text = ''

              payload = {'img': base64_text, 'ask': ask, 'mac': get_mac(), 'track':track, 'contact': contact, 'cell': cell}

              try:
                r = requests.post(host+'/api/help', data=payload, timeout=1.5).json()
                if (r['msg'] == '成功'):
                  Ticket.create(tid=r['_id'], body=ask, at=r['at'])
                  
                  url = "https://cailaixiu.com/v/"+r['nid']+"/"+r['tid']+"/"+r['key']+"/"+ask
                  qr_img = qrcode.make(url)
                  out = qr_img.resize((160,160))
                  qr_img_bytes = io.BytesIO()
                  out.save(qr_img_bytes, format='PNG')
                  qr_data = codecs.encode(qr_img_bytes.getvalue(), 'base64')

                  if  vals2['-TRACK-'] is False:
                    sg.popup_auto_close('报修成功')
                  else:
                    layout3 = [[sg.Text('请手机扫码，跟踪报修状态')],
                      [sg.Image(data=qr_data)],
                      [sg.Button('关闭',bind_return_key=True,font=('Verdana', 16))]]
                    sg.Window('报修成功', layout3).read(close=True)
                else:
                  sg.popup('报修失败！原因为'+r['msg'])

                win2.close()
                win2_active = False
              except Exception as e:
                sg.popup('服务不可用，请稍后再试！')      
  window.close()

if __name__ == '__main__':
  Launcher()
