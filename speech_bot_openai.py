#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2024 Mitsuo KONDOU.
# This software is released under the not MIT License.
# Permission from the right holder is required for use.
# https://github.com/konsan1101
# Thank you for keeping the rules.
# ------------------------------------------------

import sys
import os
import time
import datetime
import codecs
import shutil

import glob
import importlib
import base64

import json

import socket
qHOSTNAME = socket.gethostname().lower()



import _v6__qRiKi_key
qRiKi_key = _v6__qRiKi_key.qRiKi_key_class()



# openai チャットボット
import openai
import tiktoken
import speech_bot_openai_key  as openai_key



qPath_temp           = 'temp/'
qPath_output         = 'temp/output/'
qPath_work           = 'temp/work/'
qPath_retrieval_work = 'temp/retrieval_work/'



# base64 encode
def base64_encode(file_path):
    with open(file_path, "rb") as input_file:
        return base64.b64encode(input_file.read()).decode('utf-8')



class ChatBotAPI:

    def __init__(self, ):
        self.bot_auth               = None
        self.default_gpt            = 'auto'
        self.default_class          = 'auto'
        self.auto_continue          = 3
        self.max_step               = 10
        self.max_assistant          = 5

        self.client_ab              = None
        self.client_v               = None
        self.client_x               = None

        self.assistant_name         = qHOSTNAME
        self.assistant_id           = {}
        self.thread_id              = {}

        self.temperature            = 0.8
        self.timeOut                = 60
        self.last_input_class       = 'chat'
        self.last_chat_class        = 'chat'
        self.last_model_select      = 'auto'
        self.last_auto_inpText      = None
        
        self.openai_api_type        = None
        self.openai_default_gpt     = None
        self.openai_organization    = None
        self.openai_key_id          = None
        self.azure_endpoint         = None
        self.azure_version          = None
        self.azure_key_id           = None

        self.gpt_a_enable           = False
        self.gpt_a_nick_name        = ''
        self.gpt_a_model1           = None
        self.gpt_a_token1           = 0
        self.gpt_a_model2           = None
        self.gpt_a_token2           = 0
        self.gpt_a_model3           = None
        self.gpt_a_token3           = 0

        self.gpt_b_enable           = False
        self.gpt_b_nick_name        = ''
        self.gpt_b_model1           = None
        self.gpt_b_token1           = 0
        self.gpt_b_model2           = None
        self.gpt_b_token2           = 0
        self.gpt_b_model3           = None
        self.gpt_b_token3           = 0

        self.gpt_b_length           = 500

        self.gpt_v_enable           = False
        self.gpt_v_nick_name        = ''
        self.gpt_v_model1           = None
        self.gpt_v_token1           = 0

        self.gpt_x_enable           = False
        self.gpt_x_nick_name        = ''
        self.gpt_x_model1           = None
        self.gpt_x_token1           = 0
        self.gpt_x_model2           = None
        self.gpt_x_token2           = 0

        self.seq                    = 0
        self.history                = []

        self.ext_module             = []

    def extensions_load(self, extensions_path='_extensions/openai_gpt/', secure_level='medium', ):
        self.last_input_class       = 'chat'
        self.last_chat_class        = 'chat'
        self.last_model_select      = 'auto'
        self.last_auto_inpText      = None
        self.assistant_id           = {}
        self.thread_id              = {}

        res_load_all = True
        res_load_msg = ''
        self.extensions_unload()
        #print('Load Extensions... ')

        path = extensions_path
        path_files = glob.glob(path + '*.py')
        path_files.sort()
        if (len(path_files) > 0):
            for f in path_files:
                try:
                    file_name   = os.path.splitext(os.path.basename(f))[0]
                    script_name = os.path.basename(f)
                    print('Loading ... "' + script_name.replace('.py', '') + '" ...')
                    loader = importlib.machinery.SourceFileLoader(file_name, f)
                    ext_script = script_name.replace('.py', '')
                    ext_module = loader.load_module()
                    ext_onoff  = 'off'
                    ext_class  = ext_module._class()
                    print('Loading ... "' + ext_script + '" (' + ext_class.func_name + ') _class.func_proc')
                    ext_version     = ext_class.version
                    ext_func_name   = ext_class.func_name
                    ext_func_ver    = ext_class.func_ver
                    ext_func_auth   = ext_class.func_auth
                    ext_function    = ext_class.function
                    ext_func_reset  = ext_class.func_reset
                    ext_func_proc   = ext_class.func_proc
                    #print(ext_version, ext_func_auth, )

                    # コード認証
                    auth = False
                    if   (secure_level == 'low') or (secure_level == 'medium'):
                        if (ext_func_auth == ''):
                            auth = '1' #注意
                            if (secure_level != 'low'):
                                res_load_msg += '"' + ext_script + '"が認証されていません。(Warning!)' + '\n'
                        else:
                            auth = qRiKi_key.decryptText(text=ext_func_auth)
                            if  (auth != ext_func_name + '-' + ext_func_ver) \
                            and (auth != self.openai_organization):
                                #print(ext_func_auth, auth)
                                if (secure_level == 'low'):
                                    auth = '1' #注意
                                    res_load_msg += '"' + ext_script + '"は改ざんされたコードです。(Warning!)' + '\n'
                                else:
                                    res_load_msg += '"' + ext_script + '"は改ざんされたコードです。Loadingはキャンセルされます。' + '\n'
                                    res_load_all = False
                            else:
                                auth = '2' #認証
                                ext_onoff  = 'on'
                    else:
                        if (ext_func_auth == ''):
                            res_load_msg += '"' + ext_script + '"が認証されていません。Loadingはキャンセルされます。' + '\n'
                            res_load_all = False
                        else:
                            auth = qRiKi_key.decryptText(text=ext_func_auth)
                            if  (auth != ext_func_name + '-' + ext_func_ver) \
                            and (auth != self.openai_organization):
                                #print(ext_func_auth, auth)
                                res_load_msg += '"' + ext_script + '"は改ざんされたコードです。Loadingはキャンセルされます。' + '\n'
                                res_load_all = False
                            else:
                                auth = '2' #認証
                                ext_onoff  = 'on'

                    if (auth != False):
                        module_dic = {}
                        module_dic['script']     = ext_script
                        module_dic['module']     = ext_module
                        module_dic['onoff']      = ext_onoff
                        module_dic['class']      = ext_class
                        module_dic['func_name']  = ext_func_name
                        module_dic['func_ver']   = ext_func_ver
                        module_dic['func_auth']  = ext_func_auth
                        module_dic['function']   = ext_function
                        module_dic['func_reset'] = ext_func_reset
                        module_dic['func_proc']  = ext_func_proc
                        self.ext_module.append(module_dic)

                except Exception as e:
                    print(e)

        return res_load_all, res_load_msg

    def extensions_reset(self, ):
        self.last_input_class       = 'chat'
        self.last_chat_class        = 'chat'
        self.last_model_select      = 'auto'
        self.last_auto_inpText      = None
        self.assistant_id           = {}
        self.thread_id              = {}

        res_reset_all = True
        res_reset_msg = ''
        #print('Reset Extensions... ')
        for module_dic in self.ext_module:
            ext_script     = module_dic['script']
            ext_func_name  = module_dic['func_name']
            ext_func_reset = module_dic['func_reset']
            print('Reset ... "' + ext_script + '" (' + ext_func_name + ') _class.func_reset')
            try:
                res = ext_func_reset()
            except:
                res_reset_all = False
                res_reset_msg += ext_func_name + 'のリセット中にエラーがありました。' + '\n'

        return res_reset_all, res_reset_msg

    def extensions_unload(self, ):
        self.last_input_class       = 'chat'
        self.last_chat_class        = 'chat'
        self.last_model_select      = 'auto'
        self.last_auto_inpText      = None
        self.assistant_id           = {}
        self.thread_id              = {}

        res_unload_all = True
        res_unload_msg = ''
        #print('Unload Extensions... ')

        for module_dic in self.ext_module:
            ext_script     = module_dic['script']
            ext_func_name  = module_dic['func_name']
            ext_module    = module_dic['module']
            ext_class     = module_dic['class']
            ext_func_proc = module_dic['func_proc']
            print('Unload ... "' + ext_script + '" (' + ext_func_name + ') _class.func_proc')

            try:
                #del ext_func_proc
                del ext_class
                del ext_module
            except:
                res_unload_all = False
                res_unload_msg += ext_func_name + 'の開放中にエラーがありました。' + '\n'

        self.ext_module             = []

        return res_unload_all, res_unload_msg

    def assistantFiles_del(self, assistant_id=None, ):

        # アップロード済確認
        assistant_files_list = self.client_x.beta.assistants.files.list(
            assistant_id = assistant_id, )
        #print(assistant_files_list)

        # 削除
        for a in range(len(assistant_files_list.data)):
            file_id   = assistant_files_list.data[a].id

            # 削除
            try:
                res = self.client_x.beta.assistants.files.delete(
                    assistant_id = assistant_id, 
                    file_id=file_id, )
            except Exception as e:
                print(e)

            try:
                upload_file = self.client_x.files.retrieve(
                    file_id=file_id, )
                print(' Assistant :', 'Delete file_name = "' + upload_file.filename + '",')
            except Exception as e:
                print(e)

            try:
                res = self.client_x.files.delete(
                    file_id=file_id, )
            except Exception as e:
                print(e)
        
        return True

    def assistantFiles_load(self, retrievalFiles_path='_extensions/retrieval_files/', assistant_id=None, assistant_name='', ):
        assistant_file_ids   = []
        assistant_file_names = {}

        # フォルダクリア
        if (os.path.isdir(qPath_retrieval_work)):
            shutil.rmtree(qPath_retrieval_work)
        if (not os.path.isdir(qPath_retrieval_work)):
            os.mkdir(qPath_retrieval_work)

        # ファイルコピー
        path_files = glob.glob(retrievalFiles_path + '*.*')
        path_files.sort()
        if (len(path_files) > 0):
            for f in path_files:
                fn1 = retrievalFiles_path   + os.path.basename(f)
                fn2 = qPath_retrieval_work + assistant_name + '_' + os.path.basename(f)
                shutil.copy(fn1, fn2)

        # アップロード済確認
        assistant_files_list = self.client_x.beta.assistants.files.list(
            assistant_id = assistant_id, )
        #print(assistant_files_list)
        for a in range(len(assistant_files_list.data)):
            file_id   = assistant_files_list.data[a].id
            upload_file = self.client_x.files.retrieve(
                file_id=file_id, )
            file_name = upload_file.filename
            assistant_file_names[file_name] = file_id
            #print("##" + file_name + "##")

            # 削除
            #res = self.client_x.beta.assistants.files.delete(
            #    assistant_id = assistant_id, 
            #    file_id=file_id, )
            #res = self.client_x.files.delete(
            #    file_id=file_id, )
            #del assistant_file_names[file_name]

        # 新規アップロード
        path_files = glob.glob(qPath_retrieval_work + '*.*')
        path_files.sort()
        if (len(path_files) > 0):
            try:

                for f in path_files:
                    if (os.path.isfile(f)):
                        if (os.path.getsize(f) <= 20000000):

                            file_name = os.path.basename(f)
                            source    = qPath_retrieval_work + file_name
                            #print("##" + file_name + "##")

                            file_id  = assistant_file_names.get(file_name)
                            #print(source, file_id)
                            if (file_id == None):
                                print(' Assistant :', 'Upload file_name = "' + file_name + '", ')
                                upload_file = self.client_x.files.create(
                                    file = open(source, 'rb'),
                                    purpose='assistants', )
                                assistant_file_ids.append(upload_file.id)
                                #try:
                                #    res = self.client_x.beta.assistants.files.create(
                                #        assistant_id = assistant_id, 
                                #        file_id = upload_file.id, )
                                #except:
                                #    pass
                            else:
                                assistant_file_ids.append(file_id)

            except Exception as e:
                print(e)

        return assistant_file_ids

    def threadFile_set(self, upload_files=[], assistant_name='', ):
        upload_ids = []

        for upload_file in upload_files:
            base_name   = os.path.basename(upload_file)
            work_name   = assistant_name + '_' + base_name
            upload_work = qPath_work + work_name
            shutil.copy(upload_file, upload_work)

            # 既に存在なら、置換えの為、削除
            assistant_files_list = self.client_x.files.list()
            for a in range(len(assistant_files_list.data)):
                file_id   = assistant_files_list.data[a].id
                file_name = assistant_files_list.data[a].filename
                if (file_name == work_name):
                    res = self.client_x.files.delete(
                        file_id=file_id, )
            # アップロード
            upload = self.client_x.files.create(
                file = open(upload_work, 'rb'),
                purpose='assistants', )
            print(' Assistant :', 'Upload ...', upload.id, base_name, )

            upload_ids.append(upload.id)

        return upload_ids

    def threadFile_del(self, upload_ids=[], ):
        # 削除
        for upload_id in upload_ids:
            try:
                res = self.client_x.files.delete(
                    file_id=upload_id, )
                print(' Assistant :', 'Delete ...', upload_id, )
            except:
                pass
        return True

    def setTimeOut(self, timeOut=20, ):
        self.timeOut      = timeOut

    def authenticate(self, api,
                     openai_api_type,
                     openai_default_gpt, openai_default_class,
                     openai_auto_continue,
                     openai_max_step, openai_max_assistant,

                     openai_organization, openai_key_id,
                     azure_endpoint, azure_version, azure_key_id,

                     gpt_a_nick_name, 
                     gpt_a_model1, gpt_a_token1, 
                     gpt_a_model2, gpt_a_token2, 
                     gpt_a_model3, gpt_a_token3,
                     gpt_b_nick_name, 
                     gpt_b_model1, gpt_b_token1, 
                     gpt_b_model2, gpt_b_token2, 
                     gpt_b_model3, gpt_b_token3,
                     gpt_b_length,
                     gpt_v_nick_name, 
                     gpt_v_model1, gpt_v_token1, 
                     gpt_x_nick_name, 
                     gpt_x_model1, gpt_x_token1, 
                     gpt_x_model2, gpt_x_token2, 
                    ):

        # 設定
        if (not os.path.isdir(qPath_temp)):
            os.mkdir(qPath_temp)
        if (not os.path.isdir(qPath_output)):
            os.mkdir(qPath_output)
        if (not os.path.isdir(qPath_work)):
            os.mkdir(qPath_work)

        # 認証
        self.bot_auth               = None

        self.default_gpt            = openai_default_gpt
        self.default_class          = openai_default_class
        if (str(openai_auto_continue) != 'auto'):
            self.auto_continue      = int(openai_auto_continue)
        if (str(openai_max_step)      != 'auto'):
            self.max_step           = int(openai_max_step)
        if (str(openai_max_assistant) != 'auto'):
            self.max_assistant      = int(openai_max_assistant)

        self.client_ab              = None
        self.client_v               = None
        self.client_x               = None

        my_assistant_name         = qHOSTNAME
        self.assistant_session      = {}

        # openai チャットボット
        if (api == 'chatgpt'):

            self.gpt_a_enable       = False
            #self.gpt_a_nick_name    = gpt_a_nick_name
            self.gpt_a_model1       = gpt_a_model1
            self.gpt_a_token1       = int(gpt_a_token1)
            self.gpt_a_model2       = gpt_a_model2
            self.gpt_a_token2       = int(gpt_a_token2)
            self.gpt_a_model3       = gpt_a_model3
            self.gpt_a_token3       = int(gpt_a_token3)

            self.gpt_b_enable       = False
            #self.gpt_b_nick_name    = gpt_b_nick_name
            self.gpt_b_model1       = gpt_b_model1
            self.gpt_b_token1       = int(gpt_b_token1)
            self.gpt_b_model2       = gpt_b_model2
            self.gpt_b_token2       = int(gpt_b_token2)
            self.gpt_b_model3       = gpt_b_model3
            self.gpt_b_token3       = int(gpt_b_token3)

            self.gpt_b_length       = int(gpt_b_length)

            self.gpt_v_enable       = False
            #self.gpt_v_nick_name    = gpt_v_nick_name
            self.gpt_v_model1       = gpt_v_model1
            self.gpt_v_token1       = int(gpt_v_token1)

            self.gpt_x_enable       = False
            #self.gpt_x_nick_name    = gpt_x_nick_name
            self.gpt_x_model1       = gpt_x_model1
            self.gpt_x_token1       = int(gpt_x_token1)
            self.gpt_x_model2       = gpt_x_model2
            self.gpt_x_token2       = int(gpt_x_token2)

            if (openai_api_type == 'openai'):
                self.openai_api_type = openai_api_type
                self.client_ab = openai.OpenAI(
                    organization=openai_organization,
                    api_key=openai_key_id,
                )
                self.client_v  = openai.OpenAI(
                    organization=openai_organization,
                    api_key=openai_key_id,
                )
                self.client_x  = openai.OpenAI(
                    organization=openai_organization,
                    api_key=openai_key_id,
                )

                try:
                    res = self.client_ab.models.list()
                    for model in res:
                        if (model.id == gpt_a_model1):
                            if (self.gpt_a_token1 > 0):
                                self.bot_auth        = True
                                self.gpt_a_enable    = True
                                self.gpt_a_nick_name = gpt_a_nick_name
                        if (model.id == gpt_b_model1):
                            if (self.gpt_b_token1 > 0):
                                self.bot_auth        = True
                                self.gpt_b_enable    = True
                                self.gpt_b_nick_name = gpt_b_nick_name
                        if (model.id == gpt_v_model1):
                            if (self.gpt_v_token1 > 0):
                                self.bot_auth        = True
                                self.gpt_v_enable    = True
                                self.gpt_v_nick_name = gpt_v_nick_name
                        if (model.id == gpt_x_model1):
                            if (self.gpt_x_token1 > 0):
                                self.bot_auth        = True
                                self.gpt_x_enable    = True
                                self.gpt_x_nick_name = gpt_x_nick_name

                    if (self.bot_auth == True):
                        self.openai_organization = openai_organization
                        self.openai_key_id       = openai_key_id
                        return True

                    print('★Model nothing,', gpt_a_model1, gpt_b_model1)
                    for dt in res['data']:
                        print(dt['id'])

                    return False

                except Exception as e:
                    print(e)

            if (openai_api_type == 'azure'):
                self.openai_api_type    = openai_api_type
                self.client_ab = openai.AzureOpenAI(
                    azure_endpoint=azure_endpoint,
                    api_version=azure_version,
                    api_key=azure_key_id,
                )
                self.client_v  = openai.AzureOpenAI(
                    azure_endpoint=azure_endpoint,
                    api_version=azure_version,
                    api_key=azure_key_id,
                )
                self.client_x  = openai.AzureOpenAI(
                    azure_endpoint=azure_endpoint,
                    api_version=azure_version,
                    api_key=azure_key_id,
                )

                self.azure_endpoint     = azure_endpoint
                self.azure_version      = azure_version
                self.azure_key_id       = azure_key_id

                if (gpt_a_nick_name != '') and (gpt_a_model1 != ''):
                    if (self.gpt_a_token1 > 0):
                        self.bot_auth           = True
                        self.gpt_a_enable       = True
                        self.gpt_a_nick_name    = gpt_a_nick_name

                if (gpt_b_nick_name != '') and (gpt_b_model1 != ''):
                    if (self.gpt_b_token1 > 0):
                        self.bot_auth           = True
                        self.gpt_b_enable       = True
                        self.gpt_b_nick_name    = gpt_b_nick_name

                if (gpt_v_nick_name != '') and (gpt_v_model1 != ''):
                    if (self.gpt_v_token1 > 0):
                        self.bot_auth           = True
                        self.gpt_v_enable       = True
                        self.gpt_v_nick_name    = gpt_v_nick_name

                if (gpt_x_nick_name != '') and (gpt_x_model1 != ''):
                    if (self.gpt_x_token1 > 0):
                        self.bot_auth           = True
                        self.gpt_x_enable       = True
                        self.gpt_x_nick_name    = gpt_x_nick_name

                return True

        return False

    def history_add(self, history=[], sysText=None, reqText=None, inpText='こんにちは', ):
        res_history = history

        # sysText, reqText, inpText -> history
        if (sysText == None):
            sysText = 'あなたは教師のように話す賢いアシスタントです。'
        if (sysText.strip() != ''):
            if (len(res_history) > 0):
                if (sysText.strip() != res_history[0]['content'].strip()):
                    res_history = []
            if (len(res_history) == 0):
                self.seq += 1
                dic = {'seq': self.seq, 'time': time.time(), 'role': 'system', 'name': '', 'content': sysText.strip() }
                res_history.append(dic)
        if (reqText != None):
            if (reqText.strip() != ''):
                self.seq += 1
                dic = {'seq': self.seq, 'time': time.time(), 'role': 'user', 'name': '', 'content': reqText.strip() }
                res_history.append(dic)
        if (inpText.strip() != ''):
            if (inpText.rstrip() != ''):
                self.seq += 1
                dic = {'seq': self.seq, 'time': time.time(), 'role': 'user', 'name': '', 'content': inpText.rstrip() }
                res_history.append(dic)

        return res_history

    def history_zip1(self, history=[]):
        res_history = history

        for h in reversed(range(len(res_history))):
            tm = res_history[h]['time']
            if ((time.time() - tm) > 900): #15分で忘れてもらう
                if (h != 0):
                    del res_history[h]
                else:
                    if (res_history[0]['role'] != 'system'):
                        del res_history[0]

        return res_history

    def history_zip2(self, history=[], leave_count=4, ):
        res_history = history

        if (len(res_history) > 6):
            for h in reversed(range(2, len(res_history) - leave_count)):
                del res_history[h]

        return res_history

    def history2msg_gpt(self, history=[], ):
        res_msg = []
        for h in range(len(history)):
            role    = history[h]['role']
            content = history[h]['content']
            name    = history[h]['name']
            if (role != 'function_call'):
            #if True:
                if (name == ''):
                    dic = {'role': role, 'content': content }
                    res_msg.append(dic)
                else:
                    dic = {'role': role, 'name': name, 'content': content }
                    res_msg.append(dic)

        return res_msg

    def history2msg_vision(self, history=[], image_urls=[], ):
        res_msg = []
        last_h  = 0
        for h in range(len(history)):
            role    = history[h]['role']
            if (role != 'function_call') and (role != 'function'):
                last_h = h 

        for h in range(len(history)):
            role    = history[h]['role']
            content = history[h]['content']
            name    = history[h]['name']
            if (role != 'function_call') and (role != 'function'):
                con = []
                con.append({'type': 'text', 'text': content})
                if (h == last_h):
                    for image_url in image_urls:
                        con.append(image_url)
                if (name == ''):
                    dic = {'role': role, 'content': con }
                    res_msg.append(dic)
                else:
                    dic = {'role': role, 'name': name, 'content': con }
                    res_msg.append(dic)

        return res_msg

    def checkTokens(self, messages={}, functions=[], model_select='auto', ):
        select = 'a'
        nick_name = self.gpt_a_nick_name
        model     = self.gpt_a_model1
        max       = self.gpt_a_token1
        if (model_select == 'b'):
            if (self.gpt_b_enable == True):
                select = 'b'
                nick_name = self.gpt_b_nick_name
                model     = self.gpt_b_model1
                max       = self.gpt_b_token1
        if (model_select == 'v'):
            if (self.gpt_v_enable == True):
                select = 'v'
                nick_name = self.gpt_v_nick_name
                model     = self.gpt_v_model1
                max       = self.gpt_v_token1
        if (model_select == 'x'):
            if (self.gpt_x_enable == True):
                select = 'x'
                nick_name = self.gpt_x_nick_name
                model     = self.gpt_x_model1
                max       = self.gpt_x_token1
        len_tokens = 0

        if (select == 'a') or (select == 'b'):

            #encoding_model = tiktoken.encoding_for_model(model)
            encoding_model = tiktoken.get_encoding("cl100k_base")
            for message in messages:
                len_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
                for key, value in message.items():
                    try:
                        len_tokens += len(encoding_model.encode(value))
                    except:
                        len_tokens += len(value)
                    if key == "name":  # if there's a name, the role is omitted
                        len_tokens += -1  # role is always required and always 1 token
            #len_tokens += 1  # every reply is primed with <im_start>assistant

            # functionのトークン暫定
            for dic in functions:
                len_tokens += 19
                value = dic['description']
                try:
                    len_tokens += len(encoding_model.encode(value))
                except:
                    len_tokens += len(value)
                for x in dic['parameters']['properties']:
                    len_tokens += 5
                    value = dic['parameters']['properties'][x]['description']
                    try:
                        len_tokens += len(encoding_model.encode(value))
                    except:
                        len_tokens += len(value)
                required = dic['parameters'].get('required')
                if (required != None):
                    len_tokens += len(required) + 2

            if (select == 'a'):
                if (len_tokens > self.gpt_a_token2):
                    model = self.gpt_a_model3
                    max   = self.gpt_a_token3
                    print(len_tokens, '->', model)
                elif (len_tokens > self.gpt_a_token1):
                    model = self.gpt_a_model2
                    max   = self.gpt_a_token2
                    print(len_tokens, '->', model)
                if (len_tokens > max):
                    if (model_select == 'auto'):
                        if (self.gpt_b_enable == True):
                            select = 'b'
                            nick_name = self.gpt_b_nick_name
                            model     = self.gpt_b_model1
                            max       = self.gpt_b_token1
            if (select == 'b'):
                if (len_tokens > self.gpt_b_token2):
                    model = self.gpt_b_model3
                    max   = self.gpt_b_token3
                    print(len_tokens, '->', model)
                elif (len_tokens > self.gpt_b_token1):
                    model = self.gpt_b_model2
                    max   = self.gpt_b_token2
                    print(len_tokens, '->', model)

            if (len_tokens > max):
                nick_name = None
                model     = None
        #except Exception as e:
        #    print(e)

        return nick_name, model, len_tokens



    def model_check(self, chat_class='auto', model_select='auto',
                    session_id='0', history=[],
                    sysText=None, reqText=None, inpText='こんにちは', filePath=[], ):

        # 戻り値
        chat_class   = chat_class
        model_select = model_select
        nick_name    = None
        model_name   = None
        upload_files = []
        image_urls   = []
        functions    = []

        # filePath確認
        if (len(filePath) > 0):
            try:

                for file_name in filePath:
                    if (os.path.isfile(file_name)):
                        if (os.path.getsize(file_name) <= 20000000):

                            upload_files.append(file_name)
                            file_ext = os.path.splitext(file_name)[1][1:].lower()
                            if (file_ext in ('jpg', 'jpeg', 'png')):
                                base64_text = base64_encode(file_name)
                                if (file_ext in ('jpg', 'jpeg')):
                                    url = {"url": f"data:image/jpeg;base64,{base64_text}"}
                                    image_url = {'type':'image_url', 'image_url': url}
                                    image_urls.append(image_url)
                                if (file_ext == 'png'):
                                    url = {"url": f"data:image/png;base64,{base64_text}"}
                                    image_url = {'type':'image_url', 'image_url': url}
                                    image_urls.append(image_url)

            except Exception as e:
                print(e)

        # チャットクラス判定
        if   (chat_class != 'auto'):
            self.last_input_class = chat_class
            print(' ChatGPT :', 'user chat class = [', chat_class, ']')

        elif (self.gpt_a_model1 == self.gpt_b_model1) \
        and  (self.gpt_x_model1 == self.gpt_a_model1) \
        and  (self.gpt_x_model2 == self.gpt_b_model1):
            chat_class = 'chat'
            self.last_input_class = chat_class
            print(' ChatGPT :', 'pass chat class = [', chat_class, ']')

        else:
            # history 圧縮 (最後４つ残す)
            old_history = self.history_zip2(history=history, )

