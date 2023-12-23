#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2024 Mitsuo KONDOU.
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

import queue
import threading
import subprocess

import random

import numpy as np
import cv2

import PySimpleGUI as sg



# インターフェース
qCtrl_control_ImHere     = 'temp/control_ImHere.txt'
qCtrl_control_self       = qCtrl_control_ImHere



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
qCV2   = _v6__qFFmpeg.qCV2_class()



qPath_temp = 'temp/'
qPath_log  = 'temp/_log/'

qPath_rec  = 'temp/_recorder/'



import _v6__qRiKi_key

config_file = 'RiKi_ImHere_key.json'

qRiKi_key = _v6__qRiKi_key.qRiKi_key_class()
res, dic = qRiKi_key.getCryptJson(config_file=config_file, auto_crypt=False, )
if (res == False):
    dic['_crypt_']                  = 'none'
    dic['run_priority']             = 'auto'
    dic['ImHere_validSec']          = 90
    dic['mouse_check']              = 'yes'
    dic['cam_check']                = 'auto'
    dic['cam_start']                = '0600'
    dic['cam_end']                  = '2000'
    dic['lunch_start']              = '1200'
    dic['lunch_end']                = '1300'
    dic['cam_guide']                = 'auto'
    dic['guide_screen']             = 'auto'
    dic['guide_panel']              = 'auto'
    dic['dev_intervalSec']          = 30
    dic['cv2_camScan']              = 'all'
    dic['cv2_engine']               = 'ssd'
    dic['cv2_intervalSec']          = 2
    dic['cv2_sabunLimit']           = 0
    dic['cv2_sometime']             = 'no'
    dic['action60s_mouse']          = 'yes'
    dic['action60s_key']            = 'ctrl'
    dic['feedback_mouse']           = 'yes'
    dic['feedback_fileYes']         = 'temp/control_ImHere_yes.txt'
    dic['feedback_fileNo']          = 'temp/control_ImHere_no.txt'
    dic['reception_sound1_sttm']    = '0630'
    dic['reception_sound1_entm']    = '0900'
    dic['reception_sound1_file']    = '_sounds/_voice_ohayou.mp3'
    dic['reception_sound2_sttm']    = '0900'
    dic['reception_sound2_entm']    = '1700'
    dic['reception_sound2_file']    = '_sounds/_sound_pingpong.mp3'
    dic['reception_sound3_sttm']    = '1700'
    dic['reception_sound3_entm']    = '1900'
    dic['reception_sound3_file']    = '_sounds/_voice_otukare.mp3'

    res = qRiKi_key.putCryptJson(config_file=config_file, put_dic=dic, )



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

def save_photo(image, hit_name='photo', ):
    nowTime  = datetime.datetime.now()
    stamp    = nowTime.strftime('%Y%m%d.%H%M%S')
    yyyymmdd = stamp[:8]

    # 写真保存
    main_file = ''
    try:
        if (image is not None):
            main_file = qPath_rec + stamp + '.' + hit_name + '.jpg'
            cv2.imwrite(main_file, image)
    except Exception as e:
        main_file = ''

    # 写真コピー保存
    if (main_file != ''):
        if (qPath_pictures != ''):
            folder = qPath_pictures + yyyymmdd + '/'
            qFunc.makeDirs(folder)
            qFunc.copy(main_file, folder + stamp + '.' + hit_name + '.jpg')

    return True



