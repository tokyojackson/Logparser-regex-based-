"""
This file runs & tests the Regular Expression Parser on 16 datasets.
It mainly serves for debugging & improvement purpose.
It prints out an overview of the parsing accuracy.
"""

#%%
import pandas as pd
import re
import os
from regexParserRules import get_RE_Dict

#%%
def buildDict(log_df, temp_df):
    # Dictionary: {EventTemplate: EventId}
    id_dict = dict()
    for i in range(temp_df.shape[0]):
        id_dict[temp_df["EventTemplate"][i]] = temp_df["EventId"][i]

    # Dictionary: {Event: Count}
    count_dict = dict()
    for i in range(temp_df.shape[0]):
        newID = temp_df["EventId"][i]
        newCount = log_df[log_df['EventId']==newID].shape[0]
        count_dict[newID] = newCount
    
    return id_dict, count_dict

#%%
def fit_RE(log_df, reg_dict, id_dict, count_dict, out_path):

    # Parse Templates Using RE Rules
    pred_temp_list = []
    pred_id_list = []
    correct = 0
    corr_temp_set = set()
    corr_event_id = set()
    wrong_event_id = set()
    wrong_temp_dict = dict()
    for i in range(log_df.shape[0]):
        cur_id = log_df["EventId"][i]
        true_temp = log_df["EventTemplate"][i]
        cont = log_df["Content"][i]
        res = cont
        for reg in reg_dict.keys():
            while re.search(reg, cont):
                idf_str = re.search(reg,cont)[0]
                sub_str = re.search(reg_dict[reg][0], idf_str)[0]
                new_str = reg_dict[reg][1]
                rep_str = idf_str.replace(sub_str, new_str, 1)
                cont = cont.replace(idf_str, rep_str, 1)
                res = cont
        pred_temp_list.append(res)
        if res in id_dict.keys():
            pred_id_list.append(id_dict[res])
        else:
            pred_id_list.append('None')
        if res == true_temp:
            correct += 1
            if cur_id not in wrong_event_id:
                corr_temp_set.add(res)
                corr_event_id.add(cur_id)
        else:
            wrong_event_id.add(cur_id)
            wrong_temp_dict[cur_id] = (res, true_temp)
            corr_event_id.discard(cur_id)

    wrong_dict = count_dict
    for event in corr_event_id:
        del wrong_dict[event]
    wrong_dict = {k: v for k, v in sorted(wrong_dict.items(), key=lambda item: item[1], reverse=True)}

    print("Correct Logs:", correct, "/", log_df.shape[0])
    print("Correct Events:", len(corr_event_id), "/", temp_df.shape[0])

    pred_df = log_df.loc[:,:]
    pred_df["EventTemplate"] = pred_temp_list
    pred_df["EventId"] = pred_id_list

    pred_df.to_csv(out_path+setName+"_2k.log_structured.csv")

    return pred_df, wrong_dict, correct, wrong_temp_dict

#%%
if __name__ == "__main__":

    # Test all 16 datasets
    nameList = ["BGL", "Android", "Thunderbird", "OpenStack", "Spark", "Apache", "Hadoop", "HDFS", "HealthApp", "HPC", "Linux", "Mac", "OpenSSH", "Proxifier", "Windows", "Zookeeper"]
    
    # Examine or not
    testing = False
    print_detail = False
    # ======== Set testing to True if examining a specific dataset =============
    # testing = True 
    # print_detail = True  # Uncomment this line if examining detail parsing mistakes
    testName = 'Mac'       # Specify test datatset here
    # =========================================================================

    for setName in nameList:

        if testing: setName = testName

        print("="*10, setName, "="*10)

        # ------------ Select Target -----------
        rev = ""        # before revision
        rev = "_rev"    # after revision
        # --------------------------------------

        # Specify Output Path
        out_path = "results/RE_testing"+rev+"/"+setName+"/"
        if not os.path.exists(out_path):
            os.makedirs(out_path)

        # Read Data
        log_df = pd.read_csv("logs_revising/"+setName+"/"+setName+"_2k.log_structured"+rev+".csv") # Content + Ground Truth
        temp_df = pd.read_csv("logs_revising/"+setName+"/"+setName+"_2k.log_templates"+rev+".csv") # Template-ID Dict (for converting templates to IDs)
        
        # Generate Dictionaries
        id_dict, count_dict = buildDict(log_df, temp_df)

        # Get RE Rules
        reg_dict = get_RE_Dict()

        # Parse
        pred_df, wrong_dict, correct, wrong_temp_dict = fit_RE(log_df, reg_dict, id_dict, count_dict, out_path)

        # Output
        wrong_file = open(out_path+setName+"_wrongEvents.txt",'w',encoding="utf-8")

        for check in wrong_dict.keys():
            print("===============", check, "=======================", file=wrong_file)
            print("Parsed Result:", wrong_temp_dict[check][0], sep='\n', file=wrong_file)
            print("Ground Truth:", wrong_temp_dict[check][1], sep='\n', file=wrong_file)

        wrong_file.close()

        if print_detail:
            for key, value in wrong_dict.items():
                print(key+":", value)
            for check in wrong_dict.keys():
                print("===============", check, "=======================")
                print("Parsed Result:", wrong_temp_dict[check][0], sep='\n')
                print("Ground Truth:", wrong_temp_dict[check][1], sep='\n')

        print(setName+rev, "tested.")

        if testing: break

# %%

