
def get_video_keyframe_path(path):
    idx = path.index('/')
    return path[:idx]

def get_frame_number_in_video(path):
    l = path.index('/')
    r = path.index('.')
    return int(path[l+1:r])-1