class cam_check_class:

    def __init__(self, name='thread', id='0', runMode='debug', camDev='0', ):
        self.name      = name
        self.id        = id
        self.proc_id   = '{0:10s}'.format(name).replace(' ', '_')
        self.proc_id   = self.proc_id[:-2] + '_' + str(id)
        self.runMode   = runMode
        if (runMode == 'debug'):
            self.logDisp = True
        else:
            self.logDisp = False
        qLog.log('info', self.proc_id, 'init', display=self.logDisp, )

        self.camDev    = camDev

        # 構成情報
        json_file = config_file
        self.run_priority           = 'auto'
        self.ImHere_validSec        = 90
        self.mouse_check            = 'yes'
        self.cam_check              = 'auto'
        self.cam_start              = '0600'
        self.cam_end                = '2000'
        self.lunch_start            = '1200'
        self.lunch_end              = '1300'
        self.cam_guide              = 'auto'
        self.guide_screen           = 'auto'
        self.guide_panel            = 'auto'
        self.dev_intervalSec        = 30
        self.cv2_camScan            = 'all'
        self.cv2_engine             = 'ssd'
        self.cv2_intervalSec        = 1
        self.cv2_sabunLimit         = 0
        self.cv2_sometime           = 'no'
        self.action60s_mouse        = 'yes'
        self.action60s_key          = 'ctrl'
        self.feedback_mouse         = 'yes'
        self.feedback_fileYes       = 'temp/control_ImHere_yes.txt'
        self.feedback_fileNo        = 'temp/control_ImHere_no.txt'
        self.reception_sound1_sttm  = '0630'
        self.reception_sound1_entm  = '0900'
        self.reception_sound1_file  = '_sounds/_voice_ohayou.mp3'
        self.reception_sound2_sttm  = '0900'
        self.reception_sound2_entm  = '1700'
        self.reception_sound2_file  = '_sounds/_sound_pingpong.mp3'
        self.reception_sound3_sttm  = '1700'
        self.reception_sound3_entm  = '1900'
        self.reception_sound3_file  = '_sounds/_voice_otukare.mp3'
        res, json_dic = qRiKi_key.getCryptJson(config_file=json_file, auto_crypt=False, )
        if (res == True):
            self.run_priority           = json_dic['run_priority']
            self.ImHere_validSec        = json_dic['ImHere_validSec']
            self.mouse_check            = json_dic['mouse_check']
            self.cam_check              = json_dic['cam_check']
            self.cam_start              = json_dic['cam_start']
            self.cam_end                = json_dic['cam_end']
            self.lunch_start            = json_dic['lunch_start']
            self.lunch_end              = json_dic['lunch_end']
            self.cam_guide              = json_dic['cam_guide']
            self.guide_screen           = json_dic['guide_screen']
            self.guide_panel            = json_dic['guide_panel']
            self.dev_intervalSec        = json_dic['dev_intervalSec']
            self.cv2_camScan            = json_dic['cv2_camScan']
            self.cv2_engine             = json_dic['cv2_engine']
            self.cv2_intervalSec        = json_dic['cv2_intervalSec']
            self.cv2_sabunLimit         = json_dic['cv2_sabunLimit']
            self.cv2_sometime           = json_dic['cv2_sometime']
            self.action60s_mouse        = json_dic['action60s_mouse']
            self.action60s_key          = json_dic['action60s_key']
            self.feedback_mouse         = json_dic['feedback_mouse']
            self.feedback_fileYes       = json_dic['feedback_fileYes']
            self.feedback_fileNo        = json_dic['feedback_fileNo']
            self.reception_sound1_sttm  = json_dic['reception_sound1_sttm']
            self.reception_sound1_entm  = json_dic['reception_sound1_entm']
            self.reception_sound1_file  = json_dic['reception_sound1_file']
            self.reception_sound2_sttm  = json_dic['reception_sound2_sttm']
            self.reception_sound2_entm  = json_dic['reception_sound2_entm']
            self.reception_sound2_file  = json_dic['reception_sound2_file']
            self.reception_sound3_sttm  = json_dic['reception_sound3_sttm']
            self.reception_sound3_entm  = json_dic['reception_sound3_entm']
            self.reception_sound3_file  = json_dic['reception_sound3_file']
       
        # カメラ初期化
        self.qCV2 = _v6__qFFmpeg.qCV2_class()
        if (self.cv2_sometime != 'yes'):
            self.cam = self.qCV2.cv2open(dev=self.camDev, )
            time.sleep(0.50)

    def __del__(self):
        if (self.cv2_sometime != 'yes'):
            self.qCV2.cv2close()
            time.sleep(0.50)
        qLog.log('info', self.proc_id, 'bye!', display=self.logDisp, )

    def begin(self, ):
        self.breakFlag = threading.Event()
        self.breakFlag.clear()
        self.proc_s = queue.Queue()
        self.proc_r = queue.Queue()
        self.proc_main = threading.Thread(target=self.main_proc, args=(self.proc_s, self.proc_r, ), daemon=True, )
        self.proc_beat = time.time()
        self.proc_last = time.time()
        self.proc_seq  = 0
        self.proc_main.start()

    def abort(self, waitMax=5, ):
        qLog.log('info', self.proc_id, 'stop', display=self.logDisp, )
        chktime = time.time()
        while (self.proc_beat is not None) and ((time.time() - chktime) < waitMax):
            self.breakFlag.set()
            time.sleep(0.25)
    def put(self, data, ):
        self.proc_s.put(data)
        return True
    def checkGet(self, waitMax=5, ):
        chktime = time.time()
        while (self.proc_r.qsize() == 0) and ((time.time() - chktime) < waitMax):
            time.sleep(0.10)
        data = self.get()
        return data
    def get(self, ):
        if (self.proc_r.qsize() == 0):
            return ['', '']
        data = self.proc_r.get()
        self.proc_r.task_done()
        return data

    def main_proc(self, cn_r, cn_s, ):
        # ログ
        qLog.log('info', self.proc_id, 'start ' + self.camDev, display=self.logDisp, )
        self.proc_beat = time.time()

        last_check = time.time() - self.cv2_intervalSec

        # 初回差分無視　(静止画対策)
        if (True):

            # オープン
            if (self.cv2_sometime == 'yes'):
                self.cam = self.qCV2.cv2open(dev=self.camDev, )
                time.sleep(0.50)

            # イメージ取得
            frame = self.qCV2.cv2read()
            if (frame is not None):

                # 差分確認
                if (self.cv2_sabunLimit > 0):
                    sabun_img, sabun_ritu = self.qCV2.cv2sabun(inp_image=frame, )

            # クローズ
            if (self.cv2_sometime == 'yes'):
                self.cam = self.qCV2.cv2close()
                #time.sleep(0.50)

        # ループ
        while (True):
            self.proc_beat = time.time()

            # 停止要求確認
            if (self.breakFlag.is_set()):
                self.breakFlag.clear()
                break

            # キュー取得
            if (cn_r.qsize() > 0):
                cn_r_get  = cn_r.get()
                inp_name  = cn_r_get[0]
                inp_value = cn_r_get[1]
                cn_r.task_done()
            else:
                inp_name  = ''
                inp_value = ''

            if (cn_r.qsize() > 1) or (cn_s.qsize() > 20):
                qLog.log('warning', self.proc_id, 'queue overflow warning!, ' + str(cn_r.qsize()) + ', ' + str(cn_s.qsize()))

            # 画像処理
            if (cn_s.qsize() == 0):

                if ((time.time() - last_check) > self.cv2_intervalSec):
                    last_check = time.time()
                    detect_hit = False

                    # オープン
                    if (self.cv2_sometime == 'yes'):
                        self.cam = self.qCV2.cv2open(dev=self.camDev, )

                    # イメージ取得
                    frame = self.qCV2.cv2read()
                    if (frame is None):

                        # 再取得
                        qLog.log('warning', self.proc_id, 'cam read error reopen, ' + str(self.camDev))
                        self.cam = self.qCV2.cv2close()
                        time.sleep(0.50)
                        self.cam = self.qCV2.cv2open(dev=self.camDev, )
                        time.sleep(0.50)
                        frame = self.qCV2.cv2read()

                    if (frame is not None):

                        # ログ
                        if (float(self.cv2_intervalSec) >= 0.50):
                            qLog.log('info', self.proc_id, 'Cam Image Check', display=self.logDisp, )

                        # 差分確認
                        if (self.cv2_sabunLimit > 0):
                            sabun_img, sabun_ritu = self.qCV2.cv2sabun(inp_image=frame, )
                        else:
                            sabun_img  = frame.copy()
                            sabun_ritu = 0

                        if (sabun_ritu < self.cv2_sabunLimit):
                            out_name  = '[img]'
                            out_value = sabun_img.copy()
                            cn_s.put([out_name, out_value])

                        else:

                            # 人間確認
                            parson_imgs = []
                            face_imgs   = []
                            if   (self.cv2_engine=='yolov4'):
                                parson_img, parson_imgs, _, _, _ = qCV2.cv2detect_yolov4(inp_image=frame, search='person', )
                            elif (self.cv2_engine=='ssd'):
                                parson_img, parson_imgs, _, _, _ = qCV2.cv2detect_ssd(inp_image=frame, search='person', )
                            else:
                                face_img, face_imgs  = qCV2.cv2detect_cascade(inp_image=frame, search='face', )

                            if (self.cv2_engine=='yolov4') \
                            or (self.cv2_engine=='ssd'):
                                if (len(parson_imgs) > 0):
                                    detect_hit = True
                                    out_name  = '[person_raw]'
                                    out_value = frame.copy()
                                    cn_s.put([out_name, out_value])
                                    out_name  = '[person_img]'
                                    out_value = parson_img.copy()
                                    cn_s.put([out_name, out_value])
                                else:
                                    out_name  = '[img]'
                                    out_value = sabun_img.copy()
                                    cn_s.put([out_name, out_value])
                            else:
                                if (len(face_imgs) > 0):
                                    detect_hit = True
                                    out_name  = '[face_raw]'
                                    out_value = frame.copy()
                                    cn_s.put([out_name, out_value])
                                    out_name  = '[face_img]'
                                    out_value = face_imgs[0].copy()
                                    cn_s.put([out_name, out_value])
                                else:
                                    out_name  = '[img]'
                                    out_value = sabun_img.copy()
                                    cn_s.put([out_name, out_value])

                    # クローズ
                    if (self.cv2_sometime == 'yes'):
                        self.cam = self.qCV2.cv2close()
                        last_check = time.time()

                    if (detect_hit == True):
                        last_check = time.time() + self.cv2_intervalSec

            # アイドリング
            time.sleep(0.50)



        # 終了処理
        if (True):

            # キュー削除
            while (cn_r.qsize() > 0):
                cn_r_get = cn_r.get()
                cn_r.task_done()
            while (cn_s.qsize() > 0):
                cn_s_get = cn_s.get()
                cn_s.task_done()

            # 停止サイン
            self.proc_beat = None

            # ログ
            qLog.log('info', self.proc_id, 'end', display=self.logDisp, )



