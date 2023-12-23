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

import psutil
import random

import queue
import threading

import numpy as np
import cv2

#import gc

import platform
qPLATFORM = platform.system().lower() #windows,darwin,linux
python_exe = 'python'
if (qPLATFORM == 'darwin'):
    python_exe = 'python3'

qRUNATTR  = 'python'
if getattr(sys, 'frozen', False):
    qRUNATTR = 'exe'



# インターフェース
qCtrl_control_video = 'temp/control_video.txt'
qCtrl_control_self  = qCtrl_control_video



# 共通ルーチン
import    _v6__qFunc
qFunc   = _v6__qFunc.qFunc_class()
import    _v6__qGUI
qGUI    = _v6__qGUI.qGUI_class()
import    _v6__qGuide
qGuide  = _v6__qGuide.qGuide_class()
import    _v6__qFFmpeg
qCV2    = _v6__qFFmpeg.qCV2_class()
#qFFmpeg= _v6__qFFmpeg.qFFmpeg_class()
qFFplay = _v6__qFFmpeg.qFFplay_class()
import    _v6__qLog
qLog    = _v6__qLog.qLog_class()



qPath_temp  = 'temp/'
qPath_log   = 'temp/_log/'
qPath_work  = 'temp/_work/'



import _v6__qRiKi_key

config_file = 'RiKi_showMeVideo_key.json'

qRiKi_key = _v6__qRiKi_key.qRiKi_key_class()
res, dic = qRiKi_key.getCryptJson(config_file=config_file, auto_crypt=False, )
if (res == False):
    dic['_crypt_']              = 'none'
    dic['run_priority']         = 'auto'
    dic['run_limitSec']         = 'auto'
    dic['engine']               = 'ffplay'
    dic['telop_path']           = 'temp/d6_7telop_txt/'
    dic['shuffle_play']         = 'yes'
    dic['img2mov_play']         = 'yes'
    dic['img2mov_sec']          = 60
    dic['img2mov_zoom']         = 'yes'
    dic['play_screen']          = 'auto'
    dic['play_panel']           = 'auto'
    dic['play_path_winos']      = 'C:/Users/Public/'
    dic['play_path_macos']      = '/Users/Shared/'
    dic['play_path_linux']      = '/users/kondou/Documents/'
    dic['play_folder']          = '_m4v__Clip/Perfume/'
    dic['play_volume']          = 100
    dic['play_fadeActionSec']   = 0
    dic['play_file_telop']      = 'no'
    dic['play_changeSec']       = 0
    dic['play_stopByMouseSec']  = 0
    dic['bgm_screen']           = 'auto'
    dic['bgm_panel']            = 'auto'
    dic['bgm_folder']           = 'BGM/'
    dic['bgm_volume']           = 20
    dic['bgm_fadeActionSec']    = 2
    dic['bgm_file_telop']       = 'yes'
    dic['bgm_changeSec']        = 1200
    dic['bgm_stopByMouseSec']   = 180
    dic['bgv_screen']           = 'auto'
    dic['bgv_panel']            = 'auto'
    dic['bgv_folder']           = 'BGV/'
    dic['bgv_volume']           = 0
    dic['bgv_fadeActionSec']    = 4
    dic['bgv_file_telop']       = 'no'
    dic['bgv_changeSec']        = 300
    dic['bgv_stopByMouseSec']   = 180
    dic['bgv_overlayTime']      = 'yes'
    dic['bgv_overlayDate']      = 'yes'
    dic['day_control']          = 'week'
    dic['day_start']            = '06:25:00'
    dic['day_end']              = '18:35:00'
    dic['lunch_control']        = 'yes'
    dic['lunch_start']          = '12:00:00'
    dic['lunch_end']            = '13:00:00'
    res = qRiKi_key.putCryptJson(config_file=config_file, put_dic=dic, )



