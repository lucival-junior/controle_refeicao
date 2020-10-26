#variaveis de arquivo saida
primeira_limpeza = "primeira_limpeza.txt"
segunda_limpeza = "segunda_limpeza.txt"
terceira_limpeza = "terceira_limpeza.txt"

def limpeza_sococo():
    busca_sococo_cod = '21'
    busca_sococo_emp = "SOCOCO"
    busca_sococo_valor = "Valor"
    
    with open(primeira_limpeza, 'w', encoding="ISO-8859-1") as out_f:
        with open('arquivo_sem_tratamento.txt', "r", encoding="ISO-8859-1") as in_f:
            for line in in_f:
                if busca_sococo_cod in line:
                    out_f.write(line)

    # Inicia a segunda limpeza do arquivo gerado acima.
    # Gera o arquivo final limpo
    with open(segunda_limpeza, 'w', encoding="ISO-8859-1") as out_f:
        with open('primeira_limpeza.txt', "r", encoding="ISO-8859-1") as in_f:
            for line in in_f:
                if busca_sococo_emp in line:
                    pass
                else:
                    out_f.write(line)
                    
    with open(terceira_limpeza, 'w', encoding="ISO-8859-1") as out_f:
       with open('segunda_limpeza.txt', "r", encoding="ISO-8859-1") as in_f:
           for line in in_f:
               if busca_sococo_valor in line:
                   pass
               else:
                   out_f.write(line)

def limpeza_acqua():
    busca_acqua_cod = '40'
    busca_acqua_emp = "ACQUA"
    busca_acqua_valor = "Valor"
    
    with open(primeira_limpeza, 'w', encoding="ISO-8859-1") as out_f:
        with open('arquivo_sem_tratamento.txt', "r", encoding='ISO-8859-1') as in_f:
            for line in in_f:
                if busca_acqua_cod in line:
                    out_f.write(line)

    # Inicia a segunda limpeza do arquivo gerado acima.
    # Gera o arquivo final limpo
    with open(segunda_limpeza, 'w', encoding="ISO-8859-1") as out_f:
        with open('primeira_limpeza.txt', "r", encoding="ISO-8859-1") as in_f:
            for line in in_f:
                if busca_acqua_emp in line:
                    pass
                else:
                    out_f.write(line)
    with open(terceira_limpeza, 'w', encoding="ISO-8859-1") as out_f:
        with open('segunda_limpeza.txt', "r", encoding="ISO-8859-1") as in_f:
            for line in in_f:
                if busca_acqua_valor in line:
                    pass
                else:
                    out_f.write(line)

def limpeza_amafibra():
    busca_amafibra_cod = '30'
    busca_amafibra_emp = "AMAFIBRA"
    busca_amafibra_valor = "Valor"
    
    with open(primeira_limpeza, 'w', encoding="ISO-8859-1") as out_f:
        with open('arquivo_sem_tratamento.txt', "r", encoding="ISO-8859-1") as in_f:
            for line in in_f:
                if busca_amafibra_cod in line:
                    out_f.write(line)

    # Inicia a segunda limpeza do arquivo gerado acima.
    # Gera o arquivo final limpo
    with open(segunda_limpeza, 'w', encoding="ISO-8859-1") as out_f:
        with open('primeira_limpeza.txt', "r", encoding="ISO-8859-1") as in_f:
            for line in in_f:
                if busca_amafibra_emp in line:
                    pass
                else:
                  out_f.write(line)
                
    with open(terceira_limpeza, 'w', encoding="ISO-8859-1") as out_f:
       with open('segunda_limpeza.txt', "r", encoding="ISO-8859-1") as in_f:
           for line in in_f:
               if busca_amafibra_valor in line:
                   pass
               else:
                   out_f.write(line)           
