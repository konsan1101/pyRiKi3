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

import subprocess



# インターフェース
qCtrl_control_kernel     = 'temp/control_kernel.txt'
qCtrl_control_self       = qCtrl_control_kernel



# 共通ルーチン
import    _v6__qFunc
qFunc   = _v6__qFunc.qFunc_class()
import    _v6__qLog
qLog    = _v6__qLog.qLog_class()



qPath_temp  = 'temp/'
qPath_log   = 'temp/_log/'



# シグナル処理
import signal
def signal_handler(signal_number, stack_frame):
    print(os.path.basename(__file__), 'accept signal =', signal_number)

#signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGINT,  signal.SIG_IGN)
signal.signal(signal.SIGTERM, signal.SIG_IGN)



if __name__ == '__main__':
    main_name = 'phoenix'
    if (len(sys.argv) >= 3):
        if (str(sys.argv[2]).isdigit()):
            main_name = main_name[:-1] + str(sys.argv[2])
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
        parm = sys.argv[1:]

    # 初期設定
    if (True):
        qFunc.remove(qCtrl_control_self)

    # 起動
    process_pool = {}
    process_pid  = {}
    process_parm = {}

    qLog.log('info', main_id, 'start ' + str(parm[0]) + ' ' + str(parm[1]))
    p = 0
    process_parm[p] = parm
    process_pool[p] = subprocess.Popen(process_parm[p])
    process_pid[p]  = process_pool[p].pid

    # 無限ループ
    while (True):

        # 終了確認
        txts, txt = qFunc.txtsRead(qCtrl_control_self)
        if (txts != False):
            qLog.log('info', main_id, '' + str(txt))
            # 終了
            if (txt == '_end_'):
                for p in process_pool.keys():
                    try:
                        process_pool[p].terminate()
                        process_pool[p] = None
                    except:
                        process_pool[p] = None
                    if (process_pid[p] is not None):
                        qFunc.kill_pid(process_pid[p])
                    process_pid[p] = None

                qLog.log('info', main_id, 'kill ' + str(parm[0]), )
                qFunc.kill(str(parm[0]))
                break

        # 状態確認
        for p in process_pool.keys():
            if (process_pool[p] is not None):

                # 稼働確認
                if (process_pool[p].poll() is None):
                    time.sleep(1.00)
                
                else:

                    # 終了処理
                    qLog.log('info', main_id, 'ended. ' + str(process_parm[p][0]))
                    time.sleep(5.00)
                    try:
                        process_pool[p].terminate()
                        process_pool[p] = None
                    except:
                        process_pool[p] = None
                    if (process_pid[p] is not None):
                        qFunc.kill_pid(process_pid[p])
                    process_pid[p] = None

                    # 再起動
                    qLog.log('info', main_id, '(re)start ' + str(process_parm[p][0]) + ' ' + str(process_parm[p][1]))
                    process_pool[p] = subprocess.Popen(process_parm[p])
                    process_pid[p]  = process_pool[p].pid

        time.sleep(5.00)



    # 終了処理
    if (True):
        qLog.log('info', main_id, 'terminate')

        # 終了
        qLog.log('info', main_id, 'bye!')

        sys.exit(0)


