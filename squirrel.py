# Squirrel Eat Squirrel (a 2D Katamari Damacy clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, sys, time, math, pygame
from pygame.locals import *

# Atencion: Se omiten tildes por compatibilidad (No somos tan bestias)

FRAMES_POR_SEGUNDO      = 30                         # frames por segundo para actualizar la pantalla
VENTANA_ANCHO           = 640                        # ancho de la ventana, en pixels
VENTANA_ALTURA          = 480                        # alto de la ventana, en pixels
VENTANA_MITAD_DE_ANCHO  = int(VENTANA_ANCHO / 2)
VENTANA_MITAD_DE_ALTURA = int(VENTANA_ALTURA / 2)
VENTANA_TITULO          = 'Titulo'

PASTO_COLOR = (24, 255, 0)
BLANCO      = (255, 255, 255)
ROJO        = (255, 0, 0)
IZQUIERDA   = 'left'
DERECHA     = 'right'

CAMARA_RETRASO              = 90         # que tan lejos se mueve el jugador del centro antes de que se mueva la camara
TASA_MOVIMIENTO             = 20         # que tan rapido se mueve el jugador
JUGADOR_SALTO_LONGITUD      = 20         # que tan largos son los saltos del jugador (>0)
JUGADOR_SALTO_ALTURA        = 30         # que tan altos son los saltos del jugador
JUGADOR_TAM_INICIAL         = 25         # que tan grande es el tamano del jugador al iniciar la partida
JUGADOR_TAM_GANADOR         = 300        # que tan grande tiene que ser el jugador para ganar
JUGADOR_TIEMPO_INVULNERABLE = 2          # por cuanto tiempo el jugador es invulnerable luego de haber sido tocado por un enemigo
JUGADOR_VIDAS_INICIALES     = 3          # con cuantas vidas inicia la partida el jugador
DURACION_LEYENDA_PERDISTE   = 4          # por cuanto tiempo se mustra la leyenda "game over" (en segundos)
PASTO_CANT                  = 18         # cantidad de objetos "pasto" en el area activa
ENEMIGOS_CANT               = 30         # cantidad de enemigos en el area activa
ARDILLAS_VELOCIDAD_MIN      = 3          # velocidad del enemigo mas lento
ARDILLAS_VELOCIDAD_MAX      = 7          # velocidad del enemigo mas rapido
FRECUENCIA_CAMBIO_DIR       = 2          # porcentaje de posibilidad de cambio de direccion por frame



# Aca empieza la ejecucion del programa:
#       ____
#      _|  |_
#      \    /
#       \  /
#        \/

def main():
    #defino variables que voy a usar en mi programa:
    global RELOJ, VENTANA, LETRA_FUENTE, ARD_IZQ_IMG, ARD_DER_IMG, PASTO_IMAGENES

    pygame.init()

    # incializo sus valores. 
    # (Inicializar: darles un valor inicial)
    RELOJ        = InicializarReloj()
    VENTANA      = InicializarVentana()
    LETRA_FUENTE = InicializarFuente()

    ARD_DER_IMG, ARD_IZQ_IMG, PASTO_IMAGENES = InicializarImagenes()

    while True:
        runGame()


