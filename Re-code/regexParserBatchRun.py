"""
This file runs the Regular Expression Parser on 16 datasets.
"""

#%%
import pandas as pd
import re
import os
from regexParserRules import get_RE_Dict

#%%
def fit_RE(log_df, reg_dict, out_path):

    # Parse Templates Using RE Rules
    pred_temp_list = []
    for i in range(log_df.shape[0]):
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

    # Give Event IDs
    temp_id_dict = dict()
    cur_id = 1
    for temp in sorted(list(set(pred_temp_list))):
        temp_id_dict[temp] = 'E' + str(cur_id)
        cur_id += 1

    pred_id_list = []
    for temp in pred_temp_list:
        pred_id_list.append(temp_id_dict[temp])
    
    pred_df = log_df.loc[:,:]
    pred_df["EventTemplate"] = pred_temp_list
    pred_df["EventId"] = pred_id_list

    pred_df.to_csv(out_path+setName+"_2k.log_structured.csv")

    return pred_df

#%%
if __name__ == "__main__":

    # All 16 datsets
    nameList = ["BGL", "Android", "Thunderbird", "OpenStack", "Spark", "Apache", "Hadoop", "HDFS", "HealthApp", "HPC", "Linux", "Mac", "OpenSSH", "Proxifier", "Windows", "Zookeeper"]

    for setName in nameList:

        # Select Target
        rev = ""        # before revision
        rev = "_rev"    # after revision

        print("="*10, setName+rev, "parsed", "="*10)

        # Specify Output Path
        out_path = "results/RE_batch"+rev+"/"+setName+"/"
        if not os.path.exists(out_path):
            os.makedirs(out_path)

        # Read Data
        log_df = pd.read_csv("logs_revising/"+setName+"/"+setName+"_2k.log_structured"+rev+".csv") # Log Content

        # Get RE Rules
        reg_dict = get_RE_Dict()

        # Parse
        pred_df = fit_RE(log_df, reg_dict, out_path)
    
    print("End of parsing process.")

# %%

