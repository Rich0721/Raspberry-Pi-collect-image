#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 17:28:42 2021

@author: pi
"""
from selectData import collectImageOrVideo
import os
from glob import glob

if __name__ == "__main__":
    
    jsons = glob(os.path.join("./", "*.json"))
    
    if len(jsons) >= 1:
        collect = collectImageOrVideo(json_file=jsons[0], os="pi")
        collect.collect()
        