# ----- あなたの役割 -----
# あなたは、会話履歴と最後のユーザー入力から、ユーザーの意図を推測し、適切なクラスに分類します。
# ユーザー入力の内容を理解し、それを正しい分類に関連付けて回答します。
# 以下のクラスのうち、適切なものに分類して回答してください。
# 回答はjson形式でchat_classでお願いします。

# ----- あなたへの依頼 -----
# 会話履歴と最後のユーザー入力から、ユーザーの意図を分類してください。
# 決められた単語で分類、回答してください。
# 1) おはよう、こんにちは等のあいさつは、"chat"
# 2) 画像分析に関する指示や質問なら、"vision"
# 3) 会話の続きや返事など、新たな質問ではないときは、"continue"
# 4) AIが作成、生成、計算などを伴う高度な指示なら、"code_interpreter"
# 5) ナレッジ情報や外部情報を扱う指示なら、"knowledge"
# 6) チャットAI単体で処理できる単純な指示や質問なら、"chat"
# 7) AIがtoolやfunctionと連携を行う高度な指示なら、"assistant"
# 8) 上記のいずれにも当てはまらない場合は、適切と思われる英単語

            # GPT によるモデル判定
            wk_history = []
            wk_sysText = \
"""
----- Your Role -----
You are to infer the user's intent from the conversation history and the last user input, and classify it into the appropriate category.
Understand the content of the user input and associate it with the correct classification in your response.
Please classify and respond in json format using "chat_class".
""" + '\n\n'
            wk_reqText = \