# cpuClock,saap_worker,showMeVideo 同一ロジック
def telopMSG(telop_path='', file_seq=0, title='Message', txt='', ):
    if (txt == ''):
        return False
    if (telop_path == ''):
        return False
    if (title.find('【') < 0):
        title = '【' + title + '】'
    txt = title + '\r\n' + txt

    now   = datetime.datetime.now()
    stamp = now.strftime('%Y%m%d%H%M%S')
    #self.file_seq += 1
    #if (self.file_seq > 9999):
    #    self.file_seq = 1
    seq4 = '{:04}'.format(file_seq)

    filename = telop_path + stamp + '.' + seq4 + '.showMeVideo.txt'

    res = qFunc.txtsWrite(filename, txts=[txt], mode='w', exclusive=True, )
    if (res == False):
        print('★Telop書込エラー')
        return False        

    return True        



# シグナル処理
import signal
def signal_handler(signal_number, stack_frame):
    print(os.path.basename(__file__), 'accept signal =', signal_number)

#signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGINT,  signal.SIG_IGN)
signal.signal(signal.SIGTERM, signal.SIG_IGN)



#runMode = 'debug'
runMode = 'bgmusic'
#runMode = 'bgvideo'
#runMode = 'bgm'
#runMode = 'bgv'

p_screen = ''
p_panel  = ''
p_path   = ''
#p_path   = 'C:/_共有/'
p_folder = ''
#p_folder = 'BGV/'
p_volume = ''



