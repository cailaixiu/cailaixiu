#!/usr/bin/env python
import PySimpleGUI as sg
import io, os
import codecs
import requests
import json
import webbrowser
from uuid import getnode as get_mac
import pyautogui
import qrcode
import configparser
import psutil
import tkinter as tk
import platform

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
  print(e)
  pass

def Launcher():
  sg.theme('DarkAmber')
  sg.set_options(element_padding=(0, 0),auto_size_buttons=False)
  layout = [[sg.In(size=(8, 0), key='-ASK-',font=("Verdana", 12)),
             sg.Button('报修', size=(4,0), pad=((2,0),0), bind_return_key=True) ]]

  window = sg.Window('才来修', layout,
                     location=(max_width,20),
                     no_titlebar=True,
                     grab_anywhere=True,
                     keep_on_top=True,
                     margins=(3, 2))
  win2_active=False
  while True:
    event, values = window.read()    
    if event is None:
      break
    if event == '报修' and not win2_active:
      img = pyautogui.screenshot()
      img_bytes = io.BytesIO()
      try:
        img.save(img_bytes, format='PNG')
        base64_data = codecs.encode(img_bytes.getvalue(), 'base64')
        base64_text = codecs.decode(base64_data, 'ascii')
      except Exception as e:
        base64_text = ''

      ask_txt = values['-ASK-'].strip()
      if len(ask_txt) == 0:
        url = host+'/pcs/'+str(get_mac())+'/tickets'
        webbrowser.open(url)
      elif len(ask_txt) > 100:
        sg.Popup('问题不必太长！')
      else: 
        try:
          payload = {'img': base64_text, 'ask': ask_txt, 'mac': get_mac()}
          r = requests.post(host+'/api/help', data = payload, timeout=1.5).json()
          window['-ASK-']('')

          url = "https://cailaixiu.com/v1/"+r['net']+"/"+r['loc']+"-"+r['ext']+"/"+r['tid']+"/"+r['key']+"/"+ask_txt
          qr_img = qrcode.make(url)
          out = qr_img.resize((160,160))
          qr_img_bytes = io.BytesIO()
          out.save(qr_img_bytes, format='PNG')
          qr_data = codecs.encode(qr_img_bytes.getvalue(), 'base64')

          win2_active = True
          window.Hide()
          layout2 = [[sg.Text(ask_txt, font=("Helvetica", 16))],
                     [sg.Text('改进型问题，可选扫码上报',text_color='white')],
                     [sg.Image(data=qr_data)],                     
                     [sg.Button('关闭', bind_return_key=True)]]

          win2 = sg.Window('提交成功', layout2)
          while True:
            ev2, vals2 = win2.Read()
            if ev2 is None or ev2 == '关闭':
              win2.close()
              win2_active = False
              window.UnHide()
              break
        except Exception as e:
          print(e)
          sg.Popup('服务器不可用，请稍后报修！')
  window.close()

if __name__ == '__main__':
  Launcher()