"""
----- Your Task -----
Classify the user's intent from the conversation history and the last user input.
Please classify and respond using the designated words.
1) Greetings such as "good morning" or "hello" should be classified as "chat".
2) Instructions or questions about image analysis should be classified as "vision".
3) Continuations or replies that are not new questions should be classified as "continue".
4) Advanced instructions for the AI involving creation, generation, or computation should be classified as "code_interpreter".
5) Instructions involving knowledge information or external information should be classified as "knowledge".
6) Simple instructions or questions that can be processed by the chat AI alone should be classified as "chat".
7) Advanced instructions involving collaboration with tools or functions should be classified as "assistant".
8) If it does not fit any of the above categories, classify it with an appropriate English word.
""" + '\n\n'
            wk_inpText = ''
            if (len(old_history) > 2):
                wk_inpText += '----- 会話履歴 -----' + '\n'
                for m in range(len(old_history) - 1):
                    role    = str(old_history[m].get('role', ''))
                    content = str(old_history[m].get('content', ''))
                    name    = str(old_history[m].get('name', ''))
                    if (role != 'system'):
                        # 全てユーザーメッセージにて処理
                        if (name == None) or (name == ''):
                            wk_inpText += '(' + role + ')' + '\n'
                            wk_inpText += content + '\n\n'
            wk_inpText += '----- 最後のユーザー入力 -----' + '\n'
            wk_inpText += inpText + '\n\n'

            wk_json, wk_path, wk_nick_name, wk_model_name, wk_history = \
                self.run_gpt(chat_class='check', model_select='auto',
                             nick_name=None, model_name=None,
                             session_id='sys', history=[], 
                             sysText=wk_sysText, reqText=wk_reqText, inpText=wk_inpText,
                             upload_files=[], image_urls=[], functions=[],
                             jsonMode=True, )
            chat_class = wk_json
            try:
                args_dic   = json.loads(wk_json)
                chat_class = args_dic.get('chat_class')
            except:
                print(wk_json)
            self.last_input_class = chat_class

            if  (chat_class != 'auto') \
            and (chat_class != 'vision') \
            and (chat_class != 'continue') \
            and (chat_class != 'code_interpreter') \
            and (chat_class != 'knowledge') \
            and (chat_class != 'chat') \
            and (chat_class != 'assistant'):
                print(' ChatGPT :', 'auto chat class error !, [', chat_class, '] (' + wk_model_name + ')')
                chat_class = 'auto'
            else:
                print(' ChatGPT :', 'auto chat class = [', chat_class, '] (' + wk_model_name + ')')

        # model 指定
        user_select = None
        if (self.gpt_a_nick_name != ''):
            if (inpText.strip()[:len(self.gpt_a_nick_name)+1].lower() == (self.gpt_a_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.gpt_a_nick_name)+1:]
                if (self.gpt_a_enable == True):
                    user_select  = 'a'
        if (self.gpt_b_nick_name != ''):
            if (inpText.strip()[:len(self.gpt_b_nick_name)+1].lower() == (self.gpt_b_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.gpt_b_nick_name)+1:]
                if (self.gpt_b_enable == True):
                    user_select  = 'b'
        if (self.gpt_v_nick_name != ''):
            if (inpText.strip()[:len(self.gpt_v_nick_name)+1].lower() == (self.gpt_v_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.gpt_v_nick_name)+1:]
                if (self.gpt_v_enable == True):
                    if  (len(image_urls) > 0) \
                    and (len(image_urls) == len(upload_files)):
                        user_select  = 'v'
        if (self.gpt_x_nick_name != ''):
            if (inpText.strip()[:len(self.gpt_x_nick_name)+1].lower() == (self.gpt_x_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.gpt_x_nick_name)+1:]
                if (self.gpt_x_enable == True):
                    user_select  = 'x'
        if  (user_select != None) \
        and (model_select == 'auto'):
            model_select = user_select

        # model 判定
        if (user_select == None):
            if (chat_class == 'vision'):
                if (model_select != 'v'):
                    if  (len(image_urls) > 0) \
                    and (len(image_urls) == len(upload_files)):
                        if  (self.gpt_v_nick_name != '') \
                        and (self.gpt_v_enable == True):
                            model_select = 'v'

            if (chat_class == 'continue'):
                chat_class   = self.last_chat_class
                model_select = self.last_model_select
                print(' ChatGPT :', 'continue chat class = [', chat_class, '],', model_select)

            if (chat_class == 'knowledge') \
            or (chat_class == 'code_interpreter') \
            or (chat_class == 'assistant'):
                if  (self.gpt_x_nick_name != '') \
                and (self.gpt_x_enable == True):
                    model_select = 'x'
                    #if  (chat_class != 'knowledge') \
                    #and (chat_class != 'assistant'):
                    #    print(' ChatGPT :', 'chat class auto change, [', chat_class, '] → [', 'assistant', ']')
                    #    chat_class == 'assistant'
                else:
                    # 最後の要求
                    self.last_auto_inpText = None
            else:
                    # 最後の要求
                    self.last_auto_inpText = None

        if (chat_class != 'continue'):
            self.last_chat_class  = chat_class

        # model 補正
        if (model_select == 'v'):
            if (self.gpt_v_nick_name == '') \
            or (self.gpt_v_enable == False):
                model_select = 'auto'
            if (len(image_urls) == 0) \
            or (len(image_urls) != len(upload_files)):
                model_select = 'auto'

        if (model_select == 'x'):
            if   (self.gpt_x_nick_name == '') \
            or   (self.gpt_x_enable == False):
                model_select = 'auto'

        if (model_select == 'auto'):
            if (self.gpt_b_enable == True):
                if  (self.gpt_b_length != 0) \
                and (len(inpText) >= self.gpt_b_length):
                    model_select = 'b'

        #print(res_content, model_select)

        # functions (Azureの2023-03-15,2023-05-15はファンクション未対応)
        if (model_select != 'v'):
            #if  (self.openai_api_type != 'azure') \
            #or ((self.openai_api_type == 'azure') and (self.azure_version not in ('2023-03-15-preview', '2023-05-15'))):
                for module_dic in self.ext_module:
                    if (module_dic['onoff'] == 'on'):
                        functions.append(module_dic['function'])

        if (model_select != 'v'):
            self.last_model_select = model_select
        return chat_class, model_select, nick_name, model_name, upload_files, image_urls, functions



    def run_gpt(self, chat_class='chat', model_select='auto',
                nick_name=None, model_name=None,
                session_id='0', history=[], 
                sysText=None, reqText=None, inpText='こんにちは',
                upload_files=[], image_urls=[], functions=[],
                temperature=0.8, maxStep=10, jsonMode=False, ):
        #self.assistant_id[str(session_id)] = None
        self.thread_id[str(session_id)]    = None

        # 戻り値
        res_text    = ''
        res_path    = ''
        res_history = history

        # model 指定
        user_select = None
        if (self.gpt_a_nick_name != ''):
            if (inpText.strip()[:len(self.gpt_a_nick_name)+1].lower() == (self.gpt_a_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.gpt_a_nick_name)+1:]
                if (self.gpt_a_enable == True):
                    user_select  = 'a'
        if (self.gpt_b_nick_name != ''):
            if (inpText.strip()[:len(self.gpt_b_nick_name)+1].lower() == (self.gpt_b_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.gpt_b_nick_name)+1:]
                if (self.gpt_b_enable == True):
                    user_select  = 'b'
        if (self.gpt_v_nick_name != ''):
            if (inpText.strip()[:len(self.gpt_v_nick_name)+1].lower() == (self.gpt_v_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.gpt_v_nick_name)+1:]
                if (self.gpt_v_enable == True):
                    if  (len(image_urls) > 0) \
                    and (len(image_urls) == len(upload_files)):
                        user_select  = 'v'
        if (self.gpt_x_nick_name != ''):
            if (inpText.strip()[:len(self.gpt_x_nick_name)+1].lower() == (self.gpt_x_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.gpt_x_nick_name)+1:]
                if (self.gpt_x_enable == True):
                    user_select  = 'x'
        if  (user_select != None) \
        and (model_select == 'auto'):
            model_select = user_select

        # history 追加・圧縮 (古いメッセージ)
        res_history = self.history_add(history=res_history, sysText=sysText, reqText=reqText, inpText=inpText, )
        res_history = self.history_zip1(history=res_history, )

        # メッセージ作成
        if (model_select != 'v'):
            msg = self.history2msg_gpt(history=res_history, )
        else:
            msg = self.history2msg_vision(history=res_history, image_urls=image_urls,)

        # 実行ループ
        n = 0
        function_name = ''
        while (function_name != 'exit') and (n < int(maxStep)):

            # トークン数チェック　→　モデル確定
            nick_name, model_name, len_tokens = self.checkTokens(messages=msg, functions=functions, model_select=model_select, )
            if (model_name == None):
                print(' ChatGPT :', 'Token length over ! (' + str(len_tokens) + ')')

                if (len(res_history) > 6):
                    print(' ChatGPT :', 'History compress !')

                    # history 圧縮 (最後４つ残す)
                    res_history = self.history_zip2(history=res_history, )

                    # メッセージ作成
                    if (model_select != 'v'):
                        msg = self.history2msg_gpt(history=res_history, )
                    else:
                        msg = self.history2msg_vision(history=res_history, image_urls=image_urls,)

                    # トークン数再計算
                    nick_name, model_name, len_tokens = self.checkTokens(messages=msg, functions=functions, model_select=model_select, )

            if (model_name == None):
                print(' ChatGPT :', 'History reset !')

                # history リセット
                res_history = []
                res_history = self.history_add(history=res_history, sysText=sysText, reqText=reqText, inpText=inpText, )
                #res_history = self.zipHistory(history=res_history, )

                # メッセージ作成
                if (model_select != 'v'):
                    msg = self.history2msg_gpt(history=res_history, )
                else:
                    msg = self.history2msg_vision(history=res_history, image_urls=image_urls,)

                # トークン数再計算
                nick_name, model_name, len_tokens = self.checkTokens(messages=msg, functions=functions, model_select=model_select, )

            if (model_name == None):
                print(' ChatGPT :', 'Token length Error ! (' + str(len_tokens) + ')')
                return res_text, res_path, res_name, res_api, res_history

            # GPT
            n += 1
            print(' ChatGPT :', model_name + ', pass=' + str(n) + ', tokens=' + str(len_tokens) + ', ')

            # 結果
            res_role      = None
            res_content   = None
            function_name = None
            json_kwargs   = None

            #try:
            if True:

                # OPENAI
                if (self.openai_api_type != 'azure'):

                    if   (model_select == 'v') and (len(image_urls) > 0):
                        null_history = self.history_add(history=[], sysText=sysText, reqText=reqText, inpText=inpText, )
                        msg = self.history2msg_vision(history=null_history, image_urls=image_urls,)
                        completions = self.client_v.chat.completions.create(
                            model           = model_name,
                            messages        = msg,
                            max_tokens      = 4000,
                            timeout         = self.timeOut, )

                    elif (functions != []):
                        completions = self.client_ab.chat.completions.create(
                            model           = model_name,
                            messages        = msg,
                            temperature     = float(temperature),
                            functions       = functions,
                            function_call   = 'auto',
                            timeout         = self.timeOut, )

                    else:
                        if (jsonMode == False):
                            completions = self.client_ab.chat.completions.create(
                                model           = model_name,
                                messages        = msg,
                                temperature     = float(temperature),
                                timeout         = self.timeOut, )
                        else:
                            completions = self.client_ab.chat.completions.create(
                                model           = model_name,
                                messages        = msg,
                                temperature     = float(temperature),
                                timeout         = self.timeOut, 
                                response_format = { "type": "json_object" }, )

                # Azure
                else:

                    if   (model_select == 'v') and (len(image_urls) > 0):
                        null_history = self.history_add(history=[], sysText=sysText, reqText=reqText, inpText=inpText, )
                        msg = self.history2msg_vision(history=null_history, image_urls=image_urls,)
                        completions = self.client_v.chat.completions.create(
                            model           = model_name,
                            messages        = msg,
                            max_tokens      = 4000,
                            timeout         = self.timeOut, )

                    elif (functions != []):
                        completions = self.client_ab.chat.completions.create(
                            model           = model_name,
                            messages        = msg,
                            temperature     = float(temperature),
                            functions       = functions,
                            function_call   = 'auto',
                            timeout         = self.timeOut, )

                    else:
                        completions = self.client_ab.chat.completions.create(
                            #engine          = model_name,
                            #deployment_id   = model_name,
                            model           = model_name,
                            messages        = msg,
                            temperature     = float(temperature),
                            timeout         = self.timeOut, )

            #except Exception as e:
            #    print( json.dumps(msg, indent=4, ensure_ascii=False, ) )
            #    print(e)
            #    print('  ' + nick_name.lower() + ' error!')

            # GPT 結果確認
            #print(completions.choices[0])
            #print(completions.usage['prompt_tokens'])
            #print(completions.usage['completion_tokens'])
            #print(completions.usage['total_tokens'])

            # 結果
            try:
                res_role    = str(completions.choices[0].message.role)
                res_content = str(completions.choices[0].message.content)
            except:
                pass

            # function 指示？
            try:
                function_name = str(completions.choices[0].message.function_call.name)
                json_kwargs   = str(completions.choices[0].message.function_call.arguments)
                try:
                    wk_dic      = json.loads(json_kwargs)
                    wk_text     = json.dumps(wk_dic, ensure_ascii=False, )
                    json_kwargs = wk_text
                except:
                    pass
            except:
                pass

            # function 指示
            if (res_role == 'assistant') and (function_name != None):
                #print('  function_call "' + function_name + '"')

                #if (res_content != None):
                #    res_text += res_content.rstrip() + '\n'

                # 自動的にbモデルへ切替
                if (model_select == 'a'):
                    if (self.gpt_b_enable == True):
                        if (self.gpt_b_length != 0):
                            model_select = 'b'

                hit = False
                if (hit == False):

                    print()
                    for module_dic in self.ext_module:
                        if (function_name == module_dic['func_name']):
                            hit = True
                            print(' ChatGPT :', '  function_call "' + module_dic['script'] + '" (' + function_name + ')')
                            print(' ChatGPT :', '  →', json_kwargs)

                            # メッセージ追加格納
                            self.seq += 1
                            dic = {'seq': self.seq, 'time': time.time(), 'role': 'function_call', 'name': function_name, 'content': json_kwargs }
                            res_history.append(dic)

                            # function 実行
                            try:
                                ext_func_proc  = module_dic['func_proc']
                                res_json = ext_func_proc( json_kwargs )
                            except Exception as e:
                                print(e)
                                # エラーメッセージ
                                dic = {}
                                dic['error'] = e 
                                res_json = json.dumps(dic, ensure_ascii=False, )

                            # tool_result
                            print(' ChatGPT :', '  →', res_json)
                            print()

                            # メッセージ追加格納
                            dic = {'role': 'function', 'name': function_name, 'content': res_json }
                            msg.append(dic)
                            self.seq += 1
                            dic = {'seq': self.seq, 'time': time.time(), 'role': 'function', 'name': function_name, 'content': res_json }
                            res_history.append(dic)

                            # パス情報確認
                            try:
                                dic  = json.loads(res_json)
                                path = dic['image_path']
                                if (path != None):
                                    res_path = path
                            except:
                                pass

                            break

                if (hit == False):
                    print(' ChatGPT :', '  function_call Error ! (' + function_name + ')')
                    print(res_role, res_content, function_name, json_kwargs, )
                    try:
                        print(completions)
                    except:
                        pass
                    break

            # GPT 会話終了
            elif (res_role == 'assistant') and (res_content != None):
                function_name   = 'exit'
                print(' ChatGPT :', nick_name.lower() + ' complite.')

                # 自動で(B)モデル(GPT4)実行
                if (model_select == 'auto') or (model_select == 'a'):
                    if (self.gpt_b_enable == True):
                        if (nick_name != self.gpt_b_nick_name):
                            if (self.gpt_b_length != 0) and (len(res_text) >= self.gpt_b_length):
                                nick_name2, model_name2, len_tokens = self.checkTokens(messages=msg, functions=[], model_select='b', )
                                if (model_name2 != None):
                                    print(' ChatGPT :', nick_name2.lower() + ' start.')

                                    try:
                                        # OPENAI
                                        if (self.openai_api_type != 'azure'):
                                            completions2 = self.client_ab.chat.completions.create(
                                                model           = model_name2,
                                                messages        = msg,
                                                temperature     = float(temperature),)

                                        # Azure
                                        else:
                                            completions2 = self.client_ab.chat.completions.create(
                                                deployment_id   = model_name2,
                                                messages        = msg,
                                                temperature     = float(temperature),)

                                        res_role2    = str(completions2.choices[0].message.role)
                                        res_content2 = str(completions2.choices[0].message.content)
                                        if (res_role2 == 'assistant') and (res_content2 != None):
                                            nick_name   = nick_name2
                                            model       = model_name2
                                            res_role    = res_role2
                                            res_content = res_content2
                                            print(' ChatGPT :', nick_name.lower() + ' complite.')
                                    except Exception as e:
                                        print(e)
                                        print(' ChatGPT :', nick_name2.lower() + ' error!')

                if (res_content != None):
                    #print(res_content.rstrip())
                    res_text += res_content.rstrip() + '\n'

                # History 追加格納
                self.seq += 1
                dic = {'seq': self.seq, 'time': time.time(), 'role': res_role, 'name': '', 'content': res_text }
                res_history.append(dic)

            # 予期せぬ回答
            else:
                print(' ChatGPT :', 'Error !')
                print(' ChatGPT :', 'role =', res_role, ', content =', res_content, ', function_name =', function_name)
                try:
                    print(completions)
                except:
                    pass
                break

        return res_text, res_path, nick_name, model_name, res_history



    def run_assistant(self, chat_class='assistant', model_select='auto',
                      nick_name=None, model_name=None,
                      session_id='0', history=[],
                      sysText=None, reqText=None, inpText='こんにちは',
                      upload_files=[], image_urls=[], functions=[],
                      temperature=0.8, maxStep=10, jsonMode=False, ):

        # 戻り値
        res_text    = ''
        res_path    = ''
        if (nick_name  == None):
            nick_name   = self.gpt_x_nick_name
        if (model_name == None):
            model_name  = self.gpt_x_model1
        res_history = history

        # モデル設定（1 -> 2）
        if (chat_class == 'knowledge') \
        or (chat_class == 'code_interpreter'):
            if (self.gpt_x_model2 != ''):
                model_name  = self.gpt_x_model2

        # model 指定文字削除
        if (self.gpt_a_nick_name != ''):
            if (inpText.strip()[:len(self.gpt_a_nick_name)+1].lower() == (self.gpt_a_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.gpt_a_nick_name)+1:]
        if (self.gpt_b_nick_name != ''):
            if (inpText.strip()[:len(self.gpt_b_nick_name)+1].lower() == (self.gpt_b_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.gpt_b_nick_name)+1:]
        if (self.gpt_v_nick_name != ''):
            if (inpText.strip()[:len(self.gpt_v_nick_name)+1].lower() == (self.gpt_v_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.gpt_v_nick_name)+1:]
        if (self.gpt_x_nick_name != ''):
            if (inpText.strip()[:len(self.gpt_x_nick_name)+1].lower() == (self.gpt_x_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.gpt_x_nick_name)+1:]

        # history 追加・圧縮 (古いメッセージ)
        res_history = self.history_add(history=res_history, sysText=sysText, reqText=reqText, inpText=inpText, )
        res_history = self.history_zip1(history=res_history, )

        # 結果
        res_role      = None
        res_content   = None
        download_hit  = False

        upload_ids    = []

        exit_status   = None
        last_status   = None

        # アシスタント確認
        my_assistant_name   = self.assistant_name + '-' + str(session_id)
        my_assistant_id     = self.assistant_id.get(str(session_id))
        if (my_assistant_id == None):

            # 動作設定
            instructions = sysText
            if (instructions == None) or (instructions == ''):
                instructions = 'あなたは優秀なアシスタントです。'

            # アシスタント検索
            assistants = self.client_x.beta.assistants.list(
                order = "desc",
                limit = "100", )
            for a in range(len(assistants.data)):
                assistant = assistants.data[a]
                if (assistant.name == my_assistant_name):
                    my_assistant_id = assistant.id
                    break

            # アシスタント生成
            if (my_assistant_id == None):

                # アシスタント削除
                if (self.max_assistant > 0) and (len(assistants.data) > 0):
                    for a in range(self.max_assistant -1 , len(assistants.data)):
                        assistant = assistants.data[a]
                        if (assistant.name != my_assistant_name):
                            print(' Assistant :', 'Delete assistant_name = "' + assistant.name + '",')

                            # ファイル削除
                            res = self.assistantFiles_del(
                                assistant_id = assistant.id, )

                            # アシスタント削除
                            res = self.client_x.beta.assistants.delete(
                                assistant_id = assistant.id, )

                # アシスタント生成
                print(' Assistant :', 'Create assistant_name = "' + my_assistant_name + '",')
                assistant = self.client_x.beta.assistants.create(
                    name     = my_assistant_name,
                    model    = model_name,
                    instructions = instructions,
                    tools    = [],
                    file_ids = [], )
                my_assistant_id = assistant.id
                self.assistant_id[str(session_id)] = my_assistant_id

            # アシスタント更新
            if (my_assistant_id != None):

                # 検索文書設定
                assistantFiles_ids = self.assistantFiles_load(
                    retrievalFiles_path = '_extensions/retrieval_files/',
                    assistant_id        = my_assistant_id, 
                    assistant_name      = my_assistant_name, )

                # ツール設定
                tools     = [{"type": "code_interpreter"}]
                if (len(assistantFiles_ids) > 0):
                    tools.append({"type": "retrieval"})
                if (functions != []):
                    for f in range(len(functions)):
                        tools.append({"type": "function", "function": functions[f]})
                #print(tools)

                # アシスタント取得
                assistant = self.client_x.beta.assistants.retrieve(
                    assistant_id = my_assistant_id, )

                # アシスタント更新
                if (model_name != assistant.model) \
                or (instructions != assistant.instructions) \
                or (assistantFiles_ids != assistant.file_ids):
                    print(' Assistant :', 'Update assistant_name = "' + my_assistant_name + '",')
                    assistant = self.client_x.beta.assistants.update(
                        assistant_id = my_assistant_id,
                        model        = model_name,
                        instructions = instructions,
                        tools        = tools,
                        file_ids     = assistantFiles_ids, )
                else:
                    assistant = self.client_x.beta.assistants.update(
                        assistant_id = my_assistant_id,
                        tools        = tools, )
        
        # スレッド確認
        my_thread_id = self.thread_id.get(str(session_id))
        if (my_thread_id == None):

            # スレッド生成
            print(' Assistant :', 'Create thread (assistant_name) = "' + my_assistant_name + '",')
            thread = self.client_x.beta.threads.create(
                metadata = {'assistant_name': my_assistant_name}, )
            my_thread_id = thread.id
            self.thread_id[str(session_id)] = my_thread_id

            # 過去メッセージ追加
            for m in range(len(res_history) - 1):
                role    = res_history[m].get('role','')
                content = res_history[m].get('content','')
                name    = res_history[m].get('name','')
                if (role != 'system'):
                    # 全てユーザーメッセージにて処理
                    if (name == None) or (name == ''):
                        msg_text = 'message_history / (' + role + ')' + '\n' + content
                    else:
                        if (role == 'function_call'):
                            msg_text = 'message_history / (function ' + name + ' call)'  + '\n' + content
                        else:
                            msg_text = 'message_history / (function ' + name + ' result) ' + '\n' + content
                    #print(msg_text)
                    res = self.client_x.beta.threads.messages.create(
                        thread_id = my_thread_id,
                        role      = 'user',
                        content   = msg_text, )

        # ファイルアップロード
        upload_ids = self.threadFile_set(
            upload_files   = upload_files,
            assistant_name = my_assistant_name, )
        #print("##", upload_ids, "##")

        # メッセージ生成
        res = self.client_x.beta.threads.messages.create(
            thread_id = my_thread_id,
            role      = 'user',
            content   = inpText,
            file_ids  = upload_ids, )

        # 実行開始
        run = self.client_x.beta.threads.runs.create(
            assistant_id = my_assistant_id,
            thread_id    = my_thread_id, )
        my_run_id = run.id

        # 実行ループ
        exit_status   = None
        last_status   = None
        last_step     = 0
        messages = self.client_x.beta.threads.messages.list(
                thread_id = my_thread_id, 
                order     = 'asc', )
        last_msg_step = len(messages.data) # First msg is request
        last_message  = None
        
        chkTime       = time.time()
        while (exit_status == None) and ((time.time() - chkTime) < (self.timeOut * 5)):

            # ステータス
            run = self.client_x.beta.threads.runs.retrieve(
                thread_id = my_thread_id,
                run_id    = my_run_id, )
            if (run.status != last_status):
                last_status = run.status
                chkTime     = time.time()
                print(' Assistant :', last_status)

            # 完了時は少し待機
            if (last_status == 'completed'):
                time.sleep(0.50)

            # 実行ステップ確認
            time.sleep(0.25)
            run_steps = self.client_x.beta.threads.runs.steps.list(
                    thread_id = my_thread_id,
                    run_id    = my_run_id,
                    order     = 'asc', )
            if (len(run_steps.data) > last_step):
                for r in range(last_step, len(run_steps.data)):
                    step_details_type = run_steps.data[r].step_details.type
                    if (step_details_type != 'tool_calls'):
                        print(' Assistant :', '(' + step_details_type + ')')
                    else:
                        #print(run_steps.data[r].step_details)
                        step_details_tool_type = None
                        try:
                            step_details_tool_type = run_steps.data[r].step_details.tool_calls[0].type
                        except:
                            try:
                                tc = run_steps.data[r].step_details.tool_calls[0]
                                step_details_tool_type = tc.get('type')
                            except:
                                pass
                        if (step_details_tool_type != None):
                            print(' Assistant :', '(' + step_details_tool_type + '...)')
                        else:
                            print(' Assistant :', '(' + step_details_type + ')')

                    if (step_details_type == 'message_creation'):
                        message_id = run_steps.data[r].step_details.message_creation.message_id
                        if (message_id != None):
                            messages = self.client_x.beta.threads.messages.retrieve(
                                    thread_id  = my_thread_id, 
                                    message_id = message_id, )
                            for c in range(len(messages.content)):
                                content_type = messages.content[c].type
                                if (content_type == 'text'):
                                    content_value = messages.content[c].text.value
                                    if (content_value != None) and (content_value != ''):
                                        if (last_status != 'completed'):
                                            if (content_value != last_message):
                                                last_message = content_value 
                                                print(last_message)
                                                print()

                last_step = len(run_steps.data)

            # 最大ステップ  10step x (3auto+1) / 2 = 20
            limit_step = int((int(maxStep) * (int(self.auto_continue)+1)) / 2)
            if (last_step > limit_step):
                exit_status = 'overstep'
                print(' Assistant :', 'overstep! (n=' + str(last_step) + '!)')
                break

            # 実行メッセージ確認
            time.sleep(0.25)
            messages = self.client_x.beta.threads.messages.list(
                    thread_id = my_thread_id, 
                    order     = 'asc', )
            if (len(messages.data) > last_msg_step):
                for m in range(last_msg_step, len(messages.data)):

                    res_role = messages.data[m].role
                    for c in range(len(messages.data[m].content)):
                        content_type = messages.data[m].content[c].type
                        if (content_type == 'image_file'):
                            file_type   = content_type
                            file_id     = messages.data[m].content[c].image_file.file_id
                            if (file_id != None):
                                print(' Assistant :', '(', file_type, file_id, ')', )

                        if (content_type == 'text'):
                            content_value = messages.data[m].content[c].text.value
                            if (content_value != None) and (content_value != ''):
                                last_msg_step = m
                                if (last_status != 'completed'):
                                    if (content_value != last_message):
                                        last_message = content_value 
                                        print(last_message)
                                        print()
                                else:
                                    res_content  = content_value

                            if (messages.data[m].content[c].text.annotations != None):
                                for a in range(len(messages.data[m].content[c].text.annotations)):
                                    file_type = messages.data[m].content[c].text.annotations[a].type
                                    file_text = messages.data[m].content[c].text.annotations[a].text
                                    file_id   = None
                                    try:
                                        file_id = messages.data[m].content[c].text.annotations[a].file_path.file_id
                                    except Exception as e:
                                        print(messages.data[m].content[c].text.annotations[a])
                                        print(e)

                                    print(' Assistant :', file_type, file_text, file_id, )

                                    try:
                                        if (file_id != None):
                                            download_hit = True

                                            file_dic  = self.client_x.files.retrieve(file_id)
                                            filename = os.path.basename(file_dic.filename)
                                            content_file = self.client_x.files.content(file_id)
                                            data_bytes   = content_file.read()
                                            with open(qPath_output + filename, "wb") as file:
                                                file.write(data_bytes)
                                            print(' Assistant :', 'Download ...', file_text, )
                                    except:
                                        pass

            # 処理中
            if   (last_status == 'in_progress') \
            or   (last_status == 'queued') \
            or   (last_status == 'cancelling'):
                pass

            # 終了
            elif (last_status == 'completed') \
            or   (last_status == 'cancelled') \
            or   (last_status == 'failed') \
            or   (last_status == 'expired'):
                exit_status = last_status

                # 正常終了
                if (last_status == 'completed'):
                    break

                # その他終了
                else:
                    print(' Assistant :', '!')
                    break

            # ファンクション
            elif (last_status == 'requires_action'):
                tool_result = []

                print()
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                for t in range(len(tool_calls)):
                    tool_call_id  = tool_calls[t].id
                    function_name = tool_calls[t].function.name
                    json_kwargs   = tool_calls[t].function.arguments

                    hit = False
                    for module_dic in self.ext_module:
                        if (function_name == module_dic['func_name']):
                            hit = True
                            print(' Assistant :', '  function_call "' + module_dic['script'] + '" (' + function_name + ')')
                            print(' Assistant :', '  →', json_kwargs)

                            chkTime     = time.time()

                            # メッセージ追加格納
                            self.seq += 1
                            dic = {'seq': self.seq, 'time': time.time(), 'role': 'function_call', 'name': function_name, 'content': json_kwargs }
                            res_history.append(dic)

                            # function 実行
                            try:
                                ext_func_proc  = module_dic['func_proc']
                                res_json       = ext_func_proc( json_kwargs )
                            except Exception as e:
                                print(e)
                                # エラーメッセージ
                                dic = {}
                                dic['error'] = e 
                                res_json = json.dumps(dic, ensure_ascii=False, )

                            chkTime     = time.time()

                            # メッセージ追加格納
                            self.seq += 1
                            dic = {'seq': self.seq, 'time': time.time(), 'role': 'function', 'name': function_name, 'content': res_json }
                            res_history.append(dic)

                            # パス情報確認
                            try:
                                dic  = json.loads(res_json)
                                path = dic['image_path']
                                if (path != None):
                                    res_path = path
                            except:
                                pass

                    if (hit == False):
                        print(' Assistant :', '  function_call Error ! (' + function_name + ')')
                        print(json_kwargs, )

                        dic = {}
                        dic['result'] = 'error' 
                        res_json = json.dumps(dic, ensure_ascii=False, )

                    # tool_result
                    print(' Assistant :', '  →', res_json)
                    print()
                    tool_result.append({"tool_call_id": tool_call_id, "output": res_json})

                # 結果通知
                run = self.client_x.beta.threads.runs.submit_tool_outputs(
                    thread_id    = my_thread_id,
                    run_id       = my_run_id,
                    tool_outputs = tool_result, )

            else:
                print(run)
                print()
                time.sleep(1)

        if (exit_status == None):
            exit_status = 'timeout'
            print(' Assistant :', 'timeout! (' + str(self.timeOut * 5) + 's)')
            #raise RuntimeError('assistant run timeout !')
            
        # 結果確認
        if (exit_status == 'completed'):

            if (res_content != None):
                #print(res_content.rstrip())
                res_text += res_content.rstrip() + '\n'

            if (download_hit == True):
                res_text += '\n' + '※ OpenAI API (beta版 2023/11/18時点)で、ダウンロードは安定？しているようです。' + '\n'

            # History 追加格納
            self.seq += 1
            dic = {'seq': self.seq, 'time': time.time(), 'role': res_role, 'name': '', 'content': res_text }
            res_history.append(dic)

        # 異常終了
        else:
            res_text = ''

            # History 追加格納
            self.seq += 1
            dic = {'seq': self.seq, 'time': time.time(), 'role': 'assistant', 'name': '', 'content': exit_status }
            res_history.append(dic)

            # 実行キャンセル
            runs = self.client_x.beta.threads.runs.list(
                thread_id = my_thread_id, )
            for r in range(len(runs.data)):
                run_id     = runs.data[r].id
                run_status = runs.data[r].status
                if  (run_status != 'completed') \
                and (run_status != 'cancelled') \
                and (run_status != 'failed') \
                and (run_status != 'expired') \
                and (run_status != 'cancelling'):
                    try:
                        run = self.client_x.beta.threads.runs.cancel(
                            thread_id = my_thread_id, 
                            run_id    = run_id, )
                        print(' Assistant :', 'run cancel ...', run_id, )
                    except:
                        pass

        # ファイル削除
        res = self.threadFile_del(upload_ids=upload_ids, )

        return res_text, res_path, nick_name, model_name, res_history

    def auto_assistant(self, chat_class='chat', model_select='auto',
                      nick_name=None, model_name=None,
                      session_id='0', history=[],
                      sysText=None, reqText=None, inpText='こんにちは',
                      upload_files=[], image_urls=[], functions=[], 
                      temperature=0.8, maxStep=10, jsonMode=False, ):

        # 戻り値
        res_text    = ''
        res_path    = ''
        if (nick_name  == None):
            nick_name   = self.gpt_x_nick_name
        if (model_name == None):
            model_name  = self.gpt_x_model1
        res_history = history

        # モデル設定（1 -> 2）
        if (chat_class == 'knowledge') \
        or (chat_class == 'code_interpreter'):
            if (self.gpt_x_model2 != ''):
                model_name  = self.gpt_x_model2

        # model 指定文字削除
        if (self.gpt_a_nick_name != ''):
            if (inpText.strip()[:len(self.gpt_a_nick_name)+1].lower() == (self.gpt_a_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.gpt_a_nick_name)+1:]
        if (self.gpt_b_nick_name != ''):
            if (inpText.strip()[:len(self.gpt_b_nick_name)+1].lower() == (self.gpt_b_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.gpt_b_nick_name)+1:]
        if (self.gpt_v_nick_name != ''):
            if (inpText.strip()[:len(self.gpt_v_nick_name)+1].lower() == (self.gpt_v_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.gpt_v_nick_name)+1:]
        if (self.gpt_x_nick_name != ''):
            if (inpText.strip()[:len(self.gpt_x_nick_name)+1].lower() == (self.gpt_x_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.gpt_x_nick_name)+1:]

        # history 圧縮 (最後４つ残す)
        old_history = self.history_zip2(history=history, )

