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



# 共通ルーチン
import  _v6__qFunc
qFunc = _v6__qFunc.qFunc_class()
import  _v6__qGUI
qGUI  = _v6__qGUI.qGUI_class()
import  _v6__qLog
qLog  = _v6__qLog.qLog_class()



qPath_temp  = 'temp/'
qPath_log   = 'temp/_log/'



def is_num(s):
    try:
        f=float(s)
    except:
        return False
    return True

def winRight(n=0, ):
    for i in range(n):
        qGUI.keyDown('ctrlleft')
        time.sleep(0.02)
        qGUI.keyDown('winleft')
        time.sleep(0.02)

        qGUI.keyDown('right')
        time.sleep(0.02)
        qGUI.keyUp('right')
        time.sleep(0.02)

        qGUI.keyUp('winleft')
        time.sleep(0.02)
        qGUI.keyUp('ctrlleft')
        time.sleep(0.50)

    qGUI.keyUp('right')
    qGUI.keyUp('winleft')
    qGUI.keyUp('ctrlleft')
    time.sleep(0.50)



def winLeft(n=0, ):
    for i in range(n):
        qGUI.keyDown('ctrlleft')
        time.sleep(0.02)
        qGUI.keyDown('winleft')
        time.sleep(0.02)

        qGUI.keyDown('left')
        time.sleep(0.02)
        qGUI.keyUp('left')
        time.sleep(0.02)

        qGUI.keyUp('winleft')
        time.sleep(0.02)
        qGUI.keyUp('ctrlleft')
        time.sleep(0.50)

    qGUI.keyUp('left')
    qGUI.keyUp('winleft')
    qGUI.keyUp('ctrlleft')
    time.sleep(0.50)



runMode = 'debug'
#runMode = -1



if __name__ == '__main__':
    main_name = 'changer'
    main_id   = '{0:10s}'.format(main_name).replace(' ', '_')

    # ディレクトリ作成
    qFunc.makeDirs(qPath_temp, remove=False, )
    qFunc.makeDirs(qPath_log,  remove=False, )

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

        qLog.log('info', main_id, 'runMode = ' + str(runMode ))

    # 初期設定
    if (True):
        pass

    # 起動
    if (True):
        qLog.log('info', main_id, 'start')

    # 処理
    if (True):

        if (runMode == 'debug'):
            n = 1
            qLog.log('info', main_id, 'winRight(' + str(n) + ')')
            winRight(n)
            n = 1
            qLog.log('info', main_id, 'winLeft( ' + str(n) + ')')
            winLeft(n)

        if (is_num(runMode)):
            n = int(runMode)
            if (n == 0):
                n = 1
                qLog.log('info', main_id, 'winRight(' + str(n) + ')')
                winRight(n)
                n = 9
                qLog.log('info', main_id, 'winLeft( ' + str(n) + ')')
                winLeft(n)
            elif (n > 0):
                qLog.log('info', main_id, 'winRight(' + str(n) + ')')
                winRight(n)
            elif (n < 0):
                n = abs(n)
                qLog.log('info', main_id, 'winLeft( ' + str(n) + ')')
                winLeft(n)

    # 終了処理
    if (True):
        qLog.log('info', main_id, 'terminate')

        # 終了
        qLog.log('info', main_id, 'bye!')

        sys.exit(0)


