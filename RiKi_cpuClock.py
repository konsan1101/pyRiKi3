#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2023 Mitsuo KONDOU.
# This software is released under the MIT License.
# https://github.com/konsan1101
# Thank you for keeping the rules.
# ------------------------------------------------



import sys
import os
import time
import datetime
import codecs
import glob

import psutil
import io

import subprocess

import numpy as np
import cv2

import matplotlib      #エラー対策
matplotlib.use('Agg')  #エラー対策
import matplotlib.pyplot as plt
import PySimpleGUI as sg

from PIL import Image, ImageDraw, ImageFont



# インターフェース
qCtrl_control_clock = 'temp/control_clock.txt'
qCtrl_control_self  = qCtrl_control_clock



# 共通ルーチン
import   _v6__qFunc
qFunc  = _v6__qFunc.qFunc_class()
import   _v6__qGUI
qGUI   = _v6__qGUI.qGUI_class()
import   _v6__qLog
qLog   = _v6__qLog.qLog_class()

import   _v6__qGuide
qGuide = _v6__qGuide.qGuide_class()
import   _v6__qFFmpeg
qFFmpeg= _v6__qFFmpeg.qFFmpeg_class()



# winos 音声合成
if (os.name =='nt'):
    import speech_api_winos as winos_api



qPath_temp  = 'temp/'
qPath_log   = 'temp/_log/'
qPath_work  = 'temp/_work/'
qPath_rec   = 'temp/_rec/'

qPath_fonts = '_fonts/'
qPath_icons = '_icons/'



def setFolder(name='temp'):
    if (name[-1:] == '/'):
        name = name[:-1]
    if (not os.path.isdir(name)):
        os.makedirs(name)
    return name + '/'

qPath_pictures   = ''
qPath_videos     = ''
if (os.name == 'nt'):
    qUSERNAME = os.environ["USERNAME"]
    qPath_pictures  = setFolder('C:/Users/' + qUSERNAME + '/Pictures/RiKi/')
    qPath_videos    = setFolder('C:/Users/' + qUSERNAME + '/Videos/RiKi/'  )
else:
    qUSERNAME = os.environ["USER"]



import _v6__qRiKi_key

config_file = 'RiKi_cpuClock_key.json'

qRiKi_key = _v6__qRiKi_key.qRiKi_key_class()
res, dic = qRiKi_key.getCryptJson(config_file=config_file, auto_crypt=False, )
if (res == False):
    dic['_crypt_']          = 'none'
    dic['run_priority']     = 'auto'
    dic['clock_screen']     = 'auto'
    dic['clock_panel']      = 'auto'
    dic['clock_design']     = 'auto'
    dic['clock_alpha']      = '0.7'
    dic['clock_guiTheme']   = 'black'
    dic['telop_path']       = 'temp/d6_7telop_txt/'
    dic['tts_path']         = 'temp/s6_5tts_txt/'
    dic['tts_header']       = 'ja,google,'
    dic['timeSign_sound']   = '_sounds/_sound_SeatBeltSign1.mp3'
    dic['timeSign_telop']   = 'yes'
    dic['timeSign_tts']     = 'no'
    dic['analog_pltStyle']  = 'dark_background'
    dic['analog_b_fcolor']  = 'white'
    dic['analog_b_tcolor']  = 'fuchsia'
    dic['analog_b_bcolor']  = 'black'
    dic['analog_s_fcolor']  = 'red'
    dic['analog_s_bcolor1'] = 'darkred'
    dic['analog_s_bcolor2'] = 'tomato'
    dic['analog_m_fcolor']  = 'cyan'
    dic['analog_m_bcolor1'] = 'darkgreen'
    dic['analog_m_bcolor2'] = 'limegreen'
    dic['analog_h_fcolor']  = 'cyan'
    dic['analog_h_bcolor1'] = 'darkblue'
    dic['analog_h_bcolor2'] = 'deepskyblue'
    dic['digital_b_fcolor'] = 'white'
    dic['digital_b_tcolor'] = 'fuchsia'
    dic['digital_b_bcolor'] = 'black'

    res = qRiKi_key.putCryptJson(config_file=config_file, put_dic=dic, )



