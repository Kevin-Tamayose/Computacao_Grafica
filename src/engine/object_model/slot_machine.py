import math
import OpenGL.GL as GL

from engine import renderer

class SlotMachine:
    def __init__(self, corpo_model, alavanca_model, rolo_model, textura_id, pos_x, pos_y, pos_z, escala):
        # Referências gráficas
        self.corpo_model = corpo_model
        self.alavanca_model = alavanca_model
        self.rolos_models = [rolo_model] * 5
        self.textura_id = textura_id
        
        # Posição no mundo
        self.x = pos_x
        self.y = pos_y
        self.z = pos_z
        self.escala = escala

        # Constantes de Estado
        self.ESTADO_PARADA = 0
        self.ESTADO_DESCENDO = 1
        self.ESTADO_SUBINDO = 2
        
        # Variáveis de Animação
        self.estado_atual = self.ESTADO_PARADA
        self.angulo_alavanca = 0.0
        self.velocidade_giro = 120.0
        self.pronta_para_interagir = True

        # Variáveis para os rolos
        self.angulos_rolos = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.velocidades_rolos = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.alvos_rolos = [0.0, 0.0, 0.0, 0.0, 0.0]     # Ângulo final onde devem parar
        self.rolo_parado = [True, True, True, True, True] # Controla quem terminou de girar
        if not corpo_model or not alavanca_model:
            raise Exception("Aviso: Falha ao carregar as partes da slot machine")
    
    def ativar_animacoes(self, player_x, player_y, player_z):
        """Gatilha o início da animação. Retorna True se aceitou o comando."""
        # Só permite ativar se a alavanca estiver totalmente parada

        distancia = math.sqrt((player_x - self.x)**2 + 
                              (player_y - self.y)**2 + 
                              (player_z - self.z)**2)
        
        print(f"Estado: {self.estado_atual} | Distância: {distancia:.2f} | Player: ({player_x:.1f}, {player_y:.1f}, {player_z:.1f}) | Maquina: ({self.x:.1f}, {self.y:.1f}, {self.z:.1f})")

        if distancia < 15.0 and self.estado_atual == self.ESTADO_PARADA:
            self.estado_atual = self.ESTADO_DESCENDO
            print("[SlotMachine] Alavanca puxada via teclado!")
            return True
        return False
    
    def update_lever(self, dt):
        """Atualiza a lógica e a máquina de estados da alavanca."""

        print('Chamada de update da SlotMachine')

        # Inicia a interação se estiver perto, a máquina estiver "Parada" e a trava estiver liberada
        if self.estado_atual == self.ESTADO_DESCENDO:
            self.angulo_alavanca -= self.velocidade_giro * dt
            if self.angulo_alavanca <= -60.0:
                self.angulo_alavanca = -60.0
                self.estado_atual = self.ESTADO_SUBINDO # Começa a voltar 

        elif self.estado_atual == self.ESTADO_SUBINDO:
            self.angulo_alavanca += self.velocidade_giro * dt
            if self.angulo_alavanca >= 0.0:
                self.angulo_alavanca = 0.0
                self.estado_atual = self.ESTADO_PARADA # Terminou a animação 
                return True # Retorna True para avisar o jogo que o giro terminou!
        
        return False

    def draw(self, renderer):
        """Renderiza a máquina e suas partes usando a hierarquia de matrizes."""
        renderer.push_matrix()
        # Posição e Reescala
        GL.glTranslatef(0.0, -8.0, -5.0) 
        GL.glScalef(self.escala, self.escala, self.escala)
        renderer.draw_model(self.corpo_model, texture_id=self.textura_id)

        renderer.push_matrix()
        GL.glTranslatef(0.27, 0.01, -0.021)
        GL.glRotatef(self.angulo_alavanca, 1.0, 0.0, 0.0)
        renderer.draw_model(self.alavanca_model, texture_id=self.textura_id)
        renderer.pop_matrix()

        # Ajuste esses valores base de acordo com o design do seu modelo 3D:
        x_ini = -0.175   # Posição X do primeiro rolo (mais à esquerda)
        espacamento = 0.0877 # Distância no eixo X entre o centro de cada rolo
        y_rolo = -0.0005       # Altura onde os rolos ficam dentro da máquina
        z_rolo = -0.008        # Profundidade dos rolos

        for i in range(5):
            renderer.push_matrix()
            
            # Calcula a posição X para cada um dos 5 rolos ficar lado a lado
            pos_x = x_ini + (i * espacamento)
            GL.glTranslatef(pos_x, y_rolo, z_rolo)
            
            # Aplica a rotação do giro no eixo X (fazendo o rolo girar para baixo/cima)
            angulo = self.angulos_rolos[i]
            GL.glRotatef(angulo, 1.0, 0.0, 0.0)
            
            # Desenha o modelo do rolo atual
            # Se os 5 rolos usam o mesmo modelo 3D, use apenas self.rolo_model
            renderer.draw_model(self.rolos_models[i], texture_id=self.textura_id)
            
            renderer.pop_matrix()

        renderer.pop_matrix()