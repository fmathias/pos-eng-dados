
def processar_dados_cidade(clima, qualidade_estado, qualidade_cidade, cidade):
    return {
        "cidade": cidade,
        "clima": clima,
        "dados_pais": qualidade_estado,
        "dados_ar": qualidade_cidade,
    }