# ----- あなたの役割 -----
# あなたは、会話履歴と最後のユーザーの要求、ＡＩ応答から、継続実行の必要性、回答評価を行います。
# 回答はjson形式で、continue,result_point,assessment_textで行います。
#
# ----- あなたへの依頼 -----
# 継続実行の必要性はcontinueとして、no,yes,stopで回答してください。(例) yes
# 回答評価はresult_pointで、ユーザー要求に対して、達成率で回答してください。(例) 30
# 回答評価した理由assessment_textもお願いします。(例) 動くソース要求に対して回答がメインロジックのみの回答
# 以下の条件で、回答してください。
# 1) ユーザーの要求に到達している場合、continue=no,result_point=達成率,assessment_text=評価理由
# 2) 処理途中と思われる場合で、ユーザーが新たな要求入力として「適切に判断して処理を継続してください」と入力した場合に適切に処理を継続出来そうな場合、continue=yes,result_point=達成率,assessment_text=評価理由
# 3) 上記以外の場合や継続実行がむつかしいと考えられる場合、continue=stop,result_point=達成率,assessment_text=評価理由

        # GPT 評価判定（準備）
        auto_sysText = \
"""
----- Your Role -----
You are responsible for assessing the necessity of continued execution, and evaluating responses based on the conversation history, the user's last request, and the AI's response.
Please provide your answers in JSON format, using the keys "continue," "result_point," and "assessment_text."
""" + '\n\n'
        auto_reqText = \
