/* Diapositivas interactivas del taller.
   Los números del modelo vienen de datos.js (ver herramientas/generar_datos_clase.py). */
(function () {
  "use strict";

  const DATOS = window.DATOS;

  // ------------------------------------------------------------------ ayudas

  /** Crea un elemento: crear("div", "clase", "texto"). */
  function crear(etiqueta, clase, texto) {
    const elemento = document.createElement(etiqueta);
    if (clase) elemento.className = clase;
    if (texto !== undefined) elemento.textContent = texto;
    return elemento;
  }

  function porcentaje(p) {
    return (p * 100).toFixed(1) + "%";
  }

  function miles(n) {
    return n.toLocaleString("es-AR");
  }

  /** Muestra los espacios de un token con un punto medio, para que se vean. */
  function visible(pieza) {
    // Un token que es solo parte de un carácter viene escrito en bytes, como <20 c3>: se deja igual.
    if (/^<[0-9a-f ]+>$/.test(pieza)) return pieza;
    return pieza.replace(/ /g, "·").replace(/\n/g, "↵");
  }

  /** Una fila con nombre, barra y valor. Devuelve las partes para poder actualizarlas. */
  function crearBarra(nombre) {
    const fila = crear("div", "barra");
    const etiqueta = crear("span", "nombre", nombre);
    const pista = crear("span", "pista");
    const relleno = crear("i");
    const valor = crear("span", "valor");
    pista.appendChild(relleno);
    fila.append(etiqueta, pista, valor);
    return { fila, etiqueta, relleno, valor };
  }

  // -------------------------------------------- 1. la red neuronal que infiere

  // El dibujo de la red neuronal. Es un esquema: una red real tiene millones de conexiones.
  const RED_ANCHO = 330;
  const FILA_ALTO = 40; // alto de cada barra, en píxeles (el mismo que en estilo.css)
  const FILA_ESPACIO = 12; // espacio entre una barra y la siguiente (el mismo que en estilo.css)
  const CAPAS_INTERNAS = [4, 6, 6]; // neuronas de la capa de entrada y de las dos capas ocultas
  const CAPAS_X = [34, 124, 214, 300]; // en qué posición horizontal va cada capa
  const PASO = 170; // milisegundos que tarda la señal en pasar de una capa a la siguiente

  /** Crea un elemento de dibujo (SVG) con sus atributos. */
  function crearDibujo(etiqueta, atributos) {
    const elemento = document.createElementNS("http://www.w3.org/2000/svg", etiqueta);
    Object.entries(atributos).forEach(([nombre, valor]) => elemento.setAttribute(nombre, valor));
    return elemento;
  }

  /** Números al azar repetibles: con la misma semilla salen siempre los mismos. */
  function generador(semilla) {
    return function () {
      semilla = (semilla + 0x6d2b79f5) | 0;
      let t = Math.imul(semilla ^ (semilla >>> 15), 1 | semilla);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  /** Dibuja una red con `salidas` neuronas de salida, una por barra, y devuelve cómo animarla.
      Si `ultimaEsResto` es verdadero, la última neurona representa a muchas y se dibuja punteada. */
  function armarRed(salidas, ultimaEsResto) {
    const capas = CAPAS_INTERNAS.concat(salidas);
    const ultima = capas.length - 1;
    const alto = salidas * FILA_ALTO + (salidas - 1) * FILA_ESPACIO; // el mismo alto que el bloque de barras
    const dibujo = crearDibujo("svg", { class: "red", width: RED_ANCHO, height: alto, viewBox: "0 0 " + RED_ANCHO + " " + alto });
    const azar = generador(11);

    // Dónde va cada neurona. Las de salida quedan a la altura de su barra.
    const posiciones = capas.map((cantidad, capa) =>
      Array.from({ length: cantidad }, (_, i) => ({
        x: CAPAS_X[capa],
        y: capa === ultima ? FILA_ALTO / 2 + (FILA_ALTO + FILA_ESPACIO) * i : (alto * (i + 1)) / (cantidad + 1),
      }))
    );

    // Un cable es una línea gris fija y, encima, otra de color que se enciende cuando pasa la señal.
    function crearCable(x1, y1, x2, y2) {
      dibujo.appendChild(crearDibujo("line", { class: "cable", x1, y1, x2, y2 }));
      const senal = crearDibujo("line", { class: "senal", x1, y1, x2, y2 });
      dibujo.appendChild(senal);
      return { senal, largo: Math.hypot(x2 - x1, y2 - y1) };
    }

    // Por dónde entra la imagen o el texto, las conexiones entre capas y por dónde salen los resultados.
    const cablesDeEntrada = posiciones[0].map((p) => crearCable(0, p.y, p.x, p.y));
    const conexiones = []; // conexiones[capa][i][j]: de la neurona i de una capa a la neurona j de la siguiente
    for (let capa = 0; capa < ultima; capa++) {
      conexiones.push(
        posiciones[capa].map((desde) =>
          posiciones[capa + 1].map((hasta) => {
            const cable = crearCable(desde.x, desde.y, hasta.x, hasta.y);
            cable.peso = azar() * 2 - 1; // el «peso» de la conexión: siempre el mismo, la red ya está entrenada
            return cable;
          })
        )
      );
    }
    const cablesDeSalida = posiciones[ultima].map((p) => crearCable(p.x, p.y, RED_ANCHO, p.y));

    // Las neuronas se dibujan al final, para que queden encima de los cables.
    const neuronas = posiciones.map((capa, numero) =>
      capa.map((p, i) => {
        const esResto = ultimaEsResto && numero === ultima && i === capa.length - 1;
        dibujo.appendChild(crearDibujo("circle", { class: esResto ? "neurona resto" : "neurona", cx: p.x, cy: p.y, r: 9 }));
        const luz = crearDibujo("circle", { class: "luz", cx: p.x, cy: p.y, r: 9 });
        dibujo.appendChild(luz);
        return luz;
      })
    );

    /** Cuánto se enciende cada neurona con una entrada (de 0 a 1). La última capa son las probabilidades. */
    function calcular(caso) {
      const activaciones = [caso.entrada];
      for (let capa = 0; capa < ultima - 1; capa++) {
        const anterior = activaciones[capa];
        activaciones.push(
          posiciones[capa + 1].map((_, j) => {
            const suma = anterior.reduce((total, activacion, i) => total + activacion * conexiones[capa][i][j].peso, 0);
            return 1 / (1 + Math.exp(-2.4 * suma));
          })
        );
      }
      activaciones.push(caso.p);
      return activaciones;
    }

    /** La señal recorre un cable de punta a punta. `fuerza` (de 0 a 1) dice cuánto brilla. */
    function pasarSenal(cable, fuerza) {
      const linea = cable.senal;
      linea.style.transition = "none";
      linea.style.strokeDasharray = cable.largo;
      linea.style.strokeDashoffset = cable.largo;
      linea.style.strokeOpacity = 0.08 + 0.92 * fuerza;
      linea.getBoundingClientRect(); // obliga al navegador a tomar este estado inicial antes de animar
      linea.style.transition = "stroke-dashoffset " + PASO + "ms linear, stroke-opacity 350ms ease";
      linea.style.strokeDashoffset = 0;
      cable.fuerza = fuerza;
    }

    /** Vuelve todo al estado de reposo, sin animación. */
    function apagar() {
      dibujo.querySelectorAll(".senal").forEach((linea) => {
        linea.style.transition = "none";
        linea.style.strokeOpacity = 0;
      });
      dibujo.querySelectorAll(".luz").forEach((luz) => {
        luz.style.transition = "none";
        luz.style.fillOpacity = 0;
        luz.classList.remove("gana");
      });
      dibujo.getBoundingClientRect();
      dibujo.querySelectorAll(".luz").forEach((luz) => (luz.style.transition = ""));
    }

    let corrida = 0; // si se elige otra entrada en el medio, la animación anterior se abandona

    /** Hace pasar una entrada por la red, capa por capa, y al final llama a `alTerminar`.
        `caso` trae: entrada (cuánto se enciende cada neurona de entrada), p (las probabilidades
        de salida) y ganadora (qué neurona de salida se marca en amarillo). */
    function animar(caso, alTerminar) {
      const mia = ++corrida;
      const despues = (milisegundos, hacer) => setTimeout(() => mia === corrida && hacer(), milisegundos);
      const activaciones = calcular(caso);
      apagar();

      // La imagen o el texto entra a la red.
      cablesDeEntrada.forEach((cable, i) => pasarSenal(cable, activaciones[0][i]));

      for (let capa = 0; capa <= ultima; capa++) {
        despues(PASO * (capa + 1), () => {
          // La señal llegó a esta capa: se encienden sus neuronas.
          // (En la salida se usa la raíz cuadrada para que también se vean las probabilidades chicas.)
          neuronas[capa].forEach((luz, i) => {
            const brillo = capa === ultima ? Math.sqrt(activaciones[capa][i]) : activaciones[capa][i];
            luz.style.fillOpacity = 0.1 + 0.9 * brillo;
            luz.classList.toggle("gana", capa === ultima && i === caso.ganadora);
          });
          // Los cables por los que llegó quedan tenues.
          const anteriores = capa === 0 ? cablesDeEntrada : conexiones[capa - 1].flat();
          anteriores.forEach((cable) => (cable.senal.style.strokeOpacity = 0.4 * cable.fuerza));
          // Y la señal sale hacia la capa siguiente (o hacia las barras, si es la última).
          if (capa === ultima) {
            cablesDeSalida.forEach((cable, j) => pasarSenal(cable, Math.sqrt(caso.p[j])));
            return;
          }
          conexiones[capa].forEach((desde, i) =>
            desde.forEach((cable, j) => {
              // A la salida, brillan más los cables que van a las opciones más probables.
              const destino = capa + 1 === ultima ? Math.sqrt(caso.p[j]) : Math.abs(cable.peso);
              pasarSenal(cable, activaciones[capa][i] * destino);
            })
          );
        });
      }
      despues(PASO * (ultima + 1) + 120, alTerminar);
    }

    return { dibujo, animar };
  }

  /** Arma una diapositiva de inferencia: entradas para elegir, la red, las barras y la respuesta.
      `config` trae:
        casos          las entradas que se pueden elegir. Cada una con: titulo, nombres (de las
                       barras), p (probabilidades), ganadora y entrada (ver `animar`).
        crearBoton     arma el botón de un caso.
        claseEntradas  la clase del bloque de botones.
        nombresFijos   los nombres de las barras, si son siempre los mismos y se ven desde el comienzo.
        ultimaEsResto  verdadero si la última barra junta «todo lo demás».
        ayuda          el texto que se ve antes de elegir.
        rotulo         cómo se llama la respuesta («Respuesta», «Más probable»). */
  function armarInferencia(raiz, config) {
    const cantidad = config.casos[0].p.length; // cuántas barras hay, y cuántas neuronas de salida
    const entradas = crear("div", config.claseEntradas);
    const salida = crear("div", "salida-red");
    const titulo = crear("p", "titulo-red", config.ayuda);
    const red = armarRed(cantidad, config.ultimaEsResto);
    const barras = crear("div", "barras");
    const pie = crear("p", "pie-red", "red neuronal");
    const respuesta = crear("p", "respuesta-red");
    salida.append(titulo, red.dibujo, barras, pie, respuesta);
    raiz.append(entradas, salida);

    const filas = Array.from({ length: cantidad }, (_, i) => {
      const fila = crearBarra("");
      if (config.ultimaEsResto && i === cantidad - 1) fila.fila.classList.add("resto");
      barras.appendChild(fila.fila);
      return fila;
    });

    const botones = config.casos.map((caso, posicion) => {
      const boton = config.crearBoton(caso);
      boton.addEventListener("click", () => elegir(posicion));
      entradas.appendChild(boton);
      return boton;
    });

    /** Deja las barras vacías: todavía no hay respuesta. */
    function vaciar() {
      filas.forEach((fila, i) => {
        fila.etiqueta.textContent = config.nombresFijos ? config.nombresFijos[i] : "";
        fila.relleno.style.width = "0%";
        fila.valor.textContent = "";
        fila.fila.classList.remove("viva");
      });
      respuesta.innerHTML = config.rotulo + ': <span class="gris">…</span>';
    }

    /** Muestra las probabilidades que salieron de la red. */
    function mostrar(caso) {
      filas.forEach((fila, i) => {
        fila.etiqueta.textContent = caso.nombres[i];
        // Lo normal es mostrar la probabilidad. Un caso puede traer otros anchos y textos (los logits).
        fila.relleno.style.width = (caso.anchos ? caso.anchos[i] : caso.p[i]) * 100 + "%";
        fila.valor.textContent = caso.textos ? caso.textos[i] : porcentaje(caso.p[i]);
        fila.fila.classList.toggle("viva", i === caso.ganadora);
      });
      respuesta.innerHTML = config.rotulo + ": <strong></strong>";
      respuesta.querySelector("strong").textContent = caso.nombres[caso.ganadora];
    }

    function elegir(posicion) {
      const caso = config.casos[posicion];
      botones.forEach((boton, i) => boton.classList.toggle("activa", i === posicion));
      // El botón da un saltito: la entrada «sale» hacia la red.
      botones[posicion].classList.remove("enviando");
      botones[posicion].getBoundingClientRect();
      botones[posicion].classList.add("enviando");
      titulo.textContent = caso.titulo;
      // Mientras la red trabaja las barras están vacías; se llenan cuando la señal llega a la salida.
      vaciar();
      red.animar(caso, () => mostrar(caso));
    }

    vaciar();
  }

  // ----------------------------------------- 1a. el clasificador de imágenes

  // Números ilustrativos: no salen de un modelo real.
  //   p:       la probabilidad de cada etiqueta.
  //   entrada: cuánto se enciende cada neurona de entrada (el lobo se parece al perro).
  const ETIQUETAS = ["perro", "persona", "gato", "oso", "auto"];
  const IMAGENES = [
    { icono: "🐕", titulo: "Un perro", p: [0.96, 0.01, 0.02, 0.01, 0.0], entrada: [0.95, 0.2, 0.75, 0.15] },
    { icono: "🧍", titulo: "Una persona", p: [0.01, 0.97, 0.005, 0.01, 0.005], entrada: [0.15, 0.9, 0.25, 0.85] },
    { icono: "🧍", mascara: "🐶", titulo: "Una persona disfrazada de perro", p: [0.46, 0.41, 0.04, 0.08, 0.01], entrada: [0.6, 0.6, 0.55, 0.5] },
    { icono: "🐺", titulo: "Un lobo", p: [0.71, 0.01, 0.07, 0.2, 0.01], entrada: [0.9, 0.15, 0.9, 0.35] },
    // El león tampoco está entre las etiquetas: da algo de gato y algo de oso.
    { icono: "🦁", titulo: "Un león", p: [0.1, 0.02, 0.48, 0.38, 0.02], entrada: [0.55, 0.2, 0.3, 0.9] },
    // Una imagen «basura»: no tiene nada que ver con ninguna etiqueta, y la red responde igual.
    { icono: "🍕", titulo: "Una pizza", p: [0.18, 0.22, 0.15, 0.12, 0.33], entrada: [0.4, 0.45, 0.35, 0.6] },
  ];

  function armarClasificador(raiz) {
    armarInferencia(raiz, {
      casos: IMAGENES.map((imagen) =>
        Object.assign({ nombres: ETIQUETAS, ganadora: imagen.p.indexOf(Math.max(...imagen.p)) }, imagen)
      ),
      nombresFijos: ETIQUETAS,
      ayuda: "Elegí una imagen",
      rotulo: "Respuesta",
      claseEntradas: "entradas",
      crearBoton(imagen) {
        const boton = crear("button", "entrada");
        const icono = crear("span", "icono", imagen.icono);
        if (imagen.mascara) icono.appendChild(crear("i", "", imagen.mascara));
        boton.appendChild(icono);
        boton.title = imagen.titulo;
        return boton;
      },
    });
  }

  // ------------------------------------------- 1b. el LLM: el próximo token

  // Acá los números sí son reales: salen del modelo (ver herramientas/generar_datos_clase.py).
  function armarLLM(raiz) {
    // Hay tres versiones de la diapositiva: con palabras (la introducción), con tokens (lo que
    // pasa de verdad) y con logits (lo que sale de la red antes de convertirlo en probabilidades).
    const conLogits = raiz.dataset.modo === "logits";
    const conTokens = raiz.dataset.modo === "tokens" || conLogits;
    const ejemplos = conTokens ? DATOS.ejemplos_con_tokens : DATOS.ejemplos;
    if (conLogits) raiz.classList.add("logits");
    armarInferencia(raiz, {
      casos: ejemplos.map((ejemplo, posicion) => {
        const azar = generador(50 + posicion); // cada texto enciende distinto las neuronas de entrada
        if (conLogits) {
          // La última fila ya no es «el resto»: los logits no se suman. Solo recuerda que hay muchos más.
          const mayor = ejemplo.mejores[0].logit;
          return {
            texto: ejemplo.texto,
            piezas: ejemplo.piezas,
            titulo: "Un logit por cada token",
            nombres: ejemplo.mejores.map((opcion) => visible(opcion.pieza)).concat("…"),
            p: ejemplo.mejores.map((opcion) => opcion.p).concat(ejemplo.resto),
            anchos: ejemplo.mejores.map((opcion) => opcion.logit / (mayor * 1.05)).concat(0),
            textos: ejemplo.mejores.map((opcion) => opcion.logit.toFixed(2)).concat(""),
            ganadora: 0,
            entrada: [azar(), azar(), azar(), azar()].map((valor) => 0.15 + 0.8 * valor),
          };
        }
        return {
          texto: ejemplo.texto,
          piezas: ejemplo.piezas,
          titulo: conTokens ? "¿Qué token sigue?" : "¿Qué palabra sigue?",
          // Las barras: las opciones más probables y, al final, todo lo demás junto.
          nombres: ejemplo.mejores.map((opcion) => (conTokens ? visible(opcion.pieza) : opcion.palabra)).concat("el resto"),
          p: ejemplo.mejores.map((opcion) => opcion.p).concat(ejemplo.resto),
          ganadora: 0, // la opción más probable («el resto» no cuenta)
          entrada: [azar(), azar(), azar(), azar()].map((valor) => 0.15 + 0.8 * valor),
        };
      }),
      ultimaEsResto: true,
      ayuda: "Elegí un texto",
      rotulo: conLogits ? "Logit más alto" : "Más probable",
      claseEntradas: "entradas textos",
      crearBoton(caso) {
        const boton = crear("button", "entrada texto");
        if (conTokens) {
          // El texto se muestra partido en tokens, cada uno con su color.
          caso.piezas.forEach((pieza, i) => boton.appendChild(crear("span", "ficha color-" + (i % 5), visible(pieza))));
        } else {
          boton.textContent = caso.texto + " ";
        }
        boton.appendChild(crear("span", "gris", "…"));
        return boton;
      },
    });
  }

  // -------------------------------------------------------- 2. el tokenizador

  function armarTokenizador(raiz) {
    const frases = crear("div", "botonera");
    const tokens = crear("div", "tokens-grandes");
    const pie = crear("div", "pie-tokens");
    const cuenta = crear("span", "gris");
    const verNumeros = crear("button", "boton", "Ver los números");
    pie.append(cuenta, verNumeros);
    raiz.append(frases, tokens, pie);

    let conNumeros = false;
    verNumeros.addEventListener("click", () => {
      conNumeros = !conNumeros;
      tokens.classList.toggle("con-numeros", conNumeros);
      verNumeros.textContent = conNumeros ? "Ocultar los números" : "Ver los números";
    });

    const botones = DATOS.tokens.map((frase, posicion) => {
      const boton = crear("button", "boton", frase.texto);
      boton.addEventListener("click", () => elegir(posicion));
      frases.appendChild(boton);
      return boton;
    });

    function elegir(posicion) {
      const frase = DATOS.tokens[posicion];
      botones.forEach((boton, i) => boton.classList.toggle("activa", i === posicion));
      tokens.textContent = "";
      frase.tokens.forEach((token, i) => {
        const ficha = crear("span", "ficha color-" + (i % 5));
        ficha.append(crear("b", "", visible(token.pieza)), crear("small", "", token.numero));
        tokens.appendChild(ficha);
      });
      cuenta.textContent = frase.texto.length + " caracteres → " + frase.tokens.length + " tokens";
    }

    elegir(0);
  }

  // ------------------------------------------- 3. logits, probabilidades, sorteo

  // Todos los tokens del vocabulario, del logit más alto al más bajo.
  // Los 40 mejores van de a uno; el resto, agrupado en cajones de logit parecido.
  const PROXIMO = DATOS.proximo;
  const GRUPOS = PROXIMO.mejores
    .map((token) => ({ pieza: token.pieza, logit: token.logit, cantidad: 1 }))
    .concat(PROXIMO.resto.map(([logit, cantidad]) => ({ pieza: null, logit, cantidad })));
  const LOGIT_MAXIMO = GRUPOS[0].logit;

  /** Aplica top-k, top-p y temperatura, en el mismo orden que llama.cpp.
      Devuelve, para cada grupo, cuántos tokens siguen en carrera y cuánta probabilidad juntan. */
  function calcular(temperatura, topK, topP) {
    // 1. top-k: quedan los K tokens de mayor logit.
    let lugares = topK > 0 ? topK : Infinity;
    const vivos = GRUPOS.map((grupo) => {
      const quedan = Math.min(grupo.cantidad, lugares);
      lugares -= quedan;
      return quedan;
    });

    // 2. top-p: quedan los más probables hasta juntar P (con temperatura 1).
    if (topP < 1) {
      const pesos = GRUPOS.map((grupo) => Math.exp(grupo.logit - LOGIT_MAXIMO));
      const total = pesos.reduce((suma, peso, i) => suma + peso * vivos[i], 0);
      let acumulado = 0;
      for (let i = 0; i < GRUPOS.length; i++) {
        const cadaUno = pesos[i] / total;
        if (acumulado >= topP) {
          vivos[i] = 0;
        } else {
          const hacenFalta = Math.ceil((topP - acumulado) / cadaUno);
          vivos[i] = Math.min(vivos[i], hacenFalta);
          acumulado += vivos[i] * cadaUno;
        }
      }
    }

    // 3. temperatura y softmax: logit ÷ temperatura → probabilidad.
    const pesos = GRUPOS.map((grupo, i) => vivos[i] * Math.exp((grupo.logit - LOGIT_MAXIMO) / temperatura));
    const total = pesos.reduce((suma, peso) => suma + peso, 0);
    return { vivos, probabilidades: pesos.map((peso) => peso / total) };
  }

  /** Arma un control deslizante. `mostrar` convierte el número en el texto que se ve. */
  function crearPerilla(nombre, minimo, maximo, paso, inicial, mostrar, alCambiar) {
    const caja = crear("label", "perilla");
    const titulo = crear("span", "nombre-perilla", nombre);
    const valor = crear("span", "valor-perilla", mostrar(inicial));
    const control = crear("input");
    control.type = "range";
    control.min = minimo;
    control.max = maximo;
    control.step = paso;
    control.value = inicial;
    control.addEventListener("input", () => {
      valor.textContent = mostrar(Number(control.value));
      alCambiar(Number(control.value));
    });
    // Al soltar, las flechas del teclado vuelven a pasar de diapositiva.
    control.addEventListener("change", () => control.blur());
    caja.append(titulo, control, valor);
    return caja;
  }

  function armarGrafico(raiz) {
    const controles = (raiz.dataset.controles || "").split(" ").filter(Boolean);
    const cuantasFilas = Number(raiz.dataset.filas || 10);
    const SIN_K = 41; // la última posición de la perilla de top-k quiere decir «todos»
    const estado = { temperatura: 1, topK: 0, topP: 1 };
    const nota = raiz.querySelector(".nota");
    if (nota) nota.remove();

    // Con la perilla de temperatura se agrega una columna más: logit ÷ temperatura.
    const conDivision = controles.includes("temperatura");
    if (conDivision) raiz.classList.add("con-division");

    const tabla = crear("div", "grafico-tabla");
    const encabezado = crear("div", "fila encabezado");
    encabezado.append(crear("span", "", "token"), crear("span", "", "logit"), crear("span", "", ""));
    if (conDivision) encabezado.append(crear("span", "titulo-division", "logit ÷ temperatura"));
    encabezado.append(crear("span", "", "probabilidad"), crear("span", "", ""));
    tabla.appendChild(encabezado);

    // Escala de las barras de logit: del más bajo que se muestra al más alto.
    const logitMinimo = GRUPOS[cuantasFilas - 1].logit - 1.5;
    const filas = GRUPOS.slice(0, cuantasFilas).map((grupo) => {
      const fila = crear("div", "fila");
      const pistaLogit = crear("span", "pista logit");
      const rellenoLogit = crear("i");
      rellenoLogit.style.width = ((grupo.logit - logitMinimo) / (LOGIT_MAXIMO - logitMinimo)) * 100 + "%";
      pistaLogit.appendChild(rellenoLogit);
      const pista = crear("span", "pista");
      const relleno = crear("i");
      pista.appendChild(relleno);
      const valor = crear("span", "valor");
      fila.append(crear("span", "nombre", visible(grupo.pieza)), crear("span", "numero-logit", grupo.logit.toFixed(2)), pistaLogit);
      // La columna de logit ÷ temperatura: el número y su barra.
      const numeroDivision = crear("span", "numero-division");
      const rellenoDivision = crear("i");
      if (conDivision) {
        const pistaDivision = crear("span", "pista division");
        pistaDivision.appendChild(rellenoDivision);
        fila.append(numeroDivision, pistaDivision);
      }
      fila.append(pista, valor);
      tabla.appendChild(fila);
      return { fila, relleno, valor, logit: grupo.logit, numeroDivision, rellenoDivision };
    });

    // La última fila junta a todos los tokens que no se muestran.
    const filaResto = crear("div", "fila resto");
    const nombreResto = crear("span", "nombre");
    const pistaResto = crear("span", "pista");
    const rellenoResto = crear("i");
    pistaResto.appendChild(rellenoResto);
    const valorResto = crear("span", "valor");
    filaResto.append(nombreResto, crear("span"), crear("span"));
    if (conDivision) filaResto.append(crear("span"), crear("span"));
    filaResto.append(pistaResto, valorResto);
    tabla.appendChild(filaResto);

    const panel = crear("div", "perillas");
    const carrera = crear("p", "carrera");
    const sorteo = crear("div", "sorteo");
    const salidas = crear("div", "salidas");

    if (controles.includes("temperatura")) {
      panel.appendChild(crearPerilla("Temperatura", 0.1, 3, 0.1, 1, (v) => v.toFixed(1), (v) => { estado.temperatura = v; dibujar(); }));
    }
    if (controles.includes("top-k")) {
      panel.appendChild(crearPerilla("Top-k", 1, SIN_K, 1, SIN_K, (v) => (v === SIN_K ? "todos" : String(v)), (v) => { estado.topK = v === SIN_K ? 0 : v; dibujar(); }));
    }
    if (controles.includes("top-p")) {
      panel.appendChild(crearPerilla("Top-p", 0.05, 1, 0.05, 1, (v) => v.toFixed(2), (v) => { estado.topP = v; dibujar(); }));
    }
    if (controles.includes("sortear")) {
      const tirar = crear("button", "boton fuerte", "🎲 Sortear");
      tirar.addEventListener("click", sortear);
      sorteo.append(tirar, salidas);
    }

    raiz.append(tabla);
    if (controles.length || nota) {
      const costado = crear("div", "grafico-costado");
      costado.append(panel);
      // «En carrera» solo tiene sentido si hay perillas que recortan.
      if (controles.includes("top-k") || controles.includes("top-p")) costado.append(carrera);
      costado.append(sorteo);
      // Si la diapositiva trae una nota escrita en el HTML, va debajo de las perillas.
      if (nota) costado.append(nota);
      raiz.append(costado);
    }

    let resultado = null;

    function dibujar() {
      resultado = calcular(estado.temperatura, estado.topK, estado.topP);
      const { vivos, probabilidades } = resultado;
      const mostradas = probabilidades.slice(0, cuantasFilas);
      const restoP = probabilidades.slice(cuantasFilas).reduce((suma, p) => suma + p, 0);
      const restoVivos = vivos.slice(cuantasFilas).reduce((suma, n) => suma + n, 0);
      // Cada barra es su parte del 100%: una barra llena sería toda la probabilidad.

      filas.forEach((fila, i) => {
        fila.relleno.style.width = mostradas[i] * 100 + "%";
        fila.valor.textContent = porcentaje(mostradas[i]);
        fila.fila.classList.toggle("tapada", vivos[i] === 0);

        // logit ÷ temperatura. El número es la división del logit tal como se muestra
        // (con dos decimales), para que la cuenta de la pantalla dé exacta.
        // La barra usa la misma escala que la del logit, medida desde el favorito:
        // con temperatura 1 las dos barras son iguales; con menos, las diferencias
        // con el favorito se agrandan; con más, se achican.
        fila.numeroDivision.textContent = (Number(fila.logit.toFixed(2)) / estado.temperatura).toFixed(2);
        const distancia = (LOGIT_MAXIMO - fila.logit) / estado.temperatura;
        const ancho = 1 - distancia / (LOGIT_MAXIMO - logitMinimo);
        fila.rellenoDivision.style.width = Math.max(0, ancho) * 100 + "%";
      });
      nombreResto.textContent = "el resto...";
      rellenoResto.style.width = restoP * 100 + "%";
      valorResto.textContent = porcentaje(restoP);
      filaResto.classList.toggle("tapada", restoVivos === 0);

      const enCarrera = vivos.reduce((suma, n) => suma + n, 0);
      carrera.innerHTML = "En carrera: <strong>" + miles(enCarrera) + "</strong> de " + miles(PROXIMO.vocabulario) + " tokens";
      salidas.textContent = "";
    }

    function sortear() {
      // Tirar el dado cargado: un número al azar entre 0 y 1, y vemos en qué grupo cae.
      let dado = Math.random();
      let posicion = 0;
      while (posicion < GRUPOS.length - 1 && dado >= resultado.probabilidades[posicion]) {
        dado -= resultado.probabilidades[posicion];
        posicion++;
      }
      const pieza = GRUPOS[posicion].pieza;
      const ficha = crear("span", pieza === null ? "ficha rara" : "ficha color-0", pieza === null ? "(uno del resto)" : visible(pieza));
      salidas.appendChild(ficha);
      if (salidas.children.length > 14) salidas.removeChild(salidas.firstChild);
    }

    dibujar();
  }

  // ------------------------------------------------------------ 4. el loop

  function armarLoop(raiz) {
    const generacion = DATOS.generacion;
    const FILAS = 6; // cinco favoritos y «el resto»

    // A la izquierda: el texto que entra a la red. Empieza con el texto inicial y crece de a un token.
    const izquierda = crear("div", "entrada-loop");
    const texto = crear("div", "caja texto-loop");
    const fijo = crear("span", "", generacion.texto);
    const escrito = crear("span", "azul");
    texto.append(fijo, escrito);
    const vuelve = crear("p", "vuelve", "↺ el token que salió vuelve a entrar");
    const botones = crear("div", "botonera");
    const siguiente = crear("button", "boton fuerte", "Siguiente token ▸");
    const reiniciar = crear("button", "boton", "Empezar de nuevo");
    botones.append(siguiente, reiniciar);
    izquierda.append(texto, vuelve, botones);

    // A la derecha: la misma red de las otras diapositivas, y las barras del próximo token.
    const salida = crear("div", "salida-red");
    const titulo = crear("p", "titulo-red");
    const red = armarRed(FILAS, true);
    const barras = crear("div", "barras");
    const pie = crear("p", "pie-red", "red neuronal");
    const respuesta = crear("p", "respuesta-red");
    salida.append(titulo, red.dibujo, barras, pie, respuesta);
    raiz.append(izquierda, salida);

    const filas = Array.from({ length: FILAS }, (_, i) => {
      const fila = crearBarra("");
      if (i === FILAS - 1) fila.fila.classList.add("resto");
      barras.appendChild(fila.fila);
      return fila;
    });

    let paso = 0;
    let ocupado = false;
    let corrida = 0; // cambia al empezar de nuevo, para abandonar lo que estaba en marcha

    /** Deja las barras vacías y actualiza los carteles. */
    function vaciar() {
      filas.forEach((fila) => {
        fila.etiqueta.textContent = "";
        fila.relleno.style.width = "0%";
        fila.valor.textContent = "";
        fila.fila.classList.remove("viva");
      });
      const total = generacion.pasos.length;
      titulo.textContent = paso >= total ? "Fin del ejemplo" : "Paso " + (paso + 1) + " de " + total + ": ¿qué token sigue?";
      respuesta.innerHTML = 'Salió: <span class="gris">…</span>';
      siguiente.disabled = paso >= total;
    }

    siguiente.addEventListener("click", () => {
      if (ocupado || paso >= generacion.pasos.length) return;
      ocupado = true;
      const mia = corrida;
      const actual = generacion.pasos[paso];
      const favoritos = actual.favoritos.slice(0, FILAS - 1);
      const resto = Math.max(0, 1 - favoritos.reduce((suma, favorito) => suma + favorito.p, 0));
      // Las probabilidades de las barras: los favoritos, relleno con ceros si son menos de cinco, y el resto.
      const p = favoritos.map((favorito) => favorito.p);
      while (p.length < FILAS - 1) p.push(0);
      p.push(resto);
      // Cuál salió en el sorteo. Si no está entre los favoritos, se marca «el resto».
      let elegida = favoritos.findIndex((favorito) => favorito.pieza === actual.elegido);
      if (elegida < 0) elegida = FILAS - 1;
      const azar = generador(200 + paso); // cada paso enciende distinto las neuronas de entrada
      const entrada = [azar(), azar(), azar(), azar()].map((valor) => 0.15 + 0.8 * valor);

      vaciar();
      vuelve.classList.remove("activo");
      // 1. El texto entra a la red y la señal la recorre.
      red.animar({ entrada, p, ganadora: elegida }, () => {
        if (mia !== corrida) return;
        // 2. Salen las probabilidades, y se marca el token que salió en el sorteo.
        filas.forEach((fila, i) => {
          const esResto = i === FILAS - 1;
          fila.etiqueta.textContent = esResto ? "el resto" : favoritos[i] ? visible(favoritos[i].pieza) : "";
          fila.relleno.style.width = p[i] * 100 + "%";
          fila.valor.textContent = esResto || favoritos[i] ? porcentaje(p[i]) : "";
          fila.fila.classList.toggle("viva", i === elegida);
        });
        respuesta.innerHTML = "Salió: <strong></strong>";
        respuesta.querySelector("strong").textContent = visible(actual.elegido);
        // 3. Un momento después, ese token se agrega al texto: en el próximo paso entra a la red.
        setTimeout(() => {
          if (mia !== corrida) return;
          const nuevo = crear("span", "token-nuevo", actual.elegido);
          escrito.appendChild(nuevo);
          vuelve.classList.add("activo");
          paso++;
          ocupado = false;
          siguiente.disabled = paso >= generacion.pasos.length;
          if (paso >= generacion.pasos.length) titulo.textContent = "Fin del ejemplo";
        }, 700);
      });
    });

    reiniciar.addEventListener("click", () => {
      corrida++;
      paso = 0;
      ocupado = false;
      escrito.textContent = "";
      vuelve.classList.remove("activo");
      red.animar({ entrada: [0, 0, 0, 0], p: new Array(FILAS).fill(0), ganadora: -1 }, () => {});
      vaciar();
    });

    vaciar();
  }

  // ------------------------------------------------------------------ armado

  document.querySelectorAll("[data-interactivo]").forEach((raiz) => {
    const armar = {
      clasificador: armarClasificador,
      llm: armarLLM,
      tokenizador: armarTokenizador,
      grafico: armarGrafico,
      loop: armarLoop,
    }[raiz.dataset.interactivo];
    armar(raiz);
  });

  // Después de un clic el botón suelta el foco: así la barra espaciadora y las flechas
  // siguen pasando de diapositiva, en vez de volver a apretar el botón.
  document.querySelectorAll("[data-interactivo] button").forEach((boton) => {
    boton.addEventListener("click", () => boton.blur());
  });
})();
