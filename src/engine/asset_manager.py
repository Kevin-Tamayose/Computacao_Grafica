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


class AssetManager:
    """Gerenciador centralizado de recursos (texturas, shaders, modelos)."""

    def __init__(self, assets_root: str = None):
        """
        Args:
            assets_root: Caminho raiz para assets. Se None, usa src/
        """
        if assets_root is None:
            assets_root = os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..', 'images')
            )
        self.assets_root = assets_root
        self.textures: Dict[str, int] = {}  # Nome -> ID OpenGL
        self.shaders: Dict[str, int] = {}   # Nome -> Program ID OpenGL

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

        texture_path = os.path.join(self.assets_root, filename)

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
