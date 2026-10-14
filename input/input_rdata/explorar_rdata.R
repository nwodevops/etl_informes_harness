archivo_script <- sys.frame(1)$ofile
ruta_datos <- if (is.null(archivo_script) || !nzchar(archivo_script)) {
  getwd()
} else {
  dirname(normalizePath(archivo_script))
}

archivos <- list.files(
  path = ruta_datos,
  pattern = "\\.RData$",
  full.names = TRUE
)

if (length(archivos) == 0) {
  stop("No se encontraron archivos .RData en la carpeta del script.")
}

for (archivo in sort(archivos)) {
  entorno <- new.env(parent = emptyenv())
  objetos <- load(archivo, envir = entorno)

  cat("\n###", basename(archivo), "###\n")

  if (length(objetos) == 0) {
    cat("Archivo sin objetos.\n")
    next
  }

  for (nombre in objetos) {
    objeto <- entorno[[nombre]]
    dimensiones <- dim(objeto)
    resumen_dimensiones <- if (is.null(dimensiones)) {
      "sin dimensiones"
    } else {
      paste(dimensiones, collapse = " x ")
    }

    cat(
      "\nObjeto:", nombre,
      "\nClase:", paste(class(objeto), collapse = ", "),
      "\nDimensiones:", resumen_dimensiones,
      "\nEstructura:\n"
    )
    str(objeto, max.level = 2)
  }
}