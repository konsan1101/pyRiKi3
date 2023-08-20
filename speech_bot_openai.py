#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2023 Mitsuo KONDOU.
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

import glob
import importlib

import json



import _v6__qRiKi_key
qRiKi_key = _v6__qRiKi_key.qRiKi_key_class()



# openai チャットボット
import openai
import tiktoken
import speech_bot_openai_key  as openai_key



class ChatBotAPI:

    def __init__(self, ):
        self.timeOut                = 10
        self.bot_auth               = None

        self.openai_api_type        = None
        self.openai_organization    = None
        self.openai_key_id          = None

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

        self.gpt_b_length           = 0

        self.azure_endpoint         = None
        self.azure_version          = None
        self.azure_key_id           = None
        self.azure_deploy_model     = None
        self.zaure_deploy_token     = 0

        self.seq                    = 0
        self.history                = []

        self.ext_module             = []

    def unloadExtensions(self, ):
        res_unload_all = True
        res_unload_msg = ''
        print('unload Extensions... ')

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

    def loadExtensions(self, extensions_path='_extensions/openai_gpt/', secure_level='medium', ):
        res_load_all = True
        res_load_msg = ''
        self.unloadExtensions()

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
                    ext_onoff  = 'on'
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
                    if   (secure_level == 'low'):
                        auth = '2'
                    elif (secure_level == 'medium'):
                        if (ext_func_auth == ''):
                            res_load_msg += '"' + ext_script + '"が認証されていません。(Warning!)' + '\n'
                            auth = '1'
                            ext_onoff = 'off'
                        else:
                            auth = qRiKi_key.decryptText(text=ext_func_auth)
                            if  (auth != ext_func_name + '-' + ext_func_ver) \
                            and (auth != self.openai_organization):
                                #print(ext_func_auth, auth)
                                res_load_msg += '"' + ext_script + '"は改ざんされたコードです。Loadingキャンセルされます。' + '\n'
                                res_load_all = False
                            else:
                                enable = '2'
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
                                enable = '2'

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

    def resetExtensions(self, ):
        res_reset_all = True
        res_reset_msg = ''
        print('reset Extensions... ')
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

    def setTimeOut(self, timeOut=20, ):
        self.timeOut      = timeOut

    def authenticate(self, api, openai_api_type,
                     openai_organization, openai_key_id,
                     gpt_a_nick_name, 
                     gpt_a_model1, gpt_a_token1, 
                     gpt_a_model2, gpt_a_token2, 
                     gpt_a_model3, gpt_a_token3,
                     gpt_b_nick_name, 
                     gpt_b_model1, gpt_b_token1, 
                     gpt_b_model2, gpt_b_token2, 
                     gpt_b_model3, gpt_b_token3,
                     gpt_b_length,
                     azure_endpoint, azure_version, azure_key_id,
                     azure_deploy_model, azure_deploy_token,
                    ):

        # 認証
        self.bot_auth               = None

        # openai チャットボット
        if (api == 'chatgpt'):

            if (openai_api_type == 'openai'):
                self.openai_api_type    = openai_api_type
                openai.organization     = openai_organization
                openai.api_key          = openai_key_id

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

                try:
                    res = openai.Model.list()
                    for dt in res['data']:
                        if (dt['id'] == gpt_a_model1):
                            self.bot_auth        = True
                            self.gpt_a_enable    = True
                            self.gpt_a_nick_name = gpt_a_nick_name
                        if (dt['id'] == gpt_b_model1):
                            self.bot_auth        = True
                            self.gpt_b_enable    = True
                            self.gpt_b_nick_name = gpt_b_nick_name

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
                openai.api_type         = 'azure'
                openai.api_base         = azure_endpoint 
                openai.api_version      = azure_version
                openai.api_key          = azure_key_id

                self.bot_auth           = True
                self.azure_endpoint     = azure_endpoint
                self.azure_version      = azure_version
                self.azure_key_id       = azure_key_id
                self.azure_deploy_model = azure_deploy_model
                self.azure_deploy_token = int(azure_deploy_token)
                self.gpt_a_enable       = True
                self.gpt_a_nick_name    = 'GPT'
                self.gpt_a_model1       = azure_deploy_model
                self.gpt_a_token1       = int(azure_deploy_token)
                self.gpt_a_model2       = azure_deploy_model
                self.gpt_a_token2       = int(azure_deploy_token)
                self.gpt_a_model3       = azure_deploy_model
                self.gpt_a_token3       = int(azure_deploy_token)

                return True

        return False

    def addHistory(self, history=[], sysText=None, reqText=None, inpText=u'こんにちは', ):
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

    def zipHistory(self, history=[]):
        res_history = history

        for h in reversed(range(len(res_history))):
            tm = res_history[h]['time']
            if ((time.time() - tm) > 1800): #30分で忘れてもらう
                if (h != 0):
                    del res_history[h]
                else:
                    if (res_history[0]['role'] != 'system'):
                        del res_history[0]

        return res_history

    def history2msg(self, history=[]):
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
        len_tokens = 0

        #try:
        if True:
            #encoding_model = tiktoken.encoding_for_model(model)
            encoding_model = tiktoken.get_encoding("cl100k_base")
            for message in messages:
                len_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
                for key, value in message.items():
                    len_tokens += len(encoding_model.encode(value))
                    if key == "name":  # if there's a name, the role is omitted
                        len_tokens += -1  # role is always required and always 1 token
            #len_tokens += 1  # every reply is primed with <im_start>assistant

            # functionのトークン暫定
            for dic in functions:
                try:
                    len_tokens += 19
                    value = dic['description']
                    len_tokens += len(encoding_model.encode(value))
                    for x in dic['parameters']['properties']:
                        len_tokens += 5
                        value = dic['parameters']['properties'][x]['description']
                        len_tokens += len(encoding_model.encode(value))
                    required = dic['parameters'].get('required')
                    if (required != None):
                        len_tokens += len(required) + 2
                except:
                    len_tokens += 200

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
                nick_name = ''
                model     = ''
        #except Exception as e:
        #    print(e)

        return nick_name, model, len_tokens

    def chatBot(self, history=[], sysText=None, reqText=None, inpText=u'こんにちは',
                temperature=0.5, maxStep=10, model_select='auto',
                inpLang='ja-JP', outLang='ja-JP', ):

        res_text = ''
        res_path = ''
        res_name = None
        res_api  = None
        res_history = history

        if (self.bot_auth is None):
            print('ChatGPT: Not Authenticate Error !')
            return res_text, res_path, res_name, res_api, res_history

        # functions
        functions    = []
        sandbox_name = False
        for module_dic in self.ext_module:
            if (module_dic['onoff'] == 'on'):
                functions.append(module_dic['function'])
                if (module_dic['func_name'] == 'execute_sandbox_function'):
                    sandbox_name = 'execute_sandbox_function'

        # model 選択
        if (self.gpt_a_nick_name != ''):
            if (inpText.strip()[:len(self.gpt_a_nick_name)+1].lower() == (self.gpt_a_nick_name.lower() + ',')):
                model_select = 'a'
                inpText = inpText.strip()[len(self.gpt_a_nick_name)+1:]
        if (self.gpt_b_nick_name != ''):
            if (inpText.strip()[:len(self.gpt_b_nick_name)+1].lower() == (self.gpt_b_nick_name.lower() + ',')):
                model_select = 'b'
                inpText = inpText.strip()[len(self.gpt_b_nick_name)+1:]
        if (model_select == 'auto'):
            if (self.gpt_b_enable == True):
                if (len(inpText) >= self.gpt_b_length):
                    model_select = 'b'

        # history 追加
        res_history = self.addHistory(history=res_history, sysText=sysText, reqText=reqText, inpText=inpText, )

        # history 圧縮
        res_history = self.zipHistory(history=res_history, )

        # メッセージ作成
        msg = self.history2msg(history=res_history, )

        try:

            n = 0
            res_text = ''
            function_name = ''
            while (function_name != 'exit') and (n < int(maxStep)):

                # トークン数チェック　→　モデル確定
                nick_name, model, len_tokens = self.checkTokens(messages=msg, functions=functions, model_select=model_select, )
                if (model==''):
                    print('ChatGPT: Token length Error ! (' + str(len_tokens) + ')')
                    print('ChatGPT: History reset !')

                    # history リセット
                    res_history = []
                    res_history = self.addHistory(history=res_history, sysText=sysText, reqText=reqText, inpText=inpText, )
                    #res_history = self.zipHistory(history=res_history, )

                    # メッセージ作成
                    msg = self.history2msg(history=res_history, )

                    # トークン数再計算
                    nick_name, model, len_tokens = self.checkTokens(messages=msg, functions=functions, model_select=model_select, )
                    if (model==''):
                        print('ChatGPT: Token length Error ! (' + str(len_tokens) + ')')
                        return res_text, res_path, res_name, res_api, res_history

                # GPT
                n += 1
                print(model + ', pass=' + str(n) + ', tokens=' + str(len_tokens))
                #print(self.openai_api_type)
                try:
                    # OPENAI
                    if (self.openai_api_type != 'azure'):
                        if (functions == [] ):
                            completions = openai.ChatCompletion.create(
                                model           = model,
                                messages        = msg,
                                temperature     = float(temperature),)
                        else:
                            completions = openai.ChatCompletion.create(
                                model           = model,
                                messages        = msg,
                                temperature     = float(temperature),
                                functions       = functions,
                                function_call   = 'auto',)
                    # Azure
                    else:
                        # '2023-05-15'はファンクション未対応！
                        if (functions == []) or (self.azure_version == '2023-05-15'):
                            completions = openai.ChatCompletion.create(
                                engine          = model,
                                messages        = msg,
                                temperature     = float(temperature),)
                        else:
                            completions = openai.ChatCompletion.create(
                                engine          = model,
                                messages        = msg,
                                temperature     = float(temperature),
                                functions       = functions,
                                function_call   = 'auto',)
                except Exception as e:
                    print( json.dumps(msg, indent=4, ensure_ascii=False, ) )
                    print(e)
                    print('error!!!!!!!!!')

                # GPT 結果確認
                try:
                    #print(completions.usage['prompt_tokens'])
                    #print(completions.usage['completion_tokens'])
                    #print(completions.usage['total_tokens'])
                    # 結果
                    res_role    = completions.choices[0].message['role']
                    res_content = completions.choices[0].message['content']

                    # function 指示？
                    function_name = None
                    json_kwargs   = None
                    try:
                        function_name = completions.choices[0].message['function_call']['name']
                        json_kwargs   = completions.choices[0].message['function_call']['arguments']
                        try:
                            wk_dic      = json.loads(json_kwargs)
                            wk_text     = json.dumps(wk_dic, ensure_ascii=False, )
                            json_kwargs = wk_text
                        except:
                            pass
                    except:
                        pass
                except Exception as e:
                    print(e)

                # GPT 会話終了
                if (res_role == 'assistant') and (res_content != None):
                    res_text = res_content.rstrip()
                    function_name   = 'exit'
                    print('  ' + nick_name.lower() + ' complite.')
                    #print(res_text)

                    # 自動で(B)モデル(GPT4)実行
                    try:
                        if (self.openai_api_type != 'azure'):
                            if (model_select == 'auto'):
                                if (self.gpt_b_enable == True):
                                    if (len(res_text) >= self.gpt_b_length):
                                        if (nick_name != self.gpt_b_nick_name):
                                            nick_name2, model2, len_tokens = self.checkTokens(messages=msg, functions=[], model_select='b', )
                                            if (model2 != ''):
                                                # OPENAI
                                                completions2 = openai.ChatCompletion.create(
                                                    model           = model2,
                                                    messages        = msg,
                                                    temperature     = float(temperature),)
                                                res_role2    = completions2.choices[0].message['role']
                                                res_content2 = completions2.choices[0].message['content']
                                                if (res_role2 == 'assistant') and (res_content2 != None):
                                                    nick_name   = nick_name2
                                                    model       = model2
                                                    res_role    = res_role2
                                                    res_content = res_content2
                                                    res_text    = res_content.rstrip()
                                                    print('  ' + nick_name.lower() + ' complite.')
                                                    #print(res_text)
                    except:
                        pass

                    # History 追加格納
                    self.seq += 1
                    dic = {'seq': self.seq, 'time': time.time(), 'role': res_role, 'name': '', 'content': res_text }
                    res_history.append(dic)

                # function 指示
                elif (res_role == 'assistant') and (function_name != None):
                    #print('  function_call "' + function_name + '"')

                    hit = False
                    if (hit == False):
                        if (function_name == 'python'):
                            if (sandbox_name != False):
                                print('  function_call (' + function_name + ' -> ' + sandbox_name + ')')
                                function_name = sandbox_name
                                dic = {}
                                dic['python_script'] = json_kwargs
                                json_kwargs = json.dumps(dic, ensure_ascii=False, )

                            else:
                                print('  function_call (' + function_name + ')')

                                # メッセージ追加格納
                                self.seq += 1
                                dic = {'seq': self.seq, 'time': time.time(), 'role': 'function_call', 'name': function_name, 'content': json_kwargs }
                                res_history.append(dic)

                                # function 実行不能
                                res_json = json_kwargs
                                res_text = '\n\n' + json_kwargs

                                break

                    if (hit == False):
                        for module_dic in self.ext_module:
                            if (function_name == module_dic['func_name']):
                                hit = True
                                print('  function_call "' + module_dic['script'] + '" (' + function_name + ')')

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
                        print('GPT function_call Error ! (' + function_name + ')')
                        print(res_role, res_content, function_name, json_kwargs, )
                        print(completions)
                        break

                # 予期せぬ回答
                else:
                    print('GPT Error !')
                    print(res_role, res_content)
                    print(completions)
                    break

        except Exception as e:
            print(e)

        ## 質問加筆部分無視！
        #gobi = res_text.find('\n\n')
        #if (gobi >=0):
        #    res_text = res_text[gobi+2:]

        # 文書成形
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

        res_name = nick_name
        res_api  = model

        return res_text, res_path, res_name, res_api, res_history




