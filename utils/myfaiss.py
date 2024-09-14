import faiss
# import clip
import numpy as np
from utils.embeddingserver import text_feature, image_feature_file, image_feature_url

class FaissDB:
    def __init__(self, bin_file_path_ALIGN,
                bin_file_path_CLIP, bin_file_path_DINOv2,
                clip_backbone="ViT-B/32", device = "cuda"):
        self.index = {}
        # self.index['ALIGN'] = faiss.read_index(bin_file_path_ALIGN)
        self.index['CLIP'] = faiss.read_index(bin_file_path_CLIP)
        resource = [faiss.StandardGpuResources()]
        # self.index['ALIGN'] = faiss.index_cpu_to_gpu_multiple_py(resource, self.index['ALIGN'])
        self.index['CLIP'] = faiss.index_cpu_to_gpu_multiple_py(resource, self.index['CLIP'])
        self.index_dinov2 = faiss.read_index(bin_file_path_DINOv2)
        # self.model, _ = clip.load(clip_backbone, device=device)
        # self.device = device
        print('Checking embedding server...')
        self.text_search('Deutsches Rotes Kreuz Kriseninterventionsteam, HTV9, 06:44:01', 5, 'CLIP')

    def text_search(self, text: str, k: int, model_name: str):
        # text_tokens = clip.tokenize([text]).to(self.device)
        # text_features = self.model.encode_text(text_tokens).cpu().detach().numpy().astype(np.float32)
        text_features = text_feature(text, model_name)
        norm = np.linalg.norm(text_features)
        if (norm!=0):
            text_features /= norm
        
        assert np.isnan(text_features).any()==False
        scores, idx_image = self.index[model_name].search(text_features, k=k)
        idx_image = idx_image.squeeze()
        scores = scores.squeeze()
        assert np.isnan(scores).any()==False

        return idx_image, scores
    
    def image_search(self, image, k: int, model_name: str):
        # text_tokens = clip.tokenize([text]).to(self.device)
        # text_features = self.model.encode_text(text_tokens).cpu().detach().numpy().astype(np.float32)
        image_features = image_feature_file(image)
        norm = np.linalg.norm(image_features, model_name)
        if (norm!=0):
            image_features /= norm
        
        scores, idx_image = self.index[model_name].search(image_features, k=k)
        idx_image = idx_image.squeeze()
        scores = scores.squeeze()

        return idx_image, scores
    
    def url_search(self, image, k: int, model_name: str):
        # text_tokens = clip.tokenize([text]).to(self.device)
        # text_features = self.model.encode_text(text_tokens).cpu().detach().numpy().astype(np.float32)
        image_features = image_feature_url(image, model_name)
        norm = np.linalg.norm(image_features)
        if (norm!=0):
            image_features /= norm
        
        scores, idx_image = self.index[model_name].search(image_features, k=k)
        idx_image = idx_image.squeeze()
        scores = scores.squeeze()

        return idx_image, scores

    def vec_search(self, vec, k: int, model_name: str):
        # text_tokens = clip.tokenize([text]).to(self.device)
        # text_features = self.model.encode_text(text_tokens).cpu().detach().numpy().astype(np.float32)
        norm = np.linalg.norm(vec)
        if (norm!=0):
            vec /= norm
        

        scores, idx_image = self.index[model_name].search(vec, k=k)
        idx_image = idx_image.squeeze()
        scores = scores.squeeze()

        return idx_image, scores
    
    def idx_search(self, idx, k: int, model_name: str):
        # text_tokens = clip.tokenize([text]).to(self.device)
        # text_features = self.model.encode_text(text_tokens).cpu().detach().numpy().astype(np.float32)
        vec = np.expand_dims(self.index[model_name].reconstruct(idx), axis=0)
        norm = np.linalg.norm(vec)
        if (norm!=0):
            vec /= norm
        
        scores, idx_image = self.index[model_name].search(vec, k=k)
        idx_image = idx_image.squeeze()
        scores = scores.squeeze()

        return idx_image, scores

    def idx_dinov2_search(self, idx, k:int):
        vec = np.expand_dims(self.index_dinov2.reconstruct(idx), axis=0)
        # norm = np.linalg.norm(vec)
        # if (norm!=0):
        #     vec /= norm
        
        scores, idx_image = self.index_dinov2.search(vec, k=k)
        idx_image = idx_image.squeeze()
        scores = scores.squeeze()

        return idx_image, scores