if __name__ == '__main__':
    main_name = 'player0'
    if (len(sys.argv) >= 2):
        runMode  = str(sys.argv[1]).lower()
        if (runMode == 'bgm') or (runMode == 'bgmusic') \
        or (runMode == 'bgv') or (runMode == 'bgvideo'):
            main_name = runMode + '0'
    if (len(sys.argv) >= 3):
        if (str(sys.argv[2]).isdigit()):
            main_name = main_name[:-1] + str(sys.argv[2])
    main_id   = '{0:10s}'.format(main_name).replace(' ', '_')

    # ディレクトリ作成
    qFunc.makeDirs(qPath_temp, remove=False, )
    qFunc.makeDirs(qPath_log,  remove=False, )
    qFunc.makeDirs(qPath_work, remove=False, )

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
            p_path   = str(sys.argv[4])
        if (len(sys.argv) >= 6):
            p_folder = str(sys.argv[5])
        if (len(sys.argv) >= 7):
            p_volume = str(sys.argv[6])

        qLog.log('info', main_id, 'runMode = ' + str(runMode ))
        qLog.log('info', main_id, 'screen  = ' + str(p_screen))
        qLog.log('info', main_id, 'panel   = ' + str(p_panel ))
        qLog.log('info', main_id, 'path    = ' + str(p_path  ))
        qLog.log('info', main_id, 'folder  = ' + str(p_folder))
        qLog.log('info', main_id, 'volume  = ' + str(p_volume))

        # config確認
        json_file = config_file
        run_priority        = 'auto'
        run_limitSec        = 'auto'
        engine              = 'ffplay'
        telop_path          = 'temp/d6_7telop_txt/'
        shuffle_play        = 'yes'
        img2mov_play        = 'yes'
        img2mov_sec         = 60
        img2mov_zoom        = 'yes'
        play_screen         = 'auto'
        play_panel          = 'auto'
        play_path_winos     = 'C:/Users/Public/'
        play_path_macos     = '/Users/Shared/'
        play_path_linux     = '/users/kondou/Documents/'
        play_folder         = '_m4v__Clip/Perfume/'
        play_volume         = 100
        play_fadeActionSec  = 0
        play_file_telop     = 'no'
        play_changeSec      = 0
        play_stopByMouseSec = 0
        bgm_screen          = 'auto'
        bgm_panel           = 'auto'
        bgm_folder          = 'BGM/'
        bgm_volume          = 20
        bgm_fadeActionSec   = 2
        bgm_file_telop      = 'yes'
        bgm_changeSec       = 1200
        bgm_stopByMouseSec  = 180
        bgv_screen          = 'auto'
        bgv_panel           = 'auto'
        bgv_folder          = 'BGV/'
        bgv_volume          = 0
        bgv_fadeActionSec   = 4
        bgv_file_telop      = 'no'
        bgv_changeSec       = 300
        bgv_stopByMouseSec  = 180
        bgv_overlayTime     = 'yes'
        bgv_overlayDate     = 'yes'
        day_control         = 'week'
        day_start           = '06:25:00'
        day_end             = '18:35:00'
        lunch_control       = 'yes'
        lunch_start         = '12:00:00'
        lunch_end           = '13:00:00'
        try:
            res, json_dic = qRiKi_key.getCryptJson(config_file=json_file, auto_crypt=False, )
            if (res == True):
                run_priority        = json_dic['run_priority']
                run_limitSec        = json_dic['run_limitSec']
                engine              = json_dic['engine']
                telop_path          = json_dic['telop_path']
                shuffle_play        = json_dic['shuffle_play']
                img2mov_play        = json_dic['img2mov_play']
                img2mov_sec         = json_dic['img2mov_sec']
                img2mov_zoom        = json_dic['img2mov_zoom']
                play_screen         = json_dic['play_screen']
                play_panel          = json_dic['play_panel']
                play_path_winos     = json_dic['play_path_winos']
                play_path_macos     = json_dic['play_path_macos']
                play_path_linux     = json_dic['play_path_linux']
                play_folder         = json_dic['play_folder']
                play_volume         = json_dic['play_volume']
                play_fadeActionSec  = json_dic['play_fadeActionSec']
                play_file_telop     = json_dic['play_file_telop']
                play_changeSec      = json_dic['play_changeSec']
                play_stopByMouseSec = json_dic['play_stopByMouseSec']
                bgm_screen          = json_dic['bgm_screen']
                bgm_panel           = json_dic['bgm_panel']
                bgm_folder          = json_dic['bgm_folder']
                bgm_volume          = json_dic['bgm_volume']
                bgm_fadeActionSec   = json_dic['bgm_fadeActionSec']
                bgm_file_telop      = json_dic['bgm_file_telop']
                bgm_changeSec       = json_dic['bgm_changeSec']
                bgm_stopByMouseSec  = json_dic['bgm_stopByMouseSec']
                bgv_screen          = json_dic['bgv_screen']
                bgv_panel           = json_dic['bgv_panel']
                bgv_folder          = json_dic['bgv_folder']
                bgv_volume          = json_dic['bgv_volume']
                bgv_fadeActionSec   = json_dic['bgv_fadeActionSec']
                bgv_file_telop      = json_dic['bgv_file_telop']
                bgv_changeSec       = json_dic['bgv_changeSec']
                bgv_stopByMouseSec  = json_dic['bgv_stopByMouseSec']
                bgv_overlayTime     = json_dic['bgv_overlayTime']
                bgv_overlayDate     = json_dic['bgv_overlayDate']
                day_control         = json_dic['day_control']
                day_start           = json_dic['day_start']
                day_end             = json_dic['day_end']
                lunch_control       = json_dic['lunch_control']
                lunch_start         = json_dic['lunch_start']
                lunch_end           = json_dic['lunch_end']
        except:
            pass

        # 実行優先設定
        nice = run_priority
        if (nice == 'auto'):
            nice = 'below'
        qFunc.setNice(nice, )

        # 実行時間
        if (run_limitSec == 'auto'):
            run_limitSec = 0
            if (runMode == 'bgm') or (runMode == 'bgmusic') \
            or (runMode == 'bgv') or (runMode == 'bgvideo'):
                run_limitSec = 3600 * 3 #3時間
        run_limitSec = int(run_limitSec)

        # ディレクトリ作成
        qFunc.makeDirs(telop_path, remove=False, )

        play_path = ''
        if (os.name == 'nt'):
            play_path = play_path_winos
        elif (qPLATFORM == 'darwin'):
            play_path = play_path_macos
        else:
            play_path = play_path_linux
        play_overlayTime = 'no'
        play_overlayDate = 'no'

        if   (runMode == 'bgm') or (runMode == 'bgmusic'):
            play_screen         = bgm_screen
            play_panel          = bgm_panel
            #play_path           = bgm_path
            play_folder         = bgm_folder
            play_volume         = bgm_volume
            play_fadeActionSec  = bgm_fadeActionSec
            play_file_telop     = bgm_file_telop
            play_changeSec      = bgm_changeSec
            play_stopByMouseSec = bgm_stopByMouseSec
            play_overlayTime    = 'no'
            play_overlayDate    = 'no'
        elif (runMode == 'bgv') or (runMode == 'bgvideo'):
            play_screen         = bgv_screen
            play_panel          = bgv_panel
            #play_path           = bgv_path
            play_folder         = bgv_folder
            play_volume         = bgv_volume
            play_fadeActionSec  = bgv_fadeActionSec
            play_file_telop     = bgv_file_telop
            play_changeSec      = bgv_changeSec
            play_stopByMouseSec = bgv_stopByMouseSec
            play_overlayTime    = bgv_overlayTime
            play_overlayDate    = bgv_overlayDate

        if (p_screen != ''):
            play_screen = p_screen
        if (p_panel != ''):
            play_panel  = p_panel
        if (p_path != ''):
            play_path   = p_path
        if (p_folder != ''):
            play_folder = p_folder
        if (p_volume != ''):
            play_volume = int(p_volume)

    # 初期設定
    if (True):

        # コントロールリセット
        txts, txt = qFunc.txtsRead(qCtrl_control_self)
        if (txts != False):
            if (txt == '_end_') or (txt == '_stop_'):
                qFunc.remove(qCtrl_control_self)

        # 再生リスト
        path = play_path + play_folder
        play_files = []
        if   (os.path.isfile(path)):
            play_files.append(path)
        elif (os.path.isdir(path)):
            play_files = glob.glob(path + '/*.*')
            if (shuffle_play == 'yes'):
                random.shuffle(play_files)

        # CPU 使用率
        cpu_max  = 40
        cpu_data = []
        for x in range(cpu_max):
            cpu_data.append(float(0))

    # 起動
    if (True):
        qLog.log('info', main_id, 'start')

        setting         = True
        last_setting    = time.time() 
        screen_check    = time.time()

        file_index      = 0

        thread_pool     = {}
        thread_start    = {}
        thread_limitSec = {}
        thread_max      = 3

        name = 'play0'
        if ((play_screen).isdigit()):
            name = name[:-1] + str(play_screen)
        for t in range(thread_max):
            thread_pool[t]     = _v6__qFFmpeg.qFFplay_class()
            thread_start[t]    = time.time()
            thread_limitSec[t] = 0
        last_thread     = thread_max - 1
        next_thread     = 0


        # debug
        #play_stopByMouseSec = 30
        #play_panel = '5-'



        # スクリーン
        screen = 0
        try:
            screen = int(play_screen)
            if (screen > (qGUI.screen_count-1)):
                qLog.log('error', main_id, 'screen=' + str(screen) + ' is error. ')
                screen = None
        except:
            pass
        if (str(play_screen) == 'auto'):
            if   (runMode == 'bgm') or (runMode == 'bgmusic'):
                screen = qGUI.getCornerScreen(rightLeft='right', topBottom='bottom', checkPrimary=False, )
            elif (runMode == 'bgv') or (runMode == 'bgvideo'):
                pass
            else:
                pass

        if ((runMode == 'bgmusic') or (runMode == 'bgvideo')) and (screen is not None):
            (x, y), s = qGUI.screenPosition(screen=screen)
        else:
            (x, y) = qGUI.position()
        last_mouse_x    = x
        last_mouse_y    = y
        last_mouse_time = time.time()
        if (runMode == 'bgmusic') or (runMode == 'bgvideo'):
            last_mouse_time = time.time() - play_stopByMouseSec + 120
            qLog.log('info', main_id, 'mouse move check, play waiting 120sec. ')



    # 待機ループ
    main_start = time.time()
    break_flag = False
    while (break_flag == False):

        if True:
        #try:

            # -----------------------
            # 終了確認
            # -----------------------
            txts, txt = qFunc.txtsRead(qCtrl_control_self)
            if (txts != False):
                if (txt == '_end_'):
                    break_flag = True
                    qLog.log('info', main_id, 'run stop! ' + qCtrl_control_self)

            if (run_limitSec != 0):
                if ((time.time() - main_start) > run_limitSec):
                    break_flag = True
                    qLog.log('info', main_id, 'run stop! limitSec=' + str(run_limitSec))

            if ((time.time() - screen_check) > 5):
                screen_check = time.time()
                change = qGUI.checkUpdateScreenInfo(update=True, )
                if (change == True):
                    break_flag = True
                    qLog.log('info', main_id, 'run stop! screenInfo changed.')

            # -------------
            # 再生強制終了
            # -------------
            if (thread_pool[last_thread].is_alive() == True):

                about_play = False

                # マウス操作による再生キャンセル
                if (play_stopByMouseSec != 0):
                    if ((runMode == 'bgmusic') or (runMode == 'bgvideo')) and (screen is not None):
                        (x, y),s = qGUI.screenPosition(screen=screen)
                    else:
                        (x, y) = qGUI.position()
                    if (abs(last_mouse_x-x) >= 50) or (abs(last_mouse_y-y) >= 50):
                        last_mouse_time = time.time()
                        if (thread_pool[last_thread].is_alive() == True):
                            qLog.log('info', main_id, 'Play Stop! By Mouse Move. (screen=' + str(screen) + ') Waiting sec = ' + str(play_stopByMouseSec) + 's. ' )
                            about_play = True
                    last_mouse_x    = x
                    last_mouse_y    = y

                #再生可以外の時間帯は再生キャンセル
                if (runMode == 'bgm') or (runMode == 'bgv'):
                    if (about_play == False):
                        nowTime = datetime.datetime.now()
                        HHMMSS  = nowTime.strftime('%H:%M:%S')
                        YOUBI   = nowTime.strftime('%a').lower()

                    # 曜日チェック
                    if (about_play == False):
                        if (day_control == 'week'):
                            if (YOUBI not in ['mon','tue','wed','th','fri']):
                                qLog.log('info', main_id, 'Play Stop! By day check. (day_control=' + day_control + ')' )
                                about_play = True
                        elif (day_control != 'yes') and (day_control != 'no'):
                            if (YOUBI != day_control):
                                qLog.log('info', main_id, 'Play Stop! By day check. (day_control=' + day_control + ')' )
                                about_play = True

                    # 時間チェック
                    if (about_play == False):
                        if (day_control != 'no'):
                            if (HHMMSS < day_start) or (HHMMSS > day_end):
                                qLog.log('info', main_id, 'Play Stop! By time check. (' + day_start + ' - ' + day_end + ')' )
                                about_play = True

                    # ランチチェック
                    if (about_play == False):
                        if (lunch_control != 'no'):
                            if (HHMMSS >= lunch_start) and (HHMMSS <= lunch_end):
                                qLog.log('info', main_id, 'Play Stop! By lunch check. (' + lunch_start + ' - ' + lunch_end + ')' )
                                about_play = True

                # 再生キャンセル
                if (about_play == True):

                    # 再生停止 # 1/2 
                    fadeSec = play_fadeActionSec / 2
                    if (fadeSec >= 1):
                        thread_pool[last_thread].delayAbort(delaySec=fadeSec, )

                        # フェード処理
                        qGuide.fadeOut(screen=screen, panel=panel, mask='white', outSec=fadeSec-0.90, )
                        chktime = time.time()
                        while (thread_pool[last_thread].is_alive() == True) and ((time.time() - chktime) < (fadeSec+1)):
                            time.sleep(0.25)
                        time.sleep(1.90)
                        qGuide.fadeIn(inSec=fadeSec / 2, )

                    # 再生停止
                    if (runMode == 'bgm') or (runMode == 'bgmusic') \
                    or (runMode == 'bgv') or (runMode == 'bgvideo'):
                        thread_pool[last_thread].abort()
                        break_flag = True
                        qLog.log('info', main_id, 'run stop! etc.')
                    else:
                        chktime = time.time()
                        while (thread_pool[last_thread].is_alive() == True) and ((time.time() - chktime) < 10):
                            time.sleep(0.25)
                        thread_pool[last_thread].abort()

            # -----------------------
            # 終了処理
            # -----------------------
            if (break_flag == True):

                # 全画面再生停止
                thread_pool[last_thread].abort()

                # 終了
                qLog.log('error', main_id, 'sub screen=' + str(screen) + ' is ended. ')
                break



            # -------------
            # CPU 使用率
            # -------------
            cpu  = psutil.cpu_percent(interval=None, percpu=False)
            del cpu_data[0]
            cpu_data.append(float(cpu))
            cpu_ave = np.mean(cpu_data)



            # -------------
            # 再生開始判断
            # -------------
            new_play = False

            # 前の再生無し
            if (thread_pool[last_thread].is_alive() == False):
                new_play = True

            # 前の再生の終了または play_fadeActionSec+【20】+3 秒前            
            if (thread_pool[last_thread].is_alive() == True) \
            and ((thread_limitSec[last_thread] - (time.time() - thread_start[last_thread])) < (play_fadeActionSec + 23)):
                new_play = True

            # マウス操作による再生スキップ
            if (new_play == True):
                if (play_stopByMouseSec != 0):
                    if ((time.time() - last_mouse_time) < play_stopByMouseSec):
                        sec = int(play_stopByMouseSec - (time.time() - last_mouse_time))
                        if (sec > 5):
                            time.sleep(5.00)
                        new_play = False
                    if ((runMode == 'bgmusic') or (runMode == 'bgvideo')) and (screen is not None):
                        (x, y),s = qGUI.screenPosition(screen=screen)
                    else:
                        (x, y) = qGUI.position()
                    if (abs(last_mouse_x-x) >= 50) or (abs(last_mouse_y-y) >= 50):
                        last_mouse_time = time.time()
                        new_play = False
                    last_mouse_x = x
                    last_mouse_y = y

            #再生可以外の時間帯は再生スキップ
            if (runMode == 'bgm') or (runMode == 'bgv'):
                if (new_play == True):
                    nowTime = datetime.datetime.now()
                    HHMMSS  = nowTime.strftime('%H:%M:%S')
                    YOUBI   = nowTime.strftime('%a').lower()

                # 曜日チェック
                if (new_play == True):
                    if (day_control == 'week'):
                        if (YOUBI not in ['mon','tue','wed','th','fri']):
                            time.sleep(5.00)
                            new_play = False
                    elif (day_control != 'yes') and (day_control != 'no'):
                        if (YOUBI != day_control):
                            time.sleep(5.00)
                            new_play = False

                # 時間チェック
                if (new_play == True):
                    if (day_control != 'no'):
                        if (HHMMSS < day_start) or (HHMMSS > day_end):
                            time.sleep(1.00)
                            new_play = False

                # ランチチェック
                if (new_play == True):
                    if (lunch_control != 'no'):
                        if (HHMMSS >= lunch_start) and (HHMMSS <= lunch_end):
                            time.sleep(1.00)
                            new_play = False



            # -------------
            # スクリーン設定
            # -------------
            if (new_play == True):
                if (setting == True):
                    qLog.log('info', main_id, 'Screen Setting... ')

                    qGUI.checkUpdateScreenInfo(update=True, )

                    # スクリーン
                    screen = 0
                    try:
                        screen = int(play_screen)
                        if (screen > (qGUI.screen_count-1)):
                            qLog.log('error', main_id, 'screen=' + str(screen) + ' is error. ')
                            break_flag = True
                            break
                    except:
                        pass
                    if (str(play_screen) == 'auto'):
                        if   (runMode == 'bgm') or (runMode == 'bgmusic'):
                            screen = qGUI.getCornerScreen(rightLeft='right', topBottom='bottom', checkPrimary=False, )
                        elif (runMode == 'bgv') or (runMode == 'bgvideo'):
                            pass
                        else:
                            pass

                    # パネル
                    panel = play_panel
                    if (str(play_panel) == 'auto'):
                        if   (runMode == 'bgm') or (runMode == 'bgmusic'):
                            panel = '9'
                        elif (runMode == 'bgv') or (runMode == 'bgvideo'):
                            panel = '0'
                        else:
                            panel = '5+'

                    # マウス位置
                    if (play_stopByMouseSec != 0):
                        if ((runMode == 'bgmusic') or (runMode == 'bgvideo')) and (screen is not None):
                            (x, y), s = qGUI.screenPosition(screen=screen)
                        else:
                            (x, y) = qGUI.position()
                        last_mouse_x = x
                        last_mouse_y = y

                    # 初回設定終了
                    setting = False
                    last_setting = time.time()



            # -------------
            # 再生開始
            # -------------
            if (new_play == True):

                # 起点時間
                chkTime = time.time()

                # 再生終了？
                file_index += 1
                if (file_index > (len(play_files))):

                    if   (runMode != 'bgm') and (runMode != 'bgmusic') \
                    and  (runMode != 'bgv') and (runMode != 'bgvideo'):
                        qLog.log('info', main_id, 'play folder complite! ')
                        break_flag = True
                        break
                    else:
                        file_index = 1
                        if (shuffle_play == 'yes'):
                            random.shuffle(play_files)

                # 再生ファイル
                f = file_index - 1
                play_file = play_files[f]
                proc_file = play_file
                #proc_file = proc_file.replace('/', '\\')

                # 静止画→動画変換
                if (play_file[-4:].lower() == '.jpg') \
                or (play_file[-4:].lower() == '.png'):
                    if (img2mov_play == 'no'):
                        proc_file = ''
                    else:
                        out_file = qPath_work + main_name + '.' + '{:04}'.format(f) + '.mp4'
                        #res = qCV2.cv2img2mov(inp_file=play_file, out_file=out_file, sec=play_changeSec, fps=15, zoom=True, )
                        if (img2mov_zoom == 'yes'):
                            fps = 5
                            zoom = True
                        else:
                            fps = 1
                            zoom = False
                        res = qCV2.cv2img2mov(inp_file=play_file, out_file=out_file, sec=img2mov_sec, fps=fps, zoom=zoom, )
                        if (res == False):
                            proc_file = ''
                        else:
                            proc_file = res
                        
                # 再生ファイル有効？
                if (proc_file != ''):

                    # 再生時間計算
                    limitSec = play_changeSec
                    startSec = 0
                    if  (proc_file[-4:].lower() != '.jpg') \
                    and (proc_file[-4:].lower() != '.png') \
                    and (proc_file[-4:].lower() != '.wav') \
                    and (proc_file[-4:].lower() != '.mp3') \
                    and (proc_file[-4:].lower() != '.m4a'):
                        try:
                            cap = cv2.VideoCapture(proc_file)                       # 動画を読み込む
                            video_frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)   # フレーム数を取得する
                            video_fps = cap.get(cv2.CAP_PROP_FPS)                   # フレームレートを取得する
                            video_len_sec = video_frame_count / video_fps
                            if (video_len_sec > 0):
                                if (limitSec == 0) or (video_len_sec < limitSec):
                                    limitSec = video_len_sec
                            if (shuffle_play == 'yes'):
                                if (video_len_sec > limitSec):
                                    startSec = int((video_len_sec - limitSec) * random.random())
                        except:
                            pass
                    if (limitSec == 0):
                        limitSec = 3600 * 4 # 同一ファイル最大4時間まで再生

                    # 投入スレッド計算
                    old_thread  = last_thread
                    last_thread = next_thread
                    next_thread = (last_thread + 1) % thread_max

                    # 再生スレッド開始
                    title    = os.path.basename(play_file)
                    winTitle = str(screen) + ':' + title
                    fps = 30
                    if   (runMode == 'bgm') or (runMode == 'bgmusic'):
                        fps = 5
                    elif (runMode == 'bgv') or (runMode == 'bgvideo'):
                        if (qGUI.screen_count > 1):
                            if (screen == 0):
                                if (cpu_ave <= 50):
                                    fps = 15
                                else:
                                    fps = 10
                            else:
                                if (cpu_ave <= 50):
                                    fps = 10
                                else:
                                    fps = 0.2
                                
                    #order = 'top'
                    order = 'normal'
                    #if (runMode == 'bgm') or (runMode == 'bgmusic'):
                    #    order = 'normal'

                    # 再生 【20】秒待機
                    delaySec = 20 - int(time.time() - chkTime)
                    if (delaySec < 0):
                        delaySec = 0
                    if (play_file[-4:].lower() == '.jpg') \
                    or (play_file[-4:].lower() == '.png'):
                        delaySec = 0
                    fadeSec  = play_fadeActionSec
                    qLog.log('info', main_id, 'Play "' + play_file + '" (delay=' + str(delaySec) + 's)')

                    thread_pool[last_thread].begin(
                        delaySec, fadeSec, screen, panel,
                        winTitle, proc_file, play_volume, fps, order,
                        play_overlayTime, play_overlayDate, startSec, limitSec, )
                    thread_start[last_thread] = time.time() + delaySec
                    thread_limitSec[last_thread] = limitSec

                    # フェード処理
                    if (fadeSec >= 1):
                        qGuide.fadeOut(screen=screen, panel=panel, mask='black', outSec=delaySec+fadeSec-0.90, )

                    # play_fadeActionSec+【10】+3 秒待機
                    chkTime = time.time()
                    while ((time.time() - chkTime) < delaySec) \
                    or    (thread_pool[last_thread].is_alive() == False) and ((time.time() - chkTime) < (play_fadeActionSec+13)):
                        time.sleep(0.25)

                        # マウス操作チェック
                        if ((runMode == 'bgmusic') or (runMode == 'bgvideo')) and (screen is not None):
                            (x, y),s = qGUI.screenPosition(screen=screen)
                        else:
                            (x, y) = qGUI.position()
                        if (abs(last_mouse_x-x) >= 50) or (abs(last_mouse_y-y) >= 50):
                            break

                    # フェード処理
                    if (fadeSec >= 1):
                        time.sleep(3.90)
                        qGuide.fadeIn(inSec=fadeSec / 2, )

                    # 再前面へ
                    qGUI.setForegroundWindow(winTitle=winTitle, )

                    # テロップ
                    if (play_file_telop == 'yes'):
                        header = 'Play'
                        if   (runMode == 'bgm') or (runMode == 'bgmusic'):
                            header = 'BGM'
                            telopMSG(telop_path=telop_path, file_seq=file_index, title=header, txt=title, )
                        elif (runMode == 'bgv') or (runMode == 'bgvideo'):
                            header = 'BGV'
                            telopMSG(telop_path=telop_path, file_seq=file_index, title=header, txt=winTitle, )
                        else:
                            telopMSG(telop_path=telop_path, file_seq=file_index, title=header, txt=title, )

                    # 古いスレッド終了（待機）
                    chkTime = time.time()
                    while (thread_pool[old_thread].is_alive() == True) and ((time.time() - chkTime) < 10):
                        time.sleep(0.25)

                        # マウス操作チェック
                        if ((runMode == 'bgmusic') or (runMode == 'bgvideo')) and (screen is not None):
                            (x, y),s = qGUI.screenPosition(screen=screen)
                        else:
                            (x, y) = qGUI.position()
                        if (abs(last_mouse_x-x) >= 50) or (abs(last_mouse_y-y) >= 50):
                            break

                    # 古いスレッド終了（破棄）
                    thread_pool[old_thread].abort()
                    #thread_pool[old_thread] = None
                    #del thread_pool[old_thread]
                    #thread_pool[old_thread] = _v6__qFFmpeg.qFFplay_class()
                    thread_pool[next_thread].abort()
                    #thread_pool[next_thread] = None
                    #del thread_pool[next_thread]
                    #thread_pool[next_thread] = _v6__qFFmpeg.qFFplay_class()

                    #gc.collect()

            # -------------
            # メインビート
            # -------------
            # 再生中
            if (thread_pool[last_thread].is_alive() == True):
                time.sleep(0.50)
            # アイドル中
            else:
                time.sleep(1.00)

        #except Exception as e:
        #    print(e)
        #    time.sleep(5.00)




    # 終了処理
    if (True):
        qLog.log('info', main_id, 'terminate')

        # 終了
        qLog.log('info', main_id, 'bye!')

        sys.exit(0)