def runGame():

    global gano
    comienzoInvulnerabilidad, modoGameOver, modoInvulnerableActivo, gano, momentoEnQuePerdio = InicializarVariablesDeEstado()
    rectanguloGameOver, txtSuperficieGameOver, winRect, winRect2, winSurf, winSurf2                      = InicializarTextos()

    camaraX = camaraY = 0  # camaraX y camaraY apuntan a la coordenada superior izquierda de la vista de camara
    moverIzq  = moverDer = moverArriba = moverAbajo  = False
    objetosEnemigos = []
    objetosPasto = SembrarUnPoquito(camaraX, camaraY)
    
    jugador = CrearJugador() 

    #Esto es lo que se va a repetir durante tooodo el juego
    while True:

        if modoInvulnerableActivo and TerminoTiempoInvulnerabilidad(comienzoInvulnerabilidad):
            modoInvulnerableActivo = False

        MoverEnemigos(objetosEnemigos)
        BorrarEnemigosNoVisibles(camaraX, camaraY, objetosEnemigos)
        BorrarPastoNoVisible(camaraX, camaraY, objetosPasto)
        SembrarPastoSiFalta(camaraX, camaraY, objetosPasto)
        HacerEnemigos(camaraX, camaraY, objetosEnemigos)
        camaraX, camaraY = AjustarEnfoqueDeCamara(camaraX, camaraY, jugador)
        VENTANA.fill(PASTO_COLOR)
        DibujarPastos(camaraX, camaraY, objetosPasto)
        DibujarEnemigos(camaraX, camaraY, objetosEnemigos)
        DibujarIndicadorDeVidas(jugador['vidas'])

        flashActivo = round(time.time(), 1) * 10 % 2 == 1
        if not modoGameOver and not (modoInvulnerableActivo and flashActivo): #Esta condicion hace que parpadee el jugador cuando esta en modo invulnerable
            DibujarJugador(camaraX, camaraY, jugador)

        # Aca empiezan a manejarse los eventos
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

            if event.type == KEYDOWN:
                debeReiniciar = False
                moverAbajo, moverArriba, moverDer, moverIzq, debeReiniciar = ResolverTeclaPresionada(moverIzq, moverDer, moverArriba, moverAbajo, event, jugador, debeReiniciar) 
                if debeReiniciar:
                    return

            if event.type == KEYUP:
                # Soltaron la tecla, hay que configurar todo para que deje de moverse el jugador
                if event.key in (K_LEFT, K_a):
                    moverIzq    = False
                elif event.key in (K_RIGHT, K_d):
                    moverDer    = False
                elif event.key in (K_UP, K_w):
                    moverArriba = False
                elif event.key in (K_DOWN, K_s):
                    moverAbajo  = False

                elif event.key == K_ESCAPE:
                    terminate()

        if not modoGameOver:
            # Aca se leen los valores configurados para mover efectivamente al jugador
            if moverIzq:
                jugador['x'] -= TASA_MOVIMIENTO
            if moverDer:
                jugador['x'] += TASA_MOVIMIENTO
            if moverArriba:
                jugador['y'] -= TASA_MOVIMIENTO
            if moverAbajo:
                jugador['y'] += TASA_MOVIMIENTO

            if (moverIzq or moverDer or moverArriba or moverAbajo) or jugador['salto'] != 0:
                jugador['salto'] += 1

            if jugador['salto'] > JUGADOR_SALTO_LONGITUD:
                jugador['salto'] = 0 # reseteo salto

            # chequeamos si el movimiento hizo que el jugador se chocara con algun enemigo. colliderect es la funcion que lo analiza.
            for i in range(len(objetosEnemigos)-1, -1, -1):
                enemObj = objetosEnemigos[i]
                if 'rect' in enemObj and jugador['rect'].colliderect(enemObj['rect']):
                    # hubo choque
                    if enemObj['ancho'] * enemObj['alto'] <= jugador['tam']**2:
                        # el jugador es mayor, asi que tiene que desaparecer el enemigo (lo borramos con "del")
                        jugador['tam'] += int( (enemObj['ancho'] * enemObj['alto'])**0.2 ) + 1
                        del objetosEnemigos[i]
                        # dibujamos al jugador con el nuevo tamano
                        if jugador['mirando'] == IZQUIERDA:
                            jugador['dibujo'] = pygame.transform.scale(ARD_IZQ_IMG, (jugador['tam'], jugador['tam']))
                        if jugador['mirando'] == DERECHA:
                            jugador['dibujo'] = pygame.transform.scale(ARD_DER_IMG, (jugador['tam'], jugador['tam']))

                        if jugador['tam'] > JUGADOR_TAM_GANADOR:
                            gano = True

                    elif not modoInvulnerableActivo:
                        # el jugador es menor
                        modoInvulnerableActivo   = True
                        comienzoInvulnerabilidad = time.time()
                        jugador['vidas']        -= 1
                        if jugador['vidas'] == 0:
                            modoGameOver       = True
                            momentoEnQuePerdio = time.time()
        else:
            # termino el juego
            VENTANA.blit(txtSuperficieGameOver, rectanguloGameOver)
            if time.time() - momentoEnQuePerdio > DURACION_LEYENDA_PERDISTE:
                return #termina el juego

        if gano:
            MostrarMensajesVictoria(winRect, winRect2, winSurf, winSurf2)

        pygame.display.update()
        RELOJ.tick(FRAMES_POR_SEGUNDO)


