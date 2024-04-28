import logging

import  open3d as o3d
import numpy as np
import os
import tqdm
from tqdm import tqdm


def calculateOverlap(source, target,sourceTrans,targetTrans,threshold=0.03):
    source=source.voxel_down_sample(0.01)
    target=target.voxel_down_sample(0.01)
    source=source.transform(sourceTrans)
    target=target.transform(targetTrans)

    target_kdtree=o3d.geometry.KDTreeFlann(target)
    match_count=0
    for i,points in enumerate(source.points):
        [count,_,_]=target_kdtree.search_radius_vector_3d(points,threshold)
        if(count!=0):
            match_count+=1

    return match_count/len(source.points)

def getPair(numberOfPC):
    pairs=[]
    for i in range(numberOfPC):
        for j in range(i+1,numberOfPC):
            pairs.append([i,j])
    return pairs

if __name__=="__main__":
    scenes=['7-scenes-redkitchen',
            'sun3d-home_at-home_at_scan1_2013_jan_1',
            'sun3d-home_md-home_md_scan9_2012_sep_30',
            'sun3d-hotel_uc-scan3',
            'sun3d-hotel_umd-maryland_hotel1',
            'sun3d-hotel_umd-maryland_hotel3'
            'sun3d-mit_76_studyroom-76-1studyroom2',
            'sun3d-mit_lab_hj-lab_hj_tea_nov_2_2012_scan1_erika',
            ]
    logging.basicConfig(level=logging.INFO)

    threedmatchPath ="../data/3Dmatch"
    threedmatch_trans_path = "../data/3Dmatch/Predator"
    for scene in scenes:
        scenePath = os.path.join(threedmatchPath,scene)
        scene_trans_path = os.path.join(threedmatch_trans_path,scene)
        logging.info("*"*10)
        logging.info(f"Processing scene {scene}, path: {scenePath}")
        allPointCloudsFiles=os.listdir(scenePath)
        pairs=getPair(len(allPointCloudsFiles))
        allPointCLoudTransFiles=os.listdir(scenePath)
        pair_overlaps=[]


        for pair in tqdm(pairs,desc="Processing", unit="pair"):
            pair_overlap=[]
            pair_overlap.append(pair[0])
            pair_overlap.append(pair[1])
            targetPLYPath = os.path.join(scenePath,"cloud_bin_%d.ply"%pair[0])
            sourcePLYPath = os.path.join(scenePath,"cloud_bin_%d.ply"%pair[1])
            targetTransPath = os.path.join(scene_trans_path,"cloud_bin_%d.info.txt"%pair[0])
            sourceTransPath = os.path.join(scene_trans_path, "cloud_bin_%d.info.txt"% pair[1])
            targetPLY=o3d.io.read_point_cloud(targetPLYPath)
            sourcePLY=o3d.io.read_point_cloud(sourcePLYPath)
            targetTrans=np.loadtxt(targetTransPath, skiprows=1, usecols=None)
            sourceTrans=np.loadtxt(sourceTransPath, skiprows=1, usecols=None)
            overlap=calculateOverlap(sourcePLY,targetPLY,sourceTrans,targetTrans)
            pair_overlap.append(overlap)
            pair_overlaps.append(pair_overlap)
        eval_path=scenePath+"-evaluation"
        if not os.path.exists(eval_path):
            os.makedirs(eval_path)
        with open(os.path.join(eval_path,"overlap.txt"),"w") as f:
            for pair_overlap in pair_overlaps:
                f.write(str(pair_overlap)+"\n")

