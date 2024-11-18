import json
import re
import os
import csv

import time
from datetime import datetime
import dateparser

from dotenv import dotenv_values

# from langchain.prompts import PromptTemplate
# from langchain.output_parsers import DatetimeOutputParser
# from langchain.chains import LLMChain
# from langchain.llms import OpenAI

config = dotenv_values(".env")
os.environ["OPENAI_API_KEY"] = config['GPT_KEY']
models = ['gpt-3.5-turbo', 'text-davinci-002', 'babbage-002', 'text-curie-001']




us_geos_reorg = {}

with open('reference/citylatlon.txt', mode='r') as f:
    us_geos = csv.DictReader(f, delimiter='\t')
    for item in us_geos:
        if item['state'] not in us_geos_reorg:
            us_geos_reorg[item['state']] = {}
        if item['city'] not in us_geos_reorg[item['state']]:
            us_geos_reorg[item['state']][item['city']] = {}
        us_geos_reorg[item['state']][item['city']]['lat'] = item['latitude']
        us_geos_reorg[item['state']][item['city']]['lon'] = item['longitude']
    f.close()


def format_timestamp(ts):
    output = None
    try:
        # Use dateparser to parse the timestamp
        dt = dateparser.parse(ts)
        if dt:
            # Convert datetime object to epoch time (seconds since 1970-01-01)
            output = int(time.mktime(dt.timetuple()))
    except Exception as e:
        print(f"Error parsing timestamp: {ts} -> {e}")
    return output

# def format_timestamp(ts):
#     output = ts
#     try:
#         output = dateparser.parse(ts).strftime('%Y-%m-%d %H:%M:%S')
#     except:
#         # output_parser = DatetimeOutputParser()
#         # output_parser.format = '%Y-%m-%d %H:%M:%S'
#         # template = """Answer the users question:

#         # {question}

#         # {format_instructions}"""
#         # prompt = PromptTemplate.from_template(
#         #     template,
#         #     partial_variables={"format_instructions": output_parser.get_format_instructions()},
#         # )
#         # chain = LLMChain(prompt=prompt, llm=OpenAI(model_name=models[1], temperature=0.1))
#         # output = chain.run(f'format {ts}').strip('\n')
#         output = None
#     return output

def format_location(loc):
    # 29709 entries in esri doc
    # 29708 entries in reform dict
    output = None
    split_loc = loc.split(',')
    city = split_loc[0].strip()
    state = split_loc[1].strip()
    city_split = re.findall(r'[\w\s.]+', city)
    if len(city_split) > 0:
        city = city_split[0].strip()
    if state.upper() in us_geos_reorg and city.upper() in us_geos_reorg[state.upper()]:
        output = [us_geos_reorg[state.upper()][city.upper()]['lat'], us_geos_reorg[state.upper()][city.upper()]['lon']]
    else:
        output = None
    return output

def format_shape(shape):
    lower_shape = str(shape).lower()
    return lower_shape

# def format_duration(dur):
#     """
#     Here's some ugly code but the point is to get as much of the easy stuff parsed before using API
#     Duration is uniformed into seconds
#     """
#     output = 0
#     skip = False
#     low_dur = str(dur).lower()
#     sub_dur = re.sub(r'[\'+~,]', '', low_dur)
#     split_dur = re.findall('(\d+[.\d+]*[\s]*[-to]*[\s]*[.\d+]*|[a-z]+)', sub_dur)
#     cleaned_list = []

#     if dur and ':' in dur:
#         multiplyer = 1
#         hhmmss = re.findall('\d+:\d+[:\d+]?', dur)
#         split_ssmmhh = hhmmss[0].split(':')
#         split_ssmmhh.reverse()
#         for idx, i in enumerate(split_ssmmhh):
#             output = output + int(i) * multiplyer
#             multiplyer = multiplyer * 60
#         return output

#     for idx, i in enumerate(split_dur):
#         if i in ['a', 'an']:
#             cleaned_list.append(1)
#         elif i in ['few']:
#             # fun with data
#             cleaned_list.append(5)
#         elif re.match(r'\d+[.\d+]*[\s]*[-to]*[\s]*\d+[.\d+]*', i):
#             split_element = re.findall(r'\d+', i)
#             try:
#                 cleaned_list.append((float(split_element[0]) + float(split_element[1]))/2)
#             except:
#                 cleaned_list.append(split_element[0].strip())
#         elif i not in ['approx', 'aprox', 'about', 'over', 'under', 'less', 'more', 'than', 'about']:
#             cleaned_list.append(i.strip())