def InicializarImagenes():
    ARD_IZQ_IMG = pygame.image.load('squirrel.png')
    ARD_DER_IMG = pygame.transform.flip(ARD_IZQ_IMG, True, False)

    PASTO_IMAGENES = []
    for i in range(1, 5):
        PASTO_IMAGENES.append(pygame.image.load('grass%s.png' % i))

    return ARD_DER_IMG, ARD_IZQ_IMG, PASTO_IMAGENES

def InicializarVentana():
    VENTANA = pygame.display.set_mode((VENTANA_ANCHO, VENTANA_ALTURA))
    pygame.display.set_caption(VENTANA_TITULO)
    pygame.display.set_icon(pygame.image.load('gameicon.png'))
    return VENTANA

def InicializarFuente():
    return pygame.font.Font('freesansbold.ttf', 32)

def InicializarReloj():
    return pygame.time.Clock()

def InicializarTextos():
    txtSuperficieGameOver = LETRA_FUENTE.render('Perdiste :c', True, BLANCO)
    rectanguloGameOver = txtSuperficieGameOver.get_rect()
    rectanguloGameOver.center = (VENTANA_MITAD_DE_ANCHO, VENTANA_MITAD_DE_ALTURA)
    
    winSurf = LETRA_FUENTE.render('Llegaste al tamano Venti!', True, BLANCO)
    winRect = winSurf.get_rect()
    winRect.center = (VENTANA_MITAD_DE_ANCHO, VENTANA_MITAD_DE_ALTURA)
    
    winSurf2 = LETRA_FUENTE.render('(Presiona "r" para volver a jugar.)', True, BLANCO)
    winRect2 = winSurf2.get_rect()
    winRect2.center = (VENTANA_MITAD_DE_ANCHO, VENTANA_MITAD_DE_ALTURA + 30)
    return rectanguloGameOver, txtSuperficieGameOver, winRect, winRect2, winSurf, winSurf2

def CrearJugador():
    jugador = { 
                'dibujo' : pygame.transform.scale(ARD_IZQ_IMG, (JUGADOR_TAM_INICIAL, JUGADOR_TAM_INICIAL)),
                'mirando': IZQUIERDA,
                'tam'    : JUGADOR_TAM_INICIAL,
                'x'      : VENTANA_MITAD_DE_ANCHO,
                'y'      : VENTANA_MITAD_DE_ALTURA,
                'salto'  : 0,
                'vidas'  : JUGADOR_VIDAS_INICIALES
                }
    return jugador

def InicializarVariablesDeEstado():

    modoInvulnerable         = False           # si el jugador es invulnerable
    comienzoInvulnerabilidad = 0               # momento en que el jugador empieza a ser invulnerable
    modoGameOver             = False           # si el jugador perdio
    momentoEnQuePerdio       = 0               # momento en que el jugador perdio
    gano                     = False           # indica si el jugador gano

    return comienzoInvulnerabilidad, modoGameOver, modoInvulnerable, gano, momentoEnQuePerdio

