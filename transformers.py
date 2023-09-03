import json
import re
import os

import time
from datetime import datetime
import dateparser

from dotenv import dotenv_values
import pandas

from langchain.prompts import PromptTemplate
from langchain.output_parsers import DatetimeOutputParser
from langchain.chains import LLMChain
from langchain.llms import OpenAI

config = dotenv_values(".env")
os.environ["OPENAI_API_KEY"] = config['GPT_KEY']
models = ['gpt-3.5-turbo', 'text-davinci-002', 'babbage-002', 'text-curie-001']

def format_timestamp(ts):
    output = ts
    try:
        output = dateparser.parse(ts).strftime('%Y-%m-%d %H:%M:%S')
    except:
        output_parser = DatetimeOutputParser()
        output_parser.format = '%Y-%m-%d %H:%M:%S'
        template = """Answer the users question:

        {question}

        {format_instructions}"""
        prompt = PromptTemplate.from_template(
            template,
            partial_variables={"format_instructions": output_parser.get_format_instructions()},
        )
        chain = LLMChain(prompt=prompt, llm=OpenAI(model_name=models[1], temperature=1))
        output = chain.run(f'format {ts}').strip('\n')
    return output

def format_location(loc):
    return loc

def format_shape(shape):
    return shape

def format_duration(dur):
    """
    Here's some ugly code but the point is to get as much of the easy stuff parsed before using API
    """
    output = 0
    skip = False
    low_dur = str(dur).lower()
    sub_dur = re.sub(r'[\'+~,]', '', low_dur)
    split_dur = re.findall('(\d+[.\d+]*[\s]*[-to]*[\s]*[.\d+]*|[a-z]+)', sub_dur)
    cleaned_list = []

    if dur and ':' in dur:
        multiplyer = 1
        hhmmss = re.findall('\d+:\d+[:\d+]?', dur)
        split_ssmmhh = hhmmss[0].split(':')
        split_ssmmhh.reverse()
        for idx, i in enumerate(split_ssmmhh):
            output = output + int(i) * multiplyer
            multiplyer = multiplyer * 60
        return output

    for idx, i in enumerate(split_dur):
        if i in ['a', 'an']:
            cleaned_list.append(1)
        elif i in ['few']:
            # fun with data
            cleaned_list.append(5)
        elif re.match(r'\d+[.\d+]*[\s]*[-to]*[\s]*\d+[.\d+]*', i):
            split_element = re.findall(r'\d+', i)
            try:
                cleaned_list.append((float(split_element[0]) + float(split_element[1]))/2)
            except:
                cleaned_list.append(split_element[0].strip())
        elif i not in ['approx', 'aprox', 'about', 'over', 'under', 'less', 'more', 'than', 'about']:
            cleaned_list.append(i.strip())

    try:
        for jdx, j in enumerate(cleaned_list):
            if jdx == len(cleaned_list) - 1:
                break
            try:
                temp_num = float(cleaned_list[jdx])
                prefix = ''.join([*cleaned_list[jdx + 1]][0:3])
                if prefix in ['sec', 's']:
                    output = output + temp_num * 1
                elif prefix in ['min', 'mns', 'mn', 'm']:
                    output = output + temp_num * 60
                elif prefix in ['hou', 'hrs', 'hr', 'h']:
                    output = output + temp_num * 3660
                elif prefix in ['day']:
                    output = output + temp_num * 86400
                else:
                    skip = True
            except:
                continue
        
    except:
        skip = True

    output = int(output)

    if skip or output == 0:
        output = f'Do Some AI Stuff with {dur}'       

    return output