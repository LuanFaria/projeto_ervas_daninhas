import os
import geopandas as gpd
import pandas as pd
import re
import warnings


directory = 'X://Sigmagis//Projetos//Grupo Ipiranga//ESTUDO ERVAS//Vetores//Shape//ERVAS_TESTE_3//23_24'
talhoes_path = 'X:/Sigmagis/Projetos/Grupo Ipiranga/ESTUDO ERVAS/Vetores/Shape/BASE_TALHOES/BASE_TALHOES_MOCOCA.shp'

warnings.filterwarnings("ignore")  #IGNORA OS AVISOS DE ALERTASD
#PARTE 1: Ervas Mensal
def validate_and_fix_topology(gdf):
    """
    Função para corrigir a topologia dos shapefiles, corrigindo geometrias inválidas.
    """
    # Aplicar buffer(0) para corrigir possíveis problemas topológicos
    gdf['geometry'] = gdf['geometry'].buffer(0)
    return gdf

def merge_and_dissolve_shapes(directory):
    # Lista para armazenar os shapefiles dissolvidos de cada subpasta
    dissolved_shapes = []
    
    # Loop para percorrer todas as subpastas no diretório
    for subdir, _, files in os.walk(directory):
        shapefiles = []
        
        # Coletar todos os shapefiles da subpasta atual
        for file in files:
            if file.endswith(".shp"):
                filepath = os.path.join(subdir, file)
                gdf = gpd.read_file(filepath)
                
                # Validar e corrigir a topologia
                gdf = validate_and_fix_topology(gdf)
                shapefiles.append(gdf)
        
        # Realizar o merge dos shapefiles da subpasta
        if shapefiles:
            merged = gpd.GeoDataFrame(pd.concat(shapefiles, ignore_index=True))
            
            # Realizar o dissolve baseado em um campo, ou use o default (tudo em um único polígono)
            dissolved = merged.dissolve()

            # Pegar o nome da subpasta atual
            subfolder_name = os.path.basename(subdir)

            # Definir o caminho de saída com o nome da subpasta
            output_path = os.path.join(directory, f"{subfolder_name}_merge_mensal.shp")

            # Salvar o shapefile resultantclear
            dissolved.to_file(output_path)
            #print(f"Shapefile salvo: {output_path}")
            
            
            # Adicionar o shapefile dissolvido à lista para o merge final
            dissolved_shapes.append(dissolved)

    # Realizar o merge de todos os shapefiles dissolvidos
    #if dissolved_shapes:
        #consolidated = gpd.GeoDataFrame(pd.concat(dissolved_shapes, ignore_index=True))
        
        # Realizar o dissolve final
        #final_dissolved = consolidated.dissolve()

        # Definir o caminho de saída para o shapefile consolidado
        #output_consolidated_path = os.path.join(directory, "area_consolidada.shp")

        # Salvar o shapefile final dissolvido
        #final_dissolved.to_file(output_consolidated_path)
        #print(f"Shapefile consolidado salvo: {output_consolidated_path}")


#output_directory = os.path.join(directory, "merge")
print("\nPARTE 1: Gerando Ervas Mensais")
merge_and_dissolve_shapes(directory)

#----------------------------------------------------------------------------------------------------------------
#PARTE 2: Ervas Acumuladas e Planilha Mensal

def validate_and_fix_topology(gdf):
    """
    Função para corrigir a topologia dos shapefiles, corrigindo geometrias inválidas.
    """
    gdf['geometry'] = gdf['geometry'].buffer(0)
    return gdf

def merge_and_dissolve_by_rule(directory, output_directory):
    # Obter todos os arquivos .shp do diretório
    shapefile_dict = {}
    for subdir, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".shp"):
                # Usar regex para extrair o índice do nome do arquivo
                match = re.match(r"(\d+)_.*\.shp", file)
                if match:
                    index = int(match.group(1))  # Extrair o número inicial do nome
                    filepath = os.path.join(subdir, file)
                    if index not in shapefile_dict:
                        shapefile_dict[index] = []
                    shapefile_dict[index].append(filepath)
    
    # Ordenar os índices para garantir que os arquivos sejam processados na ordem correta
    indices = sorted(shapefile_dict.keys())

    # Realizar merge e dissolve acumulativo
    for i in range(1, len(indices)):
        merged_shapes = []
        for j in range(i+1):
            index = indices[j]
            for shapefile in shapefile_dict[index]:
                # Ler o shapefile
                gdf = gpd.read_file(shapefile)

                # Validar e corrigir a topologia
                gdf = validate_and_fix_topology(gdf)
                merged_shapes.append(gdf)
        
        # Concatenar e dissolver os shapefiles acumulados
        if merged_shapes:
            merged = gpd.GeoDataFrame(pd.concat(merged_shapes, ignore_index=True))
            dissolved = merged.dissolve()

            # Criar o nome do arquivo de saída com base nos índices acumulados
            accumulated_indices = "_".join([str(indices[k]) for k in range(i+1)])
            output_filename = f"merge_acumulado_{accumulated_indices}.shp"
            output_path = os.path.join(output_directory, output_filename)

            dissolved['AREA_GIS'] = dissolved.area / 10000  # Conversão para hectares

            # Salvar o shapefile acumulado e dissolvido
            dissolved.to_file(output_path)
            #print(f"Shapefile salvo: {output_path}")
            