def SembrarUnPoquito(camaraX, camaraY):
    objetosPasto = []
    for i in range(10):
        objetosPasto.append(CrearPasto(camaraX, camaraY))
        objetosPasto[i]['x'] = random.randint(0, VENTANA_ANCHO)
        objetosPasto[i]['y'] = random.randint(0, VENTANA_ALTURA)
    return objetosPasto

def TerminoTiempoInvulnerabilidad(comienzoInvulnerabilidad):
    return time.time() - comienzoInvulnerabilidad > JUGADOR_TIEMPO_INVULNERABLE

def SembrarPastoSiFalta(camaraX, camaraY, objetosPasto):
    while len(objetosPasto) < PASTO_CANT:
        objetosPasto.append(CrearPasto(camaraX, camaraY))

def BorrarPastoNoVisible(camaraX, camaraY, objetosPasto):
    for i in range(len(objetosPasto) - 1, -1, -1):
        if EstaFueraDelAreaActiva(camaraX, camaraY, objetosPasto[i]):
            del objetosPasto[i]

def BorrarEnemigosNoVisibles(camaraX, camaraY, objetosEnemigos):
    for i in range(len(objetosEnemigos) - 1, -1, -1):
        if EstaFueraDelAreaActiva(camaraX, camaraY, objetosEnemigos[i]):
            del objetosEnemigos[i]

def MoverEnemigos(objetosEnemigos):
    for enemigo in objetosEnemigos:
        # move the squirrel, and adjust for their salto
        enemigo['x']     += enemigo['movimientoHorizontal']
        enemigo['y']     += enemigo['movimientoVertical']
        enemigo['salto'] += 1
        if enemigo['salto'] > enemigo['longitudSalto']:
            enemigo['salto'] = 0 # reset salto amount
    
        # random chance they change direction
        if random.randint(0, 99) < FRECUENCIA_CAMBIO_DIR:
            enemigo['movimientoHorizontal'] = GetVelocidadAleatoria()
            enemigo['movimientoVertical'] = GetVelocidadAleatoria()
            if enemigo['movimientoHorizontal'] > 0: # faces right
                enemigo['dibujo'] = pygame.transform.scale(ARD_DER_IMG, (enemigo['ancho'], enemigo['alto']))
            else: # faces left
                enemigo['dibujo'] = pygame.transform.scale(ARD_IZQ_IMG, (enemigo['ancho'], enemigo['alto']))

def HacerEnemigos(camaraX, camaraY, objetosEnemigos):
    while len(objetosEnemigos) < ENEMIGOS_CANT:
        objetosEnemigos.append(crearEnemigoNuevo(camaraX, camaraY))

def AjustarEnfoqueDeCamara(camaraX, camaraY, jugador):
    jugadorCentroHorizontal = jugador['x'] + int(jugador['tam'] / 2)
    jugadorCentroVertical = jugador['y'] + int(jugador['tam'] / 2)
    if (camaraX + VENTANA_MITAD_DE_ANCHO) - jugadorCentroHorizontal > CAMARA_RETRASO:
        camaraX = jugadorCentroHorizontal + CAMARA_RETRASO - VENTANA_MITAD_DE_ANCHO
    elif jugadorCentroHorizontal - (camaraX + VENTANA_MITAD_DE_ANCHO) > CAMARA_RETRASO:
        camaraX = jugadorCentroHorizontal - CAMARA_RETRASO - VENTANA_MITAD_DE_ANCHO
    if (camaraY + VENTANA_MITAD_DE_ALTURA) - jugadorCentroVertical > CAMARA_RETRASO:
        camaraY = jugadorCentroVertical + CAMARA_RETRASO - VENTANA_MITAD_DE_ALTURA
    elif jugadorCentroVertical - (camaraY + VENTANA_MITAD_DE_ALTURA) > CAMARA_RETRASO:
        camaraY = jugadorCentroVertical - CAMARA_RETRASO - VENTANA_MITAD_DE_ALTURA
    return camaraX, camaraY

