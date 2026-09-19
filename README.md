# Sysvar Imagens

Gerador em lote das imagens de teste do catálogo Sysvar.

## Padrão
- 1 imagem principal por referência
- catálogo/studio, produto inteiro centralizado
- fundo branco/neutro
- sem texto, sem logo e sem modelo
- saída PNG 600 x 1200 px (proporção 1:2)
- nome = referência sem hífens: `27-01-01002 -> 270101002.png`

## Uso

Instale:

```powershell
pip install -r requirements.txt
```

Defina a chave da OpenAI:

```powershell
$env:OPENAI_API_KEY="SUA_CHAVE"
```

Para gerar a partir de CSV:

```powershell
python gerar_imagens.py --csv produtos.csv
```

CSV esperado:

```csv
referencia,descricao
27-01-01002,Calça Jeans Mom Safira
```

Para continuar uma execução interrompida, execute o mesmo comando novamente. Arquivos já existentes são ignorados por padrão.

Use `--force` para regenerar arquivos existentes.

As imagens ficam em `imagens/`.
