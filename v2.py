
import geopandas as gpd
import os

fazendas = gpd.read_file('C:/Users/Luan/Desktop/PROJETO_ERVAS-20241007T003219Z-001/PROJETO_ERVAS/BASE_TALHOES_MOCOCA.shp')
caminho_pasta = 'C:/Users/Luan/Desktop/PROJETO_ERVAS-20241007T003219Z-001/PROJETO_ERVAS/teste_saida/recorrencias'
caminho_saida = "C:/Users/Luan/Desktop/PROJETO_ERVAS-20241007T003219Z-001/PROJETO_ERVAS/teste_saida/fim"
os.makedirs(caminho_saida, exist_ok=True)  # Criar a pasta de saída se não existir

# Obtenha uma lista de arquivos shapefile na pasta
arquivos_shapefiles = [os.path.join(caminho_pasta, f) for f in os.listdir(caminho_pasta) if f.endswith('.shp')]

# Leia o primeiro shapefile como base
shapefile_base = gpd.read_file(arquivos_shapefiles[0])

for i in range(1, len(arquivos_shapefiles)):
    # Mescle o shapefile_base com o próximo shapefile
    shapefile_atual = gpd.read_file(arquivos_shapefiles[i])
    
    # Combine o shapefile_base com o shapefile_atual usando o método 'overlay'
    shapefile_base = shapefile_base.overlay(shapefile_atual, how='union')
    
    # Remover todas as colunas, exceto a coluna geometry
    shapefile_base = shapefile_base[['geometry']]
    
    # Aplicar o dissolve para unir os polígonos
    shapefile_base = shapefile_base.dissolve()

    gdf_interseccao = gpd.overlay(shapefile_base, fazendas, how='intersection')

    #area_gis
    gdf_interseccao['AREA_GIS'] = gdf_interseccao.area / 10000  # Conversão para hectares

    # Salvar o shapefile mesclado e dissolvido na pasta de saída
    caminho_arquivo_saida = os.path.join(caminho_saida, f"shapefile_dissolve_{i}.shp")
    gdf_interseccao.to_file(caminho_arquivo_saida)

print(f"Mesclagem e dissolve aplicados com sucesso! Arquivos salvos em: {caminho_saida}")