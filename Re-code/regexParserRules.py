"""
This file defines all regular expressions used to identify log parameters.
The regular expressions are arranged in the order of priority. The earlier-appeared expressions are used in identification before the later ones.
"""

#%%
def get_RE_Dict():

    reg_dict = dict()

    # ========================== Prefix/Suffix Expressions ======================================

    # Prefix: non-number+dot, colon, space, parentheses(3 kinds), equal, comma, start, |, <, quotation(single+double), semi-colon
    prefix = r'([^0-9]\.|:|\s|\(|\)|\[|]|\{|}|=|,|^|\||<|\"|\')'

    # Suffix: space, parentheses(3 kinds), comma, end, colon, dot+space/end, |, >, equal, quotation(single+double), semi-colon
    suffix = r'(\s|\(|\)|\[|]|\{|}|,|$|:|\. |\.$|\||>|=|\"|\'|;)'

    # ================= Long Expressions ======================================================

    # 1. URL (http/hdfs + ://)
    # Spark E12: Input split: hdfs://10.10.34.11:9000/pjhe/logs/2kSOSP.log:21876+7292
    param = r'[A-Za-z\.]+://[A-Za-z0-9\./\+#@:_\-]+(?<![:\.])'
    reg_dict[prefix+param+suffix] = (param, '<*>')

    # 2. Path start with (.)/
    param = r'([A-Za-z]:|\.){0,1}(/|\\)[0-9A-Za-z\-_\.:/\*\+\$#@!\\\?=%&]+(?<![:\.])'
    reg_dict[prefix+param+suffix] = (param, '<*>')

    # 3. After Keywords
    # user
    param = r'user( |  )[A-Za-z0-9]+(?<!request)(?! methods)'
    reg_dict[param+suffix] = (param, 'user <*>')
    # driver
    param = r'driver [A-Za-z0-9]+'
    reg_dict[param+suffix] = (param, 'driver <*>')
    # core.xxxx
    param = r'core\.[0-9]+'
    reg_dict[prefix+param+suffix] = (r'[0-9]+', '<*>')
    # from ... to ...
    param = r'from [A-Za-z0-9_]+ to [A-Za-z0-9_]+'
    reg_dict[prefix+param+suffix] = (param, 'from <*> to <*>')
    # Failed password for ... from ... (针对 OpenSSH E9)
    param = r'Failed password for [A-Za-z]+ from'
    reg_dict[prefix+param+suffix] = (param, 'Failed password for <*> from')
    # by client ...
    param = r'by client [A-Za-z]+'
    reg_dict[prefix+param+suffix] = (param, 'by client <*>')
    # CurrentState:NUM (针对 Windows E29)
    param = r'CurrentState:[0-9]+'
    reg_dict[prefix+param+suffix] = (param, 'CurrentState:<*>')
    # : Yes/No/onSleep/Normal Sleep , (针对 Mac E134)
    param = r': (Normal Sleep|onSleep|onWake|Standby|Yes|No),'
    reg_dict[param] = (param, ': <*>,')

    # 4. After =
    param = r'(([A-Za-z0-9\.:_\-#@/\?]+)|(\[\]))(?<![:\.])(?![\{=\(])'
    reg_dict[r'(=|= )'+param+suffix] = (param, '<*>')

    # 5. Special Cases of IP
    # For HDFS E3: 10.251.30.85:50010:Got exception while serving blk_-2918118818249673980 to /10.251.90.64:
    # ip:number:Got
    param = r'[0-9]+(\.[0-9]+)+:[0-9]+:Got'
    reg_dict[prefix+param+suffix] = (param, '<*>:Got')
    # For OpenStack E25: 10.11.21.143,10.11.10.1 "GET /openstack/2013-10-17/vendor_data.json HTTP/1.1" status: 200 len: 124 time: 0.2292829
    # ip connected by ","
    param = r'[0-9]+(\.[0-9]+)+(,[0-9]+(\.[0-9]+)+)+'
    reg_dict[prefix+param+suffix] = (param, '<*>')

    # 6. Continuous Expressions with .
    long_expr = r'[A-Za-z0-9\._\-/@#\$\\~]+'                            
    param = r'(?<!BLOCK\* )' + long_expr + r'(?<!\.)(\.)(?!\.)' + long_expr + r'((\(\)))?(?<!HTTP/1\.1)(?!(=| =))' # (有GT的网址后有引号, 但由于冲突已删去\"?)
    reg_dict[prefix+param+suffix] = (param, '<*>')

    # 7. IP
    param = r'[0-9]+\.[0-9\.:]*[0-9]'
    reg_dict[prefix+param+suffix] = (param, '<*>')

    # 8. Num/Letter/- + :
    param = r'[0-9A-Za-z\-]*[0-9\-A-Fa-f][0-9A-Za-z\-]*(:[0-9A-Za-z\-]*[0-9\-A-Fa-f][0-9A-Za-z\-])+(?!:)'
    reg_dict[prefix+param+suffix] = (param, '<*>')

    # 9. Groups of Coordinates
    param = r'(\[[0-9,]+]){2,}'
    reg_dict[prefix+param+suffix] = (param, '<*>')

    # ================== Short Expressions =============================

    # 10. Inside <>
    # Thunderbird E15：msgid=<200511091911.jA9JBXVI027337@dadmin1>
    param = r'[A-Za-z0-9#@\.]+'
    reg_dict[r'\<'+param+r'\>'] = (param, '<*>')

    # 11. Inside ""
    param = r'"[A-za-z0-9\.\-@#\*]+"(?!:)'
    reg_dict[prefix+param+suffix] = (param, '"<*>"')
    param = r"'[A-za-z0-9\.\-@#\*]+'(?!:)"
    reg_dict[prefix+param+suffix] = (param, "'<*>'")

    # 12. Inside #
    param = r'#[0-9]+#'
    reg_dict[param] = (param, '<*>')

    # 13. Inside []
    param = r'(?<!^)\[[A-Za-z]+\]'
    reg_dict[param] = (r'\[[A-Za-z]+\]', '[<*>]')

    # 14. < or > + number
    param = r'(<|>)[0-9]+'
    reg_dict[param+suffix] = (param, '<*>')

    # 15. __NUM-[
    # Mac E50: __<*>-[NetworkAnalyticsEngine observeValueForKeyPath:ofObject:change:context:]_block_invoke unexpected switch value <*>
    param = r'^__[0-9]+\-\['
    reg_dict[param] = (param, '__<*>-[')

    # 16. Month+[double space]+Date (For Linux E119)
    param = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)  [0-9]+'
    reg_dict[prefix+param+suffix] = (param, '<*> <*>')

    # 17. Number(mandatory) + (choose from) letter,_,-,#,@,+,/
    # 2022.08.29 restrict parameters from jk2_init, (Apache E1)
    # 2022.08.30 restrict parameters from NAT64, IPV6, (Mac E142,276)
    param = r'[0-9A-Za-z_\-#@\+/]*[0-9]+[0-9A-Za-z_\-#@\+/]*(?<!(jk2_init|.{3}NAT64|.{3} (IPv6|IPV6)))(?!(=| =))'
    reg_dict[prefix+param+suffix] = (param, '<*>')

    # 18. Positive/Negative number （短匹配，放于末位）
    param = r'(\-|\+){0,1}[0-9]+(\.[0-9]+){0,1}'
    reg_dict[prefix+param+suffix] = (param, '<*>')

    # 19. Null, True, False, ffffffff, HTTPS, yarn,curi, sshd, fztu
    param = r'(null|True|False|true|false|ffffffff|HTTPS|yarn,curi|fztu|QQ)'
    reg_dict[prefix+param+suffix] = (param, '<*>')

    # 20. Days
    param = r'(Mon|Tue|Wed|Thu|Fri|Sat|Sun)'
    reg_dict[prefix+param+suffix] = (param, '<*>')

    # 21. Months
    param = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
    reg_dict[prefix+param+suffix] = (param, '<*>')

    # ================ Lastly, Deal With remaining improper <*>  ==========================

    # 22. Merge <*>:<*>, <*>:[end]
    param = r'(<\*>)(:(<\*>|[A-Za-z0-9]+))+(?<!<\*>:Got)'
    reg_dict[prefix+param+suffix] = (param, '<*>')
    param = r'(<\*>):((<\*>|[A-Za-z0-9]+):)*$'
    reg_dict[prefix+param+suffix] = (param, '<*>')

    # 23. Merge <*> KB/MB
    param = r'<\*> (B|KB|MB)'
    reg_dict[prefix+param+suffix] = (param, '<*>')

    return reg_dict
