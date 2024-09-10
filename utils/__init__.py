
from numpy import sqrt
import numpy as np

def get_video_keyframe_path(path):
    idx = path.index('/')
    return path[:idx]

def get_frame_number_in_video(path):
    l = path.index('/')
    r = path.index('.')
    return int(path[l+1:r])-1

def metric_2_ids(idx1, scores1, idx2, scores2, k):
    assert len(idx1) == len(scores1)
    assert len(idx2) == len(scores2)
    # assert len(idx1) == len(idx2)
    res = []
    for id1, score1 in zip(idx1, scores1):
        for id2, score2 in zip(idx2, scores2):
            if (id1>id2): continue
            score = score1**2*score2*1/sqrt(id2-id1+25)
            res.append((score, id1, id2, score1, score2))
    res.sort(reverse=True)
    assert k <= len(res)
    res = res[:k]
    ids = [x[1] for x in res]
    scores = [x[0] for x in res]
    for i in range(10):
        print(ids[i], res[i][2], res[i][3], res[i][4],' = ', scores[i])
    return ids, scores