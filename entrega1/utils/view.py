import matplotlib.pyplot as plt
import seaborn as sns

def view_plot_pizza(df, valor_col, label_col, title, size=(8, 8), palette="Set2"):
    """
    Gera um gráfico de pizza a partir de um DataFrame.

    Parâmetros:
    - df: DataFrame com os dados
    - valor_col: nome da coluna com os valores (numéricos)
    - label_col: nome da coluna com os rótulos (strings)
    - title: título do gráfico
    - size: tupla com tamanho do gráfico (largura, altura)
    - palette: nome da paleta de cores do seaborn (opcional)
    """

    plt.figure(figsize=size)

    plt.pie(
        df[valor_col],
        labels=df[label_col],
        autopct='%1.1f%%',
        startangle=140,
        colors=sns.color_palette(palette)
    )

    plt.title(title, fontsize=16)
    plt.axis('equal')  # Deixar o gráfico circular
    plt.tight_layout()
    plt.show()

def view_correlacao(df):
        
    if len(df) > 1:
        plt.figure(figsize=(10, 6))
        sns.regplot(data=df, x='temperatura', y='tempo_medio_aluguel_dias', 
            scatter_kws={'alpha':0.5, 's': df['num_alugueis_cidade']/10}, # Tamanho do ponto pelo num de alugueis
            line_kws={'color':'red'})
        plt.title('Tempo Médio de Aluguel vs. Temperatura da Cidade', fontsize=15)
        plt.xlabel('Temperatura Atual (°C)', fontsize=12)
        plt.ylabel('Tempo Médio de Aluguel (dias)', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