output_directory = os.path.join(directory, "saida/ervas_acumuladas")
os.makedirs(output_directory, exist_ok=True)
print("\nPARTE 2: Exportando Ervas Mensais e Ervas Acumuladas para Excel ")
merge_and_dissolve_by_rule(directory, output_directory)


# Carregar o shapefile de referência
gdf_referencia = gpd.read_file(talhoes_path)

# Inicializar uma lista para armazenar os dados de cada interseção
lista_df_interseccao = []

# Iterar por todos os arquivos na pasta
for arquivo in os.listdir(output_directory):
    if arquivo.endswith(".shp"):  # Verifica se o arquivo é um shapefile
        caminho_shapefile = os.path.join(output_directory, arquivo)
        gdf = gpd.read_file(caminho_shapefile)  # Lê o shapefile como GeoDataFrame
        
        # Realizar a interseção entre o shapefile atual e o shapefile de referência
        gdf_interseccao = gpd.overlay(gdf, gdf_referencia, how='intersection')
        
        # Adiciona uma coluna com o nome do arquivo original
        
        gdf_interseccao['Arquivo'] = arquivo
        gdf_interseccao['AREA_GIS'] = gdf_interseccao.area/10000
        
        # Adiciona o GeoDataFrame resultante à lista
        lista_df_interseccao.append(gdf_interseccao)

# Concatenar todos os GeoDataFrames resultantes em um único DataFrame
df_concatenado_interseccao = pd.concat(lista_df_interseccao)

colunas_para_remover = ['id','DATA_IMG', 'LAYER', 'CNPJ','geometry']  # Substitua pelos nomes das colunas que deseja remover
df_concatenado_interseccao = df_concatenado_interseccao.drop(columns=colunas_para_remover, errors='ignore')

# Exportar o DataFrame para um arquivo Excel
caminho_saida = directory+'/saida/planilhas/ervas_mensal_acumulado_fazendas.xlsx'  
df_concatenado_interseccao.to_excel(caminho_saida, index=False)
lista_acumulado=[]
for mensal in os.listdir(directory):
    if mensal.endswith("mensal.shp"):  # Verifica se o arquivo é um shapefile
        caminho_shapefile = os.path.join(directory, mensal)
        gdf = gpd.read_file(caminho_shapefile)  # Lê o shapefile como GeoDataFrame
        gdf_interseccao_mensal = gpd.overlay(gdf, gdf_referencia, how='intersection')
        
        gdf_interseccao_mensal['Arquivo'] = mensal  # Adiciona uma coluna com o nome do arquivo
        gdf_interseccao_mensal['id'] = mensal[:2]
        gdf_interseccao_mensal['AREA_GIS'] = gdf_interseccao_mensal.area/10000
        lista_acumulado.append(gdf_interseccao_mensal)  # Adiciona os dados do shapefile à lista

# Concatenar todos os GeoDataFrames em um único DataFrame
df_conca = pd.concat(lista_acumulado)

colunas_para_remover = ['DATA_IMG', 'LAYER', 'CNPJ','geometry']  # Substitua pelos nomes das colunas que deseja remover
df_conca = df_conca.drop(columns=colunas_para_remover, errors='ignore')

# Exportar o DataFrame para um arquivo Excel
caminho_saida = directory+'/saida/planilhas/ervas_mensal_fazendas.xlsx'   # Substitua pelo caminho desejado
df_conca.to_excel(caminho_saida, index=False)

print(f"Dados exportados com sucesso para {caminho_saida}")

#-------------------------------------------------------------------------------------------
#Parte 3: Recorrencias
def calcular_area_ha(gdf, area_field):
    """
    Calcula a área em hectares e insere no campo especificado.
    """
    gdf[area_field] = gdf['geometry'].area / 10000  # Conversão para hectares
    return gdf

