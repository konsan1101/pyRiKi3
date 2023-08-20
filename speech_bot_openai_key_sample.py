#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2023 Mitsuo KONDOU.
# This software is released under the not MIT License.
# Permission from the right holder is required for use.
# https://github.com/konsan1101
# Thank you for keeping the rules.
# ------------------------------------------------

def getkey(api, key):

    # openai チャットボット
    if (api == 'chatgpt'):
        print('speech_bot_openai_key.py')
        print('set your key!')
        if (key == 'openai_api_type'):
            return 'use api type'
        if (key == 'openai_organization'):
            return 'your openai organization'
        if (key == 'openai_key_id'):
            return 'your openai key'

        if (key == 'gpt_a_nick_name'):
            return 'your gpt (a) nick name'
        if (key == 'gpt_a_model1'):
            return 'your gpt (a) model1'
        if (key == 'gpt_a_token1'):
            return 'your gpt (a) token1'
        if (key == 'gpt_a_model2'):
            return 'your gpt (a) model2'
        if (key == 'gpt_a_token2'):
            return 'your gpt (a) token2'
        if (key == 'gpt_a_model3'):
            return 'your gpt (a) model3'
        if (key == 'gpt_a_token3'):
            return 'your gpt (a) token3'

        if (key == 'gpt_b_nick_name'):
            return 'your gpt (b) nick name'
        if (key == 'gpt_b_model1'):
            return 'your gpt (b) model1'
        if (key == 'gpt_b_token1'):
            return 'your gpt (b) token1'
        if (key == 'gpt_b_model2'):
            return 'your gpt (b) model2'
        if (key == 'gpt_b_token2'):
            return 'your gpt (b) token2'
        if (key == 'gpt_b_model3'):
            return 'your gpt (b) model3'
        if (key == 'gpt_b_token3'):
            return 'your gpt (b) token3'
        
        if (key == 'gpt_b_length'):
            return 'your gpt (b) length'

        if (key == 'azure_endpoint'):
            return 'your azure endpoint'
        if (key == 'azure_version'):
            return 'your azure version'
        if (key == 'azure_key_id'):
            return 'your azure key'
        if (key == 'azure_deploy_model'):
            return 'your azure deploy model'
        if (key == 'azure_deploy_token'):
            return 'your azure deploy token'

    return False


