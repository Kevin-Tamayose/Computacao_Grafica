"""
Asset Manager - Gerenciador Centralizado de Recursos

Responsabilidades:
1. Carregar texturas uma única vez e cache-lás
2. Carregar modelos 3D (quando necessário)
3. Carregar e compilar shaders
4. Fornecer referências aos recursos para toda a aplicação

Princípio: Nenhum recurso deve ser carregado múltiplas vezes na memória.
"""

import os
from typing import Dict, Optional, Tuple
import OpenGL.GL as GL
from PIL import Image

from engine.object_model.objmodel import OBJModel

class AssetManager:
    """Gerenciador centralizado de recursos (texturas, shaders, modelos)."""

    def __init__(self):
        """
        Args:
            assets_root: Caminho raiz para assets. Se None, usa src/
        """
        assets_root_img = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images'))
        assets_root_obj = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'objects'))
        self.assets_root_images = assets_root_img
        self.assets_root_models = assets_root_obj

        self.textures: Dict[str, int] = {}  # Nome -> ID OpenGL
        self.shaders: Dict[str, int] = {}   # Nome -> Program ID OpenGL
        self.models: Dict[str, OBJModel] = {}  # Nome -> OBJModel

    def load_texture(self, filename: str, force_reload: bool = False) -> Optional[int]:
        """
        Carrega uma textura. Se já estiver carregada, retorna o ID em cache.
        
        Args:
            filename: Nome do arquivo de textura (ex: 'chats.jpg')
            force_reload: Se True, força recarregar mesmo se em cache
            
        Returns:
            ID OpenGL da textura ou None se falhar
        """
        # Retornar do cache se já estiver carregado
        if filename in self.textures and not force_reload:
            return self.textures[filename]

        texture_path = os.path.join(self.assets_root_images, filename)

        if not os.path.exists(texture_path):
            print(f'❌ Textura não encontrada: {texture_path}')
            return None

        try:
            img = Image.open(texture_path).convert('RGB')
        except Exception as e:
            print(f'❌ Erro ao carregar textura {filename}: {e}')
            return None

        # Gerar e configurar textura OpenGL
        texture_id = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
        
        # Configurações de wrapping e filtragem
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        
        # Upload dos dados de imagem
        GL.glTexImage2D(
            GL.GL_TEXTURE_2D,
            0,
            GL.GL_RGB,
            img.width,
            img.height,
            0,
            GL.GL_RGB,
            GL.GL_UNSIGNED_BYTE,
            img.tobytes(),
        )

        # Armazenar no cache
        self.textures[filename] = texture_id
        print(f'✓ Textura carregada: {filename} (ID: {texture_id})')
        return texture_id

    def load_obj(self, filename: str, force_reload: bool = False) -> Optional[OBJModel]:
        """
        Carrega um arquivo .obj de forma simplificada e armazena no cache.
        """
        if filename in self.models and not force_reload:
            return self.models[filename]

        model_path = os.path.join(self.assets_root_models, filename)

        if not os.path.exists(model_path):
            print(f'❌ Modelo não encontrado: {model_path}')
            return None

        model = OBJModel()
        
        # Listas temporárias para leitura direta do arquivo (índices baseados em 1 no OBJ)
        temp_vertices = []
        temp_texcoords = []
        temp_normals = []

        try:
            with open(model_path, 'r') as f:
                for line in f:
                    if line.startswith('#') or not line.strip():
                        continue
                    
                    parts = line.split()
                    if not parts:
                        continue

                    line_type = parts[0]

                    if line_type == 'v':
                        temp_vertices.append([float(x) for x in parts[1:4]])
                    elif line_type == 'vt':
                        temp_texcoords.append([float(x) for x in parts[1:3]])
                    elif line_type == 'vn':
                        temp_normals.append([float(x) for x in parts[1:4]])
                    elif line_type == 'f':
                        face = []
                        for vertex_str in parts[1:]:
                            # O formato pode ser v, v/vt, v//vn ou v/vt/vn
                            vals = vertex_str.split('/')
                            
                            # Índices no OBJ começam em 1. Valores negativos contam de trás para frente.
                            v_idx = int(vals[0]) - 1 if vals[0] else -1
                            vt_idx = int(vals[1]) - 1 if len(vals) > 1 and vals[1] else -1
                            vn_idx = int(vals[2]) - 1 if len(vals) > 2 and vals[2] else -1
                            
                            face.append((v_idx, vt_idx, vn_idx))
                        model.faces.append(face)

            # Montar a estrutura final indexada baseada nas faces lidas
            model.vertices = temp_vertices
            model.texcoords = temp_texcoords
            model.normals = temp_normals

            # --- COMPILAÇÃO DA DISPLAY LIST (O SEGREDO DA PERFORMANCE) ---
            # Geramos um ID de lista na GPU
            model.display_list_id = GL.glGenLists(1)
            
            # Iniciamos a gravação dos comandos na GPU
            GL.glNewList(model.display_list_id, GL.GL_COMPILE)
            
            # Executamos o loop pesado de renderização apenas ESTA VEZ
            for face in model.faces:
                if len(face) == 3:
                    GL.glBegin(GL.GL_TRIANGLES)
                elif len(face) == 4:
                    GL.glBegin(GL.GL_QUADS)
                else:
                    GL.glBegin(GL.GL_POLYGON)

                for v_idx, vt_idx, vn_idx in face:
                    if vn_idx >= 0 and vn_idx < len(model.normals):
                        GL.glNormal3fv(model.normals[vn_idx])
                    
                    if vt_idx >= 0 and vt_idx < len(model.texcoords):
                        u, v = model.texcoords[vt_idx]
                        GL.glTexCoord2f(u, 1.0 - v)
                    
                    if v_idx >= 0 and v_idx < len(model.vertices):
                        GL.glVertex3fv(model.vertices[v_idx])
                GL.glEnd()
                
            # Fechamos a gravação. Agora o modelo reside 100% na GPU.
            GL.glEndList()

            self.models[filename] = model
            print(f'✓ Modelo .obj carregado e compilado na GPU: {filename}')
            return model

        except Exception as e:
            print(f'❌ Erro ao ler arquivo .obj {filename}: {e}')
            return None
    
    def get_texture(self, filename: str) -> Optional[int]:
        """
        Retorna o ID de uma textura já carregada. Se não estiver carregada,
        carrega-a automaticamente.
        """
        if filename not in self.textures:
            return self.load_texture(filename)
        return self.textures[filename]

    def unload_texture(self, filename: str) -> None:
        """Remove uma textura da memória."""
        if filename in self.textures:
            texture_id = self.textures[filename]
            GL.glDeleteTextures([texture_id])
            del self.textures[filename]
            print(f'✓ Textura descarregada: {filename}')

    def unload_all_textures(self) -> None:
        """Remove todas as texturas da memória."""
        for filename in list(self.textures.keys()):
            self.unload_texture(filename)
        print('✓ Todas as texturas foram descarregadas')

    def get_stats(self) -> Dict[str, int]:
        """Retorna estatísticas de recursos carregados."""
        return {
            'textures_loaded': len(self.textures),
            'shaders_loaded': len(self.shaders),
        }