class clock_image_class:

    def __init__(self, runMode='debug', ):
        self.runMode = runMode
        self.proc_id = 'clock_img_'
        
        # フォント
        self.font_dseg7 = {'file':qPath_fonts + 'DSEG7Classic-Bold.ttf','offset':8}
        try:
            self.font32_dseg7 = ImageFont.truetype(self.font_dseg7['file'], 32, encoding='unic')
            self.font32_dseg7y =                   self.font_dseg7['offset']
            self.font99_dseg7 = ImageFont.truetype(self.font_dseg7['file'], 192, encoding='unic')
            self.font99_dseg7y =                   self.font_dseg7['offset']
            self.font88_dseg7 = ImageFont.truetype(self.font_dseg7['file'], 288, encoding='unic')
            self.font88_dseg7y =                   self.font_dseg7['offset']
        except:
            self.font32_dseg7  = None
            self.font32_dseg7y = 0
            self.font99_dseg7  = None
            self.font99_dseg7y = 0
            self.font88_dseg7  = None
            self.font88_dseg7y = 0

        # アイコン
        self.img_pcam6464 = None
        self.img_vcam6464 = None
        try:
            self.img_pcam6464 = cv2.imread(qPath_icons + '__pcam6464.png')
            self.img_vcam6464 = cv2.imread(qPath_icons + '__vcam6464.png')
        except:
            pass

        # 構成情報
        json_file = config_file
        self.run_priority     = 'auto'
        self.clock_screen     = 'auto'
        self.clock_panel      = 'auto'
        self.clock_design     = 'auto'
        self.clock_alpha      = '0.7'
        self.clock_guiTheme   = 'black'
        self.telop_path       = 'temp/d6_7telop_txt/'
        self.tts_path         = 'temp/s6_5tts_txt/'
        self.tts_header       = 'ja,google,'
        self.timeSign_sound   = '_sounds/_sound_SeatBeltSign1.mp3'
        self.timeSign_telop   = 'yes'
        self.timeSign_tts     = 'no'
        self.analog_pltStyle  = 'dark_background'
        self.analog_b_fcolor  = 'white'
        self.analog_b_tcolor  = 'fuchsia'
        self.analog_b_bcolor  = 'black'
        self.analog_s_fcolor  = 'red'
        self.analog_s_bcolor1 = 'darkred'
        self.analog_s_bcolor2 = 'tomato'
        self.analog_m_fcolor  = 'cyan'
        self.analog_m_bcolor1 = 'darkgreen'
        self.analog_m_bcolor2 = 'limegreen'
        self.analog_h_fcolor  = 'cyan'
        self.analog_h_bcolor1 = 'darkblue'
        self.analog_h_bcolor2 = 'deepskyblue'
        self.digital_b_fcolor = 'white'
        self.digital_b_tcolor = 'fuchsia'
        self.digital_b_bcolor = 'black'
        res, json_dic = qRiKi_key.getCryptJson(config_file=json_file, auto_crypt=False, )
        if (res == True):
            self.run_priority     = json_dic['run_priority']
            self.clock_screen     = json_dic['clock_screen']
            self.clock_panel      = json_dic['clock_panel']
            self.clock_design     = json_dic['clock_design']
            self.clock_alpha      = json_dic['clock_alpha']
            self.clock_guiTheme   = json_dic['clock_guiTheme']
            self.telop_path       = json_dic['telop_path']
            self.tts_path         = json_dic['tts_path']
            self.tts_header       = json_dic['tts_header']
            self.timeSign_sound   = json_dic['timeSign_sound']
            self.timeSign_telop   = json_dic['timeSign_telop']
            self.timeSign_tts     = json_dic['timeSign_tts']
            self.analog_pltStyle  = json_dic['analog_pltStyle']
            self.analog_b_fcolor  = json_dic['analog_b_fcolor']
            self.analog_b_tcolor  = json_dic['analog_b_tcolor']
            self.analog_b_bcolor  = json_dic['analog_b_bcolor']
            self.analog_s_fcolor  = json_dic['analog_s_fcolor']
            self.analog_s_bcolor1 = json_dic['analog_s_bcolor1']
            self.analog_s_bcolor2 = json_dic['analog_s_bcolor2']
            self.analog_m_fcolor  = json_dic['analog_m_fcolor']
            self.analog_m_bcolor1 = json_dic['analog_m_bcolor1']
            self.analog_m_bcolor2 = json_dic['analog_m_bcolor2']
            self.analog_h_fcolor  = json_dic['analog_h_fcolor']
            self.analog_h_bcolor1 = json_dic['analog_h_bcolor1']
            self.analog_h_bcolor2 = json_dic['analog_h_bcolor2']
            self.digital_b_fcolor = json_dic['digital_b_fcolor']
            self.digital_b_tcolor = json_dic['digital_b_tcolor']
            self.digital_b_bcolor = json_dic['digital_b_bcolor']

        # ディレクトリ作成
        if (self.telop_path != ''):
            if (os.path.isdir(self.telop_path)):
                qFunc.makeDirs(self.telop_path, remove=False, )
        if (self.tts_path != ''):
            if (os.path.isdir(self.tts_path)):
                qFunc.makeDirs(self.tts_path,   remove=False, )

        self.file_seq = 0
        self.last_icon = None

        # -------------
        # デジタル時計盤
        # -------------
        width  = 750
        height = 270
        self.digital_base = np.zeros((height,width,3), np.uint8)
        if (self.digital_b_bcolor == 'white'):
            cv2.rectangle(self.digital_dseg7_0,(0,0),(width,height),(255,255,255),thickness=-1,)
        if (self.font32_dseg7 is None):
            pass
        else:
            hhmm = '{:02d}:{:02d}'.format(int(88), int(88))
            pil_image = qGuide.cv2pil(self.digital_base)
            text_draw = ImageDraw.Draw(pil_image)
            if (self.digital_b_bcolor == 'white'):
                text_draw.text((int(width*0.05),int(height*0.25)), hhmm, font=self.font99_dseg7, fill=(232,232,232))
            else:
                text_draw.text((int(width*0.05),int(height*0.25)), hhmm, font=self.font99_dseg7, fill=(24,24,24))
            self.digital_base = qGuide.pil2cv(pil_image)

        self.cpu_data  = []
        self.mem_data  = []
        self.disk_data = []
        for x in range(int(width/5)):
            self.cpu_data.append(float(0))
            self.mem_data.append(float(0))
            self.disk_data.append(float(0))
        self.disk_max  = 1
        disk = psutil.disk_io_counters(perdisk=False)
        self.last_disk_write = disk.write_bytes
        self.last_disk_read  = disk.read_bytes

        self.last_hhmm = ''
        self.last_s    = 0
        self.cpu_ave   = 0
        self.mem_ave   = 0
        self.disk_ave  = 0
        self.cpu_freq  = 0

        # -------------
        # アナログ時計盤
        # -------------
        plt.style.use(self.analog_pltStyle)
        self.fig = plt.figure(figsize=(10,10))
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlim(-1.05,1.05)
        self.ax.set_ylim(-1.05,1.05)
        self.ax.axis('off')
        # 外周
        vals = np.array([100,])
        colors = [self.analog_b_fcolor,]
        self.ax.pie(vals,colors=colors,counterclock=False, startangle=90, radius=1, wedgeprops=dict(width=0.02), )
        # 目盛
        for t in range(1,60):
            t_x1 = np.sin(np.radians(t/60*360)) * 0.95
            t_x2 = np.sin(np.radians(t/60*360)) * 0.98
            t_y1 = np.cos(np.radians(t/60*360)) * 0.95
            t_y2 = np.cos(np.radians(t/60*360)) * 0.98
            self.ax.plot([t_x1,t_x2],[t_y1,t_y2],color=self.analog_b_fcolor, lw=1,)
        for t in range(1,13):
            t_x1 = np.sin(np.radians((t % 12)/12*360)) * 0.90
            t_x2 = np.sin(np.radians((t % 12)/12*360)) * 0.98
            t_y1 = np.cos(np.radians((t % 12)/12*360)) * 0.90
            t_y2 = np.cos(np.radians((t % 12)/12*360)) * 0.98
            self.ax.plot([t_x1,t_x2],[t_y1,t_y2],color=self.analog_b_fcolor, lw=3,)
        # 画像保存
        buf = io.BytesIO()
        self.fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, )
        enc = np.frombuffer(buf.getvalue(), dtype=np.uint8)
        self.analog_base   = cv2.imdecode(enc, 1)
        self.analog_height = self.analog_base.shape[0]
        self.analog_width  = self.analog_base.shape[1]
        


    def bytes2str(self, bytes, units=[' Byte', ' KByte', ' MByte', ' GByte', ' TByte', ' PByte', ' EByte']):
        if (bytes < 1024):
            return '{:4d}'.format(bytes) + units[0]
        else:
            return self.bytes2str(int(bytes) >> 10, units[1:])



    def getImage_digital(self, dt_now, design=0, eyes=True, sg_left2=0, sg_top2=0, sg_width=320, sg_height=240, ):
        self.last_icon = None

        yy = dt_now.year
        mm = dt_now.month
        dd = dt_now.day
        h = dt_now.hour
        m = dt_now.minute
        s = dt_now.second

        width  = self.digital_base.shape[1]
        height = self.digital_base.shape[0]

        #----------
        # デジタル
        #----------
        if (self.font32_dseg7 is None):
            ymd  = '{:04d}. {:02d}. {:02d}.'.format(yy, mm, dd)
        else:
            ymd  = '{:04d}.    {:02d}.    {:02d}.'.format(yy, mm, dd)
        hhmm = '{:02d}:{:02d}'.format(int(h), int(m))
        if (hhmm != self.last_hhmm):
            self.last_hhmm = hhmm
            
            self.digital_dseg7_0 = np.zeros((height,width,3), np.uint8)
            if (self.font32_dseg7 is None):
                cv2.putText(self.digital_dseg7_0, ymd, (int(width*0.27),int(height*0.2)), cv2.FONT_HERSHEY_TRIPLEX, 2, (223,223,0))
                cv2.putText(self.digital_dseg7_0, hhmm, (int(width*0.10),int(height*0.85)), cv2.FONT_HERSHEY_TRIPLEX, 7, (255,0,255))
                self.digital_dseg7_1 = self.digital_dseg7_0.copy()
            else:
                hhmm2 = '{:02d} {:02d}'.format(int(h), int(m))

                pil_image1 = qGuide.cv2pil(self.digital_dseg7_0)
                pil_image2 = qGuide.cv2pil(self.digital_dseg7_0)
                text_draw1 = ImageDraw.Draw(pil_image1)
                text_draw1.text((int(width*0.56),int(height*0.08)), ymd, font=self.font32_dseg7, fill=(0,223,223))
                text_draw1.text((int(width*0.05),int(height*0.25)), hhmm, font=self.font99_dseg7, fill=self.digital_b_tcolor)
                text_draw2 = ImageDraw.Draw(pil_image2)
                text_draw2.text((int(width*0.56),int(height*0.08)), ymd, font=self.font32_dseg7, fill=(0,223,223))
                text_draw2.text((int(width*0.05),int(height*0.25)), hhmm2, font=self.font99_dseg7, fill=self.digital_b_tcolor)
                self.digital_dseg7_0 = qGuide.pil2cv(pil_image1)
                self.digital_dseg7_1 = qGuide.pil2cv(pil_image2)

            # 画像保存　０
            base = self.digital_base        
            over = self.digital_dseg7_0.copy()
            #over = self.digital_dseg7_1.copy()
            # 表側でマスク作成
            gray = cv2.cvtColor(over, cv2.COLOR_BGR2GRAY)
            ret, mask = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
            mask_inv = cv2.bitwise_not(mask)    
            # 表側,裏側,合成
            fg = cv2.bitwise_and(over, over, mask = mask)
            bg = cv2.bitwise_and(base, base, mask = mask_inv)
            self.digital_image_0 = cv2.add(bg, fg)

            # 画像保存　１
            base = self.digital_base        
            #over = self.digital_dseg7_0.copy()
            over = self.digital_dseg7_1.copy()
            # 表側でマスク作成
            gray = cv2.cvtColor(over, cv2.COLOR_BGR2GRAY)
            ret, mask = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
            mask_inv = cv2.bitwise_not(mask)    
            # 表側,裏側,合成
            fg = cv2.bitwise_and(over, over, mask = mask)
            bg = cv2.bitwise_and(base, base, mask = mask_inv)
            self.digital_image_1 = cv2.add(bg, fg)

        #----------
        # データ収集
        #----------
        cpu  = psutil.cpu_percent(interval=None, percpu=False)
        mem  = psutil.virtual_memory().percent
        disk = psutil.disk_io_counters(perdisk=False)
        disk_io = (disk.write_bytes - self.last_disk_write) + (disk.read_bytes - self.last_disk_read)
        self.last_disk_write = disk.write_bytes
        self.last_disk_read  = disk.read_bytes
        del self.cpu_data[0]
        del self.mem_data[0]
        del self.disk_data[0]
        self.cpu_data.append(float(cpu))
        self.mem_data.append(float(mem))
        self.disk_data.append(float(disk_io))

        #----------
        # グラフ作図
        #----------
        if (eyes == True):
            graph_ymin  = 60
            graph_ymax  = height - 2
            base_img    = np.zeros((height,width,3), np.uint8)
            cpu_color   = (0,255,0)
            cpu_color1  = (0,197,0)
            cpu_color2  = (0,255,0)
            mem_color   = (255,127,0)
            mem_color1  = (63,0,0)
            mem_color2  = (163,95,0)
            disk_color  = (0,239,255)
            disk_color1 = (0,95,127)
            disk_color2 = (0,163,197)

            polly   = np.array([[width-1, graph_ymax+1], [0, graph_ymax+1]], dtype=np.int64, )
            max_val = 100
            for x in range(len(self.cpu_data)):
                val = int((1 - self.cpu_data[x]/max_val) * (graph_ymax-graph_ymin)) + graph_ymin 
                add_polly = np.array([x*5, val], dtype=np.int64, )
                polly = np.append(polly, [add_polly], axis=0, )
            cpu_fill  = cv2.fillPoly(base_img.copy(), pts=[polly], color=cpu_color1, )
            cpu_img   = cv2.polylines(cpu_fill.copy(), pts=[polly], isClosed=True, color=cpu_color2, thickness=2, )

            polly   = np.array([[width-1, graph_ymax+1], [0, graph_ymax+1]], dtype=np.int64, )
            max_val = 100
            for x in range(len(self.mem_data)):
                val = int((1 - self.mem_data[x]/max_val) * (graph_ymax-graph_ymin)) + graph_ymin 
                add_polly = np.array([x*5, val], dtype=np.int64, )
                polly = np.append(polly, [add_polly], axis=0, )
            mem_fill = cv2.fillPoly(base_img.copy(), pts=[polly], color=mem_color1, )
            mem_img  = cv2.polylines(mem_fill.copy(), pts=[polly], isClosed=True, color=mem_color2, thickness=2, )

            polly = np.array([[width-1, graph_ymax+1], [0, graph_ymax+1]], dtype=np.int64, )
            max_val = max(self.disk_data)
            if (max_val > self.disk_max):
                self.disk_max = max_val
            max_val = self.disk_max
            for x in range(len(self.disk_data)):
                val = int((1 - self.disk_data[x]/max_val) * (graph_ymax-graph_ymin)) + graph_ymin 
                add_polly = np.array([x*5, val], dtype=np.int64, )
                polly = np.append(polly, [add_polly], axis=0, )
            disk_fill = cv2.fillPoly(base_img.copy(), pts=[polly], color=disk_color1, )
            disk_img  = cv2.polylines(disk_fill.copy(), pts=[polly], isClosed=True, color=disk_color2, thickness=2, )

            base = cv2.addWeighted(mem_img, 1.0, disk_img, 1.0, 0.0)
            graph_img = cv2.addWeighted(base, 1.0, cpu_img, 1.0, 0.0)

            if (s != self.last_s):
                self.last_s   = s
                self.cpu_ave  = np.mean(self.cpu_data[-10:])
                self.mem_ave  = np.mean(self.mem_data[-10:])
                self.disk_ave = int(np.mean(self.disk_data[-10:]))
                self.cpu_freq = psutil.cpu_freq().current #Mhz

            txt = 'CPU  : {:4.1f} %'.format(self.cpu_ave) + ' ({:.1f}GHz)'.format(self.cpu_freq/1000)
            cv2.putText(graph_img, txt, (20,33), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, cpu_color, )
            txt = 'DISK : {}'.format(self.bytes2str(self.disk_ave))
            cv2.putText(graph_img, txt, (20,53), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, disk_color,)
            txt = 'MEM : {:4.1f} %'.format(self.mem_ave)
            cv2.putText(graph_img, txt, (20,73), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, mem_color, )

        #----------
        # 目ん玉
        #----------
        if (eyes == True):
            digital_eyes = np.zeros((height,width,3), np.uint8)

            color_base = (0, 0, 0)
            all_ave = np.mean(self.cpu_data)
            if   (all_ave <= 15):
                red_lv = 0
            elif (all_ave >= 65):
                red_lv = 255
            else:
                red_lv = int(((all_ave-15)/50) * 255)
                if (red_lv > 255):
                    red_lv = 255
            color_eyes = (255-red_lv, 255-red_lv, 255)
            yoko0 = int(width / 6)
            tate0 = int(height * 0.7)
            yoko1 = int(yoko0 / 5)
            tate1 = int(tate0 / 5)
            futosa = int(height * 0.05)

            eye1_center_x = int(width / 2) - int(width / 9)
            eye1_center_y = int(height / 2) + int(height / 20)

            eye2_center_x = int(width / 2) + int(width / 9)
            eye2_center_y = int(height / 2) + int(height / 20)

            (pos_x, pos_y) = qGUI.position()
            on_x = int((pos_x - sg_left2) / (sg_width/width))
            on_y = int((pos_y - sg_top2) / (sg_height/height))
            cv2.ellipse(digital_eyes, ((on_x, on_y), (10, 10), 0), (0,0,255), thickness=-1)

            # 目ん玉１
            eye_screen_x = int((eye1_center_x) * (sg_width/width)) + sg_left2
            eye_screen_y = int((eye1_center_y) * (sg_height/height)) + sg_top2
            x = pos_x - eye_screen_x
            y = eye_screen_y - pos_y
            rd = np.arctan2(x, y)
            eye_x = int(np.sin(rd) * yoko0 / 3)
            eye_y = - int(np.cos(rd) * tate0 / 3)
            if  (on_x >= (eye1_center_x-abs(eye_x)-5)) and (on_x <= (eye1_center_x+abs(eye_x)+5)) \
            and (on_y >= (eye1_center_y-abs(eye_y)-5)) and (on_y <= (eye1_center_y+abs(eye_y)+5)):
                try:
                    digital_eyes[ on_y-32:on_y+32, on_x-32:on_x+32 ] = self.img_pcam6464[ 0:64, 0:64 ]
                    self.last_icon = 'pcam'
                except:
                    cv2.ellipse(digital_eyes, ((on_x, on_y), (yoko1, tate1), 0), color_eyes, thickness=-1)
            else:
                cv2.ellipse(digital_eyes, ((eye1_center_x+eye_x, eye1_center_y+eye_y), (yoko1, tate1), 0), color_eyes, thickness=-1)
            #cv2.ellipse(digital_eyes, ((eye1_center_x, eye1_center_y), (yoko0, tate0), 0), color_base, thickness=-1)
            cv2.ellipse(digital_eyes, ((eye1_center_x, eye1_center_y), (yoko0, tate0), 0), color_eyes, thickness=futosa)

            # 目ん玉２
            eye_screen_x = int((eye2_center_x) * (sg_width/width)) + sg_left2
            eye_screen_y = int((eye2_center_y) * (sg_height/height)) + sg_top2
            x = pos_x - eye_screen_x
            y = eye_screen_y - pos_y
            rd = np.arctan2(x, y)
            eye_x = int(np.sin(rd) * yoko0 / 3)
            eye_y = - int(np.cos(rd) * tate0 / 3)
            if  (on_x >= (eye2_center_x-abs(eye_x)-5)) and (on_x <= (eye2_center_x+abs(eye_x)+5)) \
            and (on_y >= (eye2_center_y-abs(eye_y)-5)) and (on_y <= (eye2_center_y+abs(eye_y)+5)):
                try:
                    digital_eyes[ on_y-32:on_y+32, on_x-32:on_x+32 ] = self.img_vcam6464[ 0:64, 0:64 ]
                    self.last_icon = 'vcam'
                except:
                    cv2.ellipse(digital_eyes, ((on_x, on_y), (yoko1, tate1), 0), color_eyes, thickness=-1)
            else:        
                cv2.ellipse(digital_eyes, ((eye2_center_x+eye_x, eye2_center_y+eye_y), (yoko1, tate1), 0), color_eyes, thickness=-1)
            #cv2.ellipse(digital_eyes, ((eye2_center_x, eye2_center_y), (yoko0, tate0), 0), color_base, thickness=-1)
            cv2.ellipse(digital_eyes, ((eye2_center_x, eye2_center_y), (yoko0, tate0), 0), color_eyes, thickness=futosa)

        #----------
        # 画像合成
        #----------
        if ((s % 2) == 1) or (eyes == True):
            img = self.digital_image_1.copy()
        else:
            img = self.digital_image_0.copy()

        # 目ん玉合成
        if (eyes == True):
            base = cv2.addWeighted(img, 0.7, graph_img, 1.0, 0.0)
            over = digital_eyes
            # 表側でマスク作成
            gray = cv2.cvtColor(over, cv2.COLOR_BGR2GRAY)
            ret, mask = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
            mask_inv = cv2.bitwise_not(mask)    
            # 表側,裏側,合成
            fg = cv2.bitwise_and(over, over, mask = mask)
            bg = cv2.bitwise_and(base, base, mask = mask_inv)
            img = cv2.add(bg, fg)

        # 秒針
        w = int(width * (s/59))
        if (eyes != True):
            cv2.rectangle(img,(width-w,0),(width,5),(0,0,255),thickness=-1,)
        else:
            cv2.rectangle(img,(width-w,0),(width,5),(255,255,0),thickness=-1,)

        return img

    def getImage_analog(self, dt_now, design=0, ):
        self.last_icon = None

        yy = dt_now.year
        mm = dt_now.month
        dd = dt_now.day
        h = dt_now.hour
        m = dt_now.minute
        s = dt_now.second

        m = m + s/60
        h = h + m/60

        #----------
        # デジタル
        #----------
        if (self.font32_dseg7 is None):
            ymd  = '{:04d}. {:02d}. {:02d}.'.format(yy, mm, dd)
        else:
            ymd  = '{:04d}.    {:02d}.    {:02d}.'.format(yy, mm, dd)
        hhmm = '{:02d}:{:02d}'.format(int(h), int(m))
        if (hhmm != self.last_hhmm):
            self.last_hhmm = hhmm
            
            width  = self.analog_width
            height = self.analog_height
            self.analog_dseg7_0 = np.zeros((height,width,3), np.uint8)
            if (self.font32_dseg7 is None):
                cv2.putText(self.analog_dseg7_0, ymd, (int(width*0.27),int(height*0.33)), cv2.FONT_HERSHEY_TRIPLEX, 2, (223,223,0))
                cv2.putText(self.analog_dseg7_0, hhmm, (int(width*0.2),int(height*0.7)), cv2.FONT_HERSHEY_TRIPLEX, 5, (255,0,255))
                self.analog_dseg7_1 = self.analog_dseg7_0.copy()
            else:
                if ((design % 2) == 0):
                    hhmm2 = '{:02d} {:02d}'.format(int(h), int(m))
                    pil_image1 = qGuide.cv2pil(self.analog_dseg7_0)
                    pil_image2 = qGuide.cv2pil(self.analog_dseg7_0)
                    text_draw1 = ImageDraw.Draw(pil_image1)
                    text_draw1.text((int(width*0.34),int(height*0.30)), ymd, font=self.font32_dseg7, fill=(0,223,223))
                    text_draw1.text((int(width*0.06),int(height*0.6)), hhmm, font=self.font99_dseg7, fill=self.analog_b_tcolor)
                    text_draw2 = ImageDraw.Draw(pil_image2)
                    text_draw2.text((int(width*0.34),int(height*0.30)), ymd, font=self.font32_dseg7, fill=(0,223,223))
                    text_draw2.text((int(width*0.06),int(height*0.6)), hhmm2, font=self.font99_dseg7, fill=self.analog_b_tcolor)
                    self.analog_dseg7_0 = qGuide.pil2cv(pil_image1)
                    self.analog_dseg7_1 = qGuide.pil2cv(pil_image2)
                else:
                    hh = '{:02d}'.format(int(h))
                    mm = '{:02d}'.format(int(m))
                    pil_image = qGuide.cv2pil(self.analog_dseg7_0)
                    text_draw = ImageDraw.Draw(pil_image)
                    text_draw.text((int(width*0.65),int(height*0.02)), ymd, font=self.font32_dseg7, fill=(0,223,223))
                    text_draw.text((int(width*0.05),int(height*0.08)), hh, font=self.font88_dseg7, fill=self.analog_b_tcolor)
                    text_draw.text((int(width*0.35),int(height*0.53)), mm, font=self.font88_dseg7, fill=self.analog_b_tcolor)
                    self.analog_dseg7_0 = qGuide.pil2cv(pil_image)
                    self.analog_dseg7_1 = self.analog_dseg7_0.copy()

        # 文字 2 パターン
        # 盤 3 パターン
        # 素数 5 目盛
        # 素数 7 パイ配色
        # 素数 11 目盛文字

        #----------
        # パイ盤 0,1
        #----------
        if ((design % 3) == 0) \
        or ((design % 3) == 1):
            plt.cla()
            # 外周
            vals = np.array([100,])
            colors = [self.analog_b_bcolor,]
            self.ax.pie(vals,colors=colors,counterclock=False, startangle=90, radius=1, wedgeprops=dict(width=0.02), )
            # 色
            if ((design % 3) == 1) \
            or ((design % 7) == 4):
                s_colors = [self.analog_s_bcolor2, self.analog_s_bcolor1,]
                m_colors = [self.analog_m_bcolor2, self.analog_m_bcolor1,]
                h_colors = [self.analog_h_bcolor2, self.analog_h_bcolor1,]
            else:
                s_colors = [self.analog_s_bcolor1, self.analog_b_bcolor,]
                m_colors = [self.analog_m_bcolor1, self.analog_b_bcolor,]
                h_colors = [self.analog_h_bcolor1, self.analog_b_bcolor,]
            # 秒
            vals = np.array([s/60, 1-s/60,])
            self.ax.pie(vals,colors=s_colors,counterclock=False, startangle=90, radius=0.85, wedgeprops=dict(width=0.2), )
            # 分
            vals = np.array([m/60, 1-m/60,])
            self.ax.pie(vals,colors=m_colors,counterclock=False, startangle=90, radius=0.60, wedgeprops=dict(width=0.2), )
            # 時
            vals = np.array([(h % 12)/12, 1-(h % 12)/12,])
            self.ax.pie(vals,colors=h_colors,counterclock=False, startangle=90, radius=0.35, wedgeprops=dict(width=0.2), )
            # 目盛
            if ((design % 11) != 1):
                for t in range(1,13):
                    if ((t % 3)==0):
                        t_x = np.sin(np.radians((t % 12)/12*360)) * 0.75
                        t_y = np.cos(np.radians((t % 12)/12*360)) * 0.75
                        self.ax.text(t_x, t_y, str(t), color=self.analog_b_fcolor, ha='center', va='center', size=64, )
            # 画像保存
            buf = io.BytesIO()
            self.fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, )
            enc = np.frombuffer(buf.getvalue(), dtype=np.uint8)
            img_pie = cv2.imdecode(enc, 1)
            # サイズ調整
            if (img_pie.shape) != (self.analog_base.shape):
                img_pie = cv2.resize(img_pie, (self.analog_width, self.analog_height))
            #plt.show()

        #----------
        # 画像合成
        #----------
        if ((design % 3) == 1):

            if ((design % 5) == 1):
                base = img_pie.copy()
            else:
                base = img_pie
                over = self.analog_base        
                # 表側でマスク作成
                gray = cv2.cvtColor(over, cv2.COLOR_BGR2GRAY)
                ret, mask = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
                mask_inv = cv2.bitwise_not(mask)    
                # 表側,裏側,合成
                fg = cv2.bitwise_and(over, over, mask = mask)
                bg = cv2.bitwise_and(base, base, mask = mask_inv)
                base = cv2.add(bg, fg)

            if ((s % 2) == 0):
                over = self.analog_dseg7_0
            else:
                over = self.analog_dseg7_1
            # 表側でマスク作成
            gray = cv2.cvtColor(over, cv2.COLOR_BGR2GRAY)
            ret, mask = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
            mask_inv = cv2.bitwise_not(mask)    
            # 表側,裏側,合成
            fg = cv2.bitwise_and(over, over, mask = mask)
            bg = cv2.bitwise_and(base, base, mask = mask_inv)
            img = cv2.add(bg, fg)

            return img

        #----------
        # アナログ盤 0,2
        #----------
        if ((design % 3) == 0) \
        or ((design % 3) == 2):
            plt.cla()
            # 外周
            vals = np.array([100,])
            colors = [self.analog_b_bcolor,]
            self.ax.pie(vals,colors=colors,counterclock=False, startangle=90, radius=1, wedgeprops=dict(width=0.02), )
            # 目盛
            if ((design % 11) != 1):
                for t in range(1,13):
                    if ((t % 3)==0):
                        t_x = np.sin(np.radians((t % 12)/12*360)) * 0.75
                        t_y = np.cos(np.radians((t % 12)/12*360)) * 0.75
                        self.ax.text(t_x, t_y, str(t), color=self.analog_b_fcolor, ha='center', va='center', size=64, )
            # 時針
            h_x = np.sin(np.radians((h % 12)/12*360)) * 0.55
            h_y = np.cos(np.radians((h % 12)/12*360)) * 0.55
            self.ax.plot([0,h_x], [0,h_y], color=self.analog_h_fcolor, lw=32, zorder=99, )
            # 分針
            m_x = np.sin(np.radians(m/60*360)) * 0.80
            m_y = np.cos(np.radians(m/60*360)) * 0.80
            self.ax.plot([0,m_x], [0,m_y], color=self.analog_m_fcolor, lw=16, zorder=99, )
            # 秒針
            s_x = np.sin(np.radians(s/60*360)) * 0.85
            s_y = np.cos(np.radians(s/60*360)) * 0.85
            self.ax.plot([0,s_x], [0,s_y], color=self.analog_s_fcolor, lw=8, zorder=99, )
            # 画像保存
            buf = io.BytesIO()
            self.fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, )
            enc = np.frombuffer(buf.getvalue(), dtype=np.uint8)
            img_line = cv2.imdecode(enc, 1)
            # サイズ調整
            if (img_line.shape) != (self.analog_base.shape):
                img_line = cv2.resize(img_line, (self.analog_width, self.analog_height))
            #plt.show()

        #----------
        # 画像合成
        #----------
        if ((design % 3) == 2):

            if ((design % 5) == 1):
                if ((s % 2) == 0):
                    base = self.analog_dseg7_0.copy()
                else:
                    base = self.analog_dseg7_1.copy()
            else:
                base = self.analog_base
                if ((s % 2) == 0):
                    over = self.analog_dseg7_0
                else:
                    over = self.analog_dseg7_1
                # 表側でマスク作成
                gray = cv2.cvtColor(over, cv2.COLOR_BGR2GRAY)
                ret, mask = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
                mask_inv = cv2.bitwise_not(mask)    
                # 表側,裏側,合成
                fg = cv2.bitwise_and(over, over, mask = mask)
                bg = cv2.bitwise_and(base, base, mask = mask_inv)
                base = cv2.add(bg, fg)

            over = img_line
            # 表側でマスク作成
            gray = cv2.cvtColor(over, cv2.COLOR_BGR2GRAY)
            ret, mask = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
            mask_inv = cv2.bitwise_not(mask)    
            # 表側,裏側,合成
            fg = cv2.bitwise_and(over, over, mask = mask)
            bg = cv2.bitwise_and(base, base, mask = mask_inv)
            img = cv2.add(bg, fg)

            return img

        #----------
        # 画像合成
        #----------
        if True:
            base = img_pie
            if ((s % 2) == 0):
                over = self.analog_dseg7_0
            else:
                over = self.analog_dseg7_1
            # 表側でマスク作成
            gray = cv2.cvtColor(over, cv2.COLOR_BGR2GRAY)
            ret, mask = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
            mask_inv = cv2.bitwise_not(mask)    
            # 表側,裏側,合成
            fg = cv2.bitwise_and(over, over, mask = mask)
            bg = cv2.bitwise_and(base, base, mask = mask_inv)
            base = cv2.add(bg, fg)

            if ((design % 5) != 1):
                over = self.analog_base
                # 表側でマスク作成
                gray = cv2.cvtColor(over, cv2.COLOR_BGR2GRAY)
                ret, mask = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
                mask_inv = cv2.bitwise_not(mask)    
                # 表側,裏側,合成
                fg = cv2.bitwise_and(over, over, mask = mask)
                bg = cv2.bitwise_and(base, base, mask = mask_inv)
                base = cv2.add(bg, fg)

            over = img_line
            # 表側でマスク作成
            gray = cv2.cvtColor(over, cv2.COLOR_BGR2GRAY)
            ret, mask = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
            mask_inv = cv2.bitwise_not(mask)    
            # 表側,裏側,合成
            fg = cv2.bitwise_and(over, over, mask = mask)
            bg = cv2.bitwise_and(base, base, mask = mask_inv)
            img = cv2.add(bg, fg)

        return img



    def timeSign_info(self, h, m, ):
        result  = str(h) + '時'
        result += str(m) + '分'

        # 情報通知
        if (result != ''):
            title = '【時報】'
            txt   = result
            #print(title, txt)
            qLog.log('info', self.proc_id, title + result, )

            if (self.timeSign_sound != ''):
                try:
                    sox = subprocess.Popen(['sox', '-q', self.timeSign_sound, '-d', ], \
                        shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, )
                except:
                    pass

            if (self.timeSign_telop != 'no') and (self.timeSign_telop != 'off'):
                if (m==0):
                    self.telopMSG(title=title, txt= 'ただ今、' + str(h) + '時をお知らせします。', )
                else:
                    self.telopMSG(title=title, txt= 'ただ今の時間、' + str(h) + '時' + str(m) + '分です。', )

            if (self.timeSign_tts != 'no') and (self.timeSign_tts != 'off'):
                if (m==0):
                    self.ttsMSG(title='ただ今、', txt= str(h) + '時をお知らせします。', )
                else:
                    self.ttsMSG(title='ただ今の時間、', txt=str(h) + '時' + str(m) + '分です。', )

        return result

    # cpuClock,saap_worker 同一ロジック
    def telopMSG(self, title='Message', txt='', ):
        if (txt == ''):
            return False
        if (self.telop_path == ''):
            return False
        if (not os.path.isdir(self.telop_path)):
            return False
        if (title.find('【') < 0):
            title = '【' + title + '】'
        txt = title + '\r\n' + txt

        now   = datetime.datetime.now()
        stamp = now.strftime('%Y%m%d%H%M%S')
        self.file_seq += 1
        if (self.file_seq > 9999):
            self.file_seq = 1
        seq4 = '{:04}'.format(self.file_seq)

        filename = self.telop_path + stamp + '.' + seq4 + '.txt'

        res = qFunc.txtsWrite(filename, txts=[txt], mode='w', exclusive=True, )
        if (res == False):
            qLog.log('critical', self.proc_id, '★Telop書込エラー', )
            return False        

        return True        

    # cpuClock,saap_worker 同一ロジック
    def ttsMSG(self, title='Message', txt='', ):
        if (txt == ''):
            return False
        if (self.tts_path == ''):
            return False
        if (not os.path.isdir(self.tts_path)):
            return False
        txt = txt.replace('\r',' ')
        txt = txt.replace('\n',' ')
        txt = txt.replace('／','/')
        txt = txt.replace('/','スラッシュ')
        txt = txt.replace('飛田さん','ひださん')
        txt = txt.replace('信正さん','のぶまささん')
        txt = txt.replace('昂平さん','こうへいさん')

        now   = datetime.datetime.now()
        stamp = now.strftime('%Y%m%d%H%M%S')
        self.file_seq += 1
        if (self.file_seq > 9999):
            self.file_seq = 1
        seq4 = '{:04}'.format(self.file_seq)

        filename = self.tts_path + stamp + '.' + seq4 + '.txt'

        # 個人利用時のWINOSは、直接発声！
        if  (self.runMode == 'personal') \
        and (self.tts_header == 'ja,winos,') \
        and (os.name == 'nt'):

            winosAPI = winos_api.SpeechAPI()
            res = winosAPI.authenticate()
            if (res == False):
                qLog.log('critical', self.proc_id, '★winosAPI(speech)認証エラー', )
                return False        

            try:
                filename = filename[:-4] + '.mp3'
                res, api = winosAPI.vocalize(outText=txt, outLang='ja', outFile=filename, )
                if (res != ''):

                    sox = subprocess.Popen(['sox', filename, '-d', '-q'], )
                    #sox.wait()
                    #sox.terminate()
                    #sox = None

            except:
                qLog.log('critical', self.proc_id, '★winosAPI(speech)利用エラー', )
                return False

        else:

            txt = self.tts_header + txt
            res = qFunc.txtsWrite(filename, txts=[txt], mode='w', exclusive=True, )
            if (res == False):
                qLog.log('critical', self.proc_id, '★TTS書込エラー', )
                return False        

        return True



