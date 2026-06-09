# Projeto: Síntese de Imagem - Lanterna em 3D

Uma aplicação 3D interativa desenvolvida com **Python, OpenGL e PyGame**, implementando um sistema de iluminação realista com uma lanterna em primeira pessoa.

## 🎮 Recursos

- ✅ Renderização 3D com OpenGL
- ✅ Iluminação dinâmica com spotlight (lanterna)
- ✅ Câmera em primeira pessoa com suporte a mouse
- ✅ Sistema de texturização
- ✅ Menu interativo (pausa/controles)
- ✅ Arquitetura modular escalável

## 📁 Estrutura do Projeto

```
Computacao_Grafica/
├── README.md                      # Este arquivo
├── ARCHITECTURE.md                # Documentação detalhada de arquitetura
├── REORGANIZATION_SUMMARY.md      # Resumo das mudanças recentes
│
├── src/
│   ├── main.py                   # Ponto de entrada (Game Loop)
│   │
│   ├── core/                     # Sistema Central
│   │   ├── camera.py            # Câmera em primeira pessoa
│   │   └── input_manager.py     # Gerenciador centralizado de inputs
│   │
│   ├── engine/                  # Motor Gráfico (Abstração OpenGL)
│   │   ├── asset_manager.py     # Gerenciador de recursos (texturas)
│   │   └── renderer.py          # Abstração de renderização
│   │
│   ├── game/                    # Lógica do Jogo
│   │   └── state.py             # Estado e regras do jogo
│   │
│   ├── graphics/                # Renderização de Conteúdo
│   │   ├── geometry.py          # Desenho de geometria 3D
│   │   ├── lighting.py          # Sistema de iluminação
│   │   └── shaders/             # [Futuro] Arquivos de shader GLSL
│   │
│   └── images/                  # Assets (texturas)
│       ├── chats.jpg            # Textura do piso
│       └── wall.jpg             # Textura das paredes
│
└── .venv/                       # Ambiente virtual Python
```

## 🚀 Como Executar

### Pré-requisitos

- Python 3.8+
- Drivers OpenGL compatíveis com GLSL

### Instalação

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente (Windows)
.venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt
```

### Executar a Aplicação

```bash
cd src
python main.py
```

## 🎮 Controles

| Tecla | Ação |
|-------|------|
| **WASD** | Mover câmera |
| **Mouse** | Olhar ao redor |
| **Setas ↑↓←→** | Orientar lanterna |
| **L** | Liga/desliga lanterna |
| **ESC** | Abrir/fechar menu |
| **C** | Ver controles |
| **Q** | Sair do jogo |

## 🏗️ Arquitetura

A aplicação segue o padrão **Motor Gráfico Modular**, separando:

```
┌─────────────────────────────────────────┐
│         Game Loop (main.py)             │
│  INPUT → UPDATE → RENDER → DISPLAY      │
└────────┬────────┬────────┬──────────────┘
         │        │        │
    ┌────▼─┐  ┌───▼──┐  ┌──▼──────┐
    │INPUT │  │GAME  │  │RENDERER │
    │MGR   │  │STATE │  │         │
    └──────┘  └──────┘  └──────┬──┘
                               │
                   ┌───────────┼──────────┐
                   │           │          │
                ┌──▼──┐  ┌─────▼─┐  ┌────▼──┐
                │ASSET│  │CAMERA │  │GEOMETRY
                │MGR  │  │       │  │
                └─────┘  └───────┘  └────────┘
```

### Componentes Principais

| Componente | Responsabilidade |
|-----------|-----------------|
| **Input Manager** | Centraliza processamento de eventos |
| **Game Manager** | Mantém estado do jogo |
| **Asset Manager** | Carrega/cache de recursos |
| **Renderer** | Abstração de OpenGL |
| **Camera** | Transformações de visão |
| **Geometry** | Desenho de objetos 3D |

## 📊 Características de Design

### ✅ Implementadas

1. **Separação de Responsabilidades**: Cada módulo tem uma função específica
2. **Asset Manager**: Carrega recursos uma única vez (sem duplicatas)
3. **Renderer Abstrato**: Encapsula toda lógica OpenGL
4. **Input Centralizado**: Gerenciador único de eventos
5. **Game State Pattern**: Estado imutável com regras bem definidas

### ⏳ Futuras Melhorias

1. **Shaders em Arquivos**: Migrar para `.vert` e `.frag` files
2. **Entity Component System**: Arquitetura escalável para entidades
3. **Physics Engine**: Colisão e gravidade
4. **Animation System**: Animar objetos 3D
5. **Sound Manager**: Sistema de áudio

## 📚 Documentação Detalhada

Veja os arquivos de documentação para mais informações:

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detalhes técnicos da arquitetura
- **[REORGANIZATION_SUMMARY.md](REORGANIZATION_SUMMARY.md)** - Resumo das mudanças recentes

## 🔧 Desenvolvimento

### Adicionar uma Nova Textura

```python
# Em src/main.py
my_texture = asset_manager.load_texture('my_texture.jpg')

# Em src/graphics/geometry.py
renderer.draw_plane_y(..., texture_id=my_texture)
```

### Adicionar um Novo Controle

```python
# Em src/core/input_manager.py
# 1. Adicionar ao InputState
@dataclass
class InputState:
    # ... estados existentes ...
    space_pressed: bool = False

# 2. Processar em InputManager.update()
elif event.key == pygame.K_SPACE:
    self.state.space_pressed = True

# 3. Usar em main.py
if input_manager.state.space_pressed:
    game_manager.jump()
```

## 🎨 Screenshots

> [Adicionar screenshots do projeto aqui]

## 📦 Dependências

```
pygame>=2.0.0
PyOpenGL>=3.1.5
Pillow>=8.0.0
numpy>=1.20.0
```

Ver [requirements.txt](requirements.txt) para versões específicas.

## 📝 Licença

Este projeto é parte do curso de **Computação Gráfica** do LANEM.

## 👨‍💻 Autor

Desenvolvido como projeto acadêmico de síntese de imagem e renderização 3D.

## 🤝 Contribuindo

Sugestões e melhorias são bem-vindas! Abra uma issue ou pull request.

---

**Última atualização**: 2026-06-08
