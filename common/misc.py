from typing import DefaultDict
from functools import wraps
import time

def iter_fetch_data(batch_size,ids,func,nil_result):
    """iter fetch data use func by batch_size
    Args:
        batch_size:
        ids:
        func: method iterly
        nil_reulst: nil result
    Return:
        result: same type with nil_result
    """
    for x in range(0,len(ids),batch_size):
        sub_ids = ids[x:x+batch_size]
        sub_result = func(sub_ids)
        if isinstance(sub_result,list) and isinstance(nil_result,list):
            list.extend(nil_result,sub_result)
        elif isinstance(sub_result,dict) and isinstance(nil_result,dict):
            dict.update(nil_result,sub_result)
        else:
            raise TypeError("unsupoort action")
    return nil_result

def inverse_map(data:dict):
    result = DefaultDict(list)
    for k,v in data.items():
        for v_ in v:
            result[v_].append(k)
    return result

def func_exec_time(func):
    """
    Decorator function reports the execution time
    """
    @wraps(func)  # 保留元信息
    def wrapper(*args,**kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"function [{func.__name__}] execution consume {(end-start):.8f} s.")
        return result
    return wrapper