def intersecao_sequencial(directory, talhoes_path):
    # Listar todos os shapefiles no diretório dissolve_mensal
    shapefiles = sorted([f for f in os.listdir(directory) if f.endswith('.shp')])
    
    # Verificar se há shapefiles suficientes para intersecção
    if len(shapefiles) < 2:
        print("Número insuficiente de shapefiles para interseção sequencial.")
        return
    
    # Lista para armazenar os resultados das interseções sequenciais
    intersecoes_sequenciais = []

    # Fazer a interseção sequencial dos shapefiles
    for i in range(len(shapefiles) - 1):
        file1 = os.path.join(directory, shapefiles[i])
        file2 = os.path.join(directory, shapefiles[i + 1])
        
        gdf1 = gpd.read_file(file1)
        gdf2 = gpd.read_file(file2)
        
        # Realizar a interseção entre os dois shapefiles
        interseccao = gpd.overlay(gdf1, gdf2, how='intersection')

        # Calcular a área em hectares para cada resultado de interseção
        interseccao = calcular_area_ha(interseccao, 'AREA_GIS_1')
        
        # Nomear o shapefile resultante de acordo com a sequência
        interseccao_path = os.path.join(directory, f"intersect_{i+1}_{i+2}.shp")
        interseccao.to_file(interseccao_path)
        intersecoes_sequenciais.append(interseccao)
        #print(f"Interseção sequencial salva: {interseccao_path}")
        

    # Carregar o shapefile de BASE_TALHOES para fazer a interseção final
    talhoes = gpd.read_file(talhoes_path)

    cont = 0
    # Fazer a interseção de cada shapefile resultante da interseção sequencial com BASE_TALHOES
    for i, interseccao in enumerate(intersecoes_sequenciais):
        interseccao_final = gpd.overlay(interseccao, talhoes, how='intersection')
        cont = cont + 1
        nome = str(cont)
        # Calcular as áreas em hectares para o resultado final
        interseccao_final = calcular_area_ha(interseccao_final, 'AREA_GIS_2')
        interseccao_final['ID'] = i+1

        # Nomear o shapefile resultante
        final_output_path = os.path.join(saida_intersect, f"final_intersect_{i+1}_with_talhoes.shp")
        interseccao_final.to_file(final_output_path)
        # Inicializar uma lista para armazenar os dados de cada shapefile
        lista_df = []
        colunas_especificas = ['ID','FAZENDA', 'DESC_FDA', 'AREA_GIS_2']

        # Iterar por todos os arquivos na pasta
        for arquivo in os.listdir(saida_intersect):
            if arquivo.endswith(".shp"):  # Verifica se o arquivo é um shapefile
                caminho_shapefile = os.path.join(saida_intersect, arquivo)
                gdf = gpd.read_file(caminho_shapefile)  # Lê o shapefile como GeoDataFrame
                gdf = gdf[[col for col in colunas_especificas if col in gdf.columns]]
                gdf['Arquivo'] = arquivo  # Adiciona uma coluna com o nome do arquivo
                lista_df.append(gdf)  # Adiciona os dados do shapefile à lista

        # Concatenar todos os GeoDataFrames em um único DataFrame
        df_concatenado = pd.concat(lista_df)

        # Exportar o DataFrame para um arquivo Excel
        caminho_saida = directory+'/saida/planilhas/ervas_recorrentes_mensal_fazendas.xlsx' 
        df_concatenado.to_excel(caminho_saida, index=False)


saida_intersect = directory+'/saida/intersect_final/'

if not os.path.exists(saida_intersect):
    os.makedirs(saida_intersect)
print('\nPARTE 3: Exportando Recorrencias Mensais')
intersecao_sequencial(directory, talhoes_path)

#------------------------------------------------------------------------------------------------------------------
#Parte 4: Recorrencia Acumulada
print('\nPARTE 4: Exportando Recorrencias Mensais Acumuladas')
gdf_referencia = gpd.read_file(talhoes_path)
# Caminho da pasta contendo os shapefiles a serem mesclados
caminho_pasta = saida_intersect
caminho_excel = os.path.join(directory+'/saida/planilhas/ervas_recorrentes_mensal_acumulado_fazendas.xlsx')
caminho_saida = directory+'/saida/acumulado_recorrencia_erva/'
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
    gdf_interseccao = gpd.overlay(shapefile_base, talhoes_path, how='intersection')

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
df_final.to_excel(caminho_excel, index=False)

print(f"Mesclagem e dissolve aplicados com sucesso! Arquivos shapefile salvos em: {caminho_saida}")
print(f"Resultados salvos em planilha Excel: {caminho_excel}")