def DibujarPastos(camaraX, camaraY, objetosPasto):
    for pasto in objetosPasto:
        pastoRect = pygame.Rect( (pasto['x'] - camaraX,
                              pasto['y'] - camaraY,
                              pasto['ancho'],
                              pasto['alto']) )
        VENTANA.blit(PASTO_IMAGENES[pasto['imagenPasto']], pastoRect)

def DibujarEnemigos(camaraX, camaraY, objetosEnemigos):
    for enemigo in objetosEnemigos:
        enemigo['rect'] = pygame.Rect(enemigo['x'] - camaraX,
                                      enemigo['y'] - camaraY - GetMagnitudDeRebote(enemigo['salto'], enemigo['longitudSalto'], enemigo['alturaSalto']),
                                      enemigo['ancho'],
                                      enemigo['alto'])
        VENTANA.blit(enemigo['dibujo'], enemigo['rect'])

def DibujarJugador(camaraX, camaraY, jugador):
    jugador['rect'] = pygame.Rect(  jugador['x'] - camaraX,
                                    jugador['y'] - camaraY - GetMagnitudDeRebote(jugador['salto'], JUGADOR_SALTO_LONGITUD, JUGADOR_SALTO_ALTURA),
                                    jugador['tam'],
                                    jugador['tam'])
    VENTANA.blit(jugador['dibujo'], jugador['rect'])

def MostrarMensajesVictoria(winRect, winRect2, winSurf, winSurf2 ):
    VENTANA.blit(winSurf, winRect)
    VENTANA.blit(winSurf2, winRect2)

def PresionoTeclaArriba(event):
    return event.key in (K_UP, K_w)

def PresionoTeclaAbajo(event):
    return event.key in (K_DOWN, K_s)

def PresionoTeclaIzquierda(event):
    return event.key in (K_LEFT, K_a)

def PresionoTeclaDerecha(event):
    return event.key in (K_RIGHT, K_d)

def ResolverTeclaPresionada(moverIzq, moverDer, moverArriba, moverAbajo, event, jugador, debeReiniciar):
    if PresionoTeclaArriba(event):
        moverAbajo = False
        moverArriba = True
    elif PresionoTeclaAbajo(event):
        moverArriba = False
        moverAbajo = True
    elif PresionoTeclaIzquierda(event):
        moverDer = False
        moverIzq = True
        if jugador['mirando'] != IZQUIERDA:
            jugador['dibujo'] = pygame.transform.scale(ARD_IZQ_IMG, (jugador['tam'], jugador['tam']))
        jugador['mirando'] = IZQUIERDA
    elif PresionoTeclaDerecha(event):
        moverIzq = False
        moverDer = True
        if jugador['mirando'] != DERECHA:
            jugador['dibujo'] = pygame.transform.scale(ARD_DER_IMG, (jugador['tam'], jugador['tam']))
        jugador['mirando'] = DERECHA
    elif gano and event.key == K_r:
        debeReiniciar = True

    return moverAbajo, moverArriba, moverDer, moverIzq, debeReiniciar


def DibujarIndicadorDeVidas(currentHealth):
    DibujarVidasRestantes(currentHealth)
    DibujarVidasPerdidas()

def DibujarVidasRestantes(currentHealth):
    for i in range(currentHealth):
        pygame.draw.rect(VENTANA, ROJO,   (15, 5 + (10 * JUGADOR_VIDAS_INICIALES) - i * 10, 20, 10))

def DibujarVidasPerdidas():
    for i in range(JUGADOR_VIDAS_INICIALES):
        pygame.draw.rect(VENTANA, BLANCO, (15, 5 + (10 * JUGADOR_VIDAS_INICIALES) - i * 10, 20, 10), 1)

def terminate():
    pygame.quit()
    sys.exit()

def GetMagnitudDeRebote(saltoActual, longitudSalto, alturaSalto):
    # saltoActual va a ser siempre menor que longitudSalto
    return int(math.sin( (math.pi / float(longitudSalto)) * saltoActual ) * alturaSalto)

