from typing import Optional

class OBJModel:
    """Estrutura simples para armazenar dados de um modelo .obj carregado."""
    def __init__(self):
        self.vertices = []
        self.texcoords = []
        self.normals = []
        self.faces = []  # Lista de faces, onde cada face é uma lista de tuplas (v_idx, vt_idx, vn_idx)
        self.display_list_id: Optional[int] = None