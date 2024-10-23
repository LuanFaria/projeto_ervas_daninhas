import geopandas as gpd
import warnings
import os
import openpyxl
import pandas as pd 

warnings.filterwarnings("ignore")  #IGNORA OS AVISOS DE ALERTASD

#****entrada****
fazendas = gpd.read_file('X:/Sigmagis/Projetos/Grupo Ipiranga/ESTUDO ERVAS/Vetores/Shape/BASE_TALHOES/BASE_TALHOES_MOCOCA.shp')
pasta_ervas = os.path.join('X:/Sigmagis/Projetos/Grupo Ipiranga/ESTUDO ERVAS/Vetores/Shape/ERVAS_TESTE_3/23_24/por_img/') #caminho original
nome_das_pastas = ['01_outubro','02_novembro','03_dezembro','04_janeiro','05_fevereiro','06_marco','07_abril','08_maio','09_junho','10_julho','11_agosto','12_setembro']
#------------------------------------------------------------------------------------------------------------------------

saida_planilha = 'C:/SAIDA/planilhas/'
if not os.path.exists(saida_planilha):
    os.makedirs(saida_planilha)

saida_shp_recorrencia = ('C:/SAIDA/recorrencias/')
if not os.path.exists(saida_shp_recorrencia):
    os.makedirs(saida_shp_recorrencia)

saida =('C:/SAIDA/') 

#tava usando pra teste
#nome_das_pastas = ['outubro','novembro','dezembro','janeiro','marco']
#pasta_ervas = os.path.join('C:/Users/Luan/Desktop/PROJETO_ERVAS-20241007T003219Z-001/PROJETO_ERVAS/teste_entrada/meses/')

f=fazendas[['FAZENDA','geometry']]
f['FAZENDAS'] = f['FAZENDA']
dissolve_fazendas = f.dissolve('FAZENDA')
dissolve_fazendas['AREA_FAZENDA'] = dissolve_fazendas.area/10000
print(dissolve_fazendas)

lista_ervas = []
for pastas in nome_das_pastas:
    pasta_unica = pasta_ervas + pastas

    for ervas in os.listdir(pasta_unica):
                    if ervas.endswith('.shp'):
                        
                        e = gpd.read_file(os.path.join(pasta_unica,ervas))   
                        erva_unica=e[['DATA_IMG','geometry']]
                        erva_unica['AREA_ERVA'] = erva_unica.area/10000
                        intersect= erva_unica.overlay(dissolve_fazendas, how='intersection')
                        intersect['FAZ'] = intersect['FAZENDAS']
                        intersect_diss = intersect.dissolve('FAZENDAS')
                        lista_ervas.append(intersect_diss)
                        
inter_final = []
inter_final.append(lista_ervas[0])            
for i in range(1, len(lista_ervas)):
    intersect_2= lista_ervas[i].overlay(lista_ervas[i-1], how='intersection')
    inter_final.append(intersect_2)
    
cont = 0
for c in inter_final:
    cont = cont + 1
    nome = str(cont)
    c['AREA_RECORRENCIA'] = c.area/10000

    if 'FAZ_2' in c.columns:
        c.rename(columns={'FAZ_2': 'FAZ'}, inplace=True)
    if 'DATA_IMG_1' in c.columns:
        c.rename(columns={'DATA_IMG_1': 'DATA_IMG'}, inplace=True)
    if 'DATA_IMG_2' in c.columns:
        c.rename(columns={'DATA_IMG_2': 'IMG_ANTERIOR'}, inplace=True)
    if 'IMG_ANTERIOR' not in c.columns:
          c['IMG_ANTERIOR'] = '01/01/1900'
        
    c.loc[c['IMG_ANTERIOR'] == '01/01/1900', 'AREA_RECORRENCIA'] = 0

    dif_ervas_banco = c[['FAZ','IMG_ANTERIOR','DATA_IMG','AREA_RECORRENCIA']]
    dif_ervas_shp = c[['FAZ','IMG_ANTERIOR','DATA_IMG','AREA_RECORRENCIA','geometry']]

# Salvando o DataFrame em um arquivo Excel
    #df = pd.DataFrame(dif_ervas_banco)
    dif_ervas_banco.to_excel(saida_planilha + f'resultado_{nome}.xlsx', index=False)
    dif_ervas_shp.to_file(saida_shp_recorrencia+'/Res_'+nome+'.shp')         

    folder_path = 'caminho/para/suas/planilhas'

df_list = []

# Loop sobre os arquivos no diretório
for file_name in os.listdir(saida_planilha):
    if file_name.endswith('.xlsx'):  # Verifica se é um arquivo Excel
        file_path = os.path.join(saida_planilha, file_name)
        # Lê o arquivo Excel e adiciona o DataFrame à lista
        df = pd.read_excel(file_path)
        df_list.append(df)

# Concatena todos os DataFrames em um único
combined_df = pd.concat(df_list, ignore_index=True)



# Salva o DataFrame combinado em um novo arquivo Excel
combined_df.to_excel(saida+'FINAL.xlsx', index=False)