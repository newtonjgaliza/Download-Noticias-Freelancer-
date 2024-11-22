#!/bin/bash

# Caminho para a pasta raiz onde estão os arquivos e as subpastas
RAIZ="/home/newton/Documents/images"  # Caminho absoluto para a pasta onde as subpastas estão localizadas
ARQUIVO_CSV="faltantes.csv"  # Nome do arquivo CSV
ARQUIVO_PY="subir_noticia.py"  # Nome do script Python

# Caminho absoluto para os arquivos na pasta raiz
ARQUIVO_CSV_RAIZ="$RAIZ/$ARQUIVO_CSV"
ARQUIVO_PY_RAIZ="$RAIZ/$ARQUIVO_PY"

# Verificando o diretório de execução atual para depuração
echo "Diretório atual de execução: $(pwd)"

# Verificação inicial de arquivos na pasta raiz
echo "Verificando arquivos na pasta raiz ($RAIZ)..."
if [ ! -f "$ARQUIVO_CSV_RAIZ" ]; then
  echo "Erro: Arquivo '$ARQUIVO_CSV' não encontrado na pasta raiz!"
  echo "Verifique se o arquivo '$ARQUIVO_CSV' está localizado em: $ARQUIVO_CSV_RAIZ"
  exit 1
fi
if [ ! -f "$ARQUIVO_PY_RAIZ" ]; then
  echo "Erro: Arquivo '$ARQUIVO_PY' não encontrado na pasta raiz!"
  echo "Verifique se o arquivo '$ARQUIVO_PY' está localizado em: $ARQUIVO_PY_RAIZ"
  exit 1
fi

# Função para verificar se os arquivos estão presentes na subpasta
verificar_arquivos() {
  pasta="$1"
  
  # Imprime o nome da subpasta sendo processada
  echo "Processando a pasta: '$pasta'"
  
  # Verifica se faltantes.csv ou subir_noticia.py não estão na pasta
  if [ ! -f "$pasta/$ARQUIVO_CSV" ] || [ ! -f "$pasta/$ARQUIVO_PY" ]; then
    echo "Arquivos não encontrados na pasta '$pasta'. Copiando..."
    
    # Verificando se os arquivos de origem existem e são legíveis
    if [ ! -r "$ARQUIVO_CSV_RAIZ" ]; then
      echo "Erro: Arquivo '$ARQUIVO_CSV' não encontrado ou não legível!"
      exit 1
    fi
    if [ ! -r "$ARQUIVO_PY_RAIZ" ]; then
      echo "Erro: Arquivo '$ARQUIVO_PY' não encontrado ou não legível!"
      exit 1
    fi

    # Copiar os arquivos para a subpasta
    cp "$ARQUIVO_CSV_RAIZ" "$pasta/"
    cp "$ARQUIVO_PY_RAIZ" "$pasta/"
    
    # Verificar se a cópia foi bem-sucedida
    if [ -f "$pasta/$ARQUIVO_CSV" ] && [ -f "$pasta/$ARQUIVO_PY" ]; then
      echo "Arquivos copiados com sucesso para '$pasta'."
    else
      echo "Erro: Falha ao copiar arquivos para '$pasta'."
    fi
    
    # Executar o script Python na subpasta
    echo "Executando o script Python na pasta '$pasta'..."
    cd "$pasta" || exit
    python3 "$ARQUIVO_PY"  # Executa o script Python
    echo "Execução do script concluída na pasta '$pasta'."
  else
    echo "Arquivos já presentes na pasta '$pasta'. Pulando..."
  fi
}

# Loop para percorrer todas as subpastas dentro de images
echo "Iniciando o processamento das subpastas em '$RAIZ'..."
for pasta in "$RAIZ"/*; do
  if [ -d "$pasta" ]; then  # Verifica se é uma subpasta
    verificar_arquivos "$pasta"  # Chama a função para verificar os arquivos
  fi
done

echo "Processamento concluído em todas as pastas."