#     try:
#         for jdx, j in enumerate(cleaned_list):
#             if jdx == len(cleaned_list) - 1:
#                 break
#             try:
#                 temp_num = float(cleaned_list[jdx])
#                 prefix = ''.join([*cleaned_list[jdx + 1]][0:3])
#                 if prefix in ['sec', 's']:
#                     output = output + temp_num * 1
#                 elif prefix in ['min', 'mns', 'mn', 'm']:
#                     output = output + temp_num * 60
#                 elif prefix in ['hou', 'hrs', 'hr', 'h']:
#                     output = output + temp_num * 3660
#                 elif prefix in ['day']:
#                     output = output + temp_num * 86400
#                 else:
#                     skip = True
#             except:
#                 continue
        
#     except:
#         skip = True

#     output = int(output)

#     if skip or output == 0:
#         # format_instructions = """
#         # - duration = {duration}
#         # format the given duration into an integer representing the best representation of total number of seconds.
#         # If the amount of duration requires estimation, do your best job.
#         # If there is not a safe answer, respond with a value of null.
#         # """
#         # prompt = PromptTemplate(input_variables=['duration'], template=format_instructions)
#         # llm = LLMChain(prompt=prompt, llm=OpenAI(model_name=models[0], temperature=0))
#         # output = llm(prompt.format(duration=dur))
#         # print('              ')
#         # print('              ')
#         # print(dur, output)
#         # print('              ')
#         # print('              ')
#         output = f'Do Some AI Stuff with {dur}'       

#     return output



### use openAI format duration code

def format_duration(dur):
    """
    Parse the duration into seconds as accurately as possible. 
    Handle common duration formats such as '1-2 min', 'few seconds', '3:45' (HH:MM), etc.
    """
    if not dur:
        return None

    output = 0
    skip = False
    low_dur = str(dur).lower().strip()  # Ensure the duration is a string and strip extra spaces
    sub_dur = re.sub(r'[\'+~,]', '', low_dur)
    split_dur = re.findall(r'(\d+[.\d+]*[\s]*[-to]*[\s]*[.\d+]*|[a-z]+)', sub_dur)
    cleaned_list = []

    # Check if the format is in HH:MM:SS
    if ':' in dur:
        multiplyer = 1
        hhmmss = re.findall(r'\d+:\d+[:\d+]?', dur)
        if hhmmss:
            split_ssmmhh = hhmmss[0].split(':')
            split_ssmmhh.reverse()
            for idx, i in enumerate(split_ssmmhh):
                if i.isdigit():  # Check if valid digits are present
                    output = output + int(i) * multiplyer
                    multiplyer *= 60
            return output

    # Parse the non-HH:MM:SS formats
    for idx, i in enumerate(split_dur):
        if i in ['a', 'an']:
            cleaned_list.append(1)
        elif i in ['few']:
            cleaned_list.append(5)
        elif re.match(r'\d+[.\d+]*[\s]*[-to]*[\s]*\d+[.\d+]*', i):
            split_element = re.findall(r'\d+', i)
            try:
                cleaned_list.append((float(split_element[0]) + float(split_element[1])) / 2)
            except:
                cleaned_list.append(split_element[0].strip())
        elif i not in ['approx', 'aprox', 'about', 'over', 'under', 'less', 'more', 'than']:
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
                    output = output + temp_num * 3600
                elif prefix in ['day']:
                    output = output + temp_num * 86400
                else:
                    skip = True
            except (ValueError, IndexError):
                continue
    except Exception as e:
        skip = True

    output = int(output)

    if skip or output == 0:
        output = None  # Return None if unable to parse the duration properly

    return output


def clean_text(text):
    """
    This function will clean the text to prepare it for RAG input.
    """
    # Remove NUFORC notes and other non-textual elements in parentheses
    text = re.sub(r'\(\(.*?\)\)', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Convert to lowercase for consistency
    text = text.lower()
    
    # Optionally remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    
    # Remove any leading/trailing spaces
    text = text.strip()
    
    return text