# シグナル処理
import signal
def signal_handler(signal_number, stack_frame):
    print(os.path.basename(__file__), 'accept signal =', signal_number)

#signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGINT,  signal.SIG_IGN)
signal.signal(signal.SIGTERM, signal.SIG_IGN)



#runMode  = 'debug'
runMode  = 'personal'
#runMode  = 'reception'
camScan  = ''
#camScan  = 'http://repair-fujitsu:5555/MotionJpeg?w=640&h=480'



if __name__ == '__main__':
    main_name = 'ImHere'
    main_id   = '{0:10s}'.format(main_name).replace(' ', '_')

    # ディレクトリ作成
    qFunc.makeDirs(qPath_temp, remove=15, )
    qFunc.makeDirs(qPath_log,  remove=15, )
    qFunc.makeDirs(qPath_rec,  remove=15, )

    # ログ
    nowTime  = datetime.datetime.now()
    filename = qPath_log + nowTime.strftime('%Y%m%d.%H%M%S') + '.' + os.path.basename(__file__) + '.log'
    qLog.init(mode='logger', filename=filename, )
    qLog.log('info', main_id, 'init')
    qLog.log('info', main_id, 'exsample.py runMode, ')

    # パラメータ
    if (len(sys.argv) >= 2):
        runMode  = str(sys.argv[1]).lower()
    if (len(sys.argv) >= 3):
        camScan  = str(sys.argv[2])

    qLog.log('info', main_id, 'runMode = ' + str(runMode))
    qLog.log('info', main_id, 'camScan = ' + str(camScan))

    # 初期設定
    if (True):

        # コントロールリセット
        txts, txt = qFunc.txtsRead(qCtrl_control_self)
        if (txts != False):
            if (txt == '_end_') or (txt == '_stop_'):
                qFunc.remove(qCtrl_control_self)

        # config確認
        json_file = config_file
        run_priority            = 'auto'
        ImHere_validSec         = 90
        mouse_check             = 'yes'
        cam_check               = 'auto'
        cam_start               = '0600'
        cam_end                 = '2000'
        lunch_start             = '1200'
        lunch_end               = '1300'
        cam_guide               = 'auto'
        guide_screen            = 'auto'
        guide_panel             = 'auto'
        dev_intervalSec         = 30
        cv2_camScan             = 'all'
        action60s_mouse         = 'yes'
        action60s_key           = 'ctrl'
        feedback_mouse          = 'yes'
        feedback_fileYes        = 'temp/qWinImHere_yes.txt'
        feedback_fileNo         = 'temp/qWinImHere_no.txt'
        reception_sound1_sttm   = '0630'
        reception_sound1_entm   = '0900'
        reception_sound1_file   = '_sounds/_voice_ohayou.mp3'
        reception_sound2_sttm   = '0900'
        reception_sound2_entm   = '1700'
        reception_sound2_file   = '_sounds/_sound_pingpong.mp3'
        reception_sound3_sttm   = '1700'
        reception_sound3_entm   = '1900'
        reception_sound3_file   = '_sounds/_voice_otukare.mp3'
        try:
            res, json_dic = qRiKi_key.getCryptJson(config_file=json_file, auto_crypt=False, )
            if (res == True):
                run_priority            = json_dic['run_priority']
                ImHere_validSec         = json_dic['ImHere_validSec']
                mouse_check             = json_dic['mouse_check']
                cam_check               = json_dic['cam_check']
                cam_start               = json_dic['cam_start']
                cam_end                 = json_dic['cam_end']
                lunch_start             = json_dic['lunch_start']
                lunch_end               = json_dic['lunch_end']
                cam_guide               = json_dic['cam_guide']
                guide_screen            = json_dic['guide_screen']
                guide_panel             = json_dic['guide_panel']
                dev_intervalSec         = json_dic['dev_intervalSec']
                cv2_camScan             = json_dic['cv2_camScan']
                action60s_mouse         = json_dic['action60s_mouse']
                action60s_key           = json_dic['action60s_key']
                feedback_mouse          = json_dic['feedback_mouse']
                feedback_fileYes        = json_dic['feedback_fileYes']
                feedback_fileNo         = json_dic['feedback_fileNo']
                reception_sound1_sttm   = json_dic['reception_sound1_sttm']
                reception_sound1_entm   = json_dic['reception_sound1_entm']
                reception_sound1_file   = json_dic['reception_sound1_file']
                reception_sound2_sttm   = json_dic['reception_sound2_sttm']
                reception_sound2_entm   = json_dic['reception_sound2_entm']
                reception_sound2_file   = json_dic['reception_sound2_file']
                reception_sound3_sttm   = json_dic['reception_sound3_sttm']
                reception_sound3_entm   = json_dic['reception_sound3_entm']
                reception_sound3_file   = json_dic['reception_sound3_file']
        except:
            pass

        # 実行優先設定
        nice = run_priority
        if (nice == 'auto'):
            nice = 'below'
        qFunc.setNice(nice, )

        # カメラ指定
        if (camScan != ''):
            cv2_camScan = camScan

        # スクリーン、パネル指定
        if (guide_screen == 'auto'):
            guide_screen = '0'
        if (guide_panel == 'auto'):
            guide_panel = '8--'

    # 起動
    if (True):
        qLog.log('info', main_id, 'start')

        ImHere          = True
        last_ImHere     = time.time() - ImHere_validSec

        dev_setting     = True
        dev_lastCheck   = time.time()

        cam_count       = 0
        cam_class       = {}
        last_img        = {}
    
        last_action_mouse = time.time()
        (last_x, last_y)  = qGUI.position()
        last_action_key   = time.time()

        last_sound_play   = time.time() - 60

        # ファイル連携
        filename = feedback_fileYes
        if (filename != ''):
            if (qFunc.statusCheck(filename) == True):
                qFunc.statusSet(filename, False)
        filename = feedback_fileNo
        if (filename != ''):
            if (qFunc.statusCheck(filename) == True):
                qFunc.statusSet(filename, False)

    # 待機ループ
    break_flag = False
    while (break_flag == False):

        try:
            now_dt   = datetime.datetime.now()
            now_HHMM = now_dt.strftime('%H%M')

            # -----------------------
            # 終了確認
            # -----------------------
            txts, txt = qFunc.txtsRead(qCtrl_control_self)
            if (txts != False):
                if (txt == '_end_'):
                    break_flag = True
                    break

            # -----------------------
            # 変化確認
            # -----------------------
            new_ImHere = ImHere
            ImHere_hit = ''
            if (ImHere == True) and ((time.time() - last_ImHere) > ImHere_validSec):
                new_ImHere = False

            # -----------------------
            # マウス確認
            # -----------------------
            if (mouse_check != 'no') and (mouse_check != 'off'):
                (x, y) = qGUI.position()
                if (abs(last_x-x) >= 50) or (abs(last_y-y) >= 50):
                    if (new_ImHere == False) and (ImHere_hit == ''):
                        ImHere_hit = 'mouse'
                        qLog.log('info', main_id, 'ImHere! (mouse)')
                    else:
                        ImHere_hit = 'mouse'
                last_x = x
                last_y = y

            # -----------------------
            # アクション
            # -----------------------
            if (ImHere_hit == ''):
                if (runMode != 'reception'):

                    # ６０秒経過でマウスアクション
                    if (action60s_mouse != 'no') and (action60s_mouse != 'off'):

                        if ((time.time() - last_ImHere) > 60):
                            if ((time.time() - last_action_mouse) > 15):
                                last_action_mouse = time.time()

                                l,t,w,h = qGUI.getScreenPosSize(screen=0, )
                                (x, y)  = qGUI.position()

                                # マウス移動
                                x += int(random.random() * 10) - 5
                                if (x < (l + 100)):
                                    x = (l + 100)
                                if (x > (l+w-100)):
                                    x = (l+w-100)
                                y += int(random.random() * 10) - 5
                                if (y < (t+100)):
                                    y = (t+100)
                                if (y > (t+h-100)):
                                    y = (t+h-100)
                                qGUI.moveTo(int(x), int(y))
            
                                qLog.log('info', main_id, 'Idol Mouse Action, Position = (' + str(last_x) + ', ' + str(last_y) + ')', )
                                (last_x, last_y) = qGUI.position()

                    # ６０秒経過でキーアクション
                    if (action60s_key != ''):

                        if ((time.time() - last_ImHere) > 60):
                            if ((time.time() - last_action_key) > 60):
                                last_action_key = time.time()

                                # ctrlキー
                                qLog.log('info', main_id, 'Idol Key Action,   Press = "' + action60s_key + '"', )
                                try:
                                    qGUI.press(action60s_key)
                                except Exception as e:
                                    pass

            # -----------------------
            # カメラ起動
            # -----------------------
            if  (cam_check == 'yes') \
            or ((cam_check == 'auto') and (new_ImHere == False) and (ImHere_hit == '')):

                # カメラ設定
                if (dev_setting == True) or ((time.time()-dev_lastCheck) > dev_intervalSec):
                    dev_lastCheck = time.time()
                    cam_list, mic_list = qFFmpeg.ffmpeg_list_dev()
                    if (dev_setting == True) or (len(cam_list) != cam_count):
                        dev_setting = False
                        if (runMode != 'reception'):
                            qLog.log('info', main_id, 'Camera (re) Setting... ')
                        #print(cam_list)

                        # ガイド消去
                        if (cam_guide == 'auto'):
                            if (qGuide.window is not None):
                                qLog.log('info', main_id, 'Guide display end.')
                                qGuide.close()
                                qGuide.terminate()

                        # スレッド終了
                        if (len(cam_class) > 0):
                            for c in cam_class.keys():
                                if (cam_class[c] is not None):
                                    cam_class[c].abort()
                                    #del cam_class[c]
                                    cam_class[c] = None
                            cam_class = {}
                            last_img  = {}
                        cam_count = 0

                        # 時間帯確認
                        if  (runMode == 'personal') \
                        or  ( \
                                ((now_HHMM >= cam_start) and (now_HHMM <= cam_end)) \
                            and ((now_HHMM < lunch_start) or (now_HHMM > lunch_end)) \
                            ):

                            # カメラ変更
                            cam_count = len(cam_list)

                            # カメラ指定
                            st, en = None, None
                            if   (cv2_camScan == 'all'):
                                st, en = 0, cam_count
                            elif (cv2_camScan == 'min'):
                                st , en = 0, 1
                            elif (cv2_camScan == 'max'):
                                st , en = cam_count-1, cam_count
                            elif (str(cv2_camScan).isdigit()):
                                st , en = int(cv2_camScan), int(cv2_camScan)+1

                            # スレッド起動
                            if (st is not None) and (en is not None):
                                for c in range(st, en):
                                    id = str(c)
                                    cam_class[c] = cam_check_class(name='cam_proc', id=id, runMode=runMode, camDev=str(c), )
                                    cam_class[c].begin()
                                    last_img[c] = None
                                    time.sleep(3.00)
                            else:
                                    c  = 0
                                    id = str(c)
                                    cam_class[c] = cam_check_class(name='cam_proc', id=id, runMode=runMode, camDev=str(cv2_camScan), )
                                    cam_class[c].begin()
                                    last_img[c] = None
                                    time.sleep(3.00)

                        # ガイド表示
                        if (cam_guide == 'yes') and (len(cam_class) > 0):
                            if (qGuide.window is None):
                                qLog.log('info', main_id, 'Guide display start.')
                                sg_title = os.path.basename(__file__)
                                sg_title = sg_title.replace('.py','')
                                qGuide.init(screen=guide_screen, panel=guide_panel, title=sg_title, image=None, alpha_channel=1, )
                                qGuide.open()

            # -----------------------
            # 画像取得
            # -----------------------
            if (len(cam_class) > 0):

                # 画像取得
                for c in cam_class.keys():
                    if (cam_class[c] is not None):
                        while (cam_class[c].proc_r.qsize() > 0):
                            res_data  = cam_class[c].get()
                            res_name  = res_data[0]
                            res_value = res_data[1]
                            if   (res_name == ''):
                                break

                            elif (res_name == '[img]'):
                                last_img[c] = res_value.copy()

                            elif (res_name == '[person_raw]') or (res_name == '[person_img]'):
                                last_img[c] = res_value.copy()
                                if (res_name == '[person_raw]'):
                                    if (new_ImHere == False) and (ImHere_hit == ''):
                                        ImHere_hit = 'person'
                                        qLog.log('info', main_id, 'ImHere! (person:' + str(c) + ')')
                                    if  (runMode != 'personal'):
                                        save_photo(res_value.copy(), hit_name='person', )

                            elif (res_name == '[face_raw]') or (res_name == '[face_img]'):
                                last_img[c] = res_value.copy()
                                if (res_name == '[face_raw]'):
                                    if (new_ImHere == False) and (ImHere_hit == ''):
                                        ImHere_hit = 'face'
                                        qLog.log('info', main_id, 'ImHere! (face:' + str(c) + ')')
                                    if  (runMode != 'personal'):
                                        save_photo(res_value.copy(), hit_name='face', )

            # -----------------------
            # 画像生成
            # -----------------------
            dsp_image = None
            if (len(cam_class) > 0):

                width, height = 1280, 720

                img_onece = True 
                i = 0
                for c in cam_class.keys():
                    if (last_img[c] is not None):

                        if (len(cam_class) == 1):
                            img = cv2.resize(last_img[c], (width,height))
                            dsp_image = img
                        
                        else:
                            if (img_onece == True):
                                img_onece = False
                                dsp_image = np.zeros((height,width,3), np.uint8)

                            i += 1
                            if   ((i % 4) == 1):
                                w,h = 0,0
                            elif ((i % 4) == 2):
                                w,h = int(width/2),0
                            elif ((i % 4) == 3):
                                w,h = 0,int(height/2)
                            else:
                                w,h = int(width/2),int(height/2)
                            img = cv2.resize(last_img[c], (int(width/2),int(height/2)))
                            dsp_image[h:h+int(height/2),w:w+int(width/2)] = img

            # -----------------------
            # ガイド表示
            # -----------------------
            if (dsp_image is not None):
                if (cam_guide == 'yes') \
                or ((cam_guide == 'auto') and (ImHere == False)):

                    # ガイド表示
                    if (qGuide.window is None):
                        qLog.log('info', main_id, 'Guide display start.')
                        sg_title = os.path.basename(__file__)
                        sg_title = sg_title.replace('.py','')
                        qGuide.init(screen=guide_screen, panel=guide_panel, title=sg_title, image=None, alpha_channel=1, )
                        qGuide.open()

                    # 画像更新
                    qGuide.setImage(image=dsp_image, )

                    # イベントの読み込み                  ↓　timeout値でtime.sleep代用
                    event, values = qGuide.read(timeout=250, )
                    # ウィンドウの×ボタンクリックで終了
                    if event == sg.WIN_CLOSED:
                        #break_flag = True
                        #break
                        pass

                    if event in (None, '-exit-'):
                        #break_flag = True
                        #break
                        pass

                    if (event == '-timeout-'):
                        pass
                    else:
                        print(event, values, )        

            # -----------------------
            # ImHere ?
            # -----------------------
            if (new_ImHere == False) and (ImHere_hit != ''):

                # フィードバックアクション
                if (ImHere_hit != 'mouse'):
                    if (runMode != 'reception'):

                        if (feedback_mouse != 'no') and (feedback_mouse != 'off'):
                            (last_x, last_y) = qGUI.position()
                            l,t,w,h = qGUI.getScreenPosSize(screen=0, )

                            x, y  = last_x, last_y
                            while not((abs(last_x-x) >= 60) or (abs(last_y-y) >= 60)):
                                # マウス移動
                                x += int(random.random() * 60) - 30
                                if (x < (l + 100)):
                                    x = (l + 100)
                                if (x > (l+w-100)):
                                    x = (l+w-100)
                                y += int(random.random() * 60) - 30
                                if (y < (t+100)):
                                    y = (t+100)
                                if (y > (t+h-100)):
                                    y = (t+h-100)
                                #qGUI.moveTo(int(x),int(y))

                            qGUI.moveTo(int(x),int(y))
                            (last_x, last_y) = qGUI.position()
                            qLog.log('info', main_id, 'Feedback Mouse Action, Position = (' + str(last_x) + ', ' + str(last_y) + ')', )

                # サウンドフィードバック
                if (ImHere_hit != 'mouse'):
                    if (runMode != 'personal'):
    
                        if ((time.time() - last_sound_play) > 60):

                            if  (reception_sound1_file != '') \
                            and (now_HHMM >= reception_sound1_sttm) \
                            and (now_HHMM <  reception_sound1_entm):
                                qLog.log('info', main_id, 'Feedback Sound = ' + reception_sound1_file, )
                                qFunc.guideSound(filename=reception_sound1_file, sync=False, )
                                last_sound_play = time.time()

                            if  (reception_sound2_file != '') \
                            and (now_HHMM >= reception_sound2_sttm) \
                            and (now_HHMM <  reception_sound2_entm):
                                qLog.log('info', main_id, 'Feedback Sound = ' + reception_sound2_file, )
                                qFunc.guideSound(filename=reception_sound2_file, sync=False, )
                                last_sound_play = time.time()

                            if  (reception_sound3_file != '') \
                            and (now_HHMM >= reception_sound3_sttm) \
                            and (now_HHMM <  reception_sound3_entm):
                                qLog.log('info', main_id, 'Feedback Sound = ' + reception_sound3_file, )
                                qFunc.guideSound(filename=reception_sound3_file, sync=False, )
                                last_sound_play = time.time()

            if (ImHere_hit == ''):
                if (ImHere == True) and (new_ImHere == False):
                    qLog.log('info', main_id, 'Where, Me ?')
                ImHere = new_ImHere
            else:
                ImHere = True
                last_ImHere = time.time()
                ## Debug! 30秒
                #last_ImHere = time.time() - ImHere_validSec + 30

            # -----------------------
            # 時間外？
            # -----------------------
            if  (runMode != 'personal') \
            and  ( \
                    ((now_HHMM < cam_start) or (now_HHMM > cam_end)) \
                or  ((now_HHMM >= lunch_start) and (now_HHMM <= lunch_end)) \
                ):

                # スレッド終了
                if (len(cam_class) > 0):
                    for c in cam_class.keys():
                        if (cam_class[c] is not None):
                            cam_class[c].abort()
                            #del cam_class[c]
                            cam_class[c] = None
                    cam_class = {}
                    last_img  = {}
                    dev_setting = True

                # ガイド消去
                if (cam_guide == 'auto'):
                    if (qGuide.window is not None):
                        qLog.log('info', main_id, 'Guide display end.')
                        qGuide.close()
                        qGuide.terminate()

            # -----------------------
            # ImHere = Yes!
            # -----------------------
            if (ImHere == True):

                # ファイル連携
                filename = feedback_fileYes
                if (filename != ''):
                    if (qFunc.statusCheck(filename) == False):
                        qFunc.statusSet(filename, True)
                filename = feedback_fileNo
                if (filename != ''):
                    if (qFunc.statusCheck(filename) == True):
                        qFunc.statusSet(filename, False)

                # スレッド終了
                if (cam_check == 'auto'):
                    if (len(cam_class) > 0):
                        for c in cam_class.keys():
                            if (cam_class[c] is not None):
                                cam_class[c].abort()
                                #del cam_class[c]
                                cam_class[c] = None
                        cam_class = {}
                        last_img  = {}
                        dev_setting = True

                # ガイド消去
                if (cam_guide == 'auto'):
                    if (qGuide.window is not None):
                        qLog.log('info', main_id, 'Guide display end.')
                        qGuide.close()
                        qGuide.terminate()

            # -----------------------
            # ImHere = No!
            # -----------------------
            if (ImHere == False):

                # ファイル連携
                filename = feedback_fileYes
                if (filename != ''):
                    if (qFunc.statusCheck(filename) == True):
                        qFunc.statusSet(filename, False)
                filename = feedback_fileNo
                if (filename != ''):
                    if (qFunc.statusCheck(filename) == False):
                        qFunc.statusSet(filename, True)

            # -----------------------
            # メインビート
            # -----------------------
            if (ImHere == True):
                time.sleep(1.00)
            else:
                time.sleep(0.50)

        except Exception as e:
            print(e)
            time.sleep(5.00)



    # 終了処理
    if (True):
        qLog.log('info', main_id, 'terminate')

        # スレッド終了
        for c in cam_class.keys():
            if (cam_class[c] is not None):
                cam_class[c].abort()
                #del cam_class[c]
                cam_class[c] = None

        # ガイド消去
        qGuide.close()
        qGuide.terminate()

        # 終了
        qLog.log('info', main_id, 'bye!')

        sys.exit(0)