if __name__ == '__main__':

        #openaiAPI = speech_bot_openai.ChatBotAPI()
        openaiAPI = ChatBotAPI()

        res = openaiAPI.authenticate('chatgpt',
                         openai_key.getkey('chatgpt','openai_api_type'),
                         openai_key.getkey('chatgpt','openai_organization'),
                         openai_key.getkey('chatgpt','openai_key_id'),
                         openai_key.getkey('chatgpt','gpt_a_nick_name'),
                         openai_key.getkey('chatgpt','gpt_a_model1'),
                         openai_key.getkey('chatgpt','gpt_a_token1'),
                         openai_key.getkey('chatgpt','gpt_a_model2'),
                         openai_key.getkey('chatgpt','gpt_a_token2'),
                         openai_key.getkey('chatgpt','gpt_a_model3'),
                         openai_key.getkey('chatgpt','gpt_a_token3'),
                         openai_key.getkey('chatgpt','gpt_b_nick_name'),
                         openai_key.getkey('chatgpt','gpt_b_model1'),
                         openai_key.getkey('chatgpt','gpt_b_token1'),
                         openai_key.getkey('chatgpt','gpt_b_model2'),
                         openai_key.getkey('chatgpt','gpt_b_token2'),
                         openai_key.getkey('chatgpt','gpt_b_model3'),
                         openai_key.getkey('chatgpt','gpt_b_token3'),
                         openai_key.getkey('chatgpt','gpt_b_length'),
                         openai_key.getkey('chatgpt','azure_endpoint'),
                         openai_key.getkey('chatgpt','azure_version'),
                         openai_key.getkey('chatgpt','azure_key_id'),
                         openai_key.getkey('chatgpt','azure_deploy_model'),
                         openai_key.getkey('chatgpt','azure_deploy_token'),
                        )
        print('authenticate:', res, )
        if (res == True):

            if True:
                #res, msg = openaiAPI.loadExtensions(extensions_path='_extensions/openai_gpt/', secure_level='medium', )
                res, msg = openaiAPI.loadExtensions(extensions_path='_extensions/openai_gpt/', secure_level='low', )
                if (res != True) or (msg != ''):
                    print(msg)

            if True:
                sysText = None
                reqText = ''
                inpText = '現在地の天気を教えてください。'
                print()
                print('[Request]')
                print(reqText, inpText )
                print()
                res_text, res_path, res_name, res_api, openaiAPI.history = openaiAPI.chatBot(
                            history=openaiAPI.history,
                            sysText=sysText, reqText=reqText, inpText=inpText, model_select='auto',
                            inpLang='ja', outLang='ja', )
                print()
                print('[' + res_name + '] (' + res_api + ')' )
                print(res_text)

            if True:
                sysText = None
                reqText = '以下の質問には、コテコテの大阪弁で回答してください。'
                inpText = '日本で有名な観光地を教えてください。'
                print()
                print('[Request]')
                print(reqText, inpText )
                print()
                res_text, res_path, res_name, res_api, openaiAPI.history = openaiAPI.chatBot(
                            history=openaiAPI.history,
                            sysText=sysText, reqText=reqText, inpText=inpText, model_select='auto',
                            inpLang='ja', outLang='ja', )
                print()
                print('[' + res_name + '] (' + res_api + ')' )
                print(res_text)

            if False:
                sysText = None
                reqText = ''
                inpText = 'かわいい猫の画像生成してください。'
                print()
                print('[Request]')
                print(reqText, inpText )
                print()
                res_text, res_path, res_name, res_api, openaiAPI.history = openaiAPI.chatBot(
                            history=openaiAPI.history,
                            sysText=sysText, reqText=reqText, inpText=inpText, model_select='auto',
                            inpLang='ja', outLang='ja', )
                print()
                print('[' + res_name + '] (' + res_api + ')' )
                print(res_path)
                print(res_text)

            res, msg = openaiAPI.unloadExtensions()
            if (res != True) or (msg != ''):
                print(msg)

            print()
            print('[History]')
            for h in range(len(openaiAPI.history)):
                print(openaiAPI.history[h])