"""
----- Your Task -----
For the necessity of continued execution, respond with "continue" using the options "no," "yes," or "stop." (Example: yes)
Evaluate the response with "result_point" based on the achievement rate in relation to the user's request. (Example: 30)
Also, please provide the reason for your evaluation with "assessment_text." (Example: The response only addressed the main logic in response to a request for a working source code.)
Respond according to the following criteria:
1) If the user's request has been met, respond with continue=no, result_point=achievement rate, assessment_text=reason for evaluation.
2) If it seems to be in the middle of processing and the user has entered a new request saying "Please continue processing appropriately," and it seems possible to continue processing appropriately, respond with continue=yes, result_point=achievement rate, assessment_text=reason for evaluation.
3) In other cases or when continued execution is deemed difficult, respond with continue=stop, result_point=achievement rate, assessment_text=reason for evaluation.
""" + '\n\n'

        # ユーザー要求
        auto_inpText = ''
        if  (self.last_input_class == 'continue') \
        and (self.last_auto_inpText != None):
            auto_inpText = self.last_auto_inpText

        else:
            if (len(old_history) > 2):
                auto_inpText = '----- 会話履歴 -----' + '\n'
                for m in range(len(old_history) - 1):
                    role    = str(old_history[m].get('role', ''))
                    content = str(old_history[m].get('content', ''))
                    name    = str(old_history[m].get('name', ''))
                    if (role != 'system'):
                        # 全てユーザーメッセージにて処理
                        if (name == None) or (name == ''):
                            auto_inpText += '(' + role + ')' + '\n'
                            auto_inpText += content + '\n\n'
            auto_inpText += '----- 最後のユーザー入力 -----' + '\n'
            auto_inpText += inpText + '\n\n'

        self.last_auto_inpText = auto_inpText

        # 実行ループ
        n = 0
        while (n < int(self.auto_continue)):

            # GPT
            n += 1
            print(' Assistant :', model_name + ', pass=' + str(n) + ', ')

            # OpenAI
            if (self.openai_api_type != 'azure'):

                # Assistant
                res_text2, res_path2, nick_name, model_name, res_history = \
                    self.run_assistant(model_select=model_select,
                                       nick_name=nick_name, model_name=model_name,
                                       session_id=session_id, history=res_history, chat_class=chat_class,
                                       sysText=sysText, reqText=reqText, inpText=inpText,
                                       upload_files=upload_files, image_urls=image_urls, functions=functions,
                                       temperature=temperature, maxStep=maxStep, jsonMode=jsonMode, )
            
            # Azure
            else:

                # GPT
                res_text2, res_path2, nick_name, model_name, res_history = \
                    self.run_gpt(model_select=model_select,
                                 nick_name=nick_name, model_name=model_name,
                                 session_id=session_id, history=res_history, chat_class=chat_class, 
                                 sysText=sysText, reqText=reqText, inpText=inpText,
                                 upload_files=upload_files, image_urls=image_urls, functions=functions,
                                 temperature=temperature, maxStep=maxStep, jsonMode=jsonMode, )

            if  (res_text2 != None) \
            and (res_text2 != '') \
            and (res_text2 != '!'):
                res_text += res_text2
            if  (res_path2 != None) \
            and (res_path2 != ''):
                res_path = res_path2

            # 実行検査
            if  (res_text == None) \
            or  (res_text == '') \
            or  (res_text == '!'): 
                break
            else:

                # GPT 評価判定
                check_inpText  = auto_inpText
                check_inpText += '----- ＡＩ応答 -----' + '\n'
                check_inpText += res_text2 + '\n\n'
                wk_json, wk_path, wk_nick_name, wk_model_name, wk_history = \
                    self.run_gpt(chat_class='check', model_select='auto',
                                 nick_name=None, model_name=None,
                                 session_id='sys', history=[],
                                 sysText=auto_sysText, reqText=auto_reqText, inpText=check_inpText,
                                 upload_files=[], image_urls=[], functions=[], jsonMode=True, )

                continue_yn     = None
                result_point    = None
                assessment_text = None
                try:
                    args_dic        = json.loads(wk_json)
                    continue_yn     = args_dic.get('continue')
                    result_point    = args_dic.get('result_point')
                    assessment_text = args_dic.get('assessment_text')
                    print(' Assistant :', 'continue="' + continue_yn + '", point=' + str(result_point) + ', (' + wk_model_name + ')')
                    if (continue_yn != 'yes'):
                        print(assessment_text)
                except:
                    print(wk_json)

                # 継続判断
                if   (continue_yn == 'no'):
                    print(' Assistant :', 'completed OK !')
                    break
                elif (continue_yn != 'yes') \
                and  (continue_yn != 'no'):
                    print(' Assistant :', 'stop !')
                    break
                else:
                    if (n < int(self.auto_continue)):
                        #print(' Assistant :', 'assistant' + '\n' + res_text2)
                        reqText = ''
                        inpText = ''
                        if (continue_yn == 'yes'):
                            inpText += assessment_text + '\n'
                        inpText += '適切に判断して処理を継続してください' + '\n'
                        print(' Assistant :', 'auto continue,', )
                        print(inpText)
                    else:
                        print(' Assistant :', 'auto continue exit !', )

        return res_text, res_path, nick_name, model_name, res_history



    def chatBot(self, chat_class='auto', model_select='auto',
                session_id='0', history=[],
                sysText=None, reqText=None, inpText='こんにちは', 
                filePath=[],
                temperature=0.8, maxStep=10, inpLang='ja-JP', outLang='ja-JP', ):

        # 戻り値
        res_text        = ''
        res_path        = ''
        nick_name       = None
        model_name      = None
        res_history     = history

        if (self.bot_auth is None):
            print('ChatGPT: Not Authenticate Error !')
            return res_text, res_path, nick_name, model_name, res_history

        # 実行モデル判定
        upload_files    = []
        image_urls      = []
        functions       = []
        chat_class, model_select, nick_name, model_name, \
        upload_files, image_urls, functions = \
            self.model_check(chat_class=chat_class, model_select=model_select, 
                             session_id=session_id, history=[],
                             sysText=sysText, reqText=reqText, inpText=inpText, filePath=filePath, )

        # ChatGPT
        if (model_select == 'auto') \
        or (model_select == 'a') \
        or (model_select == 'b') \
        or (model_select == 'v'):
            #try:
                res_text, res_path, nick_name, model_name, res_history = \
                    self.run_gpt(chat_class=chat_class, model_select=model_select,
                                 nick_name=nick_name, model_name=model_name,
                                 session_id=session_id, history=res_history,
                                 sysText=sysText, reqText=reqText, inpText=inpText,
                                 upload_files=upload_files, image_urls=image_urls, functions=functions,
                                 temperature=temperature, maxStep=maxStep, )
            #except Exception as e:
            #    print(e)

        # Assistant
        elif (model_select == 'x'):
            #try:
                res_text, res_path, nick_name, model_name, res_history = \
                    self.auto_assistant(chat_class=chat_class, model_select=model_select,
                                        nick_name=nick_name, model_name=model_name,
                                        session_id=session_id, history=res_history,
                                        sysText=sysText, reqText=reqText, inpText=inpText,
                                        upload_files=upload_files, image_urls=image_urls, functions=functions,
                                        temperature=temperature, maxStep=maxStep, )
            #except Exception as e:
            #    print(e)
        else:
            print(' ChatGPT :', 'Model select error!', api_type, model_select)

        # 文書成形
        if (res_text != ''):
            res_text = res_text.replace('。', '。\n')
            res_text = res_text.replace('。\n」', '。」')
            res_text = res_text.replace('\r', '')
            hit = True
            while (hit == True):
                if (res_text.find('\n\n')>0):
                    hit = True
                    res_text = res_text.replace('\n\n', '\n')
                else:
                    hit = False
            res_text = res_text.strip()
        else:
            res_text = '!'

        return res_text, res_path, nick_name, model_name, res_history