def GetVelocidadAleatoria():
    velocidad = random.randint(ARDILLAS_VELOCIDAD_MIN, ARDILLAS_VELOCIDAD_MAX)
    if random.randint(0, 1) == 0:
        return velocidad
    else:
        return -velocidad

def GetPosicionRandomFueraDeCamara(camerax, cameray, objWidth, objHeight):
    # crea rectangulo de la vista de la camara. Parametros: izquierda, arriba, ancho, altura.
    rectanguloCamara = pygame.Rect(camerax, cameray, VENTANA_ANCHO, VENTANA_ALTURA)
    while True:
        x = random.randint(camerax - VENTANA_ANCHO, camerax + (2 * VENTANA_ANCHO))
        y = random.randint(cameray - VENTANA_ALTURA, cameray + (2 * VENTANA_ALTURA))
        # creo un objeto rect con las coordenadas dadas y me aseguro de que no haya interseccion con la vista de la camara
        rect = pygame.Rect(x, y, objWidth, objHeight)
        if not rect.colliderect(rectanguloCamara):
            return x, y

def EstaMirandoALaIzquierda(enemigoNuevo):
    return enemigoNuevo['movimientoHorizontal'] < 0

def crearEnemigoNuevo(camerax, cameray):
    enemigoNuevo = {}
    tamGeneral                           = random.randint(5, 25)
    multiplicador                        = random.randint(1, 3)
    enemigoNuevo['ancho']                = (tamGeneral + random.randint(0, 10)) * multiplicador
    enemigoNuevo['alto']                 = (tamGeneral + random.randint(0, 10)) * multiplicador
    enemigoNuevo['x'], enemigoNuevo['y'] = GetPosicionRandomFueraDeCamara(camerax, cameray, enemigoNuevo['ancho'], enemigoNuevo['alto'])
    enemigoNuevo['movimientoHorizontal'] = GetVelocidadAleatoria()
    enemigoNuevo['movimientoVertical']   = GetVelocidadAleatoria()
    enemigoNuevo['salto']                = 0
    enemigoNuevo['longitudSalto']        = random.randint(5, 18)
    enemigoNuevo['alturaSalto']          = random.randint(10, 50)
    
    if EstaMirandoALaIzquierda(enemigoNuevo):
        enemigoNuevo['dibujo']           = pygame.transform.scale(ARD_IZQ_IMG, (enemigoNuevo['ancho'], enemigoNuevo['alto']))
    else:
        enemigoNuevo['dibujo']           = pygame.transform.scale(ARD_DER_IMG, (enemigoNuevo['ancho'], enemigoNuevo['alto']))

    return enemigoNuevo

def CrearPasto(camerax, cameray):
    pasto = {}
    pasto['imagenPasto']   = random.randint(0, len(PASTO_IMAGENES) - 1)
    pasto['ancho']         = PASTO_IMAGENES[0].get_width()
    pasto['alto']          = PASTO_IMAGENES[0].get_height()
    pasto['x'], pasto['y'] = GetPosicionRandomFueraDeCamara(camerax, cameray, pasto['ancho'], pasto['alto'])
    pasto['rect']          = pygame.Rect( (pasto['x'], pasto['y'], pasto['ancho'], pasto['alto']) )
    return pasto

def EstaFueraDelAreaActiva(camerax, cameray, obj):
    # Return False if camerax and cameray are more than
    # a half-window length beyond the edge of the window.
    boundsLeftEdge = camerax - VENTANA_ANCHO
    boundsTopEdge = cameray - VENTANA_ALTURA
    boundsRect = pygame.Rect(boundsLeftEdge, boundsTopEdge, VENTANA_ANCHO * 3, VENTANA_ALTURA * 3)
    objRect = pygame.Rect(obj['x'], obj['y'], obj['ancho'], obj['alto'])
    return not boundsRect.colliderect(objRect)


if __name__ == '__main__':
    main()