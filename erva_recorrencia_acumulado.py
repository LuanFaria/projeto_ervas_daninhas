import geopandas as gpd
import pandas as pd
import os

# Ler o shapefile de fazendas
fazendas = gpd.read_file('C:/Users/Luan/Desktop/PROJETO_ERVAS-20241007T003219Z-001/PROJETO_ERVAS/BASE_TALHOES_MOCOCA.shp')

# Caminho da pasta contendo os shapefiles a serem mesclados
caminho_pasta = 'C:/Users/Luan/Desktop/PROJETO_ERVAS-20241007T003219Z-001/PROJETO_ERVAS/teste_saida/recorrencias'
caminho_saida = "C:/Users/Luan/Desktop/PROJETO_ERVAS-20241007T003219Z-001/PROJETO_ERVAS/teste_saida/fim"
os.makedirs(caminho_saida, exist_ok=True)  # Criar a pasta de saída se não existir

# Obtenha uma lista de arquivos shapefile na pasta
arquivos_shapefiles = [os.path.join(caminho_pasta, f) for f in os.listdir(caminho_pasta) if f.endswith('.shp')]

# Leia o primeiro shapefile como base
shapefile_base = gpd.read_file(arquivos_shapefiles[0])

# Lista para armazenar todos os resultados
todos_resultados = []

for i in range(1, len(arquivos_shapefiles)):
    # Mescle o shapefile_base com o próximo shapefile
    shapefile_atual = gpd.read_file(arquivos_shapefiles[i])
    
    # Combine o shapefile_base com o shapefile_atual usando o método 'overlay'
    shapefile_base = shapefile_base.overlay(shapefile_atual, how='union')
    
    # Remover todas as colunas, exceto a coluna geometry
    shapefile_base = shapefile_base[['geometry']]
    
    # Aplicar o dissolve para unir os polígonos
    shapefile_base = shapefile_base.dissolve()

    # Realizar interseção com o shapefile de fazendas
    gdf_interseccao = gpd.overlay(shapefile_base, fazendas, how='intersection')

    # Calcular a área em hectares
    gdf_interseccao['AREA_GIS'] = gdf_interseccao.area / 10000  # Conversão para hectares

    # Adicionar coluna com o nome do shapefile atual
    gdf_interseccao['Nome_Arquivo'] = os.path.basename(arquivos_shapefiles[i])
    
    # Salvar o shapefile resultante na pasta de saída
    caminho_arquivo_saida = os.path.join(caminho_saida, f"shapefile_dissolve_{i}.shp")
    gdf_interseccao.to_file(caminho_arquivo_saida)

    # Armazenar os resultados na lista
    todos_resultados.append(gdf_interseccao)

# Concatenar todos os resultados em um único DataFrame
df_final = pd.concat([pd.DataFrame(gdf.drop(columns='geometry')) for gdf in todos_resultados], ignore_index=True)

# Salvar todos os resultados em uma única planilha Excel
caminho_excel = os.path.join(caminho_saida, "resultados_interseccao.xlsx")
df_final.to_excel(caminho_excel, index=False)

print(f"Mesclagem e dissolve aplicados com sucesso! Arquivos shapefile salvos em: {caminho_saida}")
print(f"Resultados salvos em planilha Excel: {caminho_excel}")
