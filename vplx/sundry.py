# coding:utf-8
import socket
import signal
import time
import os
import getpass
import traceback
import re
import prettytable
import sys
from random import shuffle
import subprocess
from functools import wraps
import colorama as ca
import inspect
import consts
import pprint



def create_transaction_id():
    return int(time.time())

def create_oprt_id():
    time_stamp = str(create_transaction_id())
    str_list = list(time_stamp)
    shuffle(str_list)
    return ''.join(str_list)

def get_username():
    return getpass.getuser()



def re_findall(re_string, tgt_string):
    logger = consts.glo_log()
    re_ = re.compile(re_string)
    oprt_id = create_oprt_id()
    logger.write_to_log('OPRT', 'REGULAR', 'findall', oprt_id, {'re': re_, 'string': tgt_string})
    re_result = re_.findall(tgt_string)
    logger.write_to_log('DATA', 'REGULAR', 'findall', oprt_id, re_result)
    return re_result


def re_search(re_string, tgt_stirng):
    logger = consts.glo_log()
    re_ = re.compile(re_string)
    oprt_id = create_oprt_id()
    logger.write_to_log('OPRT','REGULAR','search',oprt_id, {'re':re_,'string':tgt_stirng})
    re_result = re_.search(tgt_stirng).group()
    logger.write_to_log('DATA', 'REGULAR', 'search', oprt_id, re_result)
    return re_result



def change_pointer(new_id):
    consts.set_glo_log_id(new_id)

def deco_cmd(type):
    """
    装饰器
    用于装饰系统命令的执行
    :param type: 系统命令的类型(sys,linstor,crm)
    :return:返回命令执行结果
    """

    def decorate(func):
        @wraps(func)
        def wrapper(cmd):
            RPL = consts.glo_rpl()
            oprt_id = create_oprt_id()
            func_name = traceback.extract_stack()[-2][2]  # 装饰器获取被调用函数的函数名
            if RPL == 'no':
                logger = consts.glo_log()
                logger.write_to_log('DATA', 'STR', func_name, '', oprt_id)
                logger.write_to_log('OPRT', 'CMD', type, oprt_id, cmd)
                result_cmd = func(cmd)
                logger.write_to_log('DATA', 'CMD', type, oprt_id, result_cmd)
                return result_cmd
            else:
                logdb = consts.glo_db()
                id_result = logdb.get_id(consts.glo_tsc_id(), func_name)
                if id_result['oprt_id']:
                    cmd_result = logdb.get_oprt_result(id_result['oprt_id'])
                else:
                    cmd_result = {'time':'','result':''}
                if type != 'sys' and cmd_result['result']:
                    result = eval(cmd_result['result'])
                    result_output = result['rst']
                else:
                    result = cmd_result['result']
                    result_output = cmd_result['result']
                print(f"RE:{id_result['time']:<20} 执行系统命令：\n{cmd}")
                print(f"RE:{cmd_result['time']:<20} 系统命令结果：\n{result_output}")
                if id_result['db_id']:
                    change_pointer(id_result['db_id'])
            return result
        return wrapper
    return decorate


@deco_cmd('sys')
def execute_cmd(cmd, timeout=60):
    p = subprocess.Popen(cmd, stderr=subprocess.STDOUT,
                         stdout=subprocess.PIPE, shell=True)
    t_beginning = time.time()
    seconds_passed = 0
    while True:
        if p.poll() is not None:
            break
        seconds_passed = time.time() - t_beginning
        if timeout and seconds_passed > timeout:
            p.terminate()
            raise TimeoutError(cmd, timeout)
        time.sleep(0.1)
    output = p.stdout.read().decode()
    return output




def prt(str, warning_level=0):
    if isinstance(warning_level, int):
        warning_str = '*' * warning_level
    else:
        warning_str = ''
    rpl = consts.glo_rpl()

    if rpl == 'no':
        print(str)
    else:
        db = consts.glo_db()
        time,cmd_output = db.get_cmd_output(consts.glo_tsc_id())
        if not time:
            time = ''
        print(f'RE:{time:<20} 日志记录输出：{warning_str:<4}\n{cmd_output}')
        print(f'RE:{"":<20} 此次执行输出：{warning_str:<4}\n{str}')


def prt_log(str, warning_level):
    """
    print, write to log and exit.
    :param logger: Logger object for logging
    :param print_str: Strings to be printed and recorded
    """
    logger = consts.glo_log()
    RPL = consts.glo_rpl()
    if RPL == 'yes':
        # pass
        prt(str, warning_level)
    elif RPL == 'no':
        prt(str, warning_level)

    if warning_level == 0:
        logger.write_to_log('INFO', 'INFO', 'finish', 'output', str)
    elif warning_level == 1:
        logger.write_to_log('INFO', 'WARNING', 'fail', 'output', str)
    elif warning_level == 2:
        logger.write_to_log('INFO', 'ERROR', 'exit', 'output', str)
        if RPL == 'no':
            sys.exit()
        else:
            raise consts.ReplayExit



def deco_json_operation(str):
    """
    Decorator providing confirmation of deletion function.
    :param func: Function to delete linstor resource
    """
    def decorate(func):
        @wraps(func)
        def wrapper(self, *args):
            RPL = consts.glo_rpl()
            if RPL == 'no':
                logger = consts.glo_log()
                oprt_id = create_oprt_id()
                logger.write_to_log('DATA', 'STR', func.__name__, '', oprt_id)
                logger.write_to_log('OPRT', 'JSON', func.__name__, oprt_id, args)
                result = func(self,*args)
                logger.write_to_log('DATA', 'JSON', func.__name__, oprt_id,result)
            else:
                logdb = consts.glo_db()
                id_result = logdb.get_id(consts.glo_tsc_id(), func.__name__)
                json_result = logdb.get_oprt_result(id_result['oprt_id'])
                if json_result['result']:
                    result = eval(json_result['result'])
                else:
                    result = ''
                print(f"RE:{id_result['time']} {str}:")
                pprint.pprint(result)
                print()
                if id_result['db_id']:
                    change_pointer(id_result['db_id'])
            return result
        return wrapper
    return decorate


def deco_db_insert(func):
    @wraps(func)
    def wrapper(self, sql, data, tablename):
        RPL = consts.glo_rpl()
        if RPL == 'no':
            logger = consts.glo_log()
            oprt_id = create_oprt_id()
            logger.write_to_log('DATA', 'STR', func.__name__, '', oprt_id)
            logger.write_to_log('OPRT', 'SQL', func.__name__, oprt_id, sql)
            func(self,sql, data, tablename)
            logger.write_to_log('DATA', 'SQL', func.__name__, oprt_id, data)
        else:
            logdb = consts.glo_db()
            id_result = logdb.get_id(consts.glo_tsc_id(), func.__name__)
            func(self, sql, data, tablename)
            print(f"RE:{id_result['time']} 插入数据表: {tablename}")
            print(f"RE:{id_result['time']} 插入数据:")
            for i in data:
                print(i)
            print()# 格式上的换行
            if id_result['db_id']:
                change_pointer(id_result['db_id'])
    return wrapper


def handle_exception():
    rpl = consts.glo_rpl()
    if rpl == 'yes':
        print('日志中无法取得相关数据，程序无法继续正常执行')
        raise consts.ReplayExit
    else:
        print('命令结果无法获取，请检查')
        sys.exit()#在这里结束会屏蔽掉程序抛出的异常，再考虑要不要直接在这里中断程序