if __name__ == '__main__':

        #openaiAPI = speech_bot_openai.ChatBotAPI()
        openaiAPI = ChatBotAPI()

        api_type = openai_key.getkey('chatgpt','openai_api_type')
        print(api_type)

        if (api_type != 'azure'):
            res = openaiAPI.authenticate('chatgpt',
                            api_type,
                            openai_key.getkey('chatgpt','openai_default_gpt'), openai_key.getkey('chatgpt','openai_default_class'),
                            openai_key.getkey('chatgpt','openai_auto_continue'),
                            openai_key.getkey('chatgpt','openai_max_step'), openai_key.getkey('chatgpt','openai_max_assistant'),
                            openai_key.getkey('chatgpt','openai_organization'), openai_key.getkey('chatgpt','openai_key_id'),
                            openai_key.getkey('chatgpt','azure_endpoint'), openai_key.getkey('chatgpt','azure_version'), openai_key.getkey('chatgpt','azure_key_id'),
                            openai_key.getkey('chatgpt','gpt_a_nick_name'),
                            openai_key.getkey('chatgpt','gpt_a_model1'), openai_key.getkey('chatgpt','gpt_a_token1'),
                            openai_key.getkey('chatgpt','gpt_a_model2'), openai_key.getkey('chatgpt','gpt_a_token2'),
                            openai_key.getkey('chatgpt','gpt_a_model3'), openai_key.getkey('chatgpt','gpt_a_token3'),
                            openai_key.getkey('chatgpt','gpt_b_nick_name'),
                            openai_key.getkey('chatgpt','gpt_b_model1'), openai_key.getkey('chatgpt','gpt_b_token1'),
                            openai_key.getkey('chatgpt','gpt_b_model2'), openai_key.getkey('chatgpt','gpt_b_token2'),
                            openai_key.getkey('chatgpt','gpt_b_model3'), openai_key.getkey('chatgpt','gpt_b_token3'),
                            openai_key.getkey('chatgpt','gpt_b_length'),
                            openai_key.getkey('chatgpt','gpt_v_nick_name'),
                            openai_key.getkey('chatgpt','gpt_v_model1'), openai_key.getkey('chatgpt','gpt_v_token1'),
                            openai_key.getkey('chatgpt','gpt_x_nick_name'),
                            openai_key.getkey('chatgpt','gpt_x_model1'), openai_key.getkey('chatgpt','gpt_x_token1'),
                            openai_key.getkey('chatgpt','gpt_x_model2'), openai_key.getkey('chatgpt','gpt_x_token2'),
                            )
        else:
            res = openaiAPI.authenticate('chatgpt',
                            api_type,
                            openai_key.getkey('chatgpt','openai_default_gpt'), openai_key.getkey('chatgpt','openai_default_class'),
                            openai_key.getkey('chatgpt','openai_auto_continue'),
                            openai_key.getkey('chatgpt','openai_max_step'), openai_key.getkey('chatgpt','openai_max_assistant'),
                            openai_key.getkey('chatgpt','openai_organization'), openai_key.getkey('chatgpt','openai_key_id'),
                            openai_key.getkey('chatgpt','azure_endpoint'), openai_key.getkey('chatgpt','azure_version'), openai_key.getkey('chatgpt','azure_key_id'),
                            openai_key.getkey('chatgpt','azure_a_nick_name'),
                            openai_key.getkey('chatgpt','azure_a_model1'), openai_key.getkey('chatgpt','azure_a_token1'),
                            openai_key.getkey('chatgpt','azure_a_model2'), openai_key.getkey('chatgpt','azure_a_token2'),
                            openai_key.getkey('chatgpt','azure_a_model3'), openai_key.getkey('chatgpt','azure_a_token3'),
                            openai_key.getkey('chatgpt','azure_b_nick_name'),
                            openai_key.getkey('chatgpt','azure_b_model1'), openai_key.getkey('chatgpt','azure_b_token1'),
                            openai_key.getkey('chatgpt','azure_b_model2'), openai_key.getkey('chatgpt','azure_b_token2'),
                            openai_key.getkey('chatgpt','azure_b_model3'), openai_key.getkey('chatgpt','azure_b_token3'),
                            openai_key.getkey('chatgpt','azure_b_length'),
                            openai_key.getkey('chatgpt','azure_v_nick_name'),
                            openai_key.getkey('chatgpt','azure_v_model1'), openai_key.getkey('chatgpt','azure_v_token1'),
                            openai_key.getkey('chatgpt','azure_x_nick_name'),
                            openai_key.getkey('chatgpt','azure_x_model1'), openai_key.getkey('chatgpt','azure_x_token1'),
                            openai_key.getkey('chatgpt','azure_x_model2'), openai_key.getkey('chatgpt','azure_x_token2'),
                            )
        print('authenticate:', res, )
        if (res == True):

            if True:
                #res, msg = openaiAPI.extensions_load(extensions_path='_extensions/openai_gpt/', secure_level='medium', )
                res, msg = openaiAPI.extensions_load(extensions_path='_extensions/openai_gpt/', secure_level='low', )
                if (res != True) or (msg != ''):
                    print(msg)
                    print()
 
            if False:
                sysText = None
                reqText = ''
                #inpText = 'おはようございます。'
                inpText = 'この画像はなんだと思いますか？'
                filePath = ['_icons/dog.jpg', '_icons/kyoto.png']
                print()
                print('[Request]')
                print(reqText, inpText )
                print()
                res_text, res_path, res_name, res_api, openaiAPI.history = openaiAPI.chatBot(
                            chat_class='vision', model_select='auto', 
                            session_id='0', history=openaiAPI.history,
                            sysText=sysText, reqText=reqText, inpText=inpText, filePath=filePath,
                            inpLang='ja', outLang='ja', )
                print()
                print('[' + res_name + '] (' + res_api + ')' )
                print('', res_text)
                print()

            if False:
                sysText = None
                reqText = ''
                #reqText = '以下の質問には、コテコテの大阪弁で回答してください。'
                #inpText = 'おはようございます。'
                inpText = '日本で有名な観光地を詳しく教えてください。'
                #inpText = '今日は何月何日？'
                #inpText = '私のニックネームは「こんさん」です。覚えましたか？'
                #inpText = '連絡先のかんべさんと連絡先のみきちゃんの電話番号？'
                #inpText = 'かわいい猫の画像生成してください。'
                filePath = []
                print('[Request]')
                print(reqText, inpText )
                print()
                res_text, res_path, res_name, res_api, openaiAPI.history = openaiAPI.chatBot(
                            chat_class='chat', model_select='auto', 
                            session_id='0', history=openaiAPI.history,
                            sysText=sysText, reqText=reqText, inpText=inpText, filePath=filePath,
                            inpLang='ja', outLang='ja', )
                print()
                print('[' + res_name + '] (' + res_api + ')' )
                print('', res_text)
                print()

            if True:
                sysText = None
                reqText = ''
                #inpText = 'おはようございます。'
                #inpText = '計算式 123 * 456 * (7 + 8) の答え？'
                #inpText = 'riki,今日は何月何日？'
                #inpText = 'riki,私のニックネームを覚えていますか？'
                inpText = 'riki,日本の主要３都市の天気？'
                #inpText = '保存してあるClip&GPTのナレッジ文書を検索して、起動方法教えて'
                #inpText = 'ランダムな数値での折れ線グラフ出力するプログラム生成。\n生成後に実行\n実行結果の画像と使ったソースをください。'
                #inpText = 'guiですぐに遊べるリバーシプログラムの生成お願いします。最後にソースをください。'
                filePath = []
                # 2023/11/12時点添付ファイルの処理には課題あり
                # 2023/11/18時点添付ファイルの処理には課題解消
                #inpText = 'riki,送信してある売上のcsvファイルの総合計を計算してください'
                #filePath = ['_icons/test_sales.csv',]
                print()
                print('[Request]')
                print(reqText, inpText )
                print()
                res_text, res_path, res_name, res_api, openaiAPI.history = openaiAPI.chatBot(
                            chat_class='auto', model_select='auto', 
                            session_id='0', history=openaiAPI.history,
                            sysText=sysText, reqText=reqText, inpText=inpText, filePath=filePath,
                            inpLang='ja', outLang='ja', )
                print()
                print('[' + res_name + '] (' + res_api + ')' )
                print('', res_text)
                print()

            if False:
                res, msg = openaiAPI.extensions_unload()
                if (res != True) or (msg != ''):
                    print(msg)
                    print()

            if False:
                print('[History]')
                for h in range(len(openaiAPI.history)):
                    print(openaiAPI.history[h])
                    print()


