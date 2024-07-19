import faiss
import clip
import numpy as np

class FaissDB:
    def __init__(self, bin_file_path, clip_backbone="ViT-B/32", device = "cuda"):
        self.index = faiss.read_index(bin_file_path)
        resource = [faiss.StandardGpuResources()]
        self.index = faiss.index_cpu_to_gpu_multiple_py(resource, self.index)
        self.model, _ = clip.load(clip_backbone, device=device)
        self.device = device

    def text_search(self, text: str, k: int):
        text_tokens = clip.tokenize([text]).to(self.device)
        text_features = self.model.encode_text(text_tokens).cpu().detach().numpy().astype(np.float32)

        scores, idx_image = self.index.search(text_features, k=k)
        idx_image = idx_image.squeeze()

        return idx_image

db = FaissDB("index.bin")
db.text_search('forest', 5)