# シグナル処理
import signal
def signal_handler(signal_number, stack_frame):
    print(os.path.basename(__file__), 'accept signal =', signal_number)

#signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGINT,  signal.SIG_IGN)
signal.signal(signal.SIGTERM, signal.SIG_IGN)



#runMode  = 'debug'
#runMode  = 'digital'
runMode  = 'personal'
#runMode  = 'analog'
p_screen = 'auto'
p_panel  = 'auto'
p_design = 'auto'
p_alpha  = ''



if __name__ == '__main__':
    main_name = 'clock'
    main_id   = '{0:10s}'.format(main_name).replace(' ', '_')

    # ディレクトリ作成
    qFunc.makeDirs(qPath_temp, remove=False, )
    qFunc.makeDirs(qPath_log,  remove=False, )
    qFunc.makeDirs(qPath_work, remove=False, )
    qFunc.makeDirs(qPath_rec,  remove=False, )

    # ログ
    nowTime  = datetime.datetime.now()
    filename = qPath_log + nowTime.strftime('%Y%m%d.%H%M%S') + '.' + os.path.basename(__file__) + '.log'
    qLog.init(mode='logger', filename=filename, )
    qLog.log('info', main_id, 'init')
    qLog.log('info', main_id, 'exsample.py runMode, ')

    # パラメータ
    if (True):
        if (len(sys.argv) >= 2):
            runMode  = str(sys.argv[1]).lower()
        if (len(sys.argv) >= 3):
            p_screen = str(sys.argv[2])
        if (len(sys.argv) >= 4):
            p_panel  = str(sys.argv[3])
        if (len(sys.argv) >= 5):
            p_design = str(sys.argv[4])
        if (len(sys.argv) >= 6):
            p_alpha  = str(sys.argv[5])

        qLog.log('info', main_id, 'runMode = ' + str(runMode ))
        qLog.log('info', main_id, 'screen  = ' + str(p_screen))
        qLog.log('info', main_id, 'panel   = ' + str(p_panel ))
        qLog.log('info', main_id, 'design  = ' + str(p_design))
        qLog.log('info', main_id, 'alpha   = ' + str(p_alpha ))

    # 初期設定
    if (True):

        # コントロールリセット
        txts, txt = qFunc.txtsRead(qCtrl_control_self)
        if (txts != False):
            if (txt == '_end_') or (txt == '_stop_'):
                qFunc.remove(qCtrl_control_self)

        # クラス設定
        qWinClock = clock_image_class(runMode=runMode, )

        # 実行優先設定
        nice = qWinClock.run_priority
        if (nice == 'auto'):
            nice = 'below'
        qFunc.setNice(nice, )

        # 実行条件設定
        if (p_screen != ''):
            qWinClock.clock_screen = p_screen
        if (p_panel != ''):
            qWinClock.clock_panel  = p_panel
        if (p_design != ''):
            qWinClock.clock_design = p_design
        if (p_alpha != ''):
            qWinClock.clock_alpha  = p_alpha

        #if (runMode == 'personal'):
        #    qWinClock.timeSign_tts = 'yes'
        #    qWinClock.tts_header   ='ja,winos,'

        # スクリーン
        screen = qGUI.getCornerScreen(rightLeft='right', topBottom='top', checkPrimary=False, )
        if (str(qWinClock.clock_screen) != 'auto'):
            try:
                screen = int(qWinClock.clock_screen)
            except:
                pass

        # パネル
        panel = qWinClock.clock_panel
        if (qWinClock.clock_panel == 'auto'):
            #l, t = 0, 0
            #w, h = qGUI.size()
            l, t, w, h = qGUI.getScreenPosSize(screen=screen, )
            if (runMode == 'digital'):
                panel = '3'
                sg_width,sg_height = 640, 320
            elif (runMode == 'personal'):
                panel = '3--'
                sg_width,sg_height = 320, 160
            else: #analog
                panel = '3'
                sg_width,sg_height = 640, 640

        # タイトル
        sg_titlex  = os.path.basename(__file__)
        sg_titlex  = sg_titlex.replace('.py','')
        sg_title = sg_titlex + '[' + runMode + ']'

        # ＧＵＩ初期化
        sg_keep_on_top   = True
        if (runMode != 'personal'):
            sg_no_titlebar   = True
        else:
            sg_no_titlebar   = False
        sg_disable_close = True
        sg_resizable     = True
        icon             = './_icons/' + sg_titlex + '.ico'
        qGuide.init(screen=screen, panel=panel, title=sg_title, image=None,
                alpha_channel=qWinClock.clock_alpha, keep_on_top=sg_keep_on_top,
                no_titlebar=sg_no_titlebar, disable_close=sg_disable_close,
                resizable=sg_resizable, icon=icon,
                )

        if (sg_no_titlebar == False):
            sg_left2 = l + 10
            sg_top2  = t + 32
        else:
            sg_left2 = l
            sg_top2  = t + 14

    # 起動
    if (True):
        qLog.log('info', main_id, 'start')

        eyes        = False
        if  (runMode == 'personal') \
        and ((p_design == 'auto') or (p_design == '1')):
            eyes        = True
        rec_running = False
        rec_time    = None
        rec_ffmpeg  = None
        rec_sox     = None

        (x, y) = qGUI.position()
        last_mouse_x = x
        last_mouse_y = y

        bk_h = 0
        bk_m = 0
        bk_s = 0

        design = 0



    # 待機ループ
    break_flag = False
    while (break_flag == False):

        try:

            # 終了確認
            txts, txt = qFunc.txtsRead(qCtrl_control_self)
            if (txts != False):
                if (txt == '_end_'):

                    if (rec_running == True):
                        rec_running = False
                        qFFmpeg.rec_stop(rec_ffmpeg, rec_sox,)
                        rec_ffmpeg = None
                        rec_sox    = None

                    break_flag = True
                    break

            # 録画中の場合
            if (rec_running == True):
                if ((time.time() - rec_time) > 120):

                    # レコーダー終了
                    rec_running = False
                    qFFmpeg.rec_stop(rec_ffmpeg, rec_sox,)
                    rec_ffmpeg = None
                    rec_sox    = None

                    qLog.log('info', main_id, 'デスクトップ録画　終了')

                    qFunc.copy(rec_filev, qPath_rec + stamp + '.recorder.mp4')
                    if (qPath_videos != ''):
                        folder = qPath_videos + yyyymmdd + '/'
                        qFunc.makeDirs(folder)
                    qFunc.copy(rec_filev, folder + stamp + '.recorder.mp4')

                    qGuide.open()

                    qWinClock.telopMSG(title='【通知】', txt='デスクトップ録画(120秒)は終了しました。', )

            # 録画中でない場合
            if (rec_running == False):

                # イベントの読み込み                 ↓　timeout値でtime.sleep代用
                event, values = qGuide.read(timeout=250, timeout_key='-timeout-')
                # ウィンドウの×ボタンクリックで終了
                if event == sg.WIN_CLOSED:
                    break_flag = True
                    break
                if event in (None, '-exit-'):
                    break_flag = True
                    break

                if (event == '-timeout-'):
                    pass

                # 時計クリック
                elif (event == '-image-'):
                    if (runMode == 'personal'):
                        if (eyes == False):
                            eyes = True
                            qGuide.setAlphaChannel(alpha_channel=1, )
                        else:
                            eyes = False
                            qGuide.setAlphaChannel(alpha_channel=qWinClock.clock_alpha, )

                            #widget = sg_win['-image-'].Widget
                            #print(widget)

                            # スクリーンキャプチャ
                            if (qWinClock.last_icon == 'pcam'):
                                qGuide.close()
                                eyes = True

                                # シャッター音
                                qFunc.guideSound('_shutter', sync=False)

                                # キャプチャー
                                nowTime   = datetime.datetime.now()
                                stamp     = nowTime.strftime('%Y%m%d.%H%M%S')
                                yyyymmdd  = nowTime.strftime('%Y%m%d')
                                work_path = qPath_work + 'capture'
                                img       = qFFmpeg.capture(dev='desktop', full=True, work_path=work_path, )
                                if (img is not None):
                                    qLog.log('info', main_id, 'スクリーンキャプチャ')

                                    proc_img = cv2.resize(img, (320, 240))
                                    cv2.imshow('capture', proc_img)
                                    cv2.waitKey(1)

                                    # キャプチャ保存
                                    save_file = qPath_rec + stamp + '.capture.jpg'
                                    cv2.imwrite(save_file, img)

                                    if (qPath_pictures != ''):
                                        folder = qPath_pictures + yyyymmdd + '/'
                                        qFunc.makeDirs(folder)
                                    qFunc.copy(save_file, folder + stamp + '.capture.jpg')

                                    # クリップボードへ
                                    qGuide.img2clip(save_file)

                                    time.sleep(1.00)
                                    cv2.destroyWindow('capture')
                                    cv2.waitKey(1)

                                    qGuide.open()

                            # デスクトップ録画
                            if (qWinClock.last_icon == 'vcam'):
                                qGuide.close()
                                eyes = True

                                # レコーダー開始
                                nowTime   = datetime.datetime.now()
                                stamp     = nowTime.strftime('%Y%m%d.%H%M%S')
                                yyyymmdd  = nowTime.strftime('%Y%m%d')
                                work_path = qPath_work + 'capture'

                                rec_filev = qPath_work + 'recorder.mp4'
                                rec_filea = qPath_work + 'recorder.wav'
                                rec_ffmpeg, rec_sox, rec_filev, rec_filea = qFFmpeg.rec_start(dev='desktop', rate=10, 
                                                                                        out_filev=rec_filev, out_filea=rec_filea,
                                                                                        retry_max=3, retry_wait=5.00,)

                                rec_running = True
                                rec_time    = time.time()

                                qLog.log('info', main_id, 'デスクトップ録画　開始')


                else:
                    print(event, values, )

            # マウス位置チェック
            (x, y) = qGUI.position()
            if (x != last_mouse_x) or (y != last_mouse_y):

                # サイズ変更対応
                w, h = qGuide.window.size
                if (sg_no_titlebar == False):
                    sg_width  = w - 4
                    sg_height = h - 22
                else:
                    sg_width  = w
                    sg_height = h - 14
                qGuide.width  = sg_width
                qGuide.height = sg_height

                # 位置変更対応
                l, t, r, b = qGUI.getWindowRect(winTitle=sg_title,)
                if (l is not None):
                    sg_left  = l
                    sg_top   = t
                    if (sg_no_titlebar == False):
                        sg_left2 = l + 10
                        sg_top2  = t + 32
                    else:
                        sg_left2 = l
                        sg_top2  = t + 14

            # 時計
            dt_now    = datetime.datetime.now()
            dt_YYMMDD = dt_now.strftime('%Y%m%d')
            dt_YOUBI  = dt_now.strftime('%a')
            dt_HHMM   = dt_now.strftime('%H%M')
            dt_YYYYMMDDHHMM  = dt_now.strftime('%H%M')
            s = dt_now.second
            m = dt_now.minute
            h = dt_now.hour
    
            # 時報処理
            if (h != bk_h):
                bk_h=h

                qWinClock.timeSign_info(h, m, )

            # デザイン変更
            if (m != bk_m):
                bk_m=m

                design = h*60+m
                if (qWinClock.clock_design != 'auto'):
                    try:
                        design = int(qWinClock.clock_design)
                    except:
                        design = 0

            # アナログ時計
            if (runMode != 'digital') and (runMode != 'personal'):
                if (s != bk_s):
                    bk_s=s

                    img = qWinClock.getImage_analog(dt_now, design, )
                    #img = cv2.resize(img, (sg_width,sg_height))
                    #imgbytes = cv2.imencode('.png', img)[1].tobytes() 
                    #sg_win['-image-'].update(data=imgbytes)
                    qGuide.setImage(image=img, refresh=True, )

                    #canvas_elem = sg_win['-image-']
                    #canvas = canvas_elem.TKCanvas
                    #canvas.create_image(sg_width/2,sg_height/2,imgbytes)
                    
            # デジタル時計 digital, personal
            if (runMode == 'digital') or (runMode == 'personal'):
    
                img = qWinClock.getImage_digital(dt_now, design, eyes, sg_left2, sg_top2, sg_width, sg_height, )
                #img = cv2.resize(img, (sg_width,sg_height))
                #imgbytes = cv2.imencode('.png', img)[1].tobytes() 
                #sg_win['-image-'].update(data=imgbytes)
                qGuide.setImage(image=img, refresh=True, )

                #imgpil = qGuide.cv2pil(img)
                #imgphoto = ImageTk.PhotoImage(image=imgpil)
                #canvas_elem = sg_win['-image-']
                #canvas = canvas_elem.TKCanvas
                #canvas.create_image(sg_width/2,sg_height/2,imgbytes)

        except Exception as e:
            print(e)
            time.sleep(5.00)



    # 終了処理
    if (True):
        qLog.log('info', main_id, 'terminate')

        # ガイド消去
        try:
            qGuide.close()
            qGuide.terminate()
        except:
            pass

        # 終了
        qLog.log('info', main_id, 'bye!')

        sys.